import pytest
import pytest_asyncio
from backend.browser.controller import BrowserController
from backend.browser.page_analyzer import PageAnalyzer


@pytest_asyncio.fixture
async def browser_controller():
    controller = BrowserController(headless=True)
    await controller.initialize()
    yield controller
    await controller.close()


@pytest.mark.asyncio
async def test_page_analyzer_structure(browser_controller: BrowserController):
    analyzer = PageAnalyzer()

    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page Analyzer</title></head>
    <body>
        <h1>Welcome to AI Browser</h1>
        <h2>Search Courses</h2>
        <form action="/search" method="GET">
            <input type="text" name="q" placeholder="Search courses..." id="search-input" />
            <button type="submit" id="search-btn">Search</button>
        </form>
        <a href="https://example.com" id="nav-link">Learn More</a>
    </body>
    </html>
    """
    await browser_controller.page.goto(f"data:text/html,{html_content}")
    analysis = await analyzer.analyze(browser_controller.page)

    assert analysis.title == "Test Page Analyzer"
    assert "Welcome to AI Browser" in analysis.headings
    assert len(analysis.elements) >= 3

    formatted_text = analysis.format_for_llm()
    assert "URL:" in formatted_text
    assert "INTERACTIVE ELEMENTS" in formatted_text
    assert "search-input" in formatted_text or "Search courses..." in formatted_text
