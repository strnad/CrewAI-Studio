"""
Tasks API Endpoints
CRUD operations for tasks
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from bend.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskValidationResponse
)
from bend.services import TaskService
from bend.database.connection import get_db_session

router = APIRouter()


@router.get("/", response_model=TaskListResponse)
async def list_tasks(db: Session = Depends(get_db_session)):
    """Get all tasks"""
    service = TaskService(db)
    tasks_list = service.list_tasks()
    tasks = [TaskResponse(**task.to_dict()) for task in tasks_list]
    return TaskListResponse(tasks=tasks, total=len(tasks))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db_session)):
    """Get a specific task by ID"""
    service = TaskService(db)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found"
        )
    return TaskResponse(**task.to_dict())


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db_session)):
    """Create a new task"""
    service = TaskService(db)
    try:
        task = service.create_task(
            description=task_data.description,
            expected_output=task_data.expected_output,
            agent_id=task_data.agent_id,
            async_execution=task_data.async_execution,
            context_from_async_tasks_ids=task_data.context_from_async_tasks_ids,
            context_from_sync_tasks_ids=task_data.context_from_sync_tasks_ids
        )
        return TaskResponse(**task.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_data: TaskUpdate, db: Session = Depends(get_db_session)):
    """Update an existing task"""
    service = TaskService(db)
    try:
        update_dict = task_data.model_dump(exclude_unset=True)
        task = service.update_task(task_id, **update_dict)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{task_id}' not found"
            )
        return TaskResponse(**task.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, db: Session = Depends(get_db_session)):
    """Delete a task"""
    service = TaskService(db)
    try:
        success = service.delete_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{task_id}' not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{task_id}/validate", response_model=TaskValidationResponse)
async def validate_task(task_id: str, db: Session = Depends(get_db_session)):
    """Validate a task configuration"""
    service = TaskService(db)
    try:
        validation = service.validate_task(task_id)
        return TaskValidationResponse(
            is_valid=validation['is_valid'],
            errors=validation['errors'],
            warnings=validation['warnings']
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
