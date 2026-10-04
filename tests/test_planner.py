import pytest
import pytest_asyncio
from backend.agent.planner import TaskPlanner
from backend.models.schemas import BrowserActionSchema


@pytest.mark.asyncio
async def test_planner_heuristic_plan_creation():
    planner = TaskPlanner(provider="mock")
    steps = await planner.create_plan("Search for Python courses")
    assert len(steps) >= 3
    assert any("search" in s.lower() or "open" in s.lower() for s in steps)


@pytest.mark.asyncio
async def test_planner_action_selection_sequence():
    planner = TaskPlanner(provider="mock")
    steps = ["Open search engine", "Search query", "Extract results"]

    # Step 1 action: open_url
    action1 = await planner.select_next_action(
        user_instruction="Search for Python courses",
        plan_steps=steps,
        current_step_idx=0,
        page_observation="Blank Page",
        action_history=[]
    )
    assert action1.action == "open_url"

    # Step 2 action: type
    action2 = await planner.select_next_action(
        user_instruction="Search for Python courses",
        plan_steps=steps,
        current_step_idx=1,
        page_observation="URL: google.com\nINTERACTIVE ELEMENTS: <input name='q'>",
        action_history=[{"action": "open_url"}]
    )
    assert action2.action == "type"
    assert "Python courses" in action2.text
