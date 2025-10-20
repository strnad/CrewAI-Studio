"""
Agent Service
Business logic for Agent operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from bend.database.repositories.agent_repository import AgentRepository
from bend.database.repositories.tool_repository import ToolRepository
from bend.database.repositories.knowledge_source_repository import KnowledgeSourceRepository
from bend.database.models.agent import Agent


class AgentService:
    """Service for Agent business logic"""

    def __init__(self, db: Session):
        """Initialize service"""
        self.db = db
        self.repo = AgentRepository(db)
        self.tool_repo = ToolRepository(db)
        self.ks_repo = KnowledgeSourceRepository(db)

    def create_agent(
        self,
        role: str,
        backstory: str,
        goal: str,
        llm_provider_model: str,
        tool_ids: List[str] = None,
        knowledge_source_ids: List[str] = None,
        temperature: float = 0.7,
        max_iter: int = 25,
        allow_delegation: bool = False,
        verbose: bool = True,
        cache: bool = True
    ) -> Agent:
        """Create new agent"""
        # Validation
        if not role or not role.strip():
            raise ValueError("Agent role is required")
        if not backstory or not backstory.strip():
            raise ValueError("Agent backstory is required")
        if not goal or not goal.strip():
            raise ValueError("Agent goal is required")
        if not llm_provider_model or not llm_provider_model.strip():
            raise ValueError("Agent llm_provider_model is required")

        # Validate tool IDs
        tool_ids = tool_ids or []
        tools = []
        for tool_id in tool_ids:
            tool = self.tool_repo.get_by_id(tool_id)
            if not tool:
                raise ValueError(f"Tool with id '{tool_id}' not found")
            tools.append(tool)

        # Validate knowledge source IDs
        knowledge_source_ids = knowledge_source_ids or []
        knowledge_sources = []
        for ks_id in knowledge_source_ids:
            ks = self.ks_repo.get_by_id(ks_id)
            if not ks:
                raise ValueError(f"Knowledge source with id '{ks_id}' not found")
            knowledge_sources.append(ks)

        # Create agent
        agent = self.repo.create(
            role=role,
            backstory=backstory,
            goal=goal,
            llm_provider_model=llm_provider_model,
            temperature=temperature,
            max_iter=max_iter,
            allow_delegation=allow_delegation,
            verbose=verbose,
            cache=cache
        )

        # Add relationships
        for tool in tools:
            agent.tools.append(tool)
        for ks in knowledge_sources:
            agent.knowledge_sources.append(ks)

        self.db.commit()
        self.db.refresh(agent)

        return agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID with relations"""
        return self.repo.get_by_id_with_relations(agent_id)

    def list_agents(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        """List all agents"""
        return self.repo.get_all(skip=skip, limit=limit)

    def update_agent(self, agent_id: str, **kwargs) -> Optional[Agent]:
        """Update agent"""
        agent = self.repo.get_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent with id '{agent_id}' not found")

        # Handle tool_ids update
        if 'tool_ids' in kwargs:
            tool_ids = kwargs.pop('tool_ids')
            tools = self.tool_repo.get_tools_by_ids(tool_ids)
            if len(tools) != len(tool_ids):
                found_ids = [t.tool_id for t in tools]
                missing = set(tool_ids) - set(found_ids)
                raise ValueError(f"Tools not found: {', '.join(missing)}")
            agent.tools = tools

        # Handle knowledge_source_ids update
        if 'knowledge_source_ids' in kwargs:
            ks_ids = kwargs.pop('knowledge_source_ids')
            knowledge_sources = self.ks_repo.get_knowledge_sources_by_ids(ks_ids)
            if len(knowledge_sources) != len(ks_ids):
                found_ids = [ks.id for ks in knowledge_sources]
                missing = set(ks_ids) - set(found_ids)
                raise ValueError(f"Knowledge sources not found: {', '.join(missing)}")
            agent.knowledge_sources = knowledge_sources

        # Update other fields
        if kwargs:
            self.repo.update(agent_id, **kwargs)

        self.db.commit()
        self.db.refresh(agent)
        return agent

    def delete_agent(self, agent_id: str) -> bool:
        """Delete agent"""
        agent = self.repo.get_by_id(agent_id)
        if not agent:
            return False

        # Check if used by crews
        if agent.crews:
            crew_names = [crew.name for crew in agent.crews]
            raise ValueError(
                f"Agent is used by crews: {', '.join(crew_names)}. "
                "Remove agent from crews before deleting."
            )

        return self.repo.delete(agent_id)

    def validate_agent(self, agent_id: str) -> Dict[str, Any]:
        """Validate agent configuration"""
        agent = self.repo.get_by_id_with_relations(agent_id)
        if not agent:
            raise ValueError(f"Agent with id '{agent_id}' not found")

        errors = []
        warnings = []

        # Validate required fields
        if not agent.role or not agent.role.strip():
            errors.append("Agent role is required")
        if not agent.backstory or not agent.backstory.strip():
            errors.append("Agent backstory is required")
        if not agent.goal or not agent.goal.strip():
            errors.append("Agent goal is required")
        if not agent.llm_provider_model or not agent.llm_provider_model.strip():
            errors.append("Agent llm_provider_model is required")

        # Check tools
        if not agent.tools:
            warnings.append("Agent has no tools assigned")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
