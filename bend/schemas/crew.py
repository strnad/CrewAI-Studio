"""
Crew Pydantic Schemas
Request/Response models for API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CrewBase(BaseModel):
    """Base schema for Crew"""
    name: str = Field(..., min_length=1, max_length=255, description="Crew name")
    agent_ids: List[str] = Field(default_factory=list, description="List of agent IDs")
    task_ids: List[str] = Field(default_factory=list, description="List of task IDs")
    process: str = Field(default="sequential", description="Process type: sequential or hierarchical")
    verbose: bool = Field(default=True, description="Enable verbose logging")
    cache: bool = Field(default=True, description="Enable caching")
    max_rpm: int = Field(default=1000, ge=1, le=10000, description="Maximum requests per minute")
    memory: bool = Field(default=False, description="Enable memory")
    planning: bool = Field(default=False, description="Enable planning")
    manager_llm: Optional[str] = Field(default=None, description="Manager LLM identifier")
    manager_agent_id: Optional[str] = Field(default=None, description="Manager agent ID")
    planning_llm: Optional[str] = Field(default=None, description="Planning LLM identifier")
    knowledge_source_ids: List[str] = Field(default_factory=list, description="List of knowledge source IDs")


class CrewCreate(CrewBase):
    """Schema for creating a new crew"""
    pass


class CrewUpdate(BaseModel):
    """Schema for updating an existing crew (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    agent_ids: Optional[List[str]] = None
    task_ids: Optional[List[str]] = None
    process: Optional[str] = None
    verbose: Optional[bool] = None
    cache: Optional[bool] = None
    max_rpm: Optional[int] = Field(None, ge=1, le=10000)
    memory: Optional[bool] = None
    planning: Optional[bool] = None
    manager_llm: Optional[str] = None
    manager_agent_id: Optional[str] = None
    planning_llm: Optional[str] = None
    knowledge_source_ids: Optional[List[str]] = None


class CrewResponse(CrewBase):
    """Schema for crew response"""
    id: str = Field(..., description="Unique crew identifier")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class CrewListResponse(BaseModel):
    """Schema for list of crews"""
    crews: List[CrewResponse]
    total: int = Field(..., description="Total number of crews")


class CrewValidationResponse(BaseModel):
    """Schema for crew validation response"""
    is_valid: bool = Field(..., description="Whether the crew is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class CrewExecutionRequest(BaseModel):
    """Schema for crew execution request"""
    crew_id: str = Field(..., description="Crew ID to execute")
    inputs: dict = Field(default_factory=dict, description="Input parameters for the crew")


class CrewExecutionResponse(BaseModel):
    """Schema for crew execution response"""
    execution_id: str = Field(..., description="Unique execution identifier")
    crew_id: str = Field(..., description="Crew ID being executed")
    status: str = Field(..., description="Execution status: pending, running, completed, failed")
    started_at: str = Field(..., description="Execution start timestamp")
    completed_at: Optional[str] = Field(None, description="Execution completion timestamp")
    result: Optional[dict] = Field(None, description="Execution result")
    error: Optional[str] = Field(None, description="Error message if failed")
