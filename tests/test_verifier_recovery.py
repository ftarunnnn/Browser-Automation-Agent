import pytest
from backend.browser.page_analyzer import PageAnalysis, PageElement
from backend.browser.actions import ActionExecutionResult
from backend.agent.verifier import ActionResultVerifier
from backend.agent.recovery import FailureRecoveryEngine
from backend.models.schemas import BrowserActionSchema


@pytest.mark.asyncio
async def test_verifier_open_url_success():
    verifier = ActionResultVerifier()
    pre = PageAnalysis("about:blank", "", [], "", [], [], [])
    post = PageAnalysis("https://google.com", "Google", [], "Search...", [], [], [])
    exec_res = ActionExecutionResult(True, "Navigated")

    res = await verifier.verify_action("open_url", {"url": "https://google.com"}, pre, post, exec_res)
    assert res.verified is True
    assert "google.com" in res.message


@pytest.mark.asyncio
async def test_recovery_engine_alternative_selector():
    engine = FailureRecoveryEngine(max_retries=3)

    failed_action = BrowserActionSchema(action="click", selector="#invalid-btn", text="Submit Form")
    elements = [
        PageElement(1, "button", "", "button", "Submit Form", "submit", "", "button[name='submit']", "")
    ]
    current_page = PageAnalysis("https://example.com", "Test", elements, "Text", [], [], [])

    recovery = engine.get_recovery_action(failed_action, "Element #invalid-btn not found", current_page, [])
    assert recovery.action.action == "click"
    assert recovery.action.selector == "button[name='submit']"
    assert "Alternative visible element" in recovery.explanation


@pytest.mark.asyncio
async def test_recovery_engine_max_retries():
    engine = FailureRecoveryEngine(max_retries=2)
    failed_action = BrowserActionSchema(action="click", selector="#missing")
    current_page = PageAnalysis("https://example.com", "Test", [], "", [], [], [])

    # Call 3 times to exceed max retries
    engine.get_recovery_action(failed_action, "Element not found", current_page, [])
    engine.get_recovery_action(failed_action, "Element not found", current_page, [])
    final_recovery = engine.get_recovery_action(failed_action, "Element not found", current_page, [])

    assert final_recovery.action.action == "finish"
    assert "exceeded" in final_recovery.action.reason
