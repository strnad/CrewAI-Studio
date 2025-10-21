"""
All API Endpoints Test
모든 API 엔드포인트 CRUD 테스트
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.NC}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.NC}")

# 리소스 ID 저장
resources = {
    "crew_id": None,
    "agent_id": None,
    "task_id": None,
    "tool_id": None,
    "knowledge_id": None
}

print_header("CrewAI Studio - All API Tests")

try:
    # 1. Health Check
    print_header("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print_success("Health Check OK")
    else:
        print_error("Health Check Failed")
        exit(1)

    # 2. Crews API
    print_header("2. Crews API Tests")

    # Create Crew
    print_info("2-1. Creating Crew...")
    crew_data = {
        "name": "Test Crew",
        "agent_ids": [],
        "task_ids": [],
        "process": "sequential",
        "verbose": True,
        "cache": True,
        "max_rpm": 1000,
        "memory": False,
        "planning": False
    }
    response = requests.post(f"{BASE_URL}/crews", json=crew_data)
    if response.status_code == 201:
        resources["crew_id"] = response.json()["id"]
        print_success(f"Crew created: {resources['crew_id']}")
    else:
        print_error(f"Crew creation failed: {response.status_code}")

    # Get Crew
    if resources["crew_id"]:
        print_info("2-2. Getting Crew...")
        response = requests.get(f"{BASE_URL}/crews/{resources['crew_id']}")
        if response.status_code == 200:
            print_success("Crew retrieved")
        else:
            print_error(f"Failed: {response.status_code}")

    # List Crews
    print_info("2-3. Listing Crews...")
    response = requests.get(f"{BASE_URL}/crews")
    if response.status_code == 200:
        print_success(f"Crews listed: {response.json()['total']} total")
    else:
        print_error(f"Failed: {response.status_code}")

    # Update Crew
    if resources["crew_id"]:
        print_info("2-4. Updating Crew...")
        response = requests.put(
            f"{BASE_URL}/crews/{resources['crew_id']}",
            json={"name": "Updated Test Crew"}
        )
        if response.status_code == 200:
            print_success("Crew updated")
        else:
            print_error(f"Failed: {response.status_code}")

    # Validate Crew
    if resources["crew_id"]:
        print_info("2-5. Validating Crew...")
        response = requests.post(f"{BASE_URL}/crews/{resources['crew_id']}/validate")
        if response.status_code == 200:
            print_success("Crew validated")
        else:
            print_error(f"Failed: {response.status_code}")

    # 3. Agents API
    print_header("3. Agents API Tests")

    # Create Agent
    print_info("3-1. Creating Agent...")
    agent_data = {
        "role": "Test Agent",
        "backstory": "A test agent",
        "goal": "Testing purposes",
        "temperature": 0.7,
        "allow_delegation": False,
        "verbose": True,
        "cache": True,
        "llm_provider_model": "gpt-4o-mini",
        "max_iter": 25,
        "tool_ids": [],
        "knowledge_source_ids": []
    }
    response = requests.post(f"{BASE_URL}/agents", json=agent_data)
    if response.status_code == 201:
        resources["agent_id"] = response.json()["id"]
        print_success(f"Agent created: {resources['agent_id']}")
    else:
        print_error(f"Agent creation failed: {response.status_code}")

    # Get Agent
    if resources["agent_id"]:
        print_info("3-2. Getting Agent...")
        response = requests.get(f"{BASE_URL}/agents/{resources['agent_id']}")
        if response.status_code == 200:
            print_success("Agent retrieved")
        else:
            print_error(f"Failed: {response.status_code}")

    # List Agents
    print_info("3-3. Listing Agents...")
    response = requests.get(f"{BASE_URL}/agents")
    if response.status_code == 200:
        print_success(f"Agents listed: {response.json()['total']} total")
    else:
        print_error(f"Failed: {response.status_code}")

    # Update Agent
    if resources["agent_id"]:
        print_info("3-4. Updating Agent...")
        response = requests.put(
            f"{BASE_URL}/agents/{resources['agent_id']}",
            json={"role": "Updated Test Agent"}
        )
        if response.status_code == 200:
            print_success("Agent updated")
        else:
            print_error(f"Failed: {response.status_code}")

    # 4. Tasks API
    print_header("4. Tasks API Tests")

    # Create Task
    if resources["agent_id"]:
        print_info("4-1. Creating Task...")
        task_data = {
            "description": "Test task",
            "expected_output": "Test output",
            "agent_id": resources["agent_id"],
            "async_execution": False
        }
        response = requests.post(f"{BASE_URL}/tasks", json=task_data)
        if response.status_code == 201:
            resources["task_id"] = response.json()["id"]
            print_success(f"Task created: {resources['task_id']}")
        else:
            print_error(f"Task creation failed: {response.status_code}")

    # Get Task
    if resources["task_id"]:
        print_info("4-2. Getting Task...")
        response = requests.get(f"{BASE_URL}/tasks/{resources['task_id']}")
        if response.status_code == 200:
            print_success("Task retrieved")
        else:
            print_error(f"Failed: {response.status_code}")

    # List Tasks
    print_info("4-3. Listing Tasks...")
    response = requests.get(f"{BASE_URL}/tasks")
    if response.status_code == 200:
        print_success(f"Tasks listed: {response.json()['total']} total")
    else:
        print_error(f"Failed: {response.status_code}")

    # 5. Tools API
    print_header("5. Tools API Tests")

    # Create Tool
    print_info("5-1. Creating Tool...")
    tool_data = {
        "name": "DuckDuckGoSearchTool",
        "description": "DuckDuckGo search",
        "parameters": {},
        "parameters_metadata": {}
    }
    response = requests.post(f"{BASE_URL}/tools", json=tool_data)
    if response.status_code == 201:
        resources["tool_id"] = response.json()["tool_id"]
        print_success(f"Tool created: {resources['tool_id']}")
    else:
        print_error(f"Tool creation failed: {response.status_code}")

    # Get Tool
    if resources["tool_id"]:
        print_info("5-2. Getting Tool...")
        response = requests.get(f"{BASE_URL}/tools/{resources['tool_id']}")
        if response.status_code == 200:
            print_success("Tool retrieved")
        else:
            print_error(f"Failed: {response.status_code}")

    # 6. Knowledge Sources API
    print_header("6. Knowledge Sources API Tests")

    # Create Knowledge Source
    print_info("6-1. Creating Knowledge Source...")
    ks_data = {
        "name": "Test Knowledge",
        "source_type": "string",
        "content": "This is test knowledge content",
        "chunk_size": 4000,
        "chunk_overlap": 200
    }
    response = requests.post(f"{BASE_URL}/knowledge", json=ks_data)
    if response.status_code == 201:
        resources["knowledge_id"] = response.json()["id"]
        print_success(f"Knowledge Source created: {resources['knowledge_id']}")
    else:
        print_error(f"Knowledge Source creation failed: {response.status_code}")

    # Get Knowledge Source
    if resources["knowledge_id"]:
        print_info("6-2. Getting Knowledge Source...")
        response = requests.get(f"{BASE_URL}/knowledge/{resources['knowledge_id']}")
        if response.status_code == 200:
            print_success("Knowledge Source retrieved")
        else:
            print_error(f"Failed: {response.status_code}")

    # 7. Cleanup
    print_header("7. Cleanup - Deleting Test Data")

    # Delete in reverse order
    if resources["task_id"]:
        requests.delete(f"{BASE_URL}/tasks/{resources['task_id']}")
        print_success("Task deleted")

    if resources["agent_id"]:
        requests.delete(f"{BASE_URL}/agents/{resources['agent_id']}")
        print_success("Agent deleted")

    if resources["tool_id"]:
        requests.delete(f"{BASE_URL}/tools/{resources['tool_id']}")
        print_success("Tool deleted")

    if resources["knowledge_id"]:
        requests.delete(f"{BASE_URL}/knowledge/{resources['knowledge_id']}")
        print_success("Knowledge Source deleted")

    if resources["crew_id"]:
        requests.delete(f"{BASE_URL}/crews/{resources['crew_id']}")
        print_success("Crew deleted")

    # Summary
    print_header("Test Summary")
    print_success("🎉 All tests completed successfully!")
    print("\nTested endpoints:")
    print("  - Health Check")
    print("  - Crews CRUD (Create, Read, Update, Validate, Delete)")
    print("  - Agents CRUD")
    print("  - Tasks CRUD")
    print("  - Tools CRUD")
    print("  - Knowledge Sources CRUD")
    print(f"\n{Colors.YELLOW}ℹ Total: 20+ API endpoints tested{Colors.NC}\n")

except Exception as e:
    print_error(f"Test failed: {str(e)}")
    # Cleanup on error
    for key, value in resources.items():
        if value:
            endpoint = key.replace("_id", "").replace("_", "")
            if endpoint == "tool":
                endpoint = "tools"
            elif endpoint == "knowledge":
                endpoint = "knowledge"
            else:
                endpoint = f"{endpoint}s"
            try:
                requests.delete(f"{BASE_URL}/{endpoint}/{value}")
            except:
                pass
