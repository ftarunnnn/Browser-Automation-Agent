import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.models.database import init_db
from backend.api.tasks import router as tasks_router
from backend.api.websocket import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup DB initialization
    await init_db()
    yield
    # Shutdown logic if any


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(tasks_router)

# Mount Screenshots Static Directory
os.makedirs(settings.SCREENSHOTS_DIR, exist_ok=True)
app.mount("/api/screenshots", StaticFiles(directory=settings.SCREENSHOTS_DIR), name="screenshots")


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.LLM_PROVIDER
    }


@app.websocket("/api/tasks/{task_id}/stream")
async def task_websocket_stream(websocket: WebSocket, task_id: str):
    await ws_manager.connect(task_id, websocket)
    try:
        while True:
            # Keep socket alive and receive incoming ping messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(task_id, websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
