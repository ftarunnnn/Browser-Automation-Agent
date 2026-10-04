from fastapi import APIRouter
from backend.config import settings

router = APIRouter(prefix="/api/browser", tags=["browser"])


@router.get("/status")
async def get_browser_status():
    return {
        "engine": "Playwright Chromium",
        "headless": settings.PLAYWRIGHT_HEADLESS,
        "action_timeout_ms": settings.ACTION_TIMEOUT_MS,
        "navigation_timeout_ms": settings.NAVIGATION_TIMEOUT_MS
    }
