"""
In-Memory Storage for Development
Temporary storage solution before database implementation
"""
from typing import Dict, List, Optional, Any
from datetime import datetime


class InMemoryStorage:
    """Simple in-memory storage for development and testing"""

    def __init__(self):
        self.crews: Dict[str, Any] = {}
        self.agents: Dict[str, Any] = {}
        self.tasks: Dict[str, Any] = {}
        self.tools: Dict[str, Any] = {}
        self.knowledge_sources: Dict[str, Any] = {}

    def clear_all(self):
        """Clear all data (for testing)"""
        self.crews.clear()
        self.agents.clear()
        self.tasks.clear()
        self.tools.clear()
        self.knowledge_sources.clear()


# Global storage instance
storage = InMemoryStorage()
