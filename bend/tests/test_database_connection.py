"""
Database Connection Test
Tests PostgreSQL connection and basic operations
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from bend.database.connection import engine, SessionLocal
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


def test_connection():
    """Test database connection"""
    print_header("Database Connection Test")

    print(f"{Colors.OKBLUE}Database URL: {settings.database_url}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}Testing connection...{Colors.ENDC}\n")

    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"{Colors.OKGREEN}✓ Connection successful!{Colors.ENDC}")
            print(f"{Colors.OKBLUE}PostgreSQL Version:{Colors.ENDC}")
            print(f"  {version}\n")

        # Test session
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"{Colors.OKGREEN}✓ Session created successfully!{Colors.ENDC}")
            print(f"{Colors.OKBLUE}Current Database: {db_name}{Colors.ENDC}\n")
        finally:
            db.close()

        print(f"{Colors.OKGREEN}✓ All connection tests passed!{Colors.ENDC}\n")
        return True

    except Exception as e:
        print(f"{Colors.FAIL}✗ Connection failed!{Colors.ENDC}")
        print(f"{Colors.FAIL}Error: {str(e)}{Colors.ENDC}\n")
        return False


def test_table_listing():
    """Test listing existing tables"""
    print_header("Existing Tables")

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
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print(f"{Colors.WARNING}No tables found (database is empty){Colors.ENDC}")
            print()

    except Exception as e:
        print(f"{Colors.FAIL}✗ Error listing tables: {str(e)}{Colors.ENDC}\n")


def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}CrewAI Studio - Database Connection Test{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    # Test connection
    if not test_connection():
        print(f"{Colors.FAIL}Database connection failed. Please check:{Colors.ENDC}")
        print(f"{Colors.WARNING}1. PostgreSQL server is running{Colors.ENDC}")
        print(f"{Colors.WARNING}2. DB_URL in .env is correct{Colors.ENDC}")
        print(f"{Colors.WARNING}3. Database credentials are valid{Colors.ENDC}\n")
        return

    # Test table listing
    test_table_listing()

    print_header("Summary")
    print(f"{Colors.OKGREEN}✓ Database is ready for use!{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
