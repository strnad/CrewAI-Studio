"""
Knowledge Sources API Endpoints
CRUD operations for knowledge sources
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from bend.schemas.knowledge import (
    KnowledgeSourceCreate,
    KnowledgeSourceUpdate,
    KnowledgeSourceResponse,
    KnowledgeSourceListResponse,
    KnowledgeSourceValidationResponse
)
from bend.services import KnowledgeSourceService
from bend.database.connection import get_db_session

router = APIRouter()


@router.get("/", response_model=KnowledgeSourceListResponse)
async def list_knowledge_sources(db: Session = Depends(get_db_session)):
    """Get all knowledge sources"""
    service = KnowledgeSourceService(db)
    ks_list = service.list_knowledge_sources()
    knowledge_sources = [KnowledgeSourceResponse(**ks.to_dict()) for ks in ks_list]
    return KnowledgeSourceListResponse(
        knowledge_sources=knowledge_sources,
        total=len(knowledge_sources)
    )


@router.get("/{knowledge_source_id}", response_model=KnowledgeSourceResponse)
async def get_knowledge_source(knowledge_source_id: str, db: Session = Depends(get_db_session)):
    """Get a specific knowledge source by ID"""
    service = KnowledgeSourceService(db)
    ks = service.get_knowledge_source(knowledge_source_id)
    if not ks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge source with id '{knowledge_source_id}' not found"
        )
    return KnowledgeSourceResponse(**ks.to_dict())


@router.post("/", response_model=KnowledgeSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_source(ks_data: KnowledgeSourceCreate, db: Session = Depends(get_db_session)):
    """Create a new knowledge source"""
    service = KnowledgeSourceService(db)
    try:
        ks = service.create_knowledge_source(
            name=ks_data.name,
            source_type=ks_data.source_type,
            source_path=ks_data.source_path,
            content=ks_data.content,
            metadata=ks_data.metadata,
            chunk_size=ks_data.chunk_size,
            chunk_overlap=ks_data.chunk_overlap
        )
        return KnowledgeSourceResponse(**ks.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{knowledge_source_id}", response_model=KnowledgeSourceResponse)
async def update_knowledge_source(knowledge_source_id: str, ks_data: KnowledgeSourceUpdate, db: Session = Depends(get_db_session)):
    """Update an existing knowledge source"""
    service = KnowledgeSourceService(db)
    try:
        update_dict = ks_data.model_dump(exclude_unset=True)
        ks = service.update_knowledge_source(knowledge_source_id, **update_dict)
        if not ks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge source with id '{knowledge_source_id}' not found"
            )
        return KnowledgeSourceResponse(**ks.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{knowledge_source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_source(knowledge_source_id: str, db: Session = Depends(get_db_session)):
    """Delete a knowledge source"""
    service = KnowledgeSourceService(db)
    try:
        success = service.delete_knowledge_source(knowledge_source_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge source with id '{knowledge_source_id}' not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{knowledge_source_id}/validate", response_model=KnowledgeSourceValidationResponse)
async def validate_knowledge_source(knowledge_source_id: str, db: Session = Depends(get_db_session)):
    """Validate a knowledge source configuration"""
    service = KnowledgeSourceService(db)
    try:
        validation = service.validate_knowledge_source(knowledge_source_id)
        return KnowledgeSourceValidationResponse(
            is_valid=validation['is_valid'],
            errors=validation['errors'],
            warnings=validation['warnings']
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
