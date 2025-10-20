"""
Tool Service
Business logic for Tool operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from bend.database.repositories.tool_repository import ToolRepository
from bend.database.models.tool import Tool


class ToolService:
    """Service for Tool business logic"""

    def __init__(self, db: Session):
        """
        Initialize service

        Args:
            db: Database session
        """
        self.db = db
        self.repo = ToolRepository(db)

    def create_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any] = None,
        parameters_metadata: Dict[str, Dict[str, Any]] = None
    ) -> Tool:
        """
        Create new tool

        Args:
            name: Tool name
            description: Tool description
            parameters: Tool parameters
            parameters_metadata: Parameter metadata

        Returns:
            Created tool

        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not name or not name.strip():
            raise ValueError("Tool name is required")
        if not description or not description.strip():
            raise ValueError("Tool description is required")

        # Check for duplicate name
        existing = self.repo.get_by_name(name)
        if existing:
            raise ValueError(f"Tool with name '{name}' already exists")

        return self.repo.create(
            name=name,
            description=description,
            parameters=parameters or {},
            parameters_metadata=parameters_metadata or {}
        )

    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """
        Get tool by ID

        Args:
            tool_id: Tool ID

        Returns:
            Tool or None
        """
        return self.repo.get_by_id(tool_id)

    def list_tools(self, skip: int = 0, limit: int = 100) -> List[Tool]:
        """
        List all tools

        Args:
            skip: Number to skip
            limit: Maximum number to return

        Returns:
            List of tools
        """
        return self.repo.get_all(skip=skip, limit=limit)

    def update_tool(
        self,
        tool_id: str,
        **kwargs
    ) -> Optional[Tool]:
        """
        Update tool

        Args:
            tool_id: Tool ID
            **kwargs: Fields to update

        Returns:
            Updated tool or None

        Raises:
            ValueError: If tool not found or validation fails
        """
        tool = self.repo.get_by_id(tool_id)
        if not tool:
            raise ValueError(f"Tool with id '{tool_id}' not found")

        # Validate name if being updated
        if 'name' in kwargs:
            if not kwargs['name'] or not kwargs['name'].strip():
                raise ValueError("Tool name cannot be empty")

            # Check for duplicate name (excluding current tool)
            existing = self.repo.get_by_name(kwargs['name'])
            if existing and existing.tool_id != tool_id:
                raise ValueError(f"Tool with name '{kwargs['name']}' already exists")

        return self.repo.update(tool_id, **kwargs)

    def delete_tool(self, tool_id: str) -> bool:
        """
        Delete tool

        Args:
            tool_id: Tool ID

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If tool is in use by agents
        """
        tool = self.repo.get_by_id(tool_id)
        if not tool:
            return False

        # Check if tool is used by any agents
        if tool.agents:
            agent_roles = [agent.role for agent in tool.agents]
            raise ValueError(
                f"Tool is used by agents: {', '.join(agent_roles)}. "
                "Remove tool from agents before deleting."
            )

        return self.repo.delete(tool_id)

    def validate_tool(self, tool_id: str) -> Dict[str, Any]:
        """
        Validate tool configuration

        Args:
            tool_id: Tool ID

        Returns:
            Validation result

        Raises:
            ValueError: If tool not found
        """
        tool = self.repo.get_by_id(tool_id)
        if not tool:
            raise ValueError(f"Tool with id '{tool_id}' not found")

        errors = []
        warnings = []

        # Validate name
        if not tool.name or not tool.name.strip():
            errors.append("Tool name is required")

        # Validate description
        if not tool.description or not tool.description.strip():
            errors.append("Tool description is required")

        # Validate parameters_metadata for mandatory parameters
        if tool.parameters_metadata:
            for param_name, metadata in tool.parameters_metadata.items():
                if metadata.get('mandatory', False):
                    if not tool.parameters or param_name not in tool.parameters:
                        errors.append(f"Mandatory parameter '{param_name}' is missing")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def search_tools(self, query: str) -> List[Tool]:
        """
        Search tools by name

        Args:
            query: Search query

        Returns:
            List of matching tools
        """
        return self.repo.search_by_name(query)
