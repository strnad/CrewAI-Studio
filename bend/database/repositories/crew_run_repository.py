"""
CrewRun Repository
Database operations for CrewRun model (execution history)
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from bend.database.models.crew_run import CrewRun
from bend.database.repositories.base import BaseRepository
from datetime import datetime


class CrewRunRepository(BaseRepository[CrewRun]):
    """Repository for CrewRun operations"""

    def __init__(self, db: Session):
        super().__init__(CrewRun, db)

    def get_by_crew_id(self, crew_id: str, limit: int = 10) -> List[CrewRun]:
        """
        Get execution history for a specific crew

        Args:
            crew_id: Crew ID
            limit: Maximum number of results

        Returns:
            List of crew runs ordered by started_at DESC
        """
        return self.db.query(CrewRun).filter(
            CrewRun.crew_id == crew_id
        ).order_by(
            CrewRun.started_at.desc()
        ).limit(limit).all()

    def get_by_status(self, status: str) -> List[CrewRun]:
        """
        Get crew runs by status

        Args:
            status: Execution status (pending, running, completed, failed)

        Returns:
            List of crew runs
        """
        return self.db.query(CrewRun).filter(
            CrewRun.status == status
        ).order_by(
            CrewRun.started_at.desc()
        ).all()

    def get_latest_run(self, crew_id: str) -> Optional[CrewRun]:
        """
        Get the latest execution for a specific crew

        Args:
            crew_id: Crew ID

        Returns:
            Latest crew run or None
        """
        return self.db.query(CrewRun).filter(
            CrewRun.crew_id == crew_id
        ).order_by(
            CrewRun.started_at.desc()
        ).first()

    def update_status(
        self,
        run_id: str,
        status: str,
        result: Optional[str] = None,
        error: Optional[str] = None
    ) -> Optional[CrewRun]:
        """
        Update execution status

        Args:
            run_id: CrewRun ID
            status: New status
            result: Execution result (optional)
            error: Error message (optional)

        Returns:
            Updated crew run or None
        """
        crew_run = self.get_by_id(run_id)
        if not crew_run:
            return None

        crew_run.status = status

        if result is not None:
            crew_run.result = result

        if error is not None:
            crew_run.error = error

        # Mark as completed if status is completed or failed
        if status in ["completed", "failed"]:
            crew_run.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(crew_run)

        return crew_run

    def mark_completed(self, run_id: str, result: str) -> Optional[CrewRun]:
        """
        Mark execution as completed

        Args:
            run_id: CrewRun ID
            result: Execution result

        Returns:
            Updated crew run or None
        """
        return self.update_status(
            run_id=run_id,
            status="completed",
            result=result
        )

    def mark_failed(self, run_id: str, error: str) -> Optional[CrewRun]:
        """
        Mark execution as failed

        Args:
            run_id: CrewRun ID
            error: Error message

        Returns:
            Updated crew run or None
        """
        return self.update_status(
            run_id=run_id,
            status="failed",
            error=error
        )

    def mark_running(self, run_id: str) -> Optional[CrewRun]:
        """
        Mark execution as running

        Args:
            run_id: CrewRun ID

        Returns:
            Updated crew run or None
        """
        return self.update_status(
            run_id=run_id,
            status="running"
        )

    def get_running_executions(self) -> List[CrewRun]:
        """
        Get all currently running executions

        Returns:
            List of running crew runs
        """
        return self.get_by_status("running")

    def get_failed_executions(self, limit: int = 10) -> List[CrewRun]:
        """
        Get recent failed executions

        Args:
            limit: Maximum number of results

        Returns:
            List of failed crew runs
        """
        return self.db.query(CrewRun).filter(
            CrewRun.status == "failed"
        ).order_by(
            CrewRun.started_at.desc()
        ).limit(limit).all()
