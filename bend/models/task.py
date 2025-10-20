"""
Task Domain Model
Pure business logic without UI dependencies
"""
from crewai import Task
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import sys
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def generate_id() -> str:
    """Generate unique ID for task"""
    import uuid
    return f"T_{uuid.uuid4().hex[:8]}"


@dataclass
class TaskModel:
    """
    Task Domain Model
    Represents a CrewAI task configuration without UI dependencies
    """

    # Core fields
    id: str = field(default_factory=generate_id)
    description: str = "Identify the next big trend in AI. Focus on identifying pros and cons and the overall narrative."
    expected_output: str = "A comprehensive 3 paragraphs long report on the latest AI trends."
    agent: Optional[Any] = None  # AgentModel reference
    async_execution: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Context references
    context_from_async_tasks_ids: Optional[List[str]] = None
    context_from_sync_tasks_ids: Optional[List[str]] = None

    def get_crewai_task(self, context_from_async_tasks=None, context_from_sync_tasks=None) -> Task:
        """
        Convert this model to CrewAI Task instance

        Args:
            context_from_async_tasks: Optional list of async task instances for context
            context_from_sync_tasks: Optional list of sync task instances for context

        Returns:
            Task: CrewAI Task instance
        """
        if not self.agent:
            raise ValueError(f"Task '{self.description[:50]}...' has no agent assigned")

        # Build context list
        context = []
        if context_from_async_tasks:
            context.extend(context_from_async_tasks)
        if context_from_sync_tasks:
            context.extend(context_from_sync_tasks)

        # Get CrewAI agent instance
        crewai_agent = self.agent.get_crewai_agent()

        # Create and return CrewAI Task
        if context:
            return Task(
                description=self.description,
                expected_output=self.expected_output,
                async_execution=self.async_execution,
                agent=crewai_agent,
                context=context
            )
        else:
            return Task(
                description=self.description,
                expected_output=self.expected_output,
                async_execution=self.async_execution,
                agent=crewai_agent
            )

    def validate(self) -> Dict[str, Any]:
        """
        Validate task configuration

        Returns:
            Dict with 'errors', 'warnings', and 'is_valid' keys
        """
        errors = []
        warnings = []

        # Validate description
        if not self.description or not self.description.strip():
            errors.append(f"Task '{self.id}' has no description")

        # Validate expected output
        if not self.expected_output or not self.expected_output.strip():
            errors.append(f"Task '{self.id}' has no expected output defined")

        # Validate agent assignment
        if not self.agent:
            errors.append(f"Task '{self.description[:50]}...' has no agent assigned")
        else:
            # Validate assigned agent
            agent_validation = self.agent.validate()
            if not agent_validation.get('is_valid', False):
                errors.append(f"Task '{self.description[:50]}...' has invalid agent: {agent_validation.get('errors', [])}")

        # Validate context task IDs
        if self.context_from_async_tasks_ids and not isinstance(self.context_from_async_tasks_ids, list):
            errors.append(f"Task '{self.id}' has invalid context_from_async_tasks_ids (must be list)")

        if self.context_from_sync_tasks_ids and not isinstance(self.context_from_sync_tasks_ids, list):
            errors.append(f"Task '{self.id}' has invalid context_from_sync_tasks_ids (must be list)")

        # Warn if async execution with no context
        if self.async_execution and not self.context_from_async_tasks_ids and not self.context_from_sync_tasks_ids:
            warnings.append(f"Task '{self.description[:50]}...' is async but has no context tasks defined")

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
            'description': self.description,
            'expected_output': self.expected_output,
            'agent_id': self.agent.id if self.agent else None,
            'async_execution': self.async_execution,
            'context_from_async_tasks_ids': self.context_from_async_tasks_ids,
            'context_from_sync_tasks_ids': self.context_from_sync_tasks_ids,
            'created_at': self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], agents_registry=None) -> 'TaskModel':
        """
        Create TaskModel from dictionary

        Args:
            data: Dictionary with task data
            agents_registry: Optional dict/list of agent_id -> AgentModel

        Returns:
            TaskModel instance
        """
        # Resolve agent
        agent = None
        if agents_registry and data.get('agent_id'):
            if isinstance(agents_registry, dict):
                agent = agents_registry.get(data['agent_id'])
            else:  # list
                agent = next((a for a in agents_registry if a.id == data['agent_id']), None)

        return cls(
            id=data.get('id'),
            description=data.get('description', ''),
            expected_output=data.get('expected_output', ''),
            agent=agent,
            async_execution=data.get('async_execution', False),
            context_from_async_tasks_ids=data.get('context_from_async_tasks_ids'),
            context_from_sync_tasks_ids=data.get('context_from_sync_tasks_ids'),
            created_at=data.get('created_at', datetime.now().isoformat()),
        )
