"""
Crew Service
Business logic for Crew operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from bend.database.repositories.crew_repository import CrewRepository
from bend.database.repositories.agent_repository import AgentRepository
from bend.database.repositories.task_repository import TaskRepository
from bend.database.repositories.knowledge_source_repository import KnowledgeSourceRepository
from bend.database.models.crew import Crew


class CrewService:
    """Service for Crew business logic"""

    def __init__(self, db: Session):
        """Initialize service"""
        self.db = db
        self.repo = CrewRepository(db)
        self.agent_repo = AgentRepository(db)
        self.task_repo = TaskRepository(db)
        self.ks_repo = KnowledgeSourceRepository(db)

    def create_crew(
        self,
        name: str,
        agent_ids: List[str] = None,
        task_ids: List[str] = None,
        knowledge_source_ids: List[str] = None,
        process: str = "sequential",
        verbose: bool = True,
        cache: bool = True,
        max_rpm: int = 1000,
        memory: bool = False,
        planning: bool = False
    ) -> Crew:
        """Create new crew"""
        # Validation
        if not name or not name.strip():
            raise ValueError("Crew name is required")

        if process not in ["sequential", "hierarchical"]:
            raise ValueError("Process must be 'sequential' or 'hierarchical'")

        # Validate agents
        agent_ids = agent_ids or []
        agents = []
        for agent_id in agent_ids:
            agent = self.agent_repo.get_by_id(agent_id)
            if not agent:
                raise ValueError(f"Agent with id '{agent_id}' not found")
            agents.append(agent)

        # Validate tasks
        task_ids = task_ids or []
        tasks = []
        for task_id in task_ids:
            task = self.task_repo.get_by_id(task_id)
            if not task:
                raise ValueError(f"Task with id '{task_id}' not found")
            tasks.append(task)

        # Validate knowledge sources
        knowledge_source_ids = knowledge_source_ids or []
        knowledge_sources = []
        for ks_id in knowledge_source_ids:
            ks = self.ks_repo.get_by_id(ks_id)
            if not ks:
                raise ValueError(f"Knowledge source with id '{ks_id}' not found")
            knowledge_sources.append(ks)

        # Create crew
        crew = self.repo.create(
            name=name,
            process=process,
            verbose=verbose,
            cache=cache,
            max_rpm=max_rpm,
            memory=memory,
            planning=planning
        )

        # Add relationships
        for agent in agents:
            crew.agents.append(agent)
        for task in tasks:
            crew.tasks.append(task)
        for ks in knowledge_sources:
            crew.knowledge_sources.append(ks)

        self.db.commit()
        self.db.refresh(crew)

        return crew

    def get_crew(self, crew_id: str) -> Optional[Crew]:
        """Get crew by ID with relations"""
        return self.repo.get_by_id_with_relations(crew_id)

    def list_crews(self, skip: int = 0, limit: int = 100) -> List[Crew]:
        """List all crews"""
        return self.repo.get_all(skip=skip, limit=limit)

    def update_crew(self, crew_id: str, **kwargs) -> Optional[Crew]:
        """Update crew"""
        crew = self.repo.get_by_id(crew_id)
        if not crew:
            raise ValueError(f"Crew with id '{crew_id}' not found")

        # Validate process
        if 'process' in kwargs:
            if kwargs['process'] not in ["sequential", "hierarchical"]:
                raise ValueError("Process must be 'sequential' or 'hierarchical'")

        # Handle agent_ids update
        if 'agent_ids' in kwargs:
            agent_ids = kwargs.pop('agent_ids')
            agents = self.agent_repo.get_agents_by_ids(agent_ids)
            if len(agents) != len(agent_ids):
                found_ids = [a.id for a in agents]
                missing = set(agent_ids) - set(found_ids)
                raise ValueError(f"Agents not found: {', '.join(missing)}")
            crew.agents = agents

        # Handle task_ids update
        if 'task_ids' in kwargs:
            task_ids = kwargs.pop('task_ids')
            tasks = self.task_repo.get_tasks_by_ids(task_ids)
            if len(tasks) != len(task_ids):
                found_ids = [t.id for t in tasks]
                missing = set(task_ids) - set(found_ids)
                raise ValueError(f"Tasks not found: {', '.join(missing)}")
            crew.tasks = tasks

        # Handle knowledge_source_ids update
        if 'knowledge_source_ids' in kwargs:
            ks_ids = kwargs.pop('knowledge_source_ids')
            knowledge_sources = self.ks_repo.get_knowledge_sources_by_ids(ks_ids)
            if len(knowledge_sources) != len(ks_ids):
                found_ids = [ks.id for ks in knowledge_sources]
                missing = set(ks_ids) - set(found_ids)
                raise ValueError(f"Knowledge sources not found: {', '.join(missing)}")
            crew.knowledge_sources = knowledge_sources

        # Update other fields
        if kwargs:
            self.repo.update(crew_id, **kwargs)

        self.db.commit()
        self.db.refresh(crew)
        return crew

    def delete_crew(self, crew_id: str) -> bool:
        """Delete crew"""
        crew = self.repo.get_by_id(crew_id)
        if not crew:
            return False

        return self.repo.delete(crew_id)

    def validate_crew(self, crew_id: str) -> Dict[str, Any]:
        """Validate crew configuration"""
        crew = self.repo.get_by_id_with_relations(crew_id)
        if not crew:
            raise ValueError(f"Crew with id '{crew_id}' not found")

        errors = []
        warnings = []

        # Validate name
        if not crew.name or not crew.name.strip():
            errors.append("Crew name is required")

        # Validate process
        if crew.process not in ["sequential", "hierarchical"]:
            errors.append("Process must be 'sequential' or 'hierarchical'")

        # Check agents
        if not crew.agents:
            warnings.append("Crew has no agents assigned")

        # Check tasks
        if not crew.tasks:
            warnings.append("Crew has no tasks assigned")

        # Check agent-task consistency
        if crew.agents and crew.tasks:
            task_agent_ids = {task.agent_id for task in crew.tasks}
            crew_agent_ids = {agent.id for agent in crew.agents}

            # Tasks referencing agents not in crew
            missing_agents = task_agent_ids - crew_agent_ids
            if missing_agents:
                warnings.append(
                    f"Some tasks reference agents not in crew: {', '.join(missing_agents)}"
                )

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
