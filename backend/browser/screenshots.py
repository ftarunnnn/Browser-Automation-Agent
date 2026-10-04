import os
import uuid
from datetime import datetime
from backend.config import settings


class ScreenshotManager:
    def __init__(self, screenshots_dir: str = settings.SCREENSHOTS_DIR):
        self.screenshots_dir = screenshots_dir
        os.makedirs(self.screenshots_dir, exist_ok=True)

    async def capture(self, page, task_id: str, action_name: str = "step") -> str:
        """
        Captures a screenshot of the current Playwright page and returns the file path.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        filename = f"{task_id}_{action_name}_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)

        try:
            await page.screenshot(path=filepath, full_page=False)
            return filepath
        except Exception as e:
            # Fallback or log if page is closed/failed
            print(f"Error taking screenshot: {e}")
            return ""


screenshot_manager = ScreenshotManager()
