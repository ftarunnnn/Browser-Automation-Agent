import pytest
import pytest_asyncio
from backend.app.browser.manager import BrowserManager
from backend.app.browser.selectors import SelectorEngine


@pytest_asyncio.fixture
async def browser_page():
    manager = BrowserManager(headless=True)
    page = await manager.start()
    yield page
    await manager.stop()


@pytest.mark.asyncio
async def test_selector_engine_priority(browser_page):
    html = """
    <html>
    <body>
        <button aria-label="Submit Button" id="btn1">Submit Role</button>
        <input placeholder="Enter Search" name="search_q" id="search_input" />
    </body>
    </html>
    """
    await browser_page.goto(f"data:text/html,{html}")

    # Test Label locator
    loc_label = SelectorEngine.get_locator(browser_page, label="Submit Button")
    assert await loc_label.is_visible() is True

    # Test Placeholder locator
    loc_place = SelectorEngine.get_locator(browser_page, placeholder="Enter Search")
    assert await loc_place.is_visible() is True
