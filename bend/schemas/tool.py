"""
Tool Pydantic Schemas
Request/Response models for API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ToolBase(BaseModel):
    """Base schema for Tool"""
    name: str = Field(..., min_length=1, max_length=255, description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    parameters_metadata: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Parameter metadata (mandatory, type, etc.)"
    )


class ToolCreate(ToolBase):
    """Schema for creating a new tool"""
    pass


class ToolUpdate(BaseModel):
    """Schema for updating an existing tool (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    parameters_metadata: Optional[Dict[str, Dict[str, Any]]] = None


class ToolResponse(ToolBase):
    """Schema for tool response"""
    tool_id: str = Field(..., description="Unique tool identifier")

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class ToolListResponse(BaseModel):
    """Schema for list of tools"""
    tools: List[ToolResponse]
    total: int = Field(..., description="Total number of tools")


class ToolValidationResponse(BaseModel):
    """Schema for tool validation response"""
    is_valid: bool = Field(..., description="Whether the tool is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class ToolTypeInfo(BaseModel):
    """Schema for available tool types information"""
    name: str = Field(..., description="Tool type name (e.g., 'ScrapeWebsiteTool')")
    description: str = Field(..., description="Tool type description")
    required_parameters: List[str] = Field(default_factory=list, description="Required parameter names")
    optional_parameters: List[str] = Field(default_factory=list, description="Optional parameter names")


class ToolTypesListResponse(BaseModel):
    """Schema for list of available tool types"""
    tool_types: List[ToolTypeInfo]
    total: int = Field(..., description="Total number of tool types")
