"""
Recreate Database Tables
기존 테이블 삭제 후 재생성
⚠️ 주의: 모든 데이터가 삭제됩니다!
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

def recreate_all_tables():
    """모든 테이블 삭제 후 재생성"""
    print("⚠️  WARNING: This will DELETE all existing data!")
    print()

    # 사용자 확인
    confirm = input("Are you sure you want to proceed? Type 'yes' to continue: ")
    if confirm.lower() != 'yes':
        print("❌ Cancelled.")
        return

    print()
    print("🗑️  Dropping all existing tables...")

    try:
        # 모든 테이블 삭제
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully!")

        print()
        print("🗄️  Creating new tables...")

        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)

        print("✅ All tables created successfully!")
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
        print("🎉 Database recreation complete!")
        print()
        print("Key changes:")
        print("  • users.is_system_admin → users.system_role (enum)")
        print("  • users.is_active → users.status (enum)")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    recreate_all_tables()
