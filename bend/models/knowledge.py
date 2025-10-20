"""
Knowledge Source Domain Model
Pure business logic without UI dependencies
"""
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import sys

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def generate_id() -> str:
    """Generate unique ID for knowledge source"""
    import uuid
    return f"KS_{uuid.uuid4().hex[:8]}"


@dataclass
class KnowledgeSourceModel:
    """
    Knowledge Source Domain Model
    Represents a CrewAI knowledge source configuration without UI dependencies
    """

    # Core fields
    id: str = field(default_factory=generate_id)
    name: str = "Knowledge Source 1"
    source_type: str = "string"  # string, text_file, pdf, csv, excel, json, docling
    source_path: str = ""  # For file-based sources
    content: str = ""  # For string-based sources
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_size: int = 4000
    chunk_overlap: int = 200
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def find_file(self, file_path: str, knowledge_base_path: str = "knowledge") -> Optional[str]:
        """
        Tries to find the file in the knowledge base directory

        Args:
            file_path: Relative file path
            knowledge_base_path: Base directory for knowledge files

        Returns:
            file_path if found, None otherwise
        """
        if not file_path:
            return None

        # Check if file exists in knowledge base directory
        full_path = Path(knowledge_base_path) / file_path
        if full_path.exists():
            return file_path
        else:
            return None

    def get_crewai_knowledge_source(self, knowledge_base_path: str = "knowledge"):
        """
        Convert this model to CrewAI Knowledge Source instance

        Args:
            knowledge_base_path: Base directory for knowledge files

        Returns:
            CrewAI Knowledge Source instance

        Raises:
            FileNotFoundError: If file-based source file not found
            ValueError: If unsupported source type
        """
        # Import knowledge source classes based on type
        if self.source_type == "string":
            from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
            return StringKnowledgeSource(
                content=self.content,
                metadata=self.metadata,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
        elif self.source_type == "docling":
            from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
            return CrewDoclingSource(
                file_paths=[self.source_path],
                metadata=self.metadata,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
        else:
            # For file-based sources, find the actual file path
            actual_path = self.find_file(self.source_path, knowledge_base_path)
            if not actual_path:
                raise FileNotFoundError(f"File not found: {self.source_path}")

            # Build full path for file-based sources
            full_path = str(Path(knowledge_base_path) / actual_path)

            # Import the appropriate class based on source type
            if self.source_type == "text_file":
                from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
                return TextFileKnowledgeSource(
                    file_paths=[full_path],
                    metadata=self.metadata,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            elif self.source_type == "pdf":
                from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
                return PDFKnowledgeSource(
                    file_paths=[full_path],
                    metadata=self.metadata,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            elif self.source_type == "csv":
                from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
                return CSVKnowledgeSource(
                    file_paths=[full_path],
                    metadata=self.metadata,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            elif self.source_type == "excel":
                from crewai.knowledge.source.excel_knowledge_source import ExcelKnowledgeSource
                return ExcelKnowledgeSource(
                    file_paths=[full_path],
                    metadata=self.metadata,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            elif self.source_type == "json":
                from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
                return JSONKnowledgeSource(
                    file_paths=[full_path],
                    metadata=self.metadata,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            else:
                raise ValueError(f"Unsupported knowledge source type: {self.source_type}")

    def validate(self, knowledge_base_path: str = "knowledge") -> Dict[str, Any]:
        """
        Validate knowledge source configuration

        Args:
            knowledge_base_path: Base directory for knowledge files

        Returns:
            Dict with 'errors', 'warnings', and 'is_valid' keys
        """
        errors = []
        warnings = []

        # Validate name
        if not self.name or not self.name.strip():
            errors.append(f"Knowledge source '{self.id}' has no name")

        # Validate source type
        valid_types = ["string", "text_file", "pdf", "csv", "excel", "json", "docling"]
        if self.source_type not in valid_types:
            errors.append(f"Knowledge source '{self.name}' has invalid type: {self.source_type}")

        # Validate content/path based on type
        if self.source_type == "string":
            if not self.content:
                errors.append(f"Knowledge source '{self.name}' (type: string) has no content")
        elif self.source_type == "docling":
            if not self.source_path:
                errors.append(f"Knowledge source '{self.name}' (type: docling) has no source path")
        else:
            # File-based sources
            if not self.source_path:
                errors.append(f"Knowledge source '{self.name}' (type: {self.source_type}) has no source path")
            else:
                # Check if file exists
                actual_path = self.find_file(self.source_path, knowledge_base_path)
                if not actual_path:
                    errors.append(f"Knowledge source '{self.name}': File not found at '{self.source_path}'")

        # Validate chunk settings
        if self.chunk_size < 100 or self.chunk_size > 8000:
            warnings.append(f"Knowledge source '{self.name}' has unusual chunk_size: {self.chunk_size} (recommended: 100-8000)")

        if self.chunk_overlap < 0 or self.chunk_overlap > 1000:
            warnings.append(f"Knowledge source '{self.name}' has unusual chunk_overlap: {self.chunk_overlap} (recommended: 0-1000)")

        if self.chunk_overlap >= self.chunk_size:
            errors.append(f"Knowledge source '{self.name}': chunk_overlap ({self.chunk_overlap}) must be less than chunk_size ({self.chunk_size})")

        return {
            'errors': errors,
            'warnings': warnings,
            'is_valid': len(errors) == 0
        }

    def is_valid(self, knowledge_base_path: str = "knowledge") -> bool:
        """Simple validation check (backward compatibility)"""
        return self.validate(knowledge_base_path)['is_valid']

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'source_type': self.source_type,
            'source_path': self.source_path,
            'content': self.content,
            'metadata': self.metadata,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'created_at': self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeSourceModel':
        """
        Create KnowledgeSourceModel from dictionary

        Args:
            data: Dictionary with knowledge source data

        Returns:
            KnowledgeSourceModel instance
        """
        return cls(
            id=data.get('id'),
            name=data.get('name', 'Knowledge Source 1'),
            source_type=data.get('source_type', 'string'),
            source_path=data.get('source_path', ''),
            content=data.get('content', ''),
            metadata=data.get('metadata', {}),
            chunk_size=data.get('chunk_size', 4000),
            chunk_overlap=data.get('chunk_overlap', 200),
            created_at=data.get('created_at', datetime.now().isoformat()),
        )
