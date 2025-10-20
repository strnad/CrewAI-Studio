"""
Tool Domain Model
Pure business logic without UI dependencies
"""
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import os
import sys
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def generate_id() -> str:
    """Generate unique ID for tool"""
    import uuid
    return uuid.uuid4().hex[:12]


@dataclass
class ToolModel:
    """
    Base Tool Domain Model
    Represents tool configuration without UI dependencies
    """

    tool_id: str = field(default_factory=generate_id)
    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    parameters_metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def create_tool(self):
        """
        Create the actual CrewAI tool instance
        Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement create_tool()")

    def get_parameters(self) -> Dict[str, Any]:
        """Get tool parameters"""
        return self.parameters

    def set_parameters(self, **kwargs):
        """Update tool parameters"""
        self.parameters.update(kwargs)

    def get_parameter_names(self) -> list:
        """Get list of parameter names"""
        return list(self.parameters_metadata.keys())

    def is_parameter_mandatory(self, param_name: str) -> bool:
        """Check if a parameter is mandatory"""
        return self.parameters_metadata.get(param_name, {}).get('mandatory', False)

    def validate(self) -> Dict[str, Any]:
        """
        Validate tool configuration

        Returns:
            Dict with 'errors', 'warnings', and 'is_valid' keys
        """
        errors = []
        warnings = []

        # Validate mandatory parameters
        for param_name, metadata in self.parameters_metadata.items():
            if metadata.get('mandatory', False) and not self.parameters.get(param_name):
                errors.append(f"Parameter '{param_name}' is mandatory for tool '{self.name}'")

        # Validate tool name
        if not self.name:
            errors.append("Tool has no name defined")

        return {
            'errors': errors,
            'warnings': warnings,
            'is_valid': len(errors) == 0
        }

    def is_valid(self) -> bool:
        """Simple validation check (backward compatibility)"""
        return self.validate()['is_valid']

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'tool_id': self.tool_id,
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'parameters_metadata': self.parameters_metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolModel':
        """
        Create ToolModel from dictionary

        Args:
            data: Dictionary with tool data

        Returns:
            ToolModel instance
        """
        return cls(
            tool_id=data.get('tool_id', generate_id()),
            name=data.get('name', ''),
            description=data.get('description', ''),
            parameters=data.get('parameters', {}),
            parameters_metadata=data.get('parameters_metadata', {}),
        )


# Note: All 29 tool subclasses (MyScrapeWebsiteTool, MyFileReadTool, etc.)
# are kept in app/my_tools.py for Streamlit UI compatibility.
#
# For REST API, we can:
# 1. Import them directly from app.my_tools
# 2. Or recreate them here without Streamlit dependencies (recommended for Phase 3)
#
# For now, the base ToolModel provides the core functionality for validation
# and serialization that will be used in the REST API.
