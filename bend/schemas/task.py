"""
Task Pydantic Schemas
Request/Response models for API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class TaskBase(BaseModel):
    """Base schema for Task"""
    description: str = Field(..., min_length=1, description="Task description")
    expected_output: str = Field(..., min_length=1, description="Expected task output")
    agent_id: str = Field(..., description="Agent ID assigned to this task")
    async_execution: bool = Field(default=False, description="Enable async execution")
    context_from_async_tasks_ids: Optional[List[str]] = Field(default=None, description="Async task IDs for context")
    context_from_sync_tasks_ids: Optional[List[str]] = Field(default=None, description="Sync task IDs for context")


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task (all fields optional)"""
    description: Optional[str] = Field(None, min_length=1)
    expected_output: Optional[str] = Field(None, min_length=1)
    agent_id: Optional[str] = None
    async_execution: Optional[bool] = None
    context_from_async_tasks_ids: Optional[List[str]] = None
    context_from_sync_tasks_ids: Optional[List[str]] = None


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: str = Field(..., description="Unique task identifier")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class TaskListResponse(BaseModel):
    """Schema for list of tasks"""
    tasks: List[TaskResponse]
    total: int = Field(..., description="Total number of tasks")


class TaskValidationResponse(BaseModel):
    """Schema for task validation response"""
    is_valid: bool = Field(..., description="Whether the task is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
