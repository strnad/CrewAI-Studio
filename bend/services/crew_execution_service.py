"""
Crew Execution Service
Business logic for executing CrewAI crews
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from crewai import Crew, Agent, Task, Process, LLM
from bend.database.repositories.crew_repository import CrewRepository
from bend.database.repositories.crew_run_repository import CrewRunRepository
from bend.database.repositories.agent_repository import AgentRepository
from bend.database.repositories.task_repository import TaskRepository
from bend.database.repositories.knowledge_source_repository import KnowledgeSourceRepository
from bend.database.repositories.tool_repository import ToolRepository
from bend.database.models.crew import Crew as CrewModel
from bend.database.models.crew_run import CrewRun
from datetime import datetime
import json


class CrewExecutionService:
    """Service for executing CrewAI crews"""

    def __init__(self, db: Session):
        """Initialize service"""
        self.db = db
        self.crew_repo = CrewRepository(db)
        self.crew_run_repo = CrewRunRepository(db)
        self.agent_repo = AgentRepository(db)
        self.task_repo = TaskRepository(db)
        self.ks_repo = KnowledgeSourceRepository(db)
        self.tool_repo = ToolRepository(db)

    def _convert_db_agent_to_crewai(self, db_agent) -> Agent:
        """
        Convert database Agent model to CrewAI Agent

        Args:
            db_agent: Database Agent model

        Returns:
            CrewAI Agent instance
        """
        # Create LLM instance from provider model string
        llm = LLM(model=db_agent.llm_provider_model, temperature=db_agent.temperature)

        # Convert tools (if any)
        tools = []
        for db_tool in db_agent.tools:
            # TODO: Implement tool conversion
            # For now, skip tools - will implement later
            pass

        # Convert knowledge sources (if any)
        knowledge_sources = []
        for db_ks in db_agent.knowledge_sources:
            # TODO: Implement knowledge source conversion
            # For now, skip knowledge sources - will implement later
            pass

        # Create CrewAI Agent
        return Agent(
            role=db_agent.role,
            goal=db_agent.goal,
            backstory=db_agent.backstory,
            llm=llm,
            tools=tools if tools else None,
            knowledge_sources=knowledge_sources if knowledge_sources else None,
            allow_delegation=db_agent.allow_delegation,
            verbose=db_agent.verbose,
            cache=db_agent.cache,
            max_iter=db_agent.max_iter,
        )

    def _convert_db_task_to_crewai(self, db_task, agent_map: Dict[str, Agent], task_map: Dict[str, Task]) -> Task:
        """
        Convert database Task model to CrewAI Task

        Args:
            db_task: Database Task model
            agent_map: Mapping of agent_id to CrewAI Agent
            task_map: Mapping of task_id to CrewAI Task (for context tasks)

        Returns:
            CrewAI Task instance
        """
        # Get agent for this task
        agent = agent_map.get(db_task.agent_id)
        if not agent:
            raise ValueError(f"Agent with id '{db_task.agent_id}' not found for task '{db_task.id}'")

        # Get context tasks (if any)
        context = []
        for context_task in db_task.context_async_tasks + db_task.context_sync_tasks:
            if context_task.id in task_map:
                context.append(task_map[context_task.id])

        # Create CrewAI Task
        return Task(
            description=db_task.description,
            expected_output=db_task.expected_output,
            agent=agent,
            async_execution=db_task.async_execution,
            context=context if context else None,
        )

    def _convert_db_crew_to_crewai(self, db_crew: CrewModel) -> Crew:
        """
        Convert database Crew model to CrewAI Crew

        Args:
            db_crew: Database Crew model

        Returns:
            CrewAI Crew instance
        """
        # Convert agents
        agent_map = {}
        crewai_agents = []
        for db_agent in db_crew.agents:
            crewai_agent = self._convert_db_agent_to_crewai(db_agent)
            agent_map[db_agent.id] = crewai_agent
            crewai_agents.append(crewai_agent)

        # Convert tasks (with dependency resolution)
        task_map = {}

        def create_task_recursive(db_task):
            """Recursively create task with its context dependencies"""
            if db_task.id in task_map:
                return task_map[db_task.id]

            # First create all context tasks
            for context_task in db_task.context_async_tasks + db_task.context_sync_tasks:
                if context_task.id not in task_map:
                    create_task_recursive(context_task)

            # Now create this task
            crewai_task = self._convert_db_task_to_crewai(db_task, agent_map, task_map)
            task_map[db_task.id] = crewai_task
            return crewai_task

        # Create all tasks
        for db_task in db_crew.tasks:
            create_task_recursive(db_task)

        # Collect tasks in original order
        crewai_tasks = [task_map[db_task.id] for db_task in db_crew.tasks]

        # Convert knowledge sources (if any)
        knowledge_sources = []
        for db_ks in db_crew.knowledge_sources:
            # TODO: Implement knowledge source conversion
            # For now, skip knowledge sources - will implement later
            pass

        # Determine process type
        process = Process.sequential if db_crew.process == "sequential" else Process.hierarchical

        # Create manager LLM if needed (for hierarchical process)
        manager_llm = None
        if process == Process.hierarchical:
            # Use first agent's LLM as manager LLM (default behavior)
            # In production, you might want to store manager_llm in database
            if crewai_agents:
                manager_llm = crewai_agents[0].llm

        # Create CrewAI Crew
        crew_params = {
            "agents": crewai_agents,
            "tasks": crewai_tasks,
            "process": process,
            "verbose": db_crew.verbose,
            "cache": db_crew.cache,
            "max_rpm": db_crew.max_rpm,
            "memory": db_crew.memory,
            "planning": db_crew.planning,
        }

        if knowledge_sources:
            crew_params["knowledge_sources"] = knowledge_sources

        if process == Process.hierarchical and manager_llm:
            crew_params["manager_llm"] = manager_llm

        return Crew(**crew_params)

    def execute_crew(self, crew_id: str, inputs: Dict[str, Any] = None) -> CrewRun:
        """
        Execute a crew and return execution result

        Args:
            crew_id: Crew ID to execute
            inputs: Input parameters for the crew

        Returns:
            CrewRun instance with execution result

        Raises:
            ValueError: If crew not found or invalid
        """
        # Get crew from database
        db_crew = self.crew_repo.get_by_id_with_relations(crew_id)
        if not db_crew:
            raise ValueError(f"Crew with id '{crew_id}' not found")

        # Validate crew
        validation = self._validate_crew_for_execution(db_crew)
        if not validation["is_valid"]:
            raise ValueError(f"Crew validation failed: {', '.join(validation['errors'])}")

        # Create execution record
        crew_run = self.crew_run_repo.create(
            crew_id=crew_id,
            inputs=inputs or {},
            status="pending"
        )

        try:
            # Mark as running
            self.crew_run_repo.mark_running(crew_run.id)

            # Convert DB crew to CrewAI crew
            crewai_crew = self._convert_db_crew_to_crewai(db_crew)

            # Execute crew
            result = crewai_crew.kickoff(inputs=inputs or {})

            # Convert result to string (it might be CrewOutput object)
            result_str = str(result)

            # Mark as completed
            crew_run = self.crew_run_repo.mark_completed(crew_run.id, result_str)

        except Exception as e:
            # Mark as failed
            crew_run = self.crew_run_repo.mark_failed(crew_run.id, str(e))
            raise

        return crew_run

    def _validate_crew_for_execution(self, db_crew: CrewModel) -> Dict[str, Any]:
        """
        Validate crew before execution

        Args:
            db_crew: Database Crew model

        Returns:
            Validation result
        """
        errors = []

        # Check agents
        if not db_crew.agents:
            errors.append("Crew has no agents")

        # Check tasks
        if not db_crew.tasks:
            errors.append("Crew has no tasks")

        # Check agent-task consistency
        if db_crew.agents and db_crew.tasks:
            task_agent_ids = {task.agent_id for task in db_crew.tasks}
            crew_agent_ids = {agent.id for agent in db_crew.agents}

            missing_agents = task_agent_ids - crew_agent_ids
            if missing_agents:
                errors.append(f"Tasks reference agents not in crew: {', '.join(missing_agents)}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    def get_execution_status(self, run_id: str) -> Optional[CrewRun]:
        """
        Get execution status

        Args:
            run_id: CrewRun ID

        Returns:
            CrewRun instance or None
        """
        return self.crew_run_repo.get_by_id(run_id)

    def get_crew_execution_history(self, crew_id: str, limit: int = 10) -> list[CrewRun]:
        """
        Get execution history for a crew

        Args:
            crew_id: Crew ID
            limit: Maximum number of results

        Returns:
            List of CrewRun instances
        """
        return self.crew_run_repo.get_by_crew_id(crew_id, limit)
