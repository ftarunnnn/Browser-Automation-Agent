import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.models.database import init_db


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await init_db()


@pytest.mark.asyncio
async def test_health_check_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "AI Browser Automation Agent" in data["project"]


@pytest.mark.asyncio
async def test_create_and_get_task_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create Task
        res_create = await client.post("/api/tasks", json={"instruction": "Search for Python courses"})
        assert res_create.status_code == 200
        task_data = res_create.json()
        task_id = task_data["id"]
        assert task_id.startswith("task_")
        assert task_data["instruction"] == "Search for Python courses"

        # Get Task
        res_get = await client.get(f"/api/tasks/{task_id}")
        assert res_get.status_code == 200
        fetched_data = res_get.json()
        assert fetched_data["id"] == task_id
