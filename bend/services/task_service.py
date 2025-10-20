"""
Task Service
Business logic for Task operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from bend.database.repositories.task_repository import TaskRepository
from bend.database.repositories.agent_repository import AgentRepository
from bend.database.models.task import Task


class TaskService:
    """Service for Task business logic"""

    def __init__(self, db: Session):
        """Initialize service"""
        self.db = db
        self.repo = TaskRepository(db)
        self.agent_repo = AgentRepository(db)

    def create_task(
        self,
        description: str,
        expected_output: str,
        agent_id: str,
        async_execution: bool = False,
        context_from_async_tasks_ids: List[str] = None,
        context_from_sync_tasks_ids: List[str] = None
    ) -> Task:
        """Create new task"""
        # Validation
        if not description or not description.strip():
            raise ValueError("Task description is required")
        if not expected_output or not expected_output.strip():
            raise ValueError("Task expected_output is required")

        # Validate agent
        agent = self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent with id '{agent_id}' not found")

        # Create task
        task = self.repo.create(
            description=description,
            expected_output=expected_output,
            agent_id=agent_id,
            async_execution=async_execution
        )

        # Add context tasks
        for ctx_task_id in (context_from_async_tasks_ids or []):
            ctx_task = self.repo.get_by_id(ctx_task_id)
            if not ctx_task:
                raise ValueError(f"Context task with id '{ctx_task_id}' not found")
            task.context_async_tasks.append(ctx_task)

        for ctx_task_id in (context_from_sync_tasks_ids or []):
            ctx_task = self.repo.get_by_id(ctx_task_id)
            if not ctx_task:
                raise ValueError(f"Context task with id '{ctx_task_id}' not found")
            task.context_sync_tasks.append(ctx_task)

        self.db.commit()
        self.db.refresh(task)

        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID with relations"""
        return self.repo.get_by_id_with_relations(task_id)

    def list_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """List all tasks"""
        return self.repo.get_all(skip=skip, limit=limit)

    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        """Update task"""
        task = self.repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with id '{task_id}' not found")

        # Handle agent_id update
        if 'agent_id' in kwargs:
            agent = self.agent_repo.get_by_id(kwargs['agent_id'])
            if not agent:
                raise ValueError(f"Agent with id '{kwargs['agent_id']}' not found")

        # Handle context tasks update
        if 'context_from_async_tasks_ids' in kwargs:
            ctx_ids = kwargs.pop('context_from_async_tasks_ids')
            task.context_async_tasks = self.repo.get_tasks_by_ids(ctx_ids)

        if 'context_from_sync_tasks_ids' in kwargs:
            ctx_ids = kwargs.pop('context_from_sync_tasks_ids')
            task.context_sync_tasks = self.repo.get_tasks_by_ids(ctx_ids)

        # Update other fields
        if kwargs:
            self.repo.update(task_id, **kwargs)

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: str) -> bool:
        """Delete task"""
        task = self.repo.get_by_id(task_id)
        if not task:
            return False

        # Check if used as context
        if self.repo.is_used_as_context(task_id):
            raise ValueError(
                "Task is used as context by other tasks. "
                "Remove task from context before deleting."
            )

        # Check if used by crews
        if task.crews:
            crew_names = [crew.name for crew in task.crews]
            raise ValueError(
                f"Task is used by crews: {', '.join(crew_names)}. "
                "Remove task from crews before deleting."
            )

        return self.repo.delete(task_id)

    def validate_task(self, task_id: str) -> Dict[str, Any]:
        """Validate task configuration"""
        task = self.repo.get_by_id_with_relations(task_id)
        if not task:
            raise ValueError(f"Task with id '{task_id}' not found")

        errors = []
        warnings = []

        # Validate required fields
        if not task.description or not task.description.strip():
            errors.append("Task description is required")
        if not task.expected_output or not task.expected_output.strip():
            errors.append("Task expected_output is required")
        if not task.agent_id:
            errors.append("Task agent_id is required")

        # Check async execution with no context
        if task.async_execution:
            if not task.context_async_tasks and not task.context_sync_tasks:
                warnings.append(
                    "Task has async_execution=true but no context tasks. "
                    "Consider adding context tasks or setting async_execution=false."
                )

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
