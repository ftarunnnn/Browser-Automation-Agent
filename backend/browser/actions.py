import time
import asyncio
from typing import Dict, Any, Optional
from backend.browser.controller import BrowserController
from backend.browser.screenshots import screenshot_manager


class ActionExecutionResult:
    def __init__(self, success: bool, message: str, data: Optional[Dict[str, Any]] = None, screenshot_path: str = ""):
        self.success = success
        self.message = message
        self.data = data or {}
        self.screenshot_path = screenshot_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "screenshot_path": self.screenshot_path
        }


class ActionDispatcher:
    def __init__(self, controller: BrowserController):
        self.controller = controller

    async def execute_action(self, action_name: str, params: Dict[str, Any], task_id: str = "task") -> ActionExecutionResult:
        """
        Executes a browser action by name with parameters.
        """
        if not self.controller.page:
            await self.controller.initialize()

        handler = getattr(self, f"action_{action_name}", None)
        if not handler:
            return ActionExecutionResult(
                success=False,
                message=f"Unknown browser action: '{action_name}'"
            )

        start_time = time.time()
        try:
            result = await handler(params)
            screenshot_path = await screenshot_manager.capture(self.controller.page, task_id, action_name)
            result.screenshot_path = screenshot_path
            return result
        except Exception as e:
            error_msg = f"Action '{action_name}' failed: {str(e)}"
            screenshot_path = ""
            try:
                screenshot_path = await screenshot_manager.capture(self.controller.page, task_id, f"{action_name}_error")
            except Exception:
                pass
            return ActionExecutionResult(
                success=False,
                message=error_msg,
                screenshot_path=screenshot_path
            )

    async def action_open_url(self, params: Dict[str, Any]) -> ActionExecutionResult:
        url = params.get("url")
        if not url:
            return ActionExecutionResult(False, "Missing required parameter 'url'")
        if not (url.startswith("http://") or url.startswith("https://") or url.startswith("file://")):
            url = "https://" + url

        await self.controller.page.goto(url, wait_until="domcontentloaded")
        await self.controller.page.wait_for_timeout(1000)
        return ActionExecutionResult(
            success=True,
            message=f"Navigated to {url}",
            data={"url": self.controller.page.url, "title": await self.controller.page.title()}
        )

    async def action_click(self, params: Dict[str, Any]) -> ActionExecutionResult:
        selector = params.get("selector")
        text = params.get("text")
        if not selector and not text:
            return ActionExecutionResult(False, "Missing 'selector' or 'text' for click action")

        page = self.controller.page
        if selector:
            # Try selector first
            locator = page.locator(selector).first
            await locator.wait_for(state="visible", timeout=5000)
            await locator.click()
        elif text:
            # Fallback to text locator
            locator = page.get_by_text(text, exact=False).first
            await locator.click()

        await page.wait_for_timeout(500)
        return ActionExecutionResult(
            success=True,
            message=f"Clicked element ({selector or text})",
            data={"url": page.url}
        )

    async def action_type(self, params: Dict[str, Any]) -> ActionExecutionResult:
        selector = params.get("selector")
        text = params.get("text", "")
        clear_first = params.get("clear_first", True)

        if not selector:
            return ActionExecutionResult(False, "Missing required parameter 'selector'")

        page = self.controller.page
        locator = page.locator(selector).first
        await locator.wait_for(state="visible", timeout=5000)
        if clear_first:
            await locator.fill("")
        await locator.type(text, delay=20)
        
        press_enter = params.get("press_enter", False)
        if press_enter:
            await locator.press("Enter")

        await page.wait_for_timeout(300)
        return ActionExecutionResult(
            success=True,
            message=f"Typed text into '{selector}'",
            data={"typed_text": text}
        )

    async def action_select(self, params: Dict[str, Any]) -> ActionExecutionResult:
        selector = params.get("selector")
        value = params.get("text") or params.get("value")

        if not selector or value is None:
            return ActionExecutionResult(False, "Missing 'selector' or 'text/value' for select action")

        page = self.controller.page
        locator = page.locator(selector).first
        await locator.select_option(value=str(value))
        return ActionExecutionResult(
            success=True,
            message=f"Selected option '{value}' in '{selector}'"
        )

    async def action_scroll(self, params: Dict[str, Any]) -> ActionExecutionResult:
        direction = params.get("direction", "down").lower()
        amount = params.get("amount", 500)
        page = self.controller.page

        if direction == "down":
            await page.evaluate(f"window.scrollBy(0, {amount})")
        elif direction == "up":
            await page.evaluate(f"window.scrollBy(0, -{amount})")
        elif direction == "top":
            await page.evaluate("window.scrollTo(0, 0)")
        elif direction == "bottom":
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        await page.wait_for_timeout(300)
        return ActionExecutionResult(
            success=True,
            message=f"Scrolled {direction} by {amount}px"
        )

    async def action_press(self, params: Dict[str, Any]) -> ActionExecutionResult:
        key = params.get("key", "Enter")
        selector = params.get("selector")
        page = self.controller.page

        if selector:
            await page.locator(selector).first.press(key)
        else:
            await page.keyboard.press(key)

        await page.wait_for_timeout(300)
        return ActionExecutionResult(
            success=True,
            message=f"Pressed key '{key}'"
        )

    async def action_extract_text(self, params: Dict[str, Any]) -> ActionExecutionResult:
        selector = params.get("selector")
        page = self.controller.page

        if selector:
            text = await page.locator(selector).first.inner_text()
        else:
            text = await page.evaluate("document.body.innerText")

        return ActionExecutionResult(
            success=True,
            message="Extracted text successfully",
            data={"extracted_text": text[:5000]}  # limit payload size
        )

    async def action_screenshot(self, params: Dict[str, Any]) -> ActionExecutionResult:
        page = self.controller.page
        path = await screenshot_manager.capture(page, "manual_screenshot")
        return ActionExecutionResult(
            success=True,
            message="Screenshot captured successfully",
            screenshot_path=path
        )

    async def action_download(self, params: Dict[str, Any]) -> ActionExecutionResult:
        url = params.get("url")
        selector = params.get("selector")
        page = self.controller.page

        if selector:
            async with page.expect_download() as download_info:
                await page.locator(selector).first.click()
            download = await download_info.value
            filepath = await download.path()
            return ActionExecutionResult(
                success=True,
                message=f"Downloaded file: {download.suggested_filename}",
                data={"filepath": filepath, "filename": download.suggested_filename}
            )
        elif url:
            await page.goto(url)
            return ActionExecutionResult(
                success=True,
                message=f"Navigated to download URL {url}"
            )
        else:
            return ActionExecutionResult(False, "Missing 'url' or 'selector' for download action")

    async def action_navigate_back(self, params: Dict[str, Any]) -> ActionExecutionResult:
        await self.controller.page.go_back()
        return ActionExecutionResult(
            success=True,
            message="Navigated back",
            data={"url": self.controller.page.url}
        )

    async def action_navigate_forward(self, params: Dict[str, Any]) -> ActionExecutionResult:
        await self.controller.page.go_forward()
        return ActionExecutionResult(
            success=True,
            message="Navigated forward",
            data={"url": self.controller.page.url}
        )
