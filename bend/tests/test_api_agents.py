"""
Agents API Test Script
Python-based API testing using requests library
"""
import requests
import json
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8000/api"


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


def print_request(method: str, endpoint: str, data: Dict[str, Any] = None):
    """Print request details"""
    print(f"{Colors.OKCYAN}{method} {endpoint}{Colors.ENDC}")
    if data:
        print(f"{Colors.OKBLUE}Request Body:{Colors.ENDC}")
        print(json.dumps(data, indent=2))


def print_response(response: requests.Response):
    """Print response details"""
    status_color = Colors.OKGREEN if response.status_code < 400 else Colors.FAIL
    print(f"\n{status_color}Status: {response.status_code} {response.reason}{Colors.ENDC}")

    try:
        data = response.json()
        print(f"{Colors.OKBLUE}Response Body:{Colors.ENDC}")
        print(json.dumps(data, indent=2))
    except:
        print(f"{Colors.WARNING}No JSON response{Colors.ENDC}")
    print()


def test_health_check():
    """Test health check endpoint"""
    print_header("Health Check")

    # Basic health check
    print_request("GET", "/api/health")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)


def test_agents_crud():
    """Test Agents CRUD operations"""
    print_header("Agents CRUD Operations")

    # 1. Create an agent (minimal - should work)
    print_request("POST", "/api/agents", {
        "role": "Senior Researcher",
        "backstory": "Driven by curiosity, exploring AI innovations",
        "goal": "Uncover groundbreaking technologies in AI",
        "temperature": 0.1,
        "allow_delegation": False,
        "verbose": True,
        "cache": True,
        "llm_provider_model": "openai/gpt-4o-mini",
        "max_iter": 25,
        "tool_ids": [],
        "knowledge_source_ids": []
    })

    response = requests.post(f"{BASE_URL}/agents", json={
        "role": "Senior Researcher",
        "backstory": "Driven by curiosity, exploring AI innovations",
        "goal": "Uncover groundbreaking technologies in AI",
        "temperature": 0.1,
        "allow_delegation": False,
        "verbose": True,
        "cache": True,
        "llm_provider_model": "openai/gpt-4o-mini",
        "max_iter": 25,
        "tool_ids": [],
        "knowledge_source_ids": []
    })
    print_response(response)

    if response.status_code == 201:
        agent_id = response.json()['id']
        print(f"{Colors.OKGREEN}✓ Created agent with ID: {agent_id}{Colors.ENDC}\n")

        # 2. Get the created agent
        print_request("GET", f"/api/agents/{agent_id}")
        response = requests.get(f"{BASE_URL}/agents/{agent_id}")
        print_response(response)

        # 3. List all agents
        print_request("GET", "/api/agents")
        response = requests.get(f"{BASE_URL}/agents")
        print_response(response)

        # 4. Update the agent
        print_request("PUT", f"/api/agents/{agent_id}", {
            "role": "Lead Researcher",
            "temperature": 0.2,
            "allow_delegation": True
        })
        response = requests.put(f"{BASE_URL}/agents/{agent_id}", json={
            "role": "Lead Researcher",
            "temperature": 0.2,
            "allow_delegation": True
        })
        print_response(response)

        # 5. Validate the agent
        print_request("POST", f"/api/agents/{agent_id}/validate")
        response = requests.post(f"{BASE_URL}/agents/{agent_id}/validate")
        print_response(response)

        validation = response.json()
        if not validation['is_valid']:
            print(f"{Colors.WARNING}⚠ Validation warnings/errors:{Colors.ENDC}")
            for error in validation['errors']:
                print(f"  {Colors.FAIL}✗ {error}{Colors.ENDC}")
            for warning in validation['warnings']:
                print(f"  {Colors.WARNING}⚠ {warning}{Colors.ENDC}")
            print()

        # 6. Delete the agent
        print_request("DELETE", f"/api/agents/{agent_id}")
        response = requests.delete(f"{BASE_URL}/agents/{agent_id}")
        print(f"\n{Colors.OKGREEN}Status: {response.status_code} {response.reason}{Colors.ENDC}\n")

        # 7. Verify deletion
        print_request("GET", f"/api/agents/{agent_id}")
        response = requests.get(f"{BASE_URL}/agents/{agent_id}")
        print_response(response)

        if response.status_code == 404:
            print(f"{Colors.OKGREEN}✓ Agent successfully deleted{Colors.ENDC}\n")
    else:
        print(f"{Colors.FAIL}✗ Failed to create agent{Colors.ENDC}\n")


def test_agent_with_invalid_tools():
    """Test agent creation with invalid tool IDs"""
    print_header("Test: Agent with Invalid Tool IDs")

    print_request("POST", "/api/agents", {
        "role": "Invalid Agent",
        "backstory": "Testing invalid tools",
        "goal": "Test validation",
        "llm_provider_model": "openai/gpt-4o-mini",
        "tool_ids": ["invalid_tool_id"]
    })

    response = requests.post(f"{BASE_URL}/agents", json={
        "role": "Invalid Agent",
        "backstory": "Testing invalid tools",
        "goal": "Test validation",
        "llm_provider_model": "openai/gpt-4o-mini",
        "tool_ids": ["invalid_tool_id"]
    })
    print_response(response)

    if response.status_code == 400:
        print(f"{Colors.OKGREEN}✓ Correctly rejected invalid tool_id{Colors.ENDC}\n")
    else:
        print(f"{Colors.FAIL}✗ Should have rejected invalid tool_id{Colors.ENDC}\n")


def test_agent_deletion_with_crew_dependency():
    """Test agent deletion when agent is used by a crew"""
    print_header("Test: Agent Deletion with Crew Dependency")

    # 1. Create an agent
    agent_response = requests.post(f"{BASE_URL}/agents", json={
        "role": "Test Agent",
        "backstory": "Testing crew dependency",
        "goal": "Test validation",
        "llm_provider_model": "openai/gpt-4o-mini",
        "tool_ids": [],
        "knowledge_source_ids": []
    })

    if agent_response.status_code == 201:
        agent_id = agent_response.json()['id']
        print(f"{Colors.OKGREEN}✓ Created agent with ID: {agent_id}{Colors.ENDC}\n")

        # 2. Create a crew using this agent
        crew_response = requests.post(f"{BASE_URL}/crews", json={
            "name": "Test Crew",
            "agent_ids": [agent_id],
            "task_ids": [],
            "process": "sequential",
            "verbose": True,
            "cache": True,
            "max_rpm": 1000,
            "memory": False,
            "planning": False,
            "knowledge_source_ids": []
        })

        if crew_response.status_code == 201:
            crew_id = crew_response.json()['id']
            print(f"{Colors.OKGREEN}✓ Created crew with ID: {crew_id}{Colors.ENDC}\n")

            # 3. Try to delete the agent (should fail)
            print_request("DELETE", f"/api/agents/{agent_id}")
            response = requests.delete(f"{BASE_URL}/agents/{agent_id}")
            print_response(response)

            if response.status_code == 400:
                print(f"{Colors.OKGREEN}✓ Correctly prevented deletion (agent in use){Colors.ENDC}\n")
            else:
                print(f"{Colors.FAIL}✗ Should have prevented deletion{Colors.ENDC}\n")

            # 4. Clean up: delete crew first
            requests.delete(f"{BASE_URL}/crews/{crew_id}")
            print(f"{Colors.OKBLUE}Cleaned up crew{Colors.ENDC}\n")

            # 5. Now delete agent (should succeed)
            response = requests.delete(f"{BASE_URL}/agents/{agent_id}")
            if response.status_code == 204:
                print(f"{Colors.OKGREEN}✓ Agent deleted successfully after crew removal{Colors.ENDC}\n")


def test_error_cases():
    """Test error handling"""
    print_header("Error Handling Tests")

    # 1. Get non-existent agent
    print_request("GET", "/api/agents/nonexistent")
    response = requests.get(f"{BASE_URL}/agents/nonexistent")
    print_response(response)

    # 2. Update non-existent agent
    print_request("PUT", "/api/agents/nonexistent", {"role": "Updated"})
    response = requests.put(f"{BASE_URL}/agents/nonexistent", json={"role": "Updated"})
    print_response(response)

    # 3. Delete non-existent agent
    print_request("DELETE", "/api/agents/nonexistent")
    response = requests.delete(f"{BASE_URL}/agents/nonexistent")
    print_response(response)

    # 4. Validate non-existent agent
    print_request("POST", "/api/agents/nonexistent/validate")
    response = requests.post(f"{BASE_URL}/agents/nonexistent/validate")
    print_response(response)


def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}CrewAI Studio - Agents API Tests{Colors.ENDC}")
    print(f"{Colors.BOLD}Base URL: {BASE_URL}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    try:
        # Test health check first
        test_health_check()

        # Test CRUD operations
        test_agents_crud()

        # Test error handling with invalid tools
        test_agent_with_invalid_tools()

        # Test agent deletion with crew dependency
        test_agent_deletion_with_crew_dependency()

        # Test error handling
        test_error_cases()

        print_header("All Tests Completed")
        print(f"{Colors.OKGREEN}✓ All API tests finished{Colors.ENDC}\n")

    except requests.exceptions.ConnectionError:
        print(f"\n{Colors.FAIL}✗ Error: Could not connect to {BASE_URL}{Colors.ENDC}")
        print(f"{Colors.WARNING}Make sure the API server is running:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  cd bend && python run.py{Colors.ENDC}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}✗ Error: {str(e)}{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
