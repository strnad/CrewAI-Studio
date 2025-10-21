"""
Create Database Tables
모든 테이블 생성 스크립트
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bend.database.connection import engine, Base
from bend.database.models import (
    User, Workspace, WorkspaceMember, CrewTemplate, TemplateFavorite,
    Agent, Crew, Task, Tool, KnowledgeSource, CrewRun
)

def create_all_tables():
    """모든 테이블 생성"""
    print("🗄️  Creating database tables...")

    try:
        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)

        print("✅ Tables created successfully!")
        print()
        print("Created tables:")

        # 생성된 테이블 목록 출력
        tables = [
            "users", "workspaces", "workspace_members",
            "crew_templates", "template_favorites",
            "agents", "crews", "tasks", "tools",
            "knowledge_sources", "crew_runs",
            "agent_tools", "agent_knowledge_sources",
            "crew_agents", "crew_tasks", "crew_knowledge_sources",
            "task_async_context", "task_sync_context"
        ]

        for table in tables:
            print(f"  ✓ {table}")

        print()
        print("🎉 Database initialization complete!")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_all_tables()
