from fastapi import APIRouter
from backend.config import settings

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.LLM_PROVIDER
    }
