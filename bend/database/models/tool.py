"""
Tool ORM Model
SQLAlchemy model for tools table
"""
from sqlalchemy import Column, String, Text, JSON
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

    # Fields
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    parameters = Column(JSON, default=dict)  # Tool parameters as JSON
    parameters_metadata = Column(JSON, default=dict)  # Parameter metadata as JSON

    # Relationships will be added when Agent model is created
    # agents = relationship("Agent", secondary="agent_tools", back_populates="tools")

    def __repr__(self):
        return f"<Tool(tool_id='{self.tool_id}', name='{self.name}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters or {},
            "parameters_metadata": self.parameters_metadata or {},
        }
