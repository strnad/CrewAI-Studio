"""
Task Repository
Database operations for Task model
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from bend.database.models.task import Task
from bend.database.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Repository for Task operations"""

    def __init__(self, db: Session):
        super().__init__(Task, db)

    def get_by_id_with_relations(self, id: str) -> Optional[Task]:
        """
        Get task by ID with related agent and context tasks

        Args:
            id: Task ID

        Returns:
            Task instance with relations loaded or None
        """
        return self.db.query(Task).options(
            joinedload(Task.agent),
            joinedload(Task.context_async_tasks),
            joinedload(Task.context_sync_tasks)
        ).filter(Task.id == id).first()

    def get_by_agent_id(self, agent_id: str) -> List[Task]:
        """
        Get all tasks for an agent

        Args:
            agent_id: Agent ID

        Returns:
            List of tasks
        """
        return self.db.query(Task).filter(Task.agent_id == agent_id).all()

    def get_tasks_by_ids(self, task_ids: List[str]) -> List[Task]:
        """
        Get multiple tasks by IDs

        Args:
            task_ids: List of task IDs

        Returns:
            List of tasks
        """
        return self.db.query(Task).filter(Task.id.in_(task_ids)).all()

    def search_by_description(self, query: str) -> List[Task]:
        """
        Search tasks by description (case-insensitive)

        Args:
            query: Search query

        Returns:
            List of matching tasks
        """
        return self.db.query(Task).filter(
            Task.description.ilike(f"%{query}%")
        ).all()

    def add_async_context_task(self, task_id: str, context_task_id: str) -> Optional[Task]:
        """
        Add async context task

        Args:
            task_id: Task ID
            context_task_id: Context task ID to add

        Returns:
            Updated task or None
        """
        task = self.get_by_id(task_id)
        if not task:
            return None

        context_task = self.get_by_id(context_task_id)
        if not context_task:
            return None

        if context_task not in task.context_async_tasks:
            task.context_async_tasks.append(context_task)
            self.db.commit()
            self.db.refresh(task)

        return task

    def remove_async_context_task(self, task_id: str, context_task_id: str) -> Optional[Task]:
        """
        Remove async context task

        Args:
            task_id: Task ID
            context_task_id: Context task ID to remove

        Returns:
            Updated task or None
        """
        task = self.get_by_id(task_id)
        if not task:
            return None

        context_task = self.get_by_id(context_task_id)
        if context_task and context_task in task.context_async_tasks:
            task.context_async_tasks.remove(context_task)
            self.db.commit()
            self.db.refresh(task)

        return task

    def add_sync_context_task(self, task_id: str, context_task_id: str) -> Optional[Task]:
        """
        Add sync context task

        Args:
            task_id: Task ID
            context_task_id: Context task ID to add

        Returns:
            Updated task or None
        """
        task = self.get_by_id(task_id)
        if not task:
            return None

        context_task = self.get_by_id(context_task_id)
        if not context_task:
            return None

        if context_task not in task.context_sync_tasks:
            task.context_sync_tasks.append(context_task)
            self.db.commit()
            self.db.refresh(task)

        return task

    def remove_sync_context_task(self, task_id: str, context_task_id: str) -> Optional[Task]:
        """
        Remove sync context task

        Args:
            task_id: Task ID
            context_task_id: Context task ID to remove

        Returns:
            Updated task or None
        """
        task = self.get_by_id(task_id)
        if not task:
            return None

        context_task = self.get_by_id(context_task_id)
        if context_task and context_task in task.context_sync_tasks:
            task.context_sync_tasks.remove(context_task)
            self.db.commit()
            self.db.refresh(task)

        return task

    def is_used_as_context(self, task_id: str) -> bool:
        """
        Check if task is used as context by other tasks

        Args:
            task_id: Task ID

        Returns:
            True if task is used as context, False otherwise
        """
        task = self.get_by_id(task_id)
        if not task:
            return False

        # Check if any tasks reference this task as context
        return len(task.referenced_by_async) > 0 or len(task.referenced_by_sync) > 0
