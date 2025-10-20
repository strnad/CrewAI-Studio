"""
Crew ORM Model
SQLAlchemy model for crews table
"""
from sqlalchemy import Column, String, Boolean, Integer, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from bend.database.connection import Base
from datetime import datetime
import uuid


def generate_crew_id():
    """Generate unique crew ID"""
    return f"C_{uuid.uuid4().hex[:8]}"


# Association table for Crew-Agent many-to-many relationship
crew_agents = Table(
    "crew_agents",
    Base.metadata,
    Column("crew_id", String(11), ForeignKey("crews.id"), primary_key=True),
    Column("agent_id", String(11), ForeignKey("agents.id"), primary_key=True),
)

# Association table for Crew-Task many-to-many relationship
crew_tasks = Table(
    "crew_tasks",
    Base.metadata,
    Column("crew_id", String(11), ForeignKey("crews.id"), primary_key=True),
    Column("task_id", String(11), ForeignKey("tasks.id"), primary_key=True),
)

# Association table for Crew-KnowledgeSource many-to-many relationship
crew_knowledge_sources = Table(
    "crew_knowledge_sources",
    Base.metadata,
    Column("crew_id", String(11), ForeignKey("crews.id"), primary_key=True),
    Column("knowledge_source_id", String(11), ForeignKey("knowledge_sources.id"), primary_key=True),
)


class Crew(Base):
    """Crew ORM Model"""

    __tablename__ = "crews"

    # Primary Key
    id = Column(String(11), primary_key=True, default=generate_crew_id)

    # Fields
    name = Column(String(255), nullable=False)
    process = Column(String(50), default="sequential")  # sequential or hierarchical
    verbose = Column(Boolean, default=True)
    cache = Column(Boolean, default=True)
    max_rpm = Column(Integer, default=1000)
    memory = Column(Boolean, default=False)
    planning = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agents = relationship(
        "Agent",
        secondary=crew_agents,
        backref="crews",
    )
    tasks = relationship(
        "Task",
        secondary=crew_tasks,
        backref="crews",
    )
    knowledge_sources = relationship(
        "KnowledgeSource",
        secondary=crew_knowledge_sources,
        backref="crews",
    )

    def __repr__(self):
        return f"<Crew(id='{self.id}', name='{self.name}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "process": self.process,
            "verbose": self.verbose,
            "cache": self.cache,
            "max_rpm": self.max_rpm,
            "memory": self.memory,
            "planning": self.planning,
            "agent_ids": [agent.id for agent in self.agents],
            "task_ids": [task.id for task in self.tasks],
            "knowledge_source_ids": [ks.id for ks in self.knowledge_sources],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
