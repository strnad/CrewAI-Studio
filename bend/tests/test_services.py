"""
Service Layer Test
Tests business logic for all services
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bend.database.connection import SessionLocal
from bend.services import (
    ToolService,
    KnowledgeSourceService,
    AgentService,
    TaskService,
    CrewService,
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


def test_tool_service():
    """Test ToolService"""
    print_header("Tool Service Test")

    db = SessionLocal()
    try:
        service = ToolService(db)

        # Create
        tool = service.create_tool(
            name="Web Scraper Pro",
            description="Advanced web scraping tool",
            parameters={"url": "https://example.com"},
            parameters_metadata={"url": {"mandatory": True}}
        )
        print(f"{Colors.OKGREEN}✓ Created tool: {tool.tool_id}{Colors.ENDC}")

        # Validate
        validation = service.validate_tool(tool.tool_id)
        assert validation['is_valid'] is True
        print(f"{Colors.OKGREEN}✓ Tool validation passed{Colors.ENDC}")

        # Update
        updated = service.update_tool(tool.tool_id, name="Super Web Scraper")
        assert updated.name == "Super Web Scraper"
        print(f"{Colors.OKGREEN}✓ Updated tool{Colors.ENDC}")

        # Delete
        success = service.delete_tool(tool.tool_id)
        assert success is True
        print(f"{Colors.OKGREEN}✓ Deleted tool{Colors.ENDC}\n")

    finally:
        db.close()


def test_knowledge_source_service():
    """Test KnowledgeSourceService"""
    print_header("Knowledge Source Service Test")

    db = SessionLocal()
    try:
        service = KnowledgeSourceService(db)

        # Create
        ks = service.create_knowledge_source(
            name="AI Research Papers",
            source_type="string",
            content="Machine learning is a subset of artificial intelligence.",
            metadata={"category": "research"}
        )
        print(f"{Colors.OKGREEN}✓ Created knowledge source: {ks.id}{Colors.ENDC}")

        # Validate
        validation = service.validate_knowledge_source(ks.id)
        assert validation['is_valid'] is True
        print(f"{Colors.OKGREEN}✓ Knowledge source validation passed{Colors.ENDC}")

        # Delete
        success = service.delete_knowledge_source(ks.id)
        assert success is True
        print(f"{Colors.OKGREEN}✓ Deleted knowledge source{Colors.ENDC}\n")

    finally:
        db.close()


def test_agent_service():
    """Test AgentService"""
    print_header("Agent Service Test")

    db = SessionLocal()
    try:
        service = AgentService(db)

        # Create
        agent = service.create_agent(
            role="Senior Researcher",
            backstory="PhD in AI with 10 years experience",
            goal="Conduct thorough research",
            llm_provider_model="openai/gpt-4o-mini"
        )
        print(f"{Colors.OKGREEN}✓ Created agent: {agent.id}{Colors.ENDC}")

        # Validate
        validation = service.validate_agent(agent.id)
        assert validation['is_valid'] is True
        print(f"{Colors.OKGREEN}✓ Agent validation passed{Colors.ENDC}")

        # Delete
        success = service.delete_agent(agent.id)
        assert success is True
        print(f"{Colors.OKGREEN}✓ Deleted agent{Colors.ENDC}\n")

    finally:
        db.close()


def test_task_service():
    """Test TaskService"""
    print_header("Task Service Test")

    db = SessionLocal()
    try:
        # Create agent first
        agent_service = AgentService(db)
        agent = agent_service.create_agent(
            role="Test Agent",
            backstory="Testing",
            goal="Testing",
            llm_provider_model="openai/gpt-4o-mini"
        )

        # Create task
        task_service = TaskService(db)
        task = task_service.create_task(
            description="Analyze market trends",
            expected_output="Market analysis report",
            agent_id=agent.id
        )
        print(f"{Colors.OKGREEN}✓ Created task: {task.id}{Colors.ENDC}")

        # Validate
        validation = task_service.validate_task(task.id)
        assert validation['is_valid'] is True
        print(f"{Colors.OKGREEN}✓ Task validation passed{Colors.ENDC}")

        # Delete
        task_service.delete_task(task.id)
        agent_service.delete_agent(agent.id)
        print(f"{Colors.OKGREEN}✓ Deleted task and agent{Colors.ENDC}\n")

    finally:
        db.close()


def test_crew_service():
    """Test CrewService"""
    print_header("Crew Service Test")

    db = SessionLocal()
    try:
        service = CrewService(db)

        # Create
        crew = service.create_crew(
            name="Research Squad",
            process="sequential"
        )
        print(f"{Colors.OKGREEN}✓ Created crew: {crew.id}{Colors.ENDC}")

        # Validate
        validation = service.validate_crew(crew.id)
        assert validation['is_valid'] is True
        print(f"{Colors.OKGREEN}✓ Crew validation passed{Colors.ENDC}")

        # Delete
        success = service.delete_crew(crew.id)
        assert success is True
        print(f"{Colors.OKGREEN}✓ Deleted crew{Colors.ENDC}\n")

    finally:
        db.close()


def main():
    """Run all service tests"""
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}CrewAI Studio - Service Layer Tests{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    try:
        test_tool_service()
        test_knowledge_source_service()
        test_agent_service()
        test_task_service()
        test_crew_service()

        print_header("Summary")
        print(f"{Colors.OKGREEN}✓ All service tests passed!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✓ Business logic working correctly{Colors.ENDC}\n")

    except AssertionError as e:
        print(f"\n{Colors.FAIL}✗ Test assertion failed: {str(e)}{Colors.ENDC}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}✗ Test error: {str(e)}{Colors.ENDC}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
