import pytest
from backend.agent.memory import TaskMemory
from backend.models.schemas import BrowserActionSchema


def test_task_memory_state():
    mem = TaskMemory("task-1", "Purchase a product online")
    mem.plan_steps = ["Open site", "Add to cart", "Checkout"]

    action = BrowserActionSchema(action="open_url", url="https://shop.com")
    mem.record_action_success(action, {"title": "Shop"}, "https://shop.com")

    assert mem.current_url == "https://shop.com"
    assert len(mem.completed_actions) == 1
    assert mem.to_summary()["completed_actions_count"] == 1


def test_sensitive_action_detection():
    mem = TaskMemory("task-2", "Buy a laptop")

    normal_action = BrowserActionSchema(action="click", selector="#search-btn")
    assert mem.is_sensitive_action(normal_action) is False

    purchase_action = BrowserActionSchema(action="click", selector="#buy-now-btn", text="Buy Now $999")
    assert mem.is_sensitive_action(purchase_action) is True

    delete_action = BrowserActionSchema(action="click", selector="#delete-account", text="Delete Account")
    assert mem.is_sensitive_action(delete_action) is True
