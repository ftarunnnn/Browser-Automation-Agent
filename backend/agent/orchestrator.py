import asyncio
import time
import json
from datetime import datetime, timezone
from typing import Optional, Callable, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.browser.controller import BrowserController
from backend.browser.actions import ActionDispatcher
from backend.browser.page_analyzer import page_analyzer
from backend.agent.planner import TaskPlanner
from backend.agent.verifier import verifier
from backend.agent.recovery import FailureRecoveryEngine
from backend.agent.memory import TaskMemory
from backend.models.database import TaskModel, TaskStepModel, AgentActionModel, TaskResultModel, ScreenshotModel, ApprovalModel
from backend.models.schemas import BrowserActionSchema


class AgentOrchestrator:
    def __init__(self, planner: Optional[TaskPlanner] = None):
        self.planner = planner or TaskPlanner()
        self.active_tasks: Dict[str, TaskMemory] = {}
        self.controllers: Dict[str, BrowserController] = {}
        self.stop_requested: Dict[str, bool] = {}

    async def run_task(
        self,
        task_id: str,
        instruction: str,
        db: AsyncSession,
        event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes the main Observe -> Plan -> Act -> Verify -> Recover loop for a task.
        """
        memory = TaskMemory(task_id, instruction)
        self.active_tasks[task_id] = memory
        self.stop_requested[task_id] = False

        controller = BrowserController(headless=settings.PLAYWRIGHT_HEADLESS)
        self.controllers[task_id] = controller
        dispatcher = ActionDispatcher(controller)
        recovery_engine = FailureRecoveryEngine(max_retries=settings.MAX_RETRY_ATTEMPTS)

        async def emit(event_type: str, payload: Dict[str, Any]):
            if event_callback:
                try:
                    await event_callback(event_type, payload)
                except Exception as e:
                    print(f"Event callback error: {e}")

        # Step 1: Update Task Status to Planning
        await emit("status_change", {"status": "planning", "message": "Analyzing natural language task..."})
        task_rec = await db.get(TaskModel, task_id)
        if task_rec:
            task_rec.status = "planning"
            await db.commit()

        # Step 2: Generate Plan Milestones
        plan_steps = await self.planner.create_plan(instruction)
        memory.plan_steps = plan_steps

        for idx, step_desc in enumerate(plan_steps, 1):
            step_rec = TaskStepModel(task_id=task_id, step_number=idx, description=step_desc, status="pending")
            db.add(step_rec)
        await db.commit()

        # Step 3: Start Execution Loop
        task_rec = await db.get(TaskModel, task_id)
        if task_rec:
            task_rec.status = "running"
            await db.commit()

        await emit("status_change", {"status": "running", "message": "Browser automation loop started", "steps": plan_steps})
        await controller.initialize()

        step_count = 0
        final_status = "completed"
        error_msg = ""

        try:
            while step_count < settings.MAX_TASK_STEPS:
                if self.stop_requested.get(task_id, False):
                    final_status = "stopped"
                    await emit("status_change", {"status": "stopped", "message": "Task manually stopped by user"})
                    break

                step_count += 1

                # 1. OBSERVE
                page_obs = await page_analyzer.analyze(controller.page)
                formatted_obs = page_obs.format_for_llm()
                memory.current_url = controller.current_url

                if task_rec:
                    task_rec.current_url = controller.current_url
                    await db.commit()

                await emit("page_observation", {
                    "url": controller.current_url,
                    "title": page_obs.title,
                    "element_count": len(page_obs.elements),
                    "headings": page_obs.headings[:5]
                })

                # 2. PLAN NEXT ACTION
                action_schema = await self.planner.select_next_action(
                    instruction,
                    memory.plan_steps,
                    memory.current_step_idx,
                    formatted_obs,
                    memory.completed_actions
                )

                # 3. SAFETY CHECK (HITL)
                if memory.is_sensitive_action(action_schema):
                    approval_rec = ApprovalModel(
                        task_id=task_id,
                        action_type=action_schema.action,
                        description=f"Agent requests confirmation for sensitive action: {action_schema.action} ({action_schema.text or action_schema.reason or ''})",
                        parameters_json=json.dumps(action_schema.model_dump(exclude_none=True)),
                        status="pending"
                    )
                    db.add(approval_rec)
                    task_rec.status = "paused_approval"
                    await db.commit()

                    memory.pending_approval_action = action_schema
                    await emit("approval_required", {
                        "approval_id": approval_rec.id,
                        "action_type": action_schema.action,
                        "description": approval_rec.description,
                        "parameters": action_schema.model_dump(exclude_none=True)
                    })

                    # Wait for user approval or rejection (polling memory flag)
                    approved = False
                    while not approved and not self.stop_requested.get(task_id, False):
                        await asyncio.sleep(1)
                        await db.refresh(approval_rec)
                        if approval_rec.status == "approved":
                            approved = True
                            break
                        elif approval_rec.status == "rejected":
                            final_status = "failed"
                            error_msg = "User rejected sensitive action request."
                            break

                    if not approved:
                        break

                    task_rec.status = "running"
                    await db.commit()
                    await emit("status_change", {"status": "running", "message": "Sensitive action approved. Resuming..."})

                # 4. FINISH CHECK
                if action_schema.action == "finish":
                    extracted = action_schema.extracted_data or {"message": action_schema.reason or "Task finished"}
                    memory.add_extracted_data(extracted)
                    result_rec = TaskResultModel(
                        task_id=task_id,
                        structured_data_json=json.dumps(extracted),
                        extracted_text=page_obs.main_text[:10000]
                    )
                    db.add(result_rec)
                    await db.commit()
                    await emit("task_finish", {"extracted_data": extracted, "reason": action_schema.reason})
                    break

                # 5. ACT
                await emit("action_start", {"action": action_schema.action, "params": action_schema.model_dump(exclude_none=True)})
                start_time = time.time()
                action_res = await dispatcher.execute_action(
                    action_schema.action,
                    action_schema.model_dump(exclude_none=True),
                    task_id=task_id
                )
                exec_time_ms = int((time.time() - start_time) * 1000)

                # Store Action & Screenshot in DB
                action_rec = AgentActionModel(
                    task_id=task_id,
                    action_type=action_schema.action,
                    parameters_json=json.dumps(action_schema.model_dump(exclude_none=True)),
                    status="verified" if action_res.success else "failed",
                    error_message=action_res.message if not action_res.success else None,
                    execution_time_ms=exec_time_ms
                )
                db.add(action_rec)
                await db.commit()

                if action_res.screenshot_path:
                    shot_rec = ScreenshotModel(
                        task_id=task_id,
                        action_id=action_rec.id,
                        filepath=action_res.screenshot_path,
                        url=controller.current_url
                    )
                    db.add(shot_rec)
                    await db.commit()

                # 6. VERIFY & RECOVER
                post_obs = await page_analyzer.analyze(controller.page)
                verify_res = await verifier.verify_action(
                    action_schema.action,
                    action_schema.model_dump(exclude_none=True),
                    page_obs,
                    post_obs,
                    action_res
                )

                if verify_res.verified:
                    memory.record_action_success(action_schema, action_res.data, controller.current_url)
                    await emit("action_verified", {
                        "action": action_schema.action,
                        "message": verify_res.message,
                        "screenshot": action_res.screenshot_path
                    })
                else:
                    memory.record_action_failure(action_schema, verify_res.message)
                    await emit("action_failed", {"action": action_schema.action, "message": verify_res.message})

                    # RECOVERY
                    recovery_strat = recovery_engine.get_recovery_action(
                        action_schema,
                        verify_res.message,
                        post_obs,
                        memory.completed_actions
                    )
                    await emit("recovery_attempt", {"explanation": recovery_strat.explanation, "recovery_action": recovery_strat.action.action})

                    if recovery_strat.action.action == "finish":
                        final_status = "failed"
                        error_msg = recovery_strat.action.reason or "Recovery limit reached"
                        break

                    # Execute recovery action
                    await dispatcher.execute_action(recovery_strat.action.action, recovery_strat.action.model_dump(exclude_none=True), task_id=task_id)

                await asyncio.sleep(0.5)

        except Exception as e:
            final_status = "failed"
            error_msg = f"Orchestrator error: {str(e)}"
            await emit("error", {"message": error_msg})
        finally:
            await controller.close()
            self.controllers.pop(task_id, None)

            # Update DB Task Status
            task_rec = await db.get(TaskModel, task_id)
            if task_rec:
                task_rec.status = final_status
                task_rec.error_message = error_msg if error_msg else None
                if final_status == "completed":
                    task_rec.completed_at = datetime.now(timezone.utc)
                await db.commit()

            await emit("status_change", {"status": final_status, "message": f"Task finished with status: {final_status}"})

        return {
            "status": final_status,
            "task_id": task_id,
            "steps_completed": step_count,
            "extracted_data": memory.extracted_data,
            "error_message": error_msg
        }

    def stop_task(self, task_id: str):
        self.stop_requested[task_id] = True


orchestrator = AgentOrchestrator()
