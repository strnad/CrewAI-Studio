"""
Knowledge Source Pydantic Schemas
Request/Response models for API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class KnowledgeSourceBase(BaseModel):
    """Base schema for Knowledge Source"""
    name: str = Field(..., min_length=1, max_length=255, description="Knowledge source name")
    source_type: str = Field(
        ...,
        description="Source type: string, text_file, pdf, csv, excel, json, docling"
    )
    source_path: str = Field(default="", description="File path for file-based sources")
    content: str = Field(default="", description="Content for string-based sources")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata")
    chunk_size: int = Field(default=4000, ge=100, le=8000, description="Chunk size for text splitting")
    chunk_overlap: int = Field(default=200, ge=0, le=1000, description="Overlap size between chunks")


class KnowledgeSourceCreate(KnowledgeSourceBase):
    """Schema for creating a new knowledge source"""
    pass


class KnowledgeSourceUpdate(BaseModel):
    """Schema for updating an existing knowledge source (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    source_type: Optional[str] = None
    source_path: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    chunk_size: Optional[int] = Field(None, ge=100, le=8000)
    chunk_overlap: Optional[int] = Field(None, ge=0, le=1000)


class KnowledgeSourceResponse(KnowledgeSourceBase):
    """Schema for knowledge source response"""
    id: str = Field(..., description="Unique knowledge source identifier")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class KnowledgeSourceListResponse(BaseModel):
    """Schema for list of knowledge sources"""
    knowledge_sources: List[KnowledgeSourceResponse]
    total: int = Field(..., description="Total number of knowledge sources")


class KnowledgeSourceValidationResponse(BaseModel):
    """Schema for knowledge source validation response"""
    is_valid: bool = Field(..., description="Whether the knowledge source is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class KnowledgeSourceTypeInfo(BaseModel):
    """Schema for available knowledge source types information"""
    type: str = Field(..., description="Source type identifier")
    display_name: str = Field(..., description="Human-readable type name")
    requires_file: bool = Field(..., description="Whether this type requires a file")
    supported_extensions: List[str] = Field(default_factory=list, description="Supported file extensions")


class KnowledgeSourceTypesListResponse(BaseModel):
    """Schema for list of available knowledge source types"""
    source_types: List[KnowledgeSourceTypeInfo]
    total: int = Field(..., description="Total number of source types")
