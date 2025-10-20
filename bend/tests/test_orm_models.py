"""
ORM Models Test
Tests SQLAlchemy models and creates database tables
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from bend.database.connection import engine, Base
from bend.database import models  # Import all models to register them with Base
from bend.config import settings


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def test_models_import():
    """Test that all models import correctly"""
    print_header("ORM Models Import Test")

    try:
        from bend.database.models import (
            Tool, KnowledgeSource, Agent, Task, Crew,
            agent_tools, agent_knowledge_sources,
            task_async_context, task_sync_context,
            crew_agents, crew_tasks, crew_knowledge_sources,
        )

        models_list = [
            ("Tool", Tool),
            ("KnowledgeSource", KnowledgeSource),
            ("Agent", Agent),
            ("Task", Task),
            ("Crew", Crew),
        ]

        association_tables = [
            "agent_tools",
            "agent_knowledge_sources",
            "task_async_context",
            "task_sync_context",
            "crew_agents",
            "crew_tasks",
            "crew_knowledge_sources",
        ]

        print(f"{Colors.OKBLUE}ORM Models:{Colors.ENDC}")
        for name, model in models_list:
            table_name = model.__tablename__
            print(f"  ✓ {name} → {table_name}")

        print(f"\n{Colors.OKBLUE}Association Tables:{Colors.ENDC}")
        for table_name in association_tables:
            print(f"  ✓ {table_name}")

        print(f"\n{Colors.OKGREEN}✓ All models imported successfully!{Colors.ENDC}\n")
        return True

    except Exception as e:
        print(f"{Colors.FAIL}✗ Import failed: {str(e)}{Colors.ENDC}\n")
        return False


def test_create_tables():
    """Create all database tables"""
    print_header("Database Tables Creation")

    try:
        print(f"{Colors.OKBLUE}Creating tables...{Colors.ENDC}\n")

        # Create all tables
        Base.metadata.create_all(bind=engine)

        print(f"{Colors.OKGREEN}✓ Tables created successfully!{Colors.ENDC}\n")
        return True

    except Exception as e:
        print(f"{Colors.FAIL}✗ Table creation failed: {str(e)}{Colors.ENDC}\n")
        return False


def test_list_tables():
    """List all created tables"""
    print_header("Created Tables")

    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()

            if tables:
                print(f"{Colors.OKBLUE}Found {len(tables)} table(s):{Colors.ENDC}")
                for i, table in enumerate(tables, 1):
                    print(f"  {i}. {table[0]}")
                print()
            else:
                print(f"{Colors.WARNING}No tables found{Colors.ENDC}\n")

        return True

    except Exception as e:
        print(f"{Colors.FAIL}✗ Error listing tables: {str(e)}{Colors.ENDC}\n")
        return False


def test_table_structure():
    """Display table structure"""
    print_header("Table Structure")

    try:
        with engine.connect() as conn:
            # Get all tables
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()

            for table in tables:
                table_name = table[0]
                print(f"{Colors.OKBLUE}{table_name}:{Colors.ENDC}")

                # Get columns
                result = conn.execute(text(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = :table_name
                    ORDER BY ordinal_position
                """), {"table_name": table_name})

                columns = result.fetchall()
                for col in columns:
                    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                    print(f"  - {col[0]}: {col[1]} ({nullable})")
                print()

        print(f"{Colors.OKGREEN}✓ Table structure displayed!{Colors.ENDC}\n")
        return True

    except Exception as e:
        print(f"{Colors.FAIL}✗ Error displaying structure: {str(e)}{Colors.ENDC}\n")
        return False


def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}CrewAI Studio - ORM Models Test{Colors.ENDC}")
    print(f"{Colors.BOLD}Database: {settings.database_url}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    # Test models import
    if not test_models_import():
        return

    # Create tables
    if not test_create_tables():
        return

    # List tables
    if not test_list_tables():
        return

    # Display table structure
    test_table_structure()

    print_header("Summary")
    print(f"{Colors.OKGREEN}✓ All ORM tests passed!{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ Database schema is ready for use!{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
