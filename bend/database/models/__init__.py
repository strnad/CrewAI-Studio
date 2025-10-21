"""
Database ORM Models Package
Exports all SQLAlchemy models and association tables
"""
# Multi-tenant models
from bend.database.models.user import User, UserRole, UserStatus
from bend.database.models.workspace import Workspace
from bend.database.models.workspace_member import WorkspaceMember, WorkspaceRole
from bend.database.models.crew_template import CrewTemplate, TemplateVisibility
from bend.database.models.template_favorite import TemplateFavorite

# Existing models
from bend.database.models.tool import Tool
from bend.database.models.knowledge_source import KnowledgeSource
from bend.database.models.agent import Agent, agent_tools, agent_knowledge_sources
from bend.database.models.task import Task, task_async_context, task_sync_context
from bend.database.models.crew import Crew, crew_agents, crew_tasks, crew_knowledge_sources
from bend.database.models.crew_run import CrewRun

__all__ = [
    # Multi-tenant Models
    "User",
    "UserRole",
    "UserStatus",
    "Workspace",
    "WorkspaceMember",
    "WorkspaceRole",
    "CrewTemplate",
    "TemplateVisibility",
    "TemplateFavorite",
    # Core Models
    "Tool",
    "KnowledgeSource",
    "Agent",
    "Task",
    "Crew",
    "CrewRun",
    # Association Tables
    "agent_tools",
    "agent_knowledge_sources",
    "task_async_context",
    "task_sync_context",
    "crew_agents",
    "crew_tasks",
    "crew_knowledge_sources",
]
