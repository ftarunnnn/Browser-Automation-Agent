import os
import pytest
import pytest_asyncio
from backend.app.browser.manager import BrowserManager
from backend.app.browser.inspector import inspector
from backend.browser.actions import ActionDispatcher


@pytest_asyncio.fixture
async def browser_manager():
    manager = BrowserManager(headless=True)
    await manager.start()
    yield manager
    await manager.stop()


@pytest.mark.asyncio
async def test_local_site_navigation_and_form(browser_manager: BrowserManager):
    page = browser_manager.page
    dispatcher = ActionDispatcher(browser_manager)

    test_site_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_site"))
    index_path = f"file:///{test_site_dir.replace('\\', '/')}/index.html"
    form_path = f"file:///{test_site_dir.replace('\\', '/')}/form.html"

    # 1. Open Index Page
    res_open = await dispatcher.execute_action("open_url", {"url": index_path}, task_id="test_local")
    assert res_open.success is True

    # 2. Inspect page elements
    obs = await inspector.inspect_page(page)
    assert obs["title"] == "WebPilot AI Local Test Suite"
    assert len(obs["elements"]) >= 6

    # 3. Open Form Page and Fill Details
    await dispatcher.execute_action("open_url", {"url": form_path}, task_id="test_local")
    await dispatcher.execute_action("type", {"selector": "#fullname", "text": "Alice Engineer"}, task_id="test_local")
    await dispatcher.execute_action("type", {"selector": "#email", "text": "alice@example.com"}, task_id="test_local")
    await dispatcher.execute_action("click", {"selector": "#submit-btn"}, task_id="test_local")

    # 4. Verify form submission
    text_res = await dispatcher.execute_action("extract_text", {"selector": "#msg"}, task_id="test_local")
    assert "Submitted Successfully" in text_res.data.get("extracted_text", "")
