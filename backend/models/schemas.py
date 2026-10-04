from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# User Schemas
class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Task Schemas
class TaskCreate(BaseModel):
    instruction: str = Field(..., min_length=3, description="Natural language task description")


class TaskStepResponse(BaseModel):
    id: int
    step_number: int
    description: str
    status: str
    model_config = ConfigDict(from_attributes=True)


class AgentActionResponse(BaseModel):
    id: int
    action_type: str
    parameters: Dict[str, Any]
    status: str
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ScreenshotResponse(BaseModel):
    id: int
    filepath: str
    url: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TaskResultResponse(BaseModel):
    id: int
    structured_data: Dict[str, Any]
    extracted_text: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ApprovalResponse(BaseModel):
    id: int
    task_id: str
    action_type: str
    description: str
    parameters: Dict[str, Any]
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    id: str
    instruction: str
    status: str
    current_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    steps: List[TaskStepResponse] = []
    actions: List[AgentActionResponse] = []
    results: List[TaskResultResponse] = []
    screenshots: List[ScreenshotResponse] = []
    approvals: List[ApprovalResponse] = []
    model_config = ConfigDict(from_attributes=True)


# Action Schema for AI tool calling
class BrowserActionSchema(BaseModel):
    action: str = Field(..., description="Action name: open_url, click, type, select, scroll, press, extract_text, screenshot, download, finish, require_approval")
    url: Optional[str] = Field(None, description="URL for open_url action")
    selector: Optional[str] = Field(None, description="CSS or XPath selector for click, type, select, etc.")
    text: Optional[str] = Field(None, description="Text content to type or option value to select")
    key: Optional[str] = Field(None, description="Keyboard key to press (e.g., Enter, Tab, Escape)")
    direction: Optional[str] = Field(None, description="Scroll direction: up, down, top, bottom")
    amount: Optional[int] = Field(None, description="Scroll pixel amount")
    reason: Optional[str] = Field(None, description="Reasoning for action or description for finish/approval")
    extracted_data: Optional[Dict[str, Any]] = Field(None, description="Extracted structured data when finishing task")
