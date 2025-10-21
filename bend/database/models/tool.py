"""
Tool ORM Model
SQLAlchemy model for tools table
"""
from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from bend.database.connection import Base
from datetime import datetime
import uuid


def generate_tool_id():
    """Generate unique tool ID"""
    return uuid.uuid4().hex[:12]


class Tool(Base):
    """Tool ORM Model"""

    __tablename__ = "tools"

    # Primary Key
    tool_id = Column(String(12), primary_key=True, default=generate_tool_id)

    # Multi-tenant fields
    workspace_id = Column(String(12), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    created_by = Column(String(12), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Fields
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    parameters = Column(JSON, default=dict)  # Tool parameters as JSON
    parameters_metadata = Column(JSON, default=dict)  # Parameter metadata as JSON

    # Relationships
    # Multi-tenant relationships
    workspace = relationship("Workspace", back_populates="tools")
    creator = relationship("User", back_populates="created_tools", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Tool(tool_id='{self.tool_id}', name='{self.name}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "tool_id": self.tool_id,
            "workspace_id": self.workspace_id,
            "created_by": self.created_by,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters or {},
            "parameters_metadata": self.parameters_metadata or {},
        }
