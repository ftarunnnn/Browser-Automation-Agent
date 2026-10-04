from datetime import datetime, timezone
import json
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.config import settings


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    tasks: Mapped[List["TaskModel"]] = relationship("TaskModel", back_populates="user", cascade="all, delete-orphan")


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)  # pending, planning, running, completed, failed, paused_approval, stopped
    current_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped[Optional["UserModel"]] = relationship("UserModel", back_populates="tasks")
    steps: Mapped[List["TaskStepModel"]] = relationship("TaskStepModel", back_populates="task", cascade="all, delete-orphan", order_by="TaskStepModel.step_number")
    actions: Mapped[List["AgentActionModel"]] = relationship("AgentActionModel", back_populates="task", cascade="all, delete-orphan", order_by="AgentActionModel.id")
    results: Mapped[List["TaskResultModel"]] = relationship("TaskResultModel", back_populates="task", cascade="all, delete-orphan")
    screenshots: Mapped[List["ScreenshotModel"]] = relationship("ScreenshotModel", back_populates="task", cascade="all, delete-orphan")
    approvals: Mapped[List["ApprovalModel"]] = relationship("ApprovalModel", back_populates="task", cascade="all, delete-orphan")


class TaskStepModel(Base):
    __tablename__ = "task_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(64), ForeignKey("tasks.id"), nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, running, completed, failed

    task: Mapped["TaskModel"] = relationship("TaskModel", back_populates="steps")
    actions: Mapped[List["AgentActionModel"]] = relationship("AgentActionModel", back_populates="step")


class AgentActionModel(Base):
    __tablename__ = "agent_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(64), ForeignKey("tasks.id"), nullable=False)
    step_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("task_steps.id"), nullable=True)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)
    parameters_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(32), default="executing")  # executing, verified, failed, pending_approval
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    task: Mapped["TaskModel"] = relationship("TaskModel", back_populates="actions")
    step: Mapped[Optional["TaskStepModel"]] = relationship("TaskStepModel", back_populates="actions")
    screenshot: Mapped[Optional["ScreenshotModel"]] = relationship("ScreenshotModel", back_populates="action", uselist=False)

    @property
    def parameters(self) -> dict:
        return json.loads(self.parameters_json) if self.parameters_json else {}

    @parameters.setter
    def parameters(self, val: dict):
        self.parameters_json = json.dumps(val)


class TaskResultModel(Base):
    __tablename__ = "task_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(64), ForeignKey("tasks.id"), nullable=False)
    structured_data_json: Mapped[str] = mapped_column(Text, default="{}")
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    task: Mapped["TaskModel"] = relationship("TaskModel", back_populates="results")

    @property
    def structured_data(self) -> dict:
        return json.loads(self.structured_data_json) if self.structured_data_json else {}

    @structured_data.setter
    def structured_data(self, val: dict):
        self.structured_data_json = json.dumps(val)


class ScreenshotModel(Base):
    __tablename__ = "screenshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(64), ForeignKey("tasks.id"), nullable=False)
    action_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("agent_actions.id"), nullable=True)
    filepath: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    task: Mapped["TaskModel"] = relationship("TaskModel", back_populates="screenshots")
    action: Mapped[Optional["AgentActionModel"]] = relationship("AgentActionModel", back_populates="screenshot")


class ApprovalModel(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(64), ForeignKey("tasks.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    parameters_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, approved, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    task: Mapped["TaskModel"] = relationship("TaskModel", back_populates="approvals")

    @property
    def parameters(self) -> dict:
        return json.loads(self.parameters_json) if self.parameters_json else {}

    @parameters.setter
    def parameters(self, val: dict):
        self.parameters_json = json.dumps(val)


# Engine & Session setup
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
