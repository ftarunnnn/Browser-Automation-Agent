import os
import uuid
import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.database import get_db, TaskModel, TaskStepModel, AgentActionModel, TaskResultModel, ScreenshotModel, ApprovalModel
from backend.models.schemas import TaskCreate, TaskResponse, AgentActionResponse, TaskResultResponse, ApprovalResponse
from backend.agent.orchestrator import orchestrator
from backend.api.websocket import ws_manager

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse)
async def create_task(payload: TaskCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    task_rec = TaskModel(
        id=task_id,
        instruction=payload.instruction,
        status="pending"
    )
    db.add(task_rec)
    await db.commit()
    await db.refresh(task_rec)

    # Event callback to push to WebSocket
    async def event_callback(event_type: str, data: dict):
        await ws_manager.broadcast_event(task_id, event_type, data)

    # Run orchestrator in background task
    async def run_in_background():
        async for session in get_db():
            await orchestrator.run_task(task_id, payload.instruction, session, event_callback)
            break

    background_tasks.add_task(run_in_background)

    # Re-fetch task with relationships
    stmt = select(TaskModel).where(TaskModel.id == task_id).options(
        selectinload(TaskModel.steps),
        selectinload(TaskModel.actions),
        selectinload(TaskModel.results),
        selectinload(TaskModel.screenshots),
        selectinload(TaskModel.approvals)
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(TaskModel).where(TaskModel.id == task_id).options(
        selectinload(TaskModel.steps),
        selectinload(TaskModel.actions),
        selectinload(TaskModel.results),
        selectinload(TaskModel.screenshots),
        selectinload(TaskModel.approvals)
    )
    res = await db.execute(stmt)
    task_rec = res.scalar_one_or_none()
    if not task_rec:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_rec


@router.post("/{task_id}/stop")
async def stop_task(task_id: str, db: AsyncSession = Depends(get_db)):
    orchestrator.stop_task(task_id)
    return {"message": f"Stop request sent for task {task_id}"}


@router.post("/{task_id}/approve")
async def approve_task_action(task_id: str, approval_id: int, db: AsyncSession = Depends(get_db)):
    approval = await db.get(ApprovalModel, approval_id)
    if not approval or approval.task_id != task_id:
        raise HTTPException(status_code=404, detail="Approval request not found")

    approval.status = "approved"
    await db.commit()
    await ws_manager.broadcast_event(task_id, "approval_response", {"approval_id": approval_id, "status": "approved"})
    return {"message": f"Action {approval_id} approved"}


@router.post("/{task_id}/reject")
async def reject_task_action(task_id: str, approval_id: int, db: AsyncSession = Depends(get_db)):
    approval = await db.get(ApprovalModel, approval_id)
    if not approval or approval.task_id != task_id:
        raise HTTPException(status_code=404, detail="Approval request not found")

    approval.status = "rejected"
    await db.commit()
    await ws_manager.broadcast_event(task_id, "approval_response", {"approval_id": approval_id, "status": "rejected"})
    return {"message": f"Action {approval_id} rejected"}


@router.get("/{task_id}/logs", response_model=List[AgentActionResponse])
async def get_task_logs(task_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(AgentActionModel).where(AgentActionModel.task_id == task_id).order_by(AgentActionModel.id)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/{task_id}/results", response_model=List[TaskResultResponse])
async def get_task_results(task_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(TaskResultModel).where(TaskResultModel.task_id == task_id)
    res = await db.execute(stmt)
    return res.scalars().all()
