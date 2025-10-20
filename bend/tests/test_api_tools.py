"""
Tools API Test Script
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


def test_tools_crud():
    """Test Tools CRUD operations"""
    print_header("Tools CRUD Operations")

    # 1. Create a tool
    print_request("POST", "/api/tools", {
        "name": "Web Scraper",
        "description": "A tool to scrape websites",
        "parameters": {
            "url": "https://example.com"
        },
        "parameters_metadata": {
            "url": {
                "mandatory": True,
                "type": "string",
                "description": "URL to scrape"
            }
        }
    })

    response = requests.post(f"{BASE_URL}/tools", json={
        "name": "Web Scraper",
        "description": "A tool to scrape websites",
        "parameters": {
            "url": "https://example.com"
        },
        "parameters_metadata": {
            "url": {
                "mandatory": True,
                "type": "string",
                "description": "URL to scrape"
            }
        }
    })
    print_response(response)

    if response.status_code == 201:
        tool_id = response.json()['tool_id']
        print(f"{Colors.OKGREEN}✓ Created tool with ID: {tool_id}{Colors.ENDC}\n")

        # 2. Get the created tool
        print_request("GET", f"/api/tools/{tool_id}")
        response = requests.get(f"{BASE_URL}/tools/{tool_id}")
        print_response(response)

        # 3. List all tools
        print_request("GET", "/api/tools")
        response = requests.get(f"{BASE_URL}/tools")
        print_response(response)

        # 4. Update the tool
        print_request("PUT", f"/api/tools/{tool_id}", {
            "name": "Advanced Web Scraper",
            "parameters": {
                "url": "https://example.com",
                "timeout": 30
            }
        })
        response = requests.put(f"{BASE_URL}/tools/{tool_id}", json={
            "name": "Advanced Web Scraper",
            "parameters": {
                "url": "https://example.com",
                "timeout": 30
            }
        })
        print_response(response)

        # 5. Validate the tool
        print_request("POST", f"/api/tools/{tool_id}/validate")
        response = requests.post(f"{BASE_URL}/tools/{tool_id}/validate")
        print_response(response)

        validation = response.json()
        if not validation['is_valid']:
            print(f"{Colors.WARNING}⚠ Validation warnings/errors:{Colors.ENDC}")
            for error in validation['errors']:
                print(f"  {Colors.FAIL}✗ {error}{Colors.ENDC}")
            for warning in validation['warnings']:
                print(f"  {Colors.WARNING}⚠ {warning}{Colors.ENDC}")
            print()

        # 6. Delete the tool
        print_request("DELETE", f"/api/tools/{tool_id}")
        response = requests.delete(f"{BASE_URL}/tools/{tool_id}")
        print(f"\n{Colors.OKGREEN}Status: {response.status_code} {response.reason}{Colors.ENDC}\n")

        # 7. Verify deletion
        print_request("GET", f"/api/tools/{tool_id}")
        response = requests.get(f"{BASE_URL}/tools/{tool_id}")
        print_response(response)

        if response.status_code == 404:
            print(f"{Colors.OKGREEN}✓ Tool successfully deleted{Colors.ENDC}\n")
    else:
        print(f"{Colors.FAIL}✗ Failed to create tool{Colors.ENDC}\n")


def test_tool_with_missing_mandatory_parameter():
    """Test tool validation with missing mandatory parameter"""
    print_header("Test: Tool with Missing Mandatory Parameter")

    # Create tool without providing required parameter value
    tool_response = requests.post(f"{BASE_URL}/tools", json={
        "name": "Test Tool",
        "description": "Tool with mandatory parameter",
        "parameters": {},  # Empty parameters
        "parameters_metadata": {
            "api_key": {
                "mandatory": True,
                "type": "string",
                "description": "API key"
            }
        }
    })

    if tool_response.status_code == 201:
        tool_id = tool_response.json()['tool_id']
        print(f"{Colors.OKGREEN}✓ Created tool: {tool_id}{Colors.ENDC}\n")

        # Validate tool (should fail)
        print_request("POST", f"/api/tools/{tool_id}/validate")
        response = requests.post(f"{BASE_URL}/tools/{tool_id}/validate")
        print_response(response)

        validation = response.json()
        if not validation['is_valid']:
            print(f"{Colors.OKGREEN}✓ Correctly detected missing mandatory parameter{Colors.ENDC}\n")
        else:
            print(f"{Colors.FAIL}✗ Should have detected missing mandatory parameter{Colors.ENDC}\n")

        # Clean up
        requests.delete(f"{BASE_URL}/tools/{tool_id}")
        print(f"{Colors.OKBLUE}Cleaned up test tool{Colors.ENDC}\n")


def test_tool_deletion_with_agent_dependency():
    """Test tool deletion when tool is used by an agent"""
    print_header("Test: Tool Deletion with Agent Dependency")

    # 1. Create a tool
    tool_response = requests.post(f"{BASE_URL}/tools", json={
        "name": "Test Tool",
        "description": "Tool for testing agent dependency",
        "parameters": {},
        "parameters_metadata": {}
    })

    if tool_response.status_code == 201:
        tool_id = tool_response.json()['tool_id']
        print(f"{Colors.OKGREEN}✓ Created tool: {tool_id}{Colors.ENDC}\n")

        # 2. Create an agent using this tool
        agent_response = requests.post(f"{BASE_URL}/agents", json={
            "role": "Test Agent",
            "backstory": "Testing tool dependency",
            "goal": "Test validation",
            "llm_provider_model": "openai/gpt-4o-mini",
            "tool_ids": [tool_id],
            "knowledge_source_ids": []
        })

        if agent_response.status_code == 201:
            agent_id = agent_response.json()['id']
            print(f"{Colors.OKGREEN}✓ Created agent: {agent_id}{Colors.ENDC}\n")

            # 3. Try to delete the tool (should fail)
            print_request("DELETE", f"/api/tools/{tool_id}")
            response = requests.delete(f"{BASE_URL}/tools/{tool_id}")
            print_response(response)

            if response.status_code == 400:
                print(f"{Colors.OKGREEN}✓ Correctly prevented deletion (tool in use by agent){Colors.ENDC}\n")
            else:
                print(f"{Colors.FAIL}✗ Should have prevented deletion{Colors.ENDC}\n")

            # Clean up
            requests.delete(f"{BASE_URL}/agents/{agent_id}")
            requests.delete(f"{BASE_URL}/tools/{tool_id}")
            print(f"{Colors.OKBLUE}Cleaned up test data{Colors.ENDC}\n")


def test_error_cases():
    """Test error handling"""
    print_header("Error Handling Tests")

    # 1. Get non-existent tool
    print_request("GET", "/api/tools/nonexistent")
    response = requests.get(f"{BASE_URL}/tools/nonexistent")
    print_response(response)

    # 2. Update non-existent tool
    print_request("PUT", "/api/tools/nonexistent", {"name": "Updated"})
    response = requests.put(f"{BASE_URL}/tools/nonexistent", json={"name": "Updated"})
    print_response(response)

    # 3. Delete non-existent tool
    print_request("DELETE", "/api/tools/nonexistent")
    response = requests.delete(f"{BASE_URL}/tools/nonexistent")
    print_response(response)

    # 4. Validate non-existent tool
    print_request("POST", "/api/tools/nonexistent/validate")
    response = requests.post(f"{BASE_URL}/tools/nonexistent/validate")
    print_response(response)


def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}CrewAI Studio - Tools API Tests{Colors.ENDC}")
    print(f"{Colors.BOLD}Base URL: {BASE_URL}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    try:
        # Test health check first
        test_health_check()

        # Test CRUD operations
        test_tools_crud()

        # Test tool validation
        test_tool_with_missing_mandatory_parameter()

        # Test tool deletion with agent dependency
        test_tool_deletion_with_agent_dependency()

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
