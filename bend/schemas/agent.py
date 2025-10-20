"""
Agent Pydantic Schemas
Request/Response models for API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AgentBase(BaseModel):
    """Base schema for Agent"""
    role: str = Field(..., min_length=1, max_length=500, description="Agent role")
    backstory: str = Field(..., min_length=1, description="Agent backstory")
    goal: str = Field(..., min_length=1, description="Agent goal")
    temperature: float = Field(default=0.1, ge=0.0, le=1.0, description="LLM temperature")
    allow_delegation: bool = Field(default=False, description="Allow agent delegation")
    verbose: bool = Field(default=True, description="Enable verbose logging")
    cache: bool = Field(default=True, description="Enable caching")
    llm_provider_model: str = Field(..., description="LLM provider and model identifier")
    max_iter: int = Field(default=25, ge=1, le=100, description="Maximum iterations")
    tool_ids: List[str] = Field(default_factory=list, description="List of tool IDs")
    knowledge_source_ids: List[str] = Field(default_factory=list, description="List of knowledge source IDs")


class AgentCreate(AgentBase):
    """Schema for creating a new agent"""
    pass


class AgentUpdate(BaseModel):
    """Schema for updating an existing agent (all fields optional)"""
    role: Optional[str] = Field(None, min_length=1, max_length=500)
    backstory: Optional[str] = Field(None, min_length=1)
    goal: Optional[str] = Field(None, min_length=1)
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    allow_delegation: Optional[bool] = None
    verbose: Optional[bool] = None
    cache: Optional[bool] = None
    llm_provider_model: Optional[str] = None
    max_iter: Optional[int] = Field(None, ge=1, le=100)
    tool_ids: Optional[List[str]] = None
    knowledge_source_ids: Optional[List[str]] = None


class AgentResponse(AgentBase):
    """Schema for agent response"""
    id: str = Field(..., description="Unique agent identifier")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class AgentListResponse(BaseModel):
    """Schema for list of agents"""
    agents: List[AgentResponse]
    total: int = Field(..., description="Total number of agents")


class AgentValidationResponse(BaseModel):
    """Schema for agent validation response"""
    is_valid: bool = Field(..., description="Whether the agent is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
