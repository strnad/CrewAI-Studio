"""
Tasks API Test Script
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


def create_agent():
    """Helper: Create an agent for testing"""
    response = requests.post(f"{BASE_URL}/agents", json={
        "role": "Test Agent for Tasks",
        "backstory": "Testing task creation",
        "goal": "Test validation",
        "llm_provider_model": "openai/gpt-4o-mini",
        "tool_ids": [],
        "knowledge_source_ids": []
    })
    if response.status_code == 201:
        return response.json()['id']
    return None


def test_tasks_crud():
    """Test Tasks CRUD operations"""
    print_header("Tasks CRUD Operations")

    # 1. Create an agent first (tasks need agents)
    agent_id = create_agent()
    if not agent_id:
        print(f"{Colors.FAIL}✗ Failed to create agent for testing{Colors.ENDC}\n")
        return

    print(f"{Colors.OKGREEN}✓ Created test agent with ID: {agent_id}{Colors.ENDC}\n")

    # 2. Create a task
    print_request("POST", "/api/tasks", {
        "description": "Analyze the latest AI trends",
        "expected_output": "A comprehensive report on AI trends",
        "agent_id": agent_id,
        "async_execution": False
    })

    response = requests.post(f"{BASE_URL}/tasks", json={
        "description": "Analyze the latest AI trends",
        "expected_output": "A comprehensive report on AI trends",
        "agent_id": agent_id,
        "async_execution": False
    })
    print_response(response)

    if response.status_code == 201:
        task_id = response.json()['id']
        print(f"{Colors.OKGREEN}✓ Created task with ID: {task_id}{Colors.ENDC}\n")

        # 3. Get the created task
        print_request("GET", f"/api/tasks/{task_id}")
        response = requests.get(f"{BASE_URL}/tasks/{task_id}")
        print_response(response)

        # 4. List all tasks
        print_request("GET", "/api/tasks")
        response = requests.get(f"{BASE_URL}/tasks")
        print_response(response)

        # 5. Update the task
        print_request("PUT", f"/api/tasks/{task_id}", {
            "description": "Analyze the latest AI trends (Updated)",
            "async_execution": True
        })
        response = requests.put(f"{BASE_URL}/tasks/{task_id}", json={
            "description": "Analyze the latest AI trends (Updated)",
            "async_execution": True
        })
        print_response(response)

        # 6. Validate the task
        print_request("POST", f"/api/tasks/{task_id}/validate")
        response = requests.post(f"{BASE_URL}/tasks/{task_id}/validate")
        print_response(response)

        validation = response.json()
        if not validation['is_valid']:
            print(f"{Colors.WARNING}⚠ Validation warnings/errors:{Colors.ENDC}")
            for error in validation['errors']:
                print(f"  {Colors.FAIL}✗ {error}{Colors.ENDC}")
            for warning in validation['warnings']:
                print(f"  {Colors.WARNING}⚠ {warning}{Colors.ENDC}")
            print()

        # 7. Delete the task
        print_request("DELETE", f"/api/tasks/{task_id}")
        response = requests.delete(f"{BASE_URL}/tasks/{task_id}")
        print(f"\n{Colors.OKGREEN}Status: {response.status_code} {response.reason}{Colors.ENDC}\n")

        # 8. Verify deletion
        print_request("GET", f"/api/tasks/{task_id}")
        response = requests.get(f"{BASE_URL}/tasks/{task_id}")
        print_response(response)

        if response.status_code == 404:
            print(f"{Colors.OKGREEN}✓ Task successfully deleted{Colors.ENDC}\n")

        # Clean up agent
        requests.delete(f"{BASE_URL}/agents/{agent_id}")
        print(f"{Colors.OKBLUE}Cleaned up test agent{Colors.ENDC}\n")
    else:
        print(f"{Colors.FAIL}✗ Failed to create task{Colors.ENDC}\n")


def test_task_with_invalid_agent():
    """Test task creation with invalid agent ID"""
    print_header("Test: Task with Invalid Agent ID")

    print_request("POST", "/api/tasks", {
        "description": "Invalid task",
        "expected_output": "Should fail",
        "agent_id": "invalid_agent_id"
    })

    response = requests.post(f"{BASE_URL}/tasks", json={
        "description": "Invalid task",
        "expected_output": "Should fail",
        "agent_id": "invalid_agent_id"
    })
    print_response(response)

    if response.status_code == 400:
        print(f"{Colors.OKGREEN}✓ Correctly rejected invalid agent_id{Colors.ENDC}\n")
    else:
        print(f"{Colors.FAIL}✗ Should have rejected invalid agent_id{Colors.ENDC}\n")


def test_task_with_context():
    """Test task creation with context task references"""
    print_header("Test: Task with Context Tasks")

    # 1. Create an agent
    agent_id = create_agent()
    if not agent_id:
        print(f"{Colors.FAIL}✗ Failed to create agent{Colors.ENDC}\n")
        return

    print(f"{Colors.OKGREEN}✓ Created test agent{Colors.ENDC}\n")

    # 2. Create first task (context task)
    context_task_response = requests.post(f"{BASE_URL}/tasks", json={
        "description": "Context task",
        "expected_output": "Context output",
        "agent_id": agent_id,
        "async_execution": False
    })

    if context_task_response.status_code == 201:
        context_task_id = context_task_response.json()['id']
        print(f"{Colors.OKGREEN}✓ Created context task: {context_task_id}{Colors.ENDC}\n")

        # 3. Create second task referencing first task as context
        print_request("POST", "/api/tasks", {
            "description": "Main task",
            "expected_output": "Main output",
            "agent_id": agent_id,
            "async_execution": False,
            "context_from_sync_tasks_ids": [context_task_id]
        })

        response = requests.post(f"{BASE_URL}/tasks", json={
            "description": "Main task",
            "expected_output": "Main output",
            "agent_id": agent_id,
            "async_execution": False,
            "context_from_sync_tasks_ids": [context_task_id]
        })
        print_response(response)

        if response.status_code == 201:
            main_task_id = response.json()['id']
            print(f"{Colors.OKGREEN}✓ Created main task with context reference{Colors.ENDC}\n")

            # 4. Try to delete context task (should fail)
            print_request("DELETE", f"/api/tasks/{context_task_id}")
            response = requests.delete(f"{BASE_URL}/tasks/{context_task_id}")
            print_response(response)

            if response.status_code == 400:
                print(f"{Colors.OKGREEN}✓ Correctly prevented deletion (task used as context){Colors.ENDC}\n")
            else:
                print(f"{Colors.FAIL}✗ Should have prevented deletion{Colors.ENDC}\n")

            # Clean up
            requests.delete(f"{BASE_URL}/tasks/{main_task_id}")
            requests.delete(f"{BASE_URL}/tasks/{context_task_id}")
            requests.delete(f"{BASE_URL}/agents/{agent_id}")
            print(f"{Colors.OKBLUE}Cleaned up test data{Colors.ENDC}\n")


def test_task_deletion_with_crew_dependency():
    """Test task deletion when task is used by a crew"""
    print_header("Test: Task Deletion with Crew Dependency")

    # 1. Create an agent
    agent_id = create_agent()
    if not agent_id:
        print(f"{Colors.FAIL}✗ Failed to create agent{Colors.ENDC}\n")
        return

    print(f"{Colors.OKGREEN}✓ Created test agent{Colors.ENDC}\n")

    # 2. Create a task
    task_response = requests.post(f"{BASE_URL}/tasks", json={
        "description": "Test task for crew",
        "expected_output": "Test output",
        "agent_id": agent_id,
        "async_execution": False
    })

    if task_response.status_code == 201:
        task_id = task_response.json()['id']
        print(f"{Colors.OKGREEN}✓ Created task: {task_id}{Colors.ENDC}\n")

        # 3. Create a crew using this task
        crew_response = requests.post(f"{BASE_URL}/crews", json={
            "name": "Test Crew",
            "agent_ids": [agent_id],
            "task_ids": [task_id],
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
            print(f"{Colors.OKGREEN}✓ Created crew: {crew_id}{Colors.ENDC}\n")

            # 4. Try to delete the task (should fail)
            print_request("DELETE", f"/api/tasks/{task_id}")
            response = requests.delete(f"{BASE_URL}/tasks/{task_id}")
            print_response(response)

            if response.status_code == 400:
                print(f"{Colors.OKGREEN}✓ Correctly prevented deletion (task in use by crew){Colors.ENDC}\n")
            else:
                print(f"{Colors.FAIL}✗ Should have prevented deletion{Colors.ENDC}\n")

            # Clean up
            requests.delete(f"{BASE_URL}/crews/{crew_id}")
            requests.delete(f"{BASE_URL}/tasks/{task_id}")
            requests.delete(f"{BASE_URL}/agents/{agent_id}")
            print(f"{Colors.OKBLUE}Cleaned up test data{Colors.ENDC}\n")


def test_error_cases():
    """Test error handling"""
    print_header("Error Handling Tests")

    # 1. Get non-existent task
    print_request("GET", "/api/tasks/nonexistent")
    response = requests.get(f"{BASE_URL}/tasks/nonexistent")
    print_response(response)

    # 2. Update non-existent task
    print_request("PUT", "/api/tasks/nonexistent", {"description": "Updated"})
    response = requests.put(f"{BASE_URL}/tasks/nonexistent", json={"description": "Updated"})
    print_response(response)

    # 3. Delete non-existent task
    print_request("DELETE", "/api/tasks/nonexistent")
    response = requests.delete(f"{BASE_URL}/tasks/nonexistent")
    print_response(response)

    # 4. Validate non-existent task
    print_request("POST", "/api/tasks/nonexistent/validate")
    response = requests.post(f"{BASE_URL}/tasks/nonexistent/validate")
    print_response(response)


def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}CrewAI Studio - Tasks API Tests{Colors.ENDC}")
    print(f"{Colors.BOLD}Base URL: {BASE_URL}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    try:
        # Test health check first
        test_health_check()

        # Test CRUD operations
        test_tasks_crud()

        # Test error handling with invalid agent
        test_task_with_invalid_agent()

        # Test task with context
        test_task_with_context()

        # Test task deletion with crew dependency
        test_task_deletion_with_crew_dependency()

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
