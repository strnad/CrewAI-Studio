"""
CrewRun ORM Model
SQLAlchemy model for crew_runs table (execution history)
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from bend.database.connection import Base
from datetime import datetime
import uuid


def generate_crew_run_id():
    """Generate unique crew run ID"""
    return f"CR_{uuid.uuid4().hex[:8]}"


class CrewRun(Base):
    """CrewRun ORM Model - Stores crew execution history"""

    __tablename__ = "crew_runs"

    # Primary Key
    id = Column(String(12), primary_key=True, default=generate_crew_run_id)

    # Foreign Key with CASCADE DELETE
    crew_id = Column(String(11), ForeignKey("crews.id", ondelete="CASCADE"), nullable=False)

    # Execution Status: pending, running, completed, failed
    status = Column(String(20), nullable=False, default="pending")

    # Inputs and Outputs
    inputs = Column(JSON, default={})  # Input parameters for execution
    result = Column(Text, nullable=True)  # Execution result (raw text or JSON string)
    error = Column(Text, nullable=True)  # Error message if failed

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    crew = relationship("Crew", backref="runs")

    def __repr__(self):
        return f"<CrewRun(id='{self.id}', crew_id='{self.crew_id}', status='{self.status}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "crew_id": self.crew_id,
            "status": self.status,
            "inputs": self.inputs,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
