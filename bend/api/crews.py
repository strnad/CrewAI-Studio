"""
Crews API Endpoints
CRUD operations for Crew management
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from bend.schemas.crew import (
    CrewCreate,
    CrewUpdate,
    CrewResponse,
    CrewListResponse,
    CrewValidationResponse
)
from bend.services import CrewService
from bend.database.connection import get_db_session

router = APIRouter()


@router.get("/", response_model=CrewListResponse)
async def list_crews(db: Session = Depends(get_db_session)):
    """Get all crews"""
    service = CrewService(db)
    crews_list = service.list_crews()
    crews = [CrewResponse(**crew.to_dict()) for crew in crews_list]
    return CrewListResponse(crews=crews, total=len(crews))


@router.get("/{crew_id}", response_model=CrewResponse)
async def get_crew(crew_id: str, db: Session = Depends(get_db_session)):
    """Get a specific crew by ID"""
    service = CrewService(db)
    crew = service.get_crew(crew_id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crew with id '{crew_id}' not found"
        )
    return CrewResponse(**crew.to_dict())


@router.post("/", response_model=CrewResponse, status_code=status.HTTP_201_CREATED)
async def create_crew(crew_data: CrewCreate, db: Session = Depends(get_db_session)):
    """Create a new crew"""
    service = CrewService(db)
    try:
        crew = service.create_crew(
            name=crew_data.name,
            agent_ids=crew_data.agent_ids,
            task_ids=crew_data.task_ids,
            knowledge_source_ids=crew_data.knowledge_source_ids,
            process=crew_data.process,
            verbose=crew_data.verbose,
            cache=crew_data.cache,
            max_rpm=crew_data.max_rpm,
            memory=crew_data.memory,
            planning=crew_data.planning
        )
        return CrewResponse(**crew.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{crew_id}", response_model=CrewResponse)
async def update_crew(crew_id: str, crew_data: CrewUpdate, db: Session = Depends(get_db_session)):
    """Update an existing crew"""
    service = CrewService(db)
    try:
        update_dict = crew_data.model_dump(exclude_unset=True)
        crew = service.update_crew(crew_id, **update_dict)
        if not crew:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crew with id '{crew_id}' not found"
            )
        return CrewResponse(**crew.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{crew_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crew(crew_id: str, db: Session = Depends(get_db_session)):
    """Delete a crew"""
    service = CrewService(db)
    try:
        success = service.delete_crew(crew_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crew with id '{crew_id}' not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{crew_id}/validate", response_model=CrewValidationResponse)
async def validate_crew(crew_id: str, db: Session = Depends(get_db_session)):
    """Validate a crew configuration"""
    service = CrewService(db)
    try:
        validation = service.validate_crew(crew_id)
        return CrewValidationResponse(
            is_valid=validation['is_valid'],
            errors=validation['errors'],
            warnings=validation['warnings']
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
