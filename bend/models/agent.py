"""
Agent Domain Model
Pure business logic without UI dependencies
"""
from crewai import Agent
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import sys
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def generate_id() -> str:
    """Generate unique ID for agent"""
    import uuid
    return f"A_{uuid.uuid4().hex[:8]}"


@dataclass
class AgentModel:
    """
    Agent Domain Model
    Represents a CrewAI agent configuration without UI dependencies
    """

    # Core fields
    id: str = field(default_factory=generate_id)
    role: str = "Senior Researcher"
    backstory: str = "Driven by curiosity, you're at the forefront of innovation, eager to explore and share knowledge that could change the world."
    goal: str = "Uncover groundbreaking technologies in AI"
    temperature: float = 0.1
    allow_delegation: bool = False
    verbose: bool = True
    cache: bool = True
    llm_provider_model: str = ""  # Will be set by application
    max_iter: int = 25
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Relations
    tools: List[Any] = field(default_factory=list)  # List of ToolModel
    knowledge_source_ids: List[str] = field(default_factory=list)

    def get_crewai_agent(self, knowledge_sources_registry=None) -> Agent:
        """
        Convert this model to CrewAI Agent instance

        Args:
            knowledge_sources_registry: Optional dict/list to fetch knowledge sources

        Returns:
            Agent: CrewAI Agent instance
        """
        # Import here to avoid circular dependencies
        from llms import create_llm

        # Create LLM with temperature
        llm = create_llm(self.llm_provider_model, temperature=self.temperature)

        # Convert tools to CrewAI tools
        crewai_tools = [tool.create_tool() for tool in self.tools]

        # Load knowledge sources if registry provided
        knowledge_sources = []
        if knowledge_sources_registry and self.knowledge_source_ids:
            for ks_id in self.knowledge_source_ids:
                try:
                    # Support both dict and list registries
                    if isinstance(knowledge_sources_registry, dict):
                        ks = knowledge_sources_registry.get(ks_id)
                    else:  # list
                        ks = next((k for k in knowledge_sources_registry if k.id == ks_id), None)

                    if ks:
                        knowledge_sources.append(ks.get_crewai_knowledge_source())
                except Exception as e:
                    print(f"Error loading knowledge source {ks_id}: {str(e)}")

        # Create and return CrewAI Agent
        return Agent(
            role=self.role,
            backstory=self.backstory,
            goal=self.goal,
            allow_delegation=self.allow_delegation,
            verbose=self.verbose,
            max_iter=self.max_iter,
            cache=self.cache,
            tools=crewai_tools,
            llm=llm,
            knowledge_sources=knowledge_sources if knowledge_sources else None
        )

    def validate(self, available_llm_models: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate agent configuration

        Args:
            available_llm_models: Optional list of valid LLM model identifiers

        Returns:
            Dict with 'errors', 'warnings', and 'is_valid' keys
        """
        errors = []
        warnings = []

        # Validate role
        if not self.role or not self.role.strip():
            errors.append(f"Agent '{self.id}' has no role defined")

        # Validate goal
        if not self.goal or not self.goal.strip():
            errors.append(f"Agent '{self.id}' has no goal defined")

        # Validate backstory
        if not self.backstory or not self.backstory.strip():
            warnings.append(f"Agent '{self.id}' has no backstory defined")

        # Validate LLM provider model
        if not self.llm_provider_model:
            errors.append(f"Agent '{self.id}' has no LLM provider/model selected")
        elif available_llm_models and self.llm_provider_model not in available_llm_models:
            errors.append(f"Agent '{self.id}' has invalid LLM provider/model: {self.llm_provider_model}")

        # Validate temperature
        if not (0.0 <= self.temperature <= 1.0):
            errors.append(f"Agent '{self.id}' has invalid temperature: {self.temperature} (must be 0.0-1.0)")

        # Validate max_iter
        if self.max_iter < 1 or self.max_iter > 100:
            warnings.append(f"Agent '{self.id}' has unusual max_iter: {self.max_iter} (recommended: 1-100)")

        # Validate tools
        for tool in self.tools:
            tool_validation = tool.validate()
            if not tool_validation.get('is_valid', False):
                errors.append(f"Agent '{self.id}' has invalid tool '{tool.name}': {tool_validation.get('errors', [])}")

        return {
            'errors': errors,
            'warnings': warnings,
            'is_valid': len(errors) == 0
        }

    def is_valid(self, available_llm_models: Optional[List[str]] = None) -> bool:
        """Simple validation check (backward compatibility)"""
        return self.validate(available_llm_models)['is_valid']

    def validate_llm_provider_model(self, available_models: List[str]):
        """
        Ensure agent has a valid LLM provider/model selection

        Args:
            available_models: List of valid LLM model identifiers
        """
        if self.llm_provider_model not in available_models:
            if available_models:
                self.llm_provider_model = available_models[0]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'role': self.role,
            'backstory': self.backstory,
            'goal': self.goal,
            'temperature': self.temperature,
            'allow_delegation': self.allow_delegation,
            'verbose': self.verbose,
            'cache': self.cache,
            'llm_provider_model': self.llm_provider_model,
            'max_iter': self.max_iter,
            'created_at': self.created_at,
            'tool_ids': [tool.tool_id for tool in self.tools],
            'knowledge_source_ids': self.knowledge_source_ids,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], tools_registry=None) -> 'AgentModel':
        """
        Create AgentModel from dictionary

        Args:
            data: Dictionary with agent data
            tools_registry: Optional dict/list of tool_id -> ToolModel

        Returns:
            AgentModel instance
        """
        # Resolve tools
        tools = []
        if tools_registry and 'tool_ids' in data:
            if isinstance(tools_registry, dict):
                tools = [tools_registry[tid] for tid in data['tool_ids'] if tid in tools_registry]
            else:  # list
                tools = [tool for tool in tools_registry if tool.tool_id in data.get('tool_ids', [])]

        return cls(
            id=data.get('id'),
            role=data.get('role', 'Senior Researcher'),
            backstory=data.get('backstory', ''),
            goal=data.get('goal', ''),
            temperature=data.get('temperature', 0.1),
            allow_delegation=data.get('allow_delegation', False),
            verbose=data.get('verbose', True),
            cache=data.get('cache', True),
            llm_provider_model=data.get('llm_provider_model', ''),
            max_iter=data.get('max_iter', 25),
            created_at=data.get('created_at', datetime.now().isoformat()),
            tools=tools,
            knowledge_source_ids=data.get('knowledge_source_ids', []),
        )
