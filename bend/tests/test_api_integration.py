"""
API Integration Test
Tests API endpoints with Service layer and PostgreSQL
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi.testclient import TestClient
from bend.main import app
from bend.database.connection import SessionLocal, engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)


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


def test_tool_api():
    """Test Tool API with Service layer"""
    print_header("Tool API Integration Test")

    # Create tool
    response = client.post("/api/tools/", json={
        "name": "API Test Tool",
        "description": "Tool for API testing",
        "parameters": {"url": "https://test.com"},
        "parameters_metadata": {"url": {"mandatory": True}}
    })
    print(f"Create Tool: {response.status_code}")
    assert response.status_code == 201
    tool_id = response.json()["tool_id"]
    print(f"{Colors.OKGREEN}✓ Tool created: {tool_id}{Colors.ENDC}")

    # Get tool
    response = client.get(f"/api/tools/{tool_id}")
    print(f"Get Tool: {response.status_code}")
    assert response.status_code == 200
    assert response.json()["name"] == "API Test Tool"
    print(f"{Colors.OKGREEN}✓ Tool retrieved successfully{Colors.ENDC}")

    # List tools
    response = client.get("/api/tools/")
    print(f"List Tools: {response.status_code}")
    assert response.status_code == 200
    assert response.json()["total"] >= 1
    print(f"{Colors.OKGREEN}✓ Tools listed: {response.json()['total']} total{Colors.ENDC}")

    # Update tool
    response = client.put(f"/api/tools/{tool_id}", json={
        "name": "Updated API Test Tool"
    })
    print(f"Update Tool: {response.status_code}")
    assert response.status_code == 200
    assert response.json()["name"] == "Updated API Test Tool"
    print(f"{Colors.OKGREEN}✓ Tool updated successfully{Colors.ENDC}")

    # Validate tool
    response = client.post(f"/api/tools/{tool_id}/validate")
    print(f"Validate Tool: {response.status_code}")
    assert response.status_code == 200
    assert response.json()["is_valid"] is True
    print(f"{Colors.OKGREEN}✓ Tool validation passed{Colors.ENDC}")

    # Delete tool
    response = client.delete(f"/api/tools/{tool_id}")
    print(f"Delete Tool: {response.status_code}")
    assert response.status_code == 204
    print(f"{Colors.OKGREEN}✓ Tool deleted successfully{Colors.ENDC}\n")

    return True


def test_knowledge_source_api():
    """Test Knowledge Source API with Service layer"""
    print_header("Knowledge Source API Integration Test")

    # Create knowledge source
    response = client.post("/api/knowledge/", json={
        "name": "API Test KS",
        "source_type": "string",
        "content": "Test content for API integration",
        "metadata": {"test": True}
    })
    print(f"Create KS: {response.status_code}")
    assert response.status_code == 201
    ks_id = response.json()["id"]
    print(f"{Colors.OKGREEN}✓ Knowledge source created: {ks_id}{Colors.ENDC}")

    # Get knowledge source
    response = client.get(f"/api/knowledge/{ks_id}")
    print(f"Get KS: {response.status_code}")
    assert response.status_code == 200
    assert response.json()["name"] == "API Test KS"
    print(f"{Colors.OKGREEN}✓ Knowledge source retrieved{Colors.ENDC}")

    # Delete knowledge source
    response = client.delete(f"/api/knowledge/{ks_id}")
    print(f"Delete KS: {response.status_code}")
    assert response.status_code == 204
    print(f"{Colors.OKGREEN}✓ Knowledge source deleted{Colors.ENDC}\n")

    return True


def test_agent_api():
    """Test Agent API with Service layer"""
    print_header("Agent API Integration Test")

    # Create tool first (agent needs tools)
    import time
    tool_name = f"Agent Test Tool {int(time.time())}"
    tool_response = client.post("/api/tools/", json={
        "name": tool_name,
        "description": "Tool for agent testing",
        "parameters": {},
        "parameters_metadata": {}
    })
    if tool_response.status_code != 201:
        print(f"{Colors.FAIL}Tool creation failed: {tool_response.json()}{Colors.ENDC}")
    assert tool_response.status_code == 201
    tool_id = tool_response.json()["tool_id"]
    print(f"{Colors.OKGREEN}✓ Tool created: {tool_id}{Colors.ENDC}")

    # Create agent
    response = client.post("/api/agents/", json={
        "role": "API Test Agent",
        "backstory": "Testing agent API",
        "goal": "Test agent creation",
        "llm_provider_model": "openai/gpt-4o-mini",
        "tool_ids": [tool_id],
        "knowledge_source_ids": []
    })
    print(f"Create Agent: {response.status_code}")
    if response.status_code != 201:
        print(f"{Colors.FAIL}Error: {response.json()}{Colors.ENDC}")
    assert response.status_code == 201
    agent_id = response.json()["id"]
    print(f"{Colors.OKGREEN}✓ Agent created: {agent_id}{Colors.ENDC}")

    # Get agent
    response = client.get(f"/api/agents/{agent_id}")
    print(f"Get Agent: {response.status_code}")
    assert response.status_code == 200
    assert response.json()["role"] == "API Test Agent"
    print(f"{Colors.OKGREEN}✓ Agent retrieved{Colors.ENDC}")

    # Delete agent
    response = client.delete(f"/api/agents/{agent_id}")
    print(f"Delete Agent: {response.status_code}")
    assert response.status_code == 204
    print(f"{Colors.OKGREEN}✓ Agent deleted{Colors.ENDC}")

    # Cleanup tool
    client.delete(f"/api/tools/{tool_id}")
    print(f"{Colors.OKGREEN}✓ Cleanup completed{Colors.ENDC}\n")

    return True


def test_task_api():
    """Test Task API with Service layer"""
    print_header("Task API Integration Test")

    # Create tool and agent first
    import time
    tool_name = f"Task Test Tool {int(time.time())}"
    tool_response = client.post("/api/tools/", json={
        "name": tool_name,
        "description": "Tool for task testing",
        "parameters": {},
        "parameters_metadata": {}
    })
    assert tool_response.status_code == 201
    tool_id = tool_response.json()["tool_id"]

    agent_response = client.post("/api/agents/", json={
        "role": "Task Test Agent",
        "backstory": "Testing",
        "goal": "Testing",
        "llm_provider_model": "openai/gpt-4o-mini",
        "tool_ids": [tool_id],
        "knowledge_source_ids": []
    })
    agent_id = agent_response.json()["id"]

    # Create task
    response = client.post("/api/tasks/", json={
        "description": "API Test Task",
        "expected_output": "Test output",
        "agent_id": agent_id
    })
    print(f"Create Task: {response.status_code}")
    assert response.status_code == 201
    task_id = response.json()["id"]
    print(f"{Colors.OKGREEN}✓ Task created: {task_id}{Colors.ENDC}")

    # Get task
    response = client.get(f"/api/tasks/{task_id}")
    print(f"Get Task: {response.status_code}")
    assert response.status_code == 200
    assert response.json()["description"] == "API Test Task"
    print(f"{Colors.OKGREEN}✓ Task retrieved{Colors.ENDC}")

    # Delete task, agent, tool
    client.delete(f"/api/tasks/{task_id}")
    client.delete(f"/api/agents/{agent_id}")
    client.delete(f"/api/tools/{tool_id}")
    print(f"{Colors.OKGREEN}✓ Cleanup completed{Colors.ENDC}\n")

    return True


def test_crew_api():
    """Test Crew API with Service layer"""
    print_header("Crew API Integration Test")

    # Create prerequisites
    import time
    tool_name = f"Crew Test Tool {int(time.time())}"
    tool_response = client.post("/api/tools/", json={
        "name": tool_name,
        "description": "Tool for crew testing",
        "parameters": {},
        "parameters_metadata": {}
    })
    assert tool_response.status_code == 201
    tool_id = tool_response.json()["tool_id"]

    agent_response = client.post("/api/agents/", json={
        "role": "Crew Test Agent",
        "backstory": "Testing",
        "goal": "Testing",
        "llm_provider_model": "openai/gpt-4o-mini",
        "tool_ids": [tool_id],
        "knowledge_source_ids": []
    })
    agent_id = agent_response.json()["id"]

    task_response = client.post("/api/tasks/", json={
        "description": "Crew Test Task",
        "expected_output": "Test output",
        "agent_id": agent_id
    })
    task_id = task_response.json()["id"]

    # Create crew
    response = client.post("/api/crews/", json={
        "name": "API Test Crew",
        "agent_ids": [agent_id],
        "task_ids": [task_id],
        "process": "sequential"
    })
    print(f"Create Crew: {response.status_code}")
    assert response.status_code == 201
    crew_id = response.json()["id"]
    print(f"{Colors.OKGREEN}✓ Crew created: {crew_id}{Colors.ENDC}")

    # Get crew
    response = client.get(f"/api/crews/{crew_id}")
    print(f"Get Crew: {response.status_code}")
    assert response.status_code == 200
    assert response.json()["name"] == "API Test Crew"
    print(f"{Colors.OKGREEN}✓ Crew retrieved{Colors.ENDC}")

    # Delete crew and cleanup
    client.delete(f"/api/crews/{crew_id}")
    client.delete(f"/api/tasks/{task_id}")
    client.delete(f"/api/agents/{agent_id}")
    client.delete(f"/api/tools/{tool_id}")
    print(f"{Colors.OKGREEN}✓ Cleanup completed{Colors.ENDC}\n")

    return True


def main():
    """Run all API integration tests"""
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}CrewAI Studio - API Integration Tests{Colors.ENDC}")
    print(f"{Colors.BOLD}Testing: API → Service → Repository → PostgreSQL{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    try:
        test_tool_api()
        test_knowledge_source_api()
        test_agent_api()
        test_task_api()
        test_crew_api()

        print_header("Summary")
        print(f"{Colors.OKGREEN}✓ All API integration tests passed!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✓ Service layer working correctly{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✓ PostgreSQL persistence confirmed{Colors.ENDC}\n")

    except AssertionError as e:
        print(f"\n{Colors.FAIL}✗ Test assertion failed: {str(e)}{Colors.ENDC}\n")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n{Colors.FAIL}✗ Test error: {str(e)}{Colors.ENDC}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
