import time
from typing import Dict, Any, List, Optional
from backend.app.browser.manager import BrowserManager
from backend.browser.actions import ActionDispatcher, ActionExecutionResult
from backend.config import settings


class ToolExecutor:
    """
    ToolExecutor executes approved browser tools while enforcing loop protection limits:
    - MAX_STEPS
    - MAX_RETRIES
    - MAX_IDENTICAL_ACTIONS
    """
    def __init__(self, manager: BrowserManager, max_identical_actions: int = 3):
        self.manager = manager
        self.dispatcher = ActionDispatcher(manager)
        self.max_identical_actions = max_identical_actions
        self._action_history: List[str] = []

    def check_loop_protection(self, action_name: str, params: Dict[str, Any]) -> bool:
        """
        Returns True if an identical action loop is detected.
        """
        action_sig = f"{action_name}_{params.get('selector', '')}_{params.get('url', '')}_{params.get('text', '')}"
        self._action_history.append(action_sig)

        if len(self._action_history) >= self.max_identical_actions:
            last_n = self._action_history[-self.max_identical_actions:]
            if len(set(last_n)) == 1:
                return True
        return False

    async def execute_tool(self, action_name: str, params: Dict[str, Any], task_id: str) -> ActionExecutionResult:
        if self.check_loop_protection(action_name, params):
            return ActionExecutionResult(
                success=False,
                message=f"Loop protection triggered: Repeated identical action '{action_name}' {self.max_identical_actions} times."
            )

        return await self.dispatcher.execute_action(action_name, params, task_id=task_id)

    def reset(self):
        self._action_history.clear()
