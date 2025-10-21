"""
Task ORM Model
SQLAlchemy model for tasks table
"""
from sqlalchemy import Column, String, Text, Boolean, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from bend.database.connection import Base
from datetime import datetime
import uuid


def generate_task_id():
    """Generate unique task ID"""
    return f"T_{uuid.uuid4().hex[:8]}"


# Association table for Task self-referencing (async context tasks)
task_async_context = Table(
    "task_async_context",
    Base.metadata,
    Column("task_id", String(11), ForeignKey("tasks.id"), primary_key=True),
    Column("context_task_id", String(11), ForeignKey("tasks.id"), primary_key=True),
)

# Association table for Task self-referencing (sync context tasks)
task_sync_context = Table(
    "task_sync_context",
    Base.metadata,
    Column("task_id", String(11), ForeignKey("tasks.id"), primary_key=True),
    Column("context_task_id", String(11), ForeignKey("tasks.id"), primary_key=True),
)


class Task(Base):
    """Task ORM Model"""

    __tablename__ = "tasks"

    # Primary Key
    id = Column(String(11), primary_key=True, default=generate_task_id)

    # Multi-tenant fields
    workspace_id = Column(String(12), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    created_by = Column(String(12), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Fields
    description = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    async_execution = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign Key
    agent_id = Column(String(11), ForeignKey("agents.id"), nullable=False)

    # Relationships
    # Multi-tenant relationships
    workspace = relationship("Workspace", back_populates="tasks")
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[created_by])

    # Agent relationship
    agent = relationship("Agent", back_populates="tasks")

    # Self-referencing relationships for context tasks
    context_async_tasks = relationship(
        "Task",
        secondary=task_async_context,
        primaryjoin=id == task_async_context.c.task_id,
        secondaryjoin=id == task_async_context.c.context_task_id,
        backref="referenced_by_async",
    )

    context_sync_tasks = relationship(
        "Task",
        secondary=task_sync_context,
        primaryjoin=id == task_sync_context.c.task_id,
        secondaryjoin=id == task_sync_context.c.context_task_id,
        backref="referenced_by_sync",
    )

    def __repr__(self):
        return f"<Task(id='{self.id}', description='{self.description[:50]}...')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "created_by": self.created_by,
            "description": self.description,
            "expected_output": self.expected_output,
            "async_execution": self.async_execution,
            "agent_id": self.agent_id,
            "context_from_async_tasks_ids": [task.id for task in self.context_async_tasks],
            "context_from_sync_tasks_ids": [task.id for task in self.context_sync_tasks],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
