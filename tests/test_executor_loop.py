import pytest
from backend.app.agent.state import TaskStatus
from backend.app.agent.executor import ToolExecutor
from backend.app.browser.manager import BrowserManager


def test_task_status_enum_values():
    assert TaskStatus.IDLE.value == "IDLE"
    assert TaskStatus.RUNNING.value == "RUNNING"
    assert TaskStatus.WAITING_FOR_APPROVAL.value == "WAITING_FOR_APPROVAL"
    assert TaskStatus.RECOVERING.value == "RECOVERING"


@pytest.mark.asyncio
async def test_tool_executor_loop_protection():
    manager = BrowserManager(headless=True)
    executor = ToolExecutor(manager, max_identical_actions=3)

    action_name = "click"
    params = {"selector": "#repeated-btn"}

    assert executor.check_loop_protection(action_name, params) is False
    assert executor.check_loop_protection(action_name, params) is False
    # 3rd identical action triggers loop protection
    assert executor.check_loop_protection(action_name, params) is True
