import os
import asyncio
from typing import Optional, List, Dict, Any
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page
from backend.config import settings
from backend.browser.screenshots import screenshot_manager


class BrowserController:
    def __init__(self, headless: bool = settings.PLAYWRIGHT_HEADLESS):
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._downloads: List[str] = []

    async def initialize(self):
        """Starts Playwright and launches Chromium browser."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ]
            )
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                accept_downloads=True
            )
            self.page = await self.context.new_page()
            self.page.set_default_timeout(settings.ACTION_TIMEOUT_MS)
            self.page.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT_MS)

            # Setup download handler
            self.page.on("download", self._handle_download)

    async def _handle_download(self, download):
        download_dir = settings.DOWNLOADS_DIR
        os.makedirs(download_dir, exist_ok=True)
        filename = download.suggested_filename
        filepath = os.path.join(download_dir, filename)
        await download.save_as(filepath)
        self._downloads.append(filepath)

    @property
    def current_url(self) -> str:
        return self.page.url if self.page else ""

    @property
    def title(self) -> str:
        return self.page.title() if self.page else ""

    async def close(self):
        """Closes browser context and Playwright instance."""
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        self.page = None
