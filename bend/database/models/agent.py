"""
Agent ORM Model
SQLAlchemy model for agents table
"""
from sqlalchemy import Column, String, Text, Float, Boolean, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship
from bend.database.connection import Base
import uuid


def generate_agent_id():
    """Generate unique agent ID"""
    return f"A_{uuid.uuid4().hex[:8]}"


# Association table for Agent-Tool many-to-many relationship
agent_tools = Table(
    "agent_tools",
    Base.metadata,
    Column("agent_id", String(11), ForeignKey("agents.id"), primary_key=True),
    Column("tool_id", String(12), ForeignKey("tools.tool_id"), primary_key=True),
)

# Association table for Agent-KnowledgeSource many-to-many relationship
agent_knowledge_sources = Table(
    "agent_knowledge_sources",
    Base.metadata,
    Column("agent_id", String(11), ForeignKey("agents.id"), primary_key=True),
    Column("knowledge_source_id", String(11), ForeignKey("knowledge_sources.id"), primary_key=True),
)


class Agent(Base):
    """Agent ORM Model"""

    __tablename__ = "agents"

    # Primary Key
    id = Column(String(11), primary_key=True, default=generate_agent_id)

    # Fields
    role = Column(String(255), nullable=False)
    backstory = Column(Text, nullable=False)
    goal = Column(Text, nullable=False)
    llm_provider_model = Column(String(255), nullable=False)
    temperature = Column(Float, default=0.7)
    max_iter = Column(Integer, default=25)
    allow_delegation = Column(Boolean, default=False)
    verbose = Column(Boolean, default=True)
    cache = Column(Boolean, default=True)

    # Relationships
    tools = relationship(
        "Tool",
        secondary=agent_tools,
        backref="agents",
    )
    knowledge_sources = relationship(
        "KnowledgeSource",
        secondary=agent_knowledge_sources,
        backref="agents",
    )
    tasks = relationship("Task", back_populates="agent")

    def __repr__(self):
        return f"<Agent(id='{self.id}', role='{self.role}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "role": self.role,
            "backstory": self.backstory,
            "goal": self.goal,
            "llm_provider_model": self.llm_provider_model,
            "temperature": self.temperature,
            "max_iter": self.max_iter,
            "allow_delegation": self.allow_delegation,
            "verbose": self.verbose,
            "cache": self.cache,
            "tool_ids": [tool.tool_id for tool in self.tools],
            "knowledge_source_ids": [ks.id for ks in self.knowledge_sources],
        }
