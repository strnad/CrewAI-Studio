"""
Crews API Endpoints
CRUD operations for Crew management
"""
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from bend.schemas.crew import (
    CrewCreate,
    CrewUpdate,
    CrewResponse,
    CrewListResponse,
    CrewValidationResponse,
    CrewExecutionRequest,
    CrewExecutionResponse
)
from bend.services import CrewService
from bend.services.crew_execution_service import CrewExecutionService
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


@router.post("/{crew_id}/kickoff", response_model=CrewExecutionResponse, status_code=status.HTTP_201_CREATED)
async def execute_crew(
    crew_id: str,
    background_tasks: BackgroundTasks,
    inputs: Dict[str, Any] = None,
    db: Session = Depends(get_db_session)
):
    """
    Execute a crew with given inputs (asynchronously)

    Args:
        crew_id: Crew ID to execute
        background_tasks: FastAPI background tasks
        inputs: Input parameters for the crew execution (optional)

    Returns:
        CrewExecutionResponse with execution details (status: pending)
    """
    service = CrewExecutionService(db)
    try:
        # Create crew run record (status: pending)
        crew_run = service.create_crew_run(crew_id, inputs or {})

        # Execute crew in background
        background_tasks.add_task(service.execute_crew_async, crew_run.id, inputs or {})

        # Return execution response immediately
        return CrewExecutionResponse(
            execution_id=crew_run.id,
            crew_id=crew_run.crew_id,
            status=crew_run.status,
            started_at=crew_run.started_at.isoformat() if crew_run.started_at else None,
            completed_at=crew_run.completed_at.isoformat() if crew_run.completed_at else None,
            result=None,
            error=None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start crew execution: {str(e)}"
        )


@router.get("/{crew_id}/runs/{run_id}", response_model=CrewExecutionResponse)
async def get_execution_status(
    crew_id: str,
    run_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Get status of a specific crew execution

    Args:
        crew_id: Crew ID
        run_id: Execution run ID

    Returns:
        CrewExecutionResponse with execution status
    """
    service = CrewExecutionService(db)
    crew_run = service.get_execution_status(run_id)

    if not crew_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution run with id '{run_id}' not found"
        )

    if crew_run.crew_id != crew_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution run '{run_id}' does not belong to crew '{crew_id}'"
        )

    return CrewExecutionResponse(
        execution_id=crew_run.id,
        crew_id=crew_run.crew_id,
        status=crew_run.status,
        started_at=crew_run.started_at.isoformat() if crew_run.started_at else None,
        completed_at=crew_run.completed_at.isoformat() if crew_run.completed_at else None,
        result={"output": crew_run.result} if crew_run.result else None,
        error=crew_run.error
    )


@router.get("/{crew_id}/runs", response_model=List[CrewExecutionResponse])
async def get_execution_history(
    crew_id: str,
    limit: int = 10,
    db: Session = Depends(get_db_session)
):
    """
    Get execution history for a crew

    Args:
        crew_id: Crew ID
        limit: Maximum number of results (default: 10)

    Returns:
        List of CrewExecutionResponse with execution history
    """
    service = CrewExecutionService(db)

    # Check if crew exists
    crew = service.crew_repo.get_by_id(crew_id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crew with id '{crew_id}' not found"
        )

    # Get execution history
    crew_runs = service.get_crew_execution_history(crew_id, limit)

    return [
        CrewExecutionResponse(
            execution_id=crew_run.id,
            crew_id=crew_run.crew_id,
            status=crew_run.status,
            started_at=crew_run.started_at.isoformat() if crew_run.started_at else None,
            completed_at=crew_run.completed_at.isoformat() if crew_run.completed_at else None,
            result={"output": crew_run.result} if crew_run.result else None,
            error=crew_run.error
        )
        for crew_run in crew_runs
    ]


@router.post("/{crew_id}/runs/{run_id}/stop", response_model=CrewExecutionResponse)
async def stop_execution(
    crew_id: str,
    run_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Stop a running crew execution

    Args:
        crew_id: Crew ID
        run_id: Execution run ID

    Returns:
        CrewExecutionResponse with updated status
    """
    service = CrewExecutionService(db)

    # Get crew run
    crew_run = service.get_execution_status(run_id)

    if not crew_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution run with id '{run_id}' not found"
        )

    if crew_run.crew_id != crew_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution run '{run_id}' does not belong to crew '{crew_id}'"
        )

    # Check if execution is still running
    if crew_run.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot stop execution with status '{crew_run.status}'. Only 'pending' or 'running' executions can be stopped."
        )

    # Cancel execution
    crew_run = service.cancel_execution(run_id)

    return CrewExecutionResponse(
        execution_id=crew_run.id,
        crew_id=crew_run.crew_id,
        status=crew_run.status,
        started_at=crew_run.started_at.isoformat() if crew_run.started_at else None,
        completed_at=crew_run.completed_at.isoformat() if crew_run.completed_at else None,
        result={"output": crew_run.result} if crew_run.result else None,
        error=crew_run.error
    )
