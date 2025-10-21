"""
Check Database Tables
데이터베이스 테이블 확인
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bend.database.connection import engine
from sqlalchemy import inspect, text

def check_tables():
    """데이터베이스 테이블 확인"""
    print("🔍 Checking database tables...\n")

    inspector = inspect(engine)

    # 1. 모든 테이블 목록
    tables = inspector.get_table_names()
    print(f"📊 Total tables: {len(tables)}\n")

    expected_tables = [
        "users", "workspaces", "workspace_members",
        "crew_templates", "template_favorites",
        "agents", "crews", "tasks", "tools",
        "knowledge_sources", "crew_runs",
        "agent_tools", "agent_knowledge_sources",
        "crew_agents", "crew_tasks", "crew_knowledge_sources",
        "task_async_context", "task_sync_context"
    ]

    print("✅ Expected tables:")
    for table in expected_tables:
        if table in tables:
            print(f"  ✓ {table}")
        else:
            print(f"  ✗ {table} (MISSING)")

    print("\n" + "="*60 + "\n")

    # 2. users 테이블 상세 확인
    if "users" in tables:
        print("👤 users table structure:\n")
        columns = inspector.get_columns("users")
        for col in columns:
            col_type = str(col['type'])
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col['default'] else ""
            print(f"  {col['name']:20} {col_type:30} {nullable}{default}")

        print("\n" + "="*60 + "\n")

    # 3. workspace_members 테이블 확인
    if "workspace_members" in tables:
        print("👥 workspace_members table structure:\n")
        columns = inspector.get_columns("workspace_members")
        for col in columns:
            col_type = str(col['type'])
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"  {col['name']:20} {col_type:30} {nullable}")

        print("\n" + "="*60 + "\n")

    # 4. 외래키 확인
    print("🔗 Foreign keys check:\n")
    key_tables = ["users", "workspaces", "workspace_members", "agents", "crews", "tasks"]
    for table in key_tables:
        if table in tables:
            fks = inspector.get_foreign_keys(table)
            if fks:
                print(f"  {table}:")
                for fk in fks:
                    print(f"    - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
            else:
                print(f"  {table}: (no foreign keys)")

    print("\n" + "="*60 + "\n")

    # 5. 인덱스 확인
    print("📑 Indexes on users table:\n")
    if "users" in tables:
        indexes = inspector.get_indexes("users")
        for idx in indexes:
            print(f"  {idx['name']:30} on {idx['column_names']}")

    print("\n" + "="*60 + "\n")

    # 6. 데이터 카운트
    print("📊 Row counts:\n")
    with engine.connect() as conn:
        for table in ["users", "workspaces", "workspace_members", "agents", "crews", "tasks", "tools", "knowledge_sources"]:
            if table in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  {table:25} {count} rows")

    print("\n✅ Database check complete!")

if __name__ == "__main__":
    check_tables()
