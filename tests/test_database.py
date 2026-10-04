import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.models.database import Base, TaskModel, TaskStepModel, AgentActionModel, TaskResultModel, ScreenshotModel, ApprovalModel


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
async def test_task_creation_and_relations(async_session: AsyncSession):
    task = TaskModel(
        id="task-test-123",
        instruction="Search for Python tutorials",
        status="running",
        current_url="https://google.com"
    )
    async_session.add(task)
    await async_session.commit()

    step = TaskStepModel(
        task_id="task-test-123",
        step_number=1,
        description="Open search engine",
        status="completed"
    )
    async_session.add(step)
    await async_session.commit()

    action = AgentActionModel(
        task_id="task-test-123",
        step_id=step.id,
        action_type="open_url",
        parameters={"url": "https://google.com"},
        status="verified"
    )
    async_session.add(action)
    await async_session.commit()

    saved_task = await async_session.get(TaskModel, "task-test-123")
    assert saved_task is not None
    assert saved_task.instruction == "Search for Python tutorials"
    assert len(saved_task.steps) == 1
    assert saved_task.steps[0].description == "Open search engine"
    assert len(saved_task.actions) == 1
    assert saved_task.actions[0].action_type == "open_url"
    assert saved_task.actions[0].parameters == {"url": "https://google.com"}
