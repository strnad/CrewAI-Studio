"""
Repository Layer Test
Tests CRUD operations for all repositories
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bend.database.connection import SessionLocal
from bend.database.repositories import (
    ToolRepository,
    KnowledgeSourceRepository,
    AgentRepository,
    TaskRepository,
    CrewRepository,
)


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


def test_tool_repository():
    """Test ToolRepository CRUD operations"""
    print_header("Tool Repository Test")

    db = SessionLocal()
    try:
        repo = ToolRepository(db)

        # Create
        tool = repo.create(
            name="Web Scraper",
            description="Scrapes web pages",
            parameters={"url": "https://example.com"},
            parameters_metadata={"url": {"mandatory": True}}
        )
        print(f"{Colors.OKGREEN}✓ Created tool: {tool.tool_id}{Colors.ENDC}")

        # Read
        found_tool = repo.get_by_id(tool.tool_id)
        assert found_tool is not None
        print(f"{Colors.OKGREEN}✓ Retrieved tool: {found_tool.name}{Colors.ENDC}")

        # Update
        updated_tool = repo.update(tool.tool_id, name="Advanced Web Scraper")
        assert updated_tool.name == "Advanced Web Scraper"
        print(f"{Colors.OKGREEN}✓ Updated tool name{Colors.ENDC}")

        # Search
        results = repo.search_by_name("scraper")
        assert len(results) > 0
        print(f"{Colors.OKGREEN}✓ Search found {len(results)} tool(s){Colors.ENDC}")

        # Delete
        success = repo.delete(tool.tool_id)
        assert success is True
        print(f"{Colors.OKGREEN}✓ Deleted tool{Colors.ENDC}\n")

    finally:
        db.close()


def test_knowledge_source_repository():
    """Test KnowledgeSourceRepository CRUD operations"""
    print_header("Knowledge Source Repository Test")

    db = SessionLocal()
    try:
        repo = KnowledgeSourceRepository(db)

        # Create
        ks = repo.create(
            name="AI Research",
            source_type="string",
            content="Artificial Intelligence is the simulation of human intelligence.",
            meta_data={"category": "research"},
            chunk_size=4000,
            chunk_overlap=200
        )
        print(f"{Colors.OKGREEN}✓ Created knowledge source: {ks.id}{Colors.ENDC}")

        # Read
        found_ks = repo.get_by_id(ks.id)
        assert found_ks is not None
        print(f"{Colors.OKGREEN}✓ Retrieved knowledge source: {found_ks.name}{Colors.ENDC}")

        # Get by type
        results = repo.get_by_source_type("string")
        assert len(results) > 0
        print(f"{Colors.OKGREEN}✓ Found {len(results)} string-type knowledge source(s){Colors.ENDC}")

        # Delete
        success = repo.delete(ks.id)
        assert success is True
        print(f"{Colors.OKGREEN}✓ Deleted knowledge source{Colors.ENDC}\n")

    finally:
        db.close()


def test_agent_repository():
    """Test AgentRepository CRUD operations"""
    print_header("Agent Repository Test")

    db = SessionLocal()
    try:
        repo = AgentRepository(db)

        # Create
        agent = repo.create(
            role="Researcher",
            backstory="Expert in AI research",
            goal="Find relevant information",
            llm_provider_model="openai/gpt-4o-mini",
            temperature=0.7
        )
        print(f"{Colors.OKGREEN}✓ Created agent: {agent.id}{Colors.ENDC}")

        # Read
        found_agent = repo.get_by_id(agent.id)
        assert found_agent is not None
        print(f"{Colors.OKGREEN}✓ Retrieved agent: {found_agent.role}{Colors.ENDC}")

        # Search
        results = repo.search_by_role("research")
        assert len(results) > 0
        print(f"{Colors.OKGREEN}✓ Search found {len(results)} agent(s){Colors.ENDC}")

        # Delete
        success = repo.delete(agent.id)
        assert success is True
        print(f"{Colors.OKGREEN}✓ Deleted agent{Colors.ENDC}\n")

    finally:
        db.close()


def test_task_repository():
    """Test TaskRepository CRUD operations"""
    print_header("Task Repository Test")

    db = SessionLocal()
    try:
        # Create agent first (required for task)
        agent_repo = AgentRepository(db)
        agent = agent_repo.create(
            role="Test Agent",
            backstory="Test",
            goal="Test",
            llm_provider_model="openai/gpt-4o-mini"
        )

        # Create task
        task_repo = TaskRepository(db)
        task = task_repo.create(
            description="Research AI trends",
            expected_output="Summary of AI trends",
            agent_id=agent.id,
            async_execution=False
        )
        print(f"{Colors.OKGREEN}✓ Created task: {task.id}{Colors.ENDC}")

        # Read
        found_task = task_repo.get_by_id(task.id)
        assert found_task is not None
        print(f"{Colors.OKGREEN}✓ Retrieved task{Colors.ENDC}")

        # Get tasks by agent
        agent_tasks = task_repo.get_by_agent_id(agent.id)
        assert len(agent_tasks) > 0
        print(f"{Colors.OKGREEN}✓ Found {len(agent_tasks)} task(s) for agent{Colors.ENDC}")

        # Delete
        task_repo.delete(task.id)
        agent_repo.delete(agent.id)
        print(f"{Colors.OKGREEN}✓ Deleted task and agent{Colors.ENDC}\n")

    finally:
        db.close()


def test_crew_repository():
    """Test CrewRepository CRUD operations"""
    print_header("Crew Repository Test")

    db = SessionLocal()
    try:
        repo = CrewRepository(db)

        # Create
        crew = repo.create(
            name="Research Team",
            process="sequential",
            verbose=True,
            cache=True,
            max_rpm=1000
        )
        print(f"{Colors.OKGREEN}✓ Created crew: {crew.id}{Colors.ENDC}")

        # Read
        found_crew = repo.get_by_id(crew.id)
        assert found_crew is not None
        print(f"{Colors.OKGREEN}✓ Retrieved crew: {found_crew.name}{Colors.ENDC}")

        # Search
        results = repo.search_by_name("research")
        assert len(results) > 0
        print(f"{Colors.OKGREEN}✓ Search found {len(results)} crew(s){Colors.ENDC}")

        # Delete
        success = repo.delete(crew.id)
        assert success is True
        print(f"{Colors.OKGREEN}✓ Deleted crew{Colors.ENDC}\n")

    finally:
        db.close()


def main():
    """Run all repository tests"""
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}CrewAI Studio - Repository Layer Tests{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    try:
        test_tool_repository()
        test_knowledge_source_repository()
        test_agent_repository()
        test_task_repository()
        test_crew_repository()

        print_header("Summary")
        print(f"{Colors.OKGREEN}✓ All repository tests passed!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✓ CRUD operations working correctly{Colors.ENDC}\n")

    except AssertionError as e:
        print(f"\n{Colors.FAIL}✗ Test assertion failed: {str(e)}{Colors.ENDC}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}✗ Test error: {str(e)}{Colors.ENDC}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
