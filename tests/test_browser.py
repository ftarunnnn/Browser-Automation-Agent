import pytest
import pytest_asyncio
from backend.browser.controller import BrowserController
from backend.browser.actions import ActionDispatcher


@pytest_asyncio.fixture
async def browser_controller():
    controller = BrowserController(headless=True)
    await controller.initialize()
    yield controller
    await controller.close()


@pytest.mark.asyncio
async def test_browser_actions_flow(browser_controller: BrowserController):
    dispatcher = ActionDispatcher(browser_controller)

    # 1. Open URL with HTML string via data URL
    html_content = """
    <!Server>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1 id="header">Hello AI Agent</h1>
        <input id="username" type="text" placeholder="Enter username" />
        <button id="submit-btn" onclick="document.getElementById('header').innerText = 'Submitted!'">Submit</button>
    </body>
    </html>
    """
    data_url = f"data:text/html,{html_content}"
    res_open = await dispatcher.execute_action("open_url", {"url": data_url}, task_id="test_task")
    assert res_open.success is True

    # 2. Type text
    res_type = await dispatcher.execute_action("type", {"selector": "#username", "text": "agent_user"}, task_id="test_task")
    assert res_type.success is True

    # 3. Click button
    res_click = await dispatcher.execute_action("click", {"selector": "#submit-btn"}, task_id="test_task")
    assert res_click.success is True

    # 4. Extract text
    res_extract = await dispatcher.execute_action("extract_text", {"selector": "#header"}, task_id="test_task")
    assert res_extract.success is True
    assert "Submitted!" in res_extract.data.get("extracted_text", "")
