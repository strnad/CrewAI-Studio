"""
Knowledge Sources API Endpoints
CRUD operations for knowledge sources
"""
from fastapi import APIRouter, HTTPException, status
from bend.schemas.knowledge import (
    KnowledgeSourceCreate,
    KnowledgeSourceUpdate,
    KnowledgeSourceResponse,
    KnowledgeSourceListResponse,
    KnowledgeSourceValidationResponse
)
from bend.models.knowledge import KnowledgeSourceModel
from bend.storage.memory import storage

router = APIRouter()


@router.get("/", response_model=KnowledgeSourceListResponse)
async def list_knowledge_sources():
    """Get all knowledge sources"""
    knowledge_sources = [
        KnowledgeSourceResponse(**ks.to_dict())
        for ks in storage.knowledge_sources.values()
    ]
    return KnowledgeSourceListResponse(
        knowledge_sources=knowledge_sources,
        total=len(knowledge_sources)
    )


@router.get("/{knowledge_source_id}", response_model=KnowledgeSourceResponse)
async def get_knowledge_source(knowledge_source_id: str):
    """Get a specific knowledge source by ID"""
    ks = storage.knowledge_sources.get(knowledge_source_id)
    if not ks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge source with id '{knowledge_source_id}' not found"
        )
    return KnowledgeSourceResponse(**ks.to_dict())


@router.post("/", response_model=KnowledgeSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_source(ks_data: KnowledgeSourceCreate):
    """Create a new knowledge source"""
    # Validate source type
    valid_types = ["string", "text_file", "pdf", "csv", "excel", "json", "docling"]
    if ks_data.source_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source_type: {ks_data.source_type}. Must be one of: {', '.join(valid_types)}"
        )

    # Create knowledge source
    ks = KnowledgeSourceModel(
        name=ks_data.name,
        source_type=ks_data.source_type,
        source_path=ks_data.source_path,
        content=ks_data.content,
        metadata=ks_data.metadata,
        chunk_size=ks_data.chunk_size,
        chunk_overlap=ks_data.chunk_overlap,
    )

    # Store knowledge source
    storage.knowledge_sources[ks.id] = ks

    return KnowledgeSourceResponse(**ks.to_dict())


@router.put("/{knowledge_source_id}", response_model=KnowledgeSourceResponse)
async def update_knowledge_source(knowledge_source_id: str, ks_data: KnowledgeSourceUpdate):
    """Update an existing knowledge source"""
    ks = storage.knowledge_sources.get(knowledge_source_id)
    if not ks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge source with id '{knowledge_source_id}' not found"
        )

    # Update fields if provided
    update_dict = ks_data.model_dump(exclude_unset=True)

    # Validate source type if being updated
    if 'source_type' in update_dict:
        valid_types = ["string", "text_file", "pdf", "csv", "excel", "json", "docling"]
        if update_dict['source_type'] not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid source_type: {update_dict['source_type']}. Must be one of: {', '.join(valid_types)}"
            )

    # Update fields
    for field, value in update_dict.items():
        if hasattr(ks, field):
            setattr(ks, field, value)

    return KnowledgeSourceResponse(**ks.to_dict())


@router.delete("/{knowledge_source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_source(knowledge_source_id: str):
    """Delete a knowledge source"""
    if knowledge_source_id not in storage.knowledge_sources:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge source with id '{knowledge_source_id}' not found"
        )

    # Check if knowledge source is used by any agents
    ks_in_use_by_agents = False
    agents_using_ks = []
    for agent in storage.agents.values():
        if knowledge_source_id in agent.knowledge_source_ids:
            ks_in_use_by_agents = True
            agents_using_ks.append(agent.role)

    if ks_in_use_by_agents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Knowledge source is used by agents: {', '.join(agents_using_ks)}. "
                   f"Remove knowledge source from agents before deleting."
        )

    # Check if knowledge source is used by any crews
    ks_in_use_by_crews = False
    crews_using_ks = []
    for crew in storage.crews.values():
        if knowledge_source_id in crew.knowledge_source_ids:
            ks_in_use_by_crews = True
            crews_using_ks.append(crew.name)

    if ks_in_use_by_crews:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Knowledge source is used by crews: {', '.join(crews_using_ks)}. "
                   f"Remove knowledge source from crews before deleting."
        )

    del storage.knowledge_sources[knowledge_source_id]


@router.post("/{knowledge_source_id}/validate", response_model=KnowledgeSourceValidationResponse)
async def validate_knowledge_source(knowledge_source_id: str):
    """Validate a knowledge source configuration"""
    ks = storage.knowledge_sources.get(knowledge_source_id)
    if not ks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge source with id '{knowledge_source_id}' not found"
        )

    # Validate knowledge source
    validation = ks.validate()

    return KnowledgeSourceValidationResponse(
        is_valid=validation['is_valid'],
        errors=validation['errors'],
        warnings=validation['warnings']
    )
