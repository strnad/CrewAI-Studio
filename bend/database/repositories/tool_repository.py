"""
Tool Repository
Database operations for Tool model
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from bend.database.models.tool import Tool
from bend.database.repositories.base import BaseRepository


class ToolRepository(BaseRepository[Tool]):
    """Repository for Tool operations"""

    def __init__(self, db: Session):
        super().__init__(Tool, db)

    def get_by_name(self, name: str) -> Optional[Tool]:
        """
        Get tool by name

        Args:
            name: Tool name

        Returns:
            Tool instance or None
        """
        return self.db.query(Tool).filter(Tool.name == name).first()

    def search_by_name(self, query: str) -> List[Tool]:
        """
        Search tools by name (case-insensitive)

        Args:
            query: Search query

        Returns:
            List of matching tools
        """
        return self.db.query(Tool).filter(
            Tool.name.ilike(f"%{query}%")
        ).all()

    def get_tools_by_ids(self, tool_ids: List[str]) -> List[Tool]:
        """
        Get multiple tools by IDs

        Args:
            tool_ids: List of tool IDs

        Returns:
            List of tools
        """
        return self.db.query(Tool).filter(Tool.tool_id.in_(tool_ids)).all()
