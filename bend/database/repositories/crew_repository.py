"""
Crew Repository
Database operations for Crew model
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from bend.database.models.crew import Crew
from bend.database.repositories.base import BaseRepository


class CrewRepository(BaseRepository[Crew]):
    """Repository for Crew operations"""

    def __init__(self, db: Session):
        super().__init__(Crew, db)

    def get_by_id_with_relations(self, id: str) -> Optional[Crew]:
        """
        Get crew by ID with related agents, tasks, and knowledge sources

        Args:
            id: Crew ID

        Returns:
            Crew instance with relations loaded or None
        """
        return self.db.query(Crew).options(
            joinedload(Crew.agents),
            joinedload(Crew.tasks),
            joinedload(Crew.knowledge_sources)
        ).filter(Crew.id == id).first()

    def get_by_name(self, name: str) -> Optional[Crew]:
        """
        Get crew by name

        Args:
            name: Crew name

        Returns:
            Crew instance or None
        """
        return self.db.query(Crew).filter(Crew.name == name).first()

    def search_by_name(self, query: str) -> List[Crew]:
        """
        Search crews by name (case-insensitive)

        Args:
            query: Search query

        Returns:
            List of matching crews
        """
        return self.db.query(Crew).filter(
            Crew.name.ilike(f"%{query}%")
        ).all()

    def add_agent(self, crew_id: str, agent_id: str) -> Optional[Crew]:
        """
        Add agent to crew

        Args:
            crew_id: Crew ID
            agent_id: Agent ID

        Returns:
            Updated crew or None
        """
        from bend.database.models.agent import Agent

        crew = self.get_by_id(crew_id)
        if not crew:
            return None

        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return None

        if agent not in crew.agents:
            crew.agents.append(agent)
            self.db.commit()
            self.db.refresh(crew)

        return crew

    def remove_agent(self, crew_id: str, agent_id: str) -> Optional[Crew]:
        """
        Remove agent from crew

        Args:
            crew_id: Crew ID
            agent_id: Agent ID

        Returns:
            Updated crew or None
        """
        from bend.database.models.agent import Agent

        crew = self.get_by_id(crew_id)
        if not crew:
            return None

        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if agent and agent in crew.agents:
            crew.agents.remove(agent)
            self.db.commit()
            self.db.refresh(crew)

        return crew

    def add_task(self, crew_id: str, task_id: str) -> Optional[Crew]:
        """
        Add task to crew

        Args:
            crew_id: Crew ID
            task_id: Task ID

        Returns:
            Updated crew or None
        """
        from bend.database.models.task import Task

        crew = self.get_by_id(crew_id)
        if not crew:
            return None

        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None

        if task not in crew.tasks:
            crew.tasks.append(task)
            self.db.commit()
            self.db.refresh(crew)

        return crew

    def remove_task(self, crew_id: str, task_id: str) -> Optional[Crew]:
        """
        Remove task from crew

        Args:
            crew_id: Crew ID
            task_id: Task ID

        Returns:
            Updated crew or None
        """
        from bend.database.models.task import Task

        crew = self.get_by_id(crew_id)
        if not crew:
            return None

        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task and task in crew.tasks:
            crew.tasks.remove(task)
            self.db.commit()
            self.db.refresh(crew)

        return crew

    def add_knowledge_source(self, crew_id: str, ks_id: str) -> Optional[Crew]:
        """
        Add knowledge source to crew

        Args:
            crew_id: Crew ID
            ks_id: Knowledge source ID

        Returns:
            Updated crew or None
        """
        from bend.database.models.knowledge_source import KnowledgeSource

        crew = self.get_by_id(crew_id)
        if not crew:
            return None

        ks = self.db.query(KnowledgeSource).filter(KnowledgeSource.id == ks_id).first()
        if not ks:
            return None

        if ks not in crew.knowledge_sources:
            crew.knowledge_sources.append(ks)
            self.db.commit()
            self.db.refresh(crew)

        return crew

    def remove_knowledge_source(self, crew_id: str, ks_id: str) -> Optional[Crew]:
        """
        Remove knowledge source from crew

        Args:
            crew_id: Crew ID
            ks_id: Knowledge source ID

        Returns:
            Updated crew or None
        """
        from bend.database.models.knowledge_source import KnowledgeSource

        crew = self.get_by_id(crew_id)
        if not crew:
            return None

        ks = self.db.query(KnowledgeSource).filter(KnowledgeSource.id == ks_id).first()
        if ks and ks in crew.knowledge_sources:
            crew.knowledge_sources.remove(ks)
            self.db.commit()
            self.db.refresh(crew)

        return crew

    def get_by_process(self, process: str) -> List[Crew]:
        """
        Get crews by process type

        Args:
            process: Process type (sequential or hierarchical)

        Returns:
            List of crews
        """
        return self.db.query(Crew).filter(Crew.process == process).all()

    def delete(self, id: str) -> bool:
        """
        Delete crew by ID
        Overrides BaseRepository.delete to handle crew_runs cascade delete

        Args:
            id: Crew ID

        Returns:
            True if deleted, False if not found

        Raises:
            SQLAlchemyError: Database error
        """
        from bend.database.models.crew_run import CrewRun
        from sqlalchemy.exc import SQLAlchemyError

        try:
            crew = self.get_by_id(id)
            if not crew:
                return False

            # Delete all crew runs first (manual cascade)
            self.db.query(CrewRun).filter(CrewRun.crew_id == id).delete()

            # Clear relationships
            crew.agents = []
            crew.tasks = []
            crew.knowledge_sources = []

            # Delete the crew
            self.db.delete(crew)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
