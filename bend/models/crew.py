"""
Crew Domain Model
Pure business logic without UI dependencies
"""
from crewai import Crew, Process
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import sys
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def generate_id() -> str:
    """Generate unique ID for crew"""
    import uuid
    return f"C_{uuid.uuid4().hex[:8]}"


@dataclass
class CrewModel:
    """
    Crew Domain Model
    Represents a CrewAI crew configuration without UI dependencies
    """

    # Core fields
    id: str = field(default_factory=generate_id)
    name: str = "Crew 1"
    agents: List[Any] = field(default_factory=list)  # List of AgentModel
    tasks: List[Any] = field(default_factory=list)  # List of TaskModel
    process: Process = Process.sequential
    verbose: bool = True
    cache: bool = True
    max_rpm: int = 1000
    memory: bool = False
    planning: bool = False

    # Optional fields
    manager_llm: Optional[str] = None
    manager_agent: Optional[Any] = None  # AgentModel
    planning_llm: Optional[str] = None
    knowledge_source_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_crewai_crew(self, knowledge_sources_registry=None, *args, **kwargs) -> Crew:
        """
        Convert this model to CrewAI Crew instance

        Args:
            knowledge_sources_registry: Optional registry to fetch knowledge sources
            *args, **kwargs: Additional parameters for Crew

        Returns:
            Crew: CrewAI Crew instance
        """
        # Import here to avoid circular dependencies
        from llms import create_llm

        # Convert agents to CrewAI agents
        crewai_agents = [agent.get_crewai_agent() for agent in self.agents]

        # Create task objects with dependency resolution
        task_objects = {}

        def create_task(task):
            """Recursively create tasks with dependencies"""
            if task.id in task_objects:
                return task_objects[task.id]

            context_tasks = []
            if task.async_execution or task.context_from_async_tasks_ids or task.context_from_sync_tasks_ids:
                for context_task_id in (task.context_from_async_tasks_ids or []) + (task.context_from_sync_tasks_ids or []):
                    if context_task_id not in task_objects:
                        context_task = next((t for t in self.tasks if t.id == context_task_id), None)
                        if context_task:
                            context_tasks.append(create_task(context_task))
                        else:
                            print(f"Warning: Context task with id {context_task_id} not found for task {task.id}")
                    else:
                        context_tasks.append(task_objects[context_task_id])

            # Pass context if it's an async task or if specific context is defined
            if task.async_execution or context_tasks:
                crewai_task = task.get_crewai_task(context_from_async_tasks=context_tasks)
            else:
                crewai_task = task.get_crewai_task()

            task_objects[task.id] = crewai_task
            return crewai_task

        # Create all tasks, resolving dependencies recursively
        for task in self.tasks:
            create_task(task)

        # Collect tasks in original order
        crewai_tasks = [task_objects[task.id] for task in self.tasks]

        # Load knowledge sources if registry provided
        knowledge_sources = []
        if knowledge_sources_registry and self.knowledge_source_ids:
            for ks_id in self.knowledge_source_ids:
                try:
                    ks = knowledge_sources_registry.get(ks_id)
                    if ks:
                        knowledge_sources.append(ks.get_crewai_knowledge_source())
                except Exception as e:
                    print(f"Error loading knowledge source {ks_id}: {str(e)}")

        # Build crew parameters
        crew_params = {
            'agents': crewai_agents,
            'tasks': crewai_tasks,
            'cache': self.cache,
            'process': self.process,
            'max_rpm': self.max_rpm,
            'verbose': self.verbose,
            'memory': self.memory,
            'planning': self.planning,
            'knowledge_sources': knowledge_sources if knowledge_sources else None,
        }

        # Add manager LLM if specified
        if self.manager_llm:
            crew_params['manager_llm'] = create_llm(self.manager_llm)

        # Add manager agent if specified
        elif self.manager_agent:
            crew_params['manager_agent'] = self.manager_agent.get_crewai_agent()

        # Add planning LLM if specified
        if self.planning and self.planning_llm:
            crew_params['planning_llm'] = create_llm(self.planning_llm)

        # Merge additional kwargs
        crew_params.update(kwargs)

        return Crew(*args, **crew_params)

    def validate(self) -> Dict[str, List[str]]:
        """
        Validate crew configuration

        Returns:
            Dict with 'errors' and 'warnings' keys containing validation messages
        """
        errors = []
        warnings = []

        # Check for agents
        if len(self.agents) == 0:
            errors.append(f"Crew '{self.name}' has no agents")

        # Check for tasks
        if len(self.tasks) == 0:
            errors.append(f"Crew '{self.name}' has no tasks")

        # Validate agents
        for agent in self.agents:
            agent_validation = agent.validate()
            if agent_validation.get('errors'):
                errors.extend(agent_validation['errors'])
            if agent_validation.get('warnings'):
                warnings.extend(agent_validation['warnings'])

        # Validate tasks
        for task in self.tasks:
            task_validation = task.validate()
            if task_validation.get('errors'):
                errors.extend(task_validation['errors'])
            if task_validation.get('warnings'):
                warnings.extend(task_validation['warnings'])

        # Check hierarchical process requirements
        if self.process == Process.hierarchical:
            if not self.manager_llm and not self.manager_agent:
                errors.append(f"Crew '{self.name}' has hierarchical process but no manager LLM or manager agent set")

        # Check planning requirements
        if self.planning and not self.planning_llm:
            warnings.append(f"Crew '{self.name}' has planning enabled but no planning LLM selected")

        return {
            'errors': errors,
            'warnings': warnings,
            'is_valid': len(errors) == 0
        }

    def is_valid(self) -> bool:
        """Simple validation check (backward compatibility)"""
        return self.validate()['is_valid']

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'agent_ids': [agent.id for agent in self.agents],
            'task_ids': [task.id for task in self.tasks],
            'process': self.process.value if isinstance(self.process, Process) else self.process,
            'verbose': self.verbose,
            'cache': self.cache,
            'max_rpm': self.max_rpm,
            'memory': self.memory,
            'planning': self.planning,
            'manager_llm': self.manager_llm,
            'manager_agent_id': self.manager_agent.id if self.manager_agent else None,
            'planning_llm': self.planning_llm,
            'knowledge_source_ids': self.knowledge_source_ids,
            'created_at': self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], agents_registry=None, tasks_registry=None) -> 'CrewModel':
        """
        Create CrewModel from dictionary

        Args:
            data: Dictionary with crew data
            agents_registry: Optional dict of agent_id -> AgentModel
            tasks_registry: Optional dict of task_id -> TaskModel

        Returns:
            CrewModel instance
        """
        # Resolve agents
        agents = []
        if agents_registry and 'agent_ids' in data:
            agents = [agents_registry[aid] for aid in data['agent_ids'] if aid in agents_registry]

        # Resolve tasks
        tasks = []
        if tasks_registry and 'task_ids' in data:
            tasks = [tasks_registry[tid] for tid in data['task_ids'] if tid in tasks_registry]

        # Resolve manager agent
        manager_agent = None
        if agents_registry and data.get('manager_agent_id'):
            manager_agent = agents_registry.get(data['manager_agent_id'])

        # Convert process string to enum if needed
        process = data.get('process', Process.sequential)
        if isinstance(process, str):
            process = Process[process] if hasattr(Process, process) else Process.sequential

        return cls(
            id=data.get('id'),
            name=data.get('name', 'Crew 1'),
            agents=agents,
            tasks=tasks,
            process=process,
            verbose=data.get('verbose', True),
            cache=data.get('cache', True),
            max_rpm=data.get('max_rpm', 1000),
            memory=data.get('memory', False),
            planning=data.get('planning', False),
            manager_llm=data.get('manager_llm'),
            manager_agent=manager_agent,
            planning_llm=data.get('planning_llm'),
            knowledge_source_ids=data.get('knowledge_source_ids', []),
            created_at=data.get('created_at', datetime.now().isoformat()),
        )
