import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.models.database import Base, TaskModel
from backend.agent.orchestrator import AgentOrchestrator
from backend.agent.planner import TaskPlanner


@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_orchestrator_full_task_loop(async_session: AsyncSession):
    task_id = "test-orch-task-1"
    task = TaskModel(id=task_id, instruction="Search for Python tutorials", status="pending")
    async_session.add(task)
    await async_session.commit()

    events_received = []

    async def event_cb(ev_type, payload):
        events_received.append((ev_type, payload))

    planner = TaskPlanner(provider="mock")
    orchestrator = AgentOrchestrator(planner=planner)

    res = await orchestrator.run_task(task_id, "Search for Python tutorials", async_session, event_cb)

    assert res["status"] in ["completed", "running"]
    assert res["steps_completed"] > 0

    stmt = select(TaskModel).where(TaskModel.id == task_id).options(
        selectinload(TaskModel.steps),
        selectinload(TaskModel.actions),
        selectinload(TaskModel.results)
    )
    result = await async_session.execute(stmt)
    saved_task = result.scalar_one_or_none()

    assert saved_task is not None
    assert len(saved_task.steps) > 0
    assert len(saved_task.actions) > 0
    assert len(events_received) > 0
