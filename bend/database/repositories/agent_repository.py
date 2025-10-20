"""
Agent Repository
Database operations for Agent model
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from bend.database.models.agent import Agent
from bend.database.repositories.base import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    """Repository for Agent operations"""

    def __init__(self, db: Session):
        super().__init__(Agent, db)

    def get_by_id_with_relations(self, id: str) -> Optional[Agent]:
        """
        Get agent by ID with related tools and knowledge sources

        Args:
            id: Agent ID

        Returns:
            Agent instance with relations loaded or None
        """
        return self.db.query(Agent).options(
            joinedload(Agent.tools),
            joinedload(Agent.knowledge_sources)
        ).filter(Agent.id == id).first()

    def get_by_role(self, role: str) -> Optional[Agent]:
        """
        Get agent by role

        Args:
            role: Agent role

        Returns:
            Agent instance or None
        """
        return self.db.query(Agent).filter(Agent.role == role).first()

    def search_by_role(self, query: str) -> List[Agent]:
        """
        Search agents by role (case-insensitive)

        Args:
            query: Search query

        Returns:
            List of matching agents
        """
        return self.db.query(Agent).filter(
            Agent.role.ilike(f"%{query}%")
        ).all()

    def get_agents_by_ids(self, agent_ids: List[str]) -> List[Agent]:
        """
        Get multiple agents by IDs

        Args:
            agent_ids: List of agent IDs

        Returns:
            List of agents
        """
        return self.db.query(Agent).filter(Agent.id.in_(agent_ids)).all()

    def add_tool(self, agent_id: str, tool_id: str) -> Optional[Agent]:
        """
        Add tool to agent

        Args:
            agent_id: Agent ID
            tool_id: Tool ID

        Returns:
            Updated agent or None
        """
        from bend.database.models.tool import Tool

        agent = self.get_by_id(agent_id)
        if not agent:
            return None

        tool = self.db.query(Tool).filter(Tool.tool_id == tool_id).first()
        if not tool:
            return None

        if tool not in agent.tools:
            agent.tools.append(tool)
            self.db.commit()
            self.db.refresh(agent)

        return agent

    def remove_tool(self, agent_id: str, tool_id: str) -> Optional[Agent]:
        """
        Remove tool from agent

        Args:
            agent_id: Agent ID
            tool_id: Tool ID

        Returns:
            Updated agent or None
        """
        from bend.database.models.tool import Tool

        agent = self.get_by_id(agent_id)
        if not agent:
            return None

        tool = self.db.query(Tool).filter(Tool.tool_id == tool_id).first()
        if tool and tool in agent.tools:
            agent.tools.remove(tool)
            self.db.commit()
            self.db.refresh(agent)

        return agent

    def add_knowledge_source(self, agent_id: str, ks_id: str) -> Optional[Agent]:
        """
        Add knowledge source to agent

        Args:
            agent_id: Agent ID
            ks_id: Knowledge source ID

        Returns:
            Updated agent or None
        """
        from bend.database.models.knowledge_source import KnowledgeSource

        agent = self.get_by_id(agent_id)
        if not agent:
            return None

        ks = self.db.query(KnowledgeSource).filter(KnowledgeSource.id == ks_id).first()
        if not ks:
            return None

        if ks not in agent.knowledge_sources:
            agent.knowledge_sources.append(ks)
            self.db.commit()
            self.db.refresh(agent)

        return agent

    def remove_knowledge_source(self, agent_id: str, ks_id: str) -> Optional[Agent]:
        """
        Remove knowledge source from agent

        Args:
            agent_id: Agent ID
            ks_id: Knowledge source ID

        Returns:
            Updated agent or None
        """
        from bend.database.models.knowledge_source import KnowledgeSource

        agent = self.get_by_id(agent_id)
        if not agent:
            return None

        ks = self.db.query(KnowledgeSource).filter(KnowledgeSource.id == ks_id).first()
        if ks and ks in agent.knowledge_sources:
            agent.knowledge_sources.remove(ks)
            self.db.commit()
            self.db.refresh(agent)

        return agent
