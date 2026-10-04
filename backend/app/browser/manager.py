import os
import asyncio
from typing import Optional, List
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page
from backend.config import settings


class BrowserManager:
    def __init__(self, headless: bool = settings.PLAYWRIGHT_HEADLESS, browser_type: str = "chromium"):
        self.headless = headless
        self.browser_type_name = browser_type
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.downloads: List[str] = []

    async def start(self) -> Page:
        """
        Launches browser instance, creates context, and returns active page.
        """
        if not self.playwright:
            self.playwright = await async_playwright().start()

        browser_engine = getattr(self.playwright, self.browser_type_name, self.playwright.chromium)

        self.browser = await browser_engine.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ]
        )

        os.makedirs(settings.DOWNLOADS_DIR, exist_ok=True)
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            accept_downloads=True
        )

        self.page = await self.context.new_page()
        self.page.set_default_timeout(settings.ACTION_TIMEOUT_MS)
        self.page.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT_MS)

        self.page.on("download", self._on_download)
        return self.page

    async def _on_download(self, download):
        filepath = os.path.join(settings.DOWNLOADS_DIR, download.suggested_filename)
        await download.save_as(filepath)
        self.downloads.append(filepath)

    async def recover_crash(self) -> Page:
        """
        Recovers browser context if crashed or unexpectedly closed.
        """
        print("Recovering crashed browser session...")
        await self.stop()
        return await self.start()

    async def stop(self):
        """
        Safely shuts down context and Playwright instance.
        """
        if self.context:
            try:
                await self.context.close()
            except Exception:
                pass
            self.context = None
        if self.browser:
            try:
                await self.browser.close()
            except Exception:
                pass
            self.browser = None
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception:
                pass
            self.playwright = None
        self.page = None
