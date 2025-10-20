"""
Knowledge Source Service
Business logic for KnowledgeSource operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from bend.database.repositories.knowledge_source_repository import KnowledgeSourceRepository
from bend.database.models.knowledge_source import KnowledgeSource


class KnowledgeSourceService:
    """Service for KnowledgeSource business logic"""

    VALID_SOURCE_TYPES = ["string", "text_file", "pdf", "csv", "excel", "json", "docling"]

    def __init__(self, db: Session):
        """
        Initialize service

        Args:
            db: Database session
        """
        self.db = db
        self.repo = KnowledgeSourceRepository(db)

    def create_knowledge_source(
        self,
        name: str,
        source_type: str,
        source_path: str = "",
        content: str = "",
        metadata: Dict[str, Any] = None,
        chunk_size: int = 4000,
        chunk_overlap: int = 200
    ) -> KnowledgeSource:
        """
        Create new knowledge source

        Args:
            name: Knowledge source name
            source_type: Source type
            source_path: Path to source file
            content: Content for string type
            metadata: Metadata
            chunk_size: Chunk size
            chunk_overlap: Chunk overlap

        Returns:
            Created knowledge source

        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not name or not name.strip():
            raise ValueError("Knowledge source name is required")

        if source_type not in self.VALID_SOURCE_TYPES:
            raise ValueError(
                f"Invalid source_type: {source_type}. "
                f"Must be one of: {', '.join(self.VALID_SOURCE_TYPES)}"
            )

        return self.repo.create(
            name=name,
            source_type=source_type,
            source_path=source_path,
            content=content,
            meta_data=metadata or {},
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def get_knowledge_source(self, ks_id: str) -> Optional[KnowledgeSource]:
        """
        Get knowledge source by ID

        Args:
            ks_id: Knowledge source ID

        Returns:
            Knowledge source or None
        """
        return self.repo.get_by_id(ks_id)

    def list_knowledge_sources(self, skip: int = 0, limit: int = 100) -> List[KnowledgeSource]:
        """
        List all knowledge sources

        Args:
            skip: Number to skip
            limit: Maximum number to return

        Returns:
            List of knowledge sources
        """
        return self.repo.get_all(skip=skip, limit=limit)

    def update_knowledge_source(
        self,
        ks_id: str,
        **kwargs
    ) -> Optional[KnowledgeSource]:
        """
        Update knowledge source

        Args:
            ks_id: Knowledge source ID
            **kwargs: Fields to update

        Returns:
            Updated knowledge source or None

        Raises:
            ValueError: If knowledge source not found or validation fails
        """
        ks = self.repo.get_by_id(ks_id)
        if not ks:
            raise ValueError(f"Knowledge source with id '{ks_id}' not found")

        # Validate source_type if being updated
        if 'source_type' in kwargs:
            if kwargs['source_type'] not in self.VALID_SOURCE_TYPES:
                raise ValueError(
                    f"Invalid source_type: {kwargs['source_type']}. "
                    f"Must be one of: {', '.join(self.VALID_SOURCE_TYPES)}"
                )

        return self.repo.update(ks_id, **kwargs)

    def delete_knowledge_source(self, ks_id: str) -> bool:
        """
        Delete knowledge source

        Args:
            ks_id: Knowledge source ID

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If knowledge source is in use
        """
        ks = self.repo.get_by_id(ks_id)
        if not ks:
            return False

        # Check if used by agents
        if ks.agents:
            agent_roles = [agent.role for agent in ks.agents]
            raise ValueError(
                f"Knowledge source is used by agents: {', '.join(agent_roles)}. "
                "Remove knowledge source from agents before deleting."
            )

        # Check if used by crews
        if ks.crews:
            crew_names = [crew.name for crew in ks.crews]
            raise ValueError(
                f"Knowledge source is used by crews: {', '.join(crew_names)}. "
                "Remove knowledge source from crews before deleting."
            )

        return self.repo.delete(ks_id)

    def validate_knowledge_source(self, ks_id: str) -> Dict[str, Any]:
        """
        Validate knowledge source configuration

        Args:
            ks_id: Knowledge source ID

        Returns:
            Validation result

        Raises:
            ValueError: If knowledge source not found
        """
        ks = self.repo.get_by_id(ks_id)
        if not ks:
            raise ValueError(f"Knowledge source with id '{ks_id}' not found")

        errors = []
        warnings = []

        # Validate name
        if not ks.name or not ks.name.strip():
            errors.append("Knowledge source name is required")

        # Validate source_type
        if ks.source_type not in self.VALID_SOURCE_TYPES:
            errors.append(f"Invalid source_type: {ks.source_type}")

        # Validate content/path based on type
        if ks.source_type == "string":
            if not ks.content or not ks.content.strip():
                errors.append(
                    f"Knowledge source '{ks.name}' (type: string) has no content"
                )
        else:
            if not ks.source_path or not ks.source_path.strip():
                warnings.append(
                    f"Knowledge source '{ks.name}' (type: {ks.source_type}) has no source_path"
                )

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def search_knowledge_sources(self, query: str) -> List[KnowledgeSource]:
        """
        Search knowledge sources by name

        Args:
            query: Search query

        Returns:
            List of matching knowledge sources
        """
        return self.repo.search_by_name(query)

    def get_by_type(self, source_type: str) -> List[KnowledgeSource]:
        """
        Get knowledge sources by type

        Args:
            source_type: Source type

        Returns:
            List of knowledge sources
        """
        return self.repo.get_by_source_type(source_type)
