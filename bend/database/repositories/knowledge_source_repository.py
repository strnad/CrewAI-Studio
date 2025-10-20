"""
Knowledge Source Repository
Database operations for KnowledgeSource model
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from bend.database.models.knowledge_source import KnowledgeSource
from bend.database.repositories.base import BaseRepository


class KnowledgeSourceRepository(BaseRepository[KnowledgeSource]):
    """Repository for KnowledgeSource operations"""

    def __init__(self, db: Session):
        super().__init__(KnowledgeSource, db)

    def get_by_name(self, name: str) -> Optional[KnowledgeSource]:
        """
        Get knowledge source by name

        Args:
            name: Knowledge source name

        Returns:
            KnowledgeSource instance or None
        """
        return self.db.query(KnowledgeSource).filter(
            KnowledgeSource.name == name
        ).first()

    def get_by_source_type(self, source_type: str) -> List[KnowledgeSource]:
        """
        Get knowledge sources by type

        Args:
            source_type: Source type (string, text_file, pdf, etc.)

        Returns:
            List of knowledge sources
        """
        return self.db.query(KnowledgeSource).filter(
            KnowledgeSource.source_type == source_type
        ).all()

    def search_by_name(self, query: str) -> List[KnowledgeSource]:
        """
        Search knowledge sources by name (case-insensitive)

        Args:
            query: Search query

        Returns:
            List of matching knowledge sources
        """
        return self.db.query(KnowledgeSource).filter(
            KnowledgeSource.name.ilike(f"%{query}%")
        ).all()

    def get_knowledge_sources_by_ids(self, ks_ids: List[str]) -> List[KnowledgeSource]:
        """
        Get multiple knowledge sources by IDs

        Args:
            ks_ids: List of knowledge source IDs

        Returns:
            List of knowledge sources
        """
        return self.db.query(KnowledgeSource).filter(
            KnowledgeSource.id.in_(ks_ids)
        ).all()
