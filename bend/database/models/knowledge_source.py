"""
Knowledge Source ORM Model
SQLAlchemy model for knowledge_sources table
"""
from sqlalchemy import Column, String, Text, Integer, JSON, DateTime
from sqlalchemy.orm import relationship
from bend.database.connection import Base
from datetime import datetime
import uuid


def generate_ks_id():
    """Generate unique knowledge source ID"""
    return f"KS_{uuid.uuid4().hex[:8]}"


class KnowledgeSource(Base):
    """Knowledge Source ORM Model"""

    __tablename__ = "knowledge_sources"

    # Primary Key
    id = Column(String(11), primary_key=True, default=generate_ks_id)

    # Fields
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # string, text_file, pdf, csv, excel, json, docling
    source_path = Column(Text, default="")
    content = Column(Text, default="")
    meta_data = Column(JSON, default=dict)  # Renamed from metadata (reserved by SQLAlchemy)
    chunk_size = Column(Integer, default=4000)
    chunk_overlap = Column(Integer, default=200)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships will be added when Agent and Crew models are created
    # agents = relationship("Agent", secondary="agent_knowledge_sources", back_populates="knowledge_sources")
    # crews = relationship("Crew", secondary="crew_knowledge_sources", back_populates="knowledge_sources")

    def __repr__(self):
        return f"<KnowledgeSource(id='{self.id}', name='{self.name}', type='{self.source_type}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "source_type": self.source_type,
            "source_path": self.source_path,
            "content": self.content,
            "metadata": self.meta_data or {},  # Return as 'metadata' for API compatibility
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
