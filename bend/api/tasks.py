"""
Tasks API Endpoints
CRUD operations for tasks
"""
from fastapi import APIRouter, HTTPException, status
from bend.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskValidationResponse
)
from bend.models.task import TaskModel
from bend.storage.memory import storage

router = APIRouter()


@router.get("/", response_model=TaskListResponse)
async def list_tasks():
    """Get all tasks"""
    tasks = [TaskResponse(**task.to_dict()) for task in storage.tasks.values()]
    return TaskListResponse(tasks=tasks, total=len(tasks))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get a specific task by ID"""
    task = storage.tasks.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found"
        )
    return TaskResponse(**task.to_dict())


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate):
    """Create a new task"""
    # Resolve agent from storage
    agent = storage.agents.get(task_data.agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent with id '{task_data.agent_id}' not found"
        )

    # Validate context task IDs if provided
    if task_data.context_from_async_tasks_ids:
        for context_task_id in task_data.context_from_async_tasks_ids:
            if context_task_id not in storage.tasks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Context task with id '{context_task_id}' not found"
                )

    if task_data.context_from_sync_tasks_ids:
        for context_task_id in task_data.context_from_sync_tasks_ids:
            if context_task_id not in storage.tasks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Context task with id '{context_task_id}' not found"
                )

    # Create task
    task = TaskModel(
        description=task_data.description,
        expected_output=task_data.expected_output,
        agent=agent,
        async_execution=task_data.async_execution,
        context_from_async_tasks_ids=task_data.context_from_async_tasks_ids,
        context_from_sync_tasks_ids=task_data.context_from_sync_tasks_ids,
    )

    # Store task
    storage.tasks[task.id] = task

    return TaskResponse(**task.to_dict())


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_data: TaskUpdate):
    """Update an existing task"""
    task = storage.tasks.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found"
        )

    # Update fields if provided
    update_dict = task_data.model_dump(exclude_unset=True)

    # Handle agent_id if provided
    if 'agent_id' in update_dict:
        agent = storage.agents.get(update_dict['agent_id'])
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent with id '{update_dict['agent_id']}' not found"
            )
        task.agent = agent
        del update_dict['agent_id']

    # Handle context_from_async_tasks_ids if provided
    if 'context_from_async_tasks_ids' in update_dict:
        if update_dict['context_from_async_tasks_ids']:
            for context_task_id in update_dict['context_from_async_tasks_ids']:
                if context_task_id not in storage.tasks:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Context task with id '{context_task_id}' not found"
                    )
        task.context_from_async_tasks_ids = update_dict['context_from_async_tasks_ids']
        del update_dict['context_from_async_tasks_ids']

    # Handle context_from_sync_tasks_ids if provided
    if 'context_from_sync_tasks_ids' in update_dict:
        if update_dict['context_from_sync_tasks_ids']:
            for context_task_id in update_dict['context_from_sync_tasks_ids']:
                if context_task_id not in storage.tasks:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Context task with id '{context_task_id}' not found"
                    )
        task.context_from_sync_tasks_ids = update_dict['context_from_sync_tasks_ids']
        del update_dict['context_from_sync_tasks_ids']

    # Update remaining fields
    for field, value in update_dict.items():
        if hasattr(task, field):
            setattr(task, field, value)

    return TaskResponse(**task.to_dict())


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """Delete a task"""
    if task_id not in storage.tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found"
        )

    # Check if task is used by any crews
    task_in_use = False
    crews_using_task = []
    for crew in storage.crews.values():
        if any(t.id == task_id for t in crew.tasks):
            task_in_use = True
            crews_using_task.append(crew.name)

    if task_in_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task is used by crews: {', '.join(crews_using_task)}. "
                   f"Remove task from crews before deleting."
        )

    # Check if task is used as context by other tasks
    task_used_as_context = False
    tasks_using_as_context = []
    for other_task in storage.tasks.values():
        if other_task.id == task_id:
            continue
        if other_task.context_from_async_tasks_ids and task_id in other_task.context_from_async_tasks_ids:
            task_used_as_context = True
            tasks_using_as_context.append(other_task.description[:50])
        if other_task.context_from_sync_tasks_ids and task_id in other_task.context_from_sync_tasks_ids:
            task_used_as_context = True
            tasks_using_as_context.append(other_task.description[:50])

    if task_used_as_context:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task is used as context by other tasks: {', '.join(tasks_using_as_context)}. "
                   f"Remove task from context references before deleting."
        )

    del storage.tasks[task_id]


@router.post("/{task_id}/validate", response_model=TaskValidationResponse)
async def validate_task(task_id: str):
    """Validate a task configuration"""
    task = storage.tasks.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found"
        )

    # Validate task
    validation = task.validate()

    return TaskValidationResponse(
        is_valid=validation['is_valid'],
        errors=validation['errors'],
        warnings=validation['warnings']
    )
