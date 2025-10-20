"""
Crews API Test Script
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

    # Detailed health check
    print_request("GET", "/api/health/detailed")
    response = requests.get(f"{BASE_URL}/health/detailed")
    print_response(response)


def test_crews_crud():
    """Test Crews CRUD operations"""
    print_header("Crews CRUD Operations")

    # 1. Create a crew (empty - should work)
    print_request("POST", "/api/crews", {
        "name": "Test Crew 1",
        "agent_ids": [],
        "task_ids": [],
        "process": "sequential",
        "verbose": True,
        "cache": True,
        "max_rpm": 1000,
        "memory": False,
        "planning": False,
        "knowledge_source_ids": []
    })

    response = requests.post(f"{BASE_URL}/crews", json={
        "name": "Test Crew 1",
        "agent_ids": [],
        "task_ids": [],
        "process": "sequential",
        "verbose": True,
        "cache": True,
        "max_rpm": 1000,
        "memory": False,
        "planning": False,
        "knowledge_source_ids": []
    })
    print_response(response)

    if response.status_code == 201:
        crew_id = response.json()['id']
        print(f"{Colors.OKGREEN}✓ Created crew with ID: {crew_id}{Colors.ENDC}\n")

        # 2. Get the created crew
        print_request("GET", f"/api/crews/{crew_id}")
        response = requests.get(f"{BASE_URL}/crews/{crew_id}")
        print_response(response)

        # 3. List all crews
        print_request("GET", "/api/crews")
        response = requests.get(f"{BASE_URL}/crews")
        print_response(response)

        # 4. Update the crew
        print_request("PUT", f"/api/crews/{crew_id}", {
            "name": "Updated Crew Name",
            "verbose": False
        })
        response = requests.put(f"{BASE_URL}/crews/{crew_id}", json={
            "name": "Updated Crew Name",
            "verbose": False
        })
        print_response(response)

        # 5. Validate the crew
        print_request("POST", f"/api/crews/{crew_id}/validate")
        response = requests.post(f"{BASE_URL}/crews/{crew_id}/validate")
        print_response(response)

        validation = response.json()
        if not validation['is_valid']:
            print(f"{Colors.WARNING}⚠ Validation warnings/errors:{Colors.ENDC}")
            for error in validation['errors']:
                print(f"  {Colors.FAIL}✗ {error}{Colors.ENDC}")
            for warning in validation['warnings']:
                print(f"  {Colors.WARNING}⚠ {warning}{Colors.ENDC}")
            print()

        # 6. Delete the crew
        print_request("DELETE", f"/api/crews/{crew_id}")
        response = requests.delete(f"{BASE_URL}/crews/{crew_id}")
        print(f"\n{Colors.OKGREEN}Status: {response.status_code} {response.reason}{Colors.ENDC}\n")

        # 7. Verify deletion
        print_request("GET", f"/api/crews/{crew_id}")
        response = requests.get(f"{BASE_URL}/crews/{crew_id}")
        print_response(response)

        if response.status_code == 404:
            print(f"{Colors.OKGREEN}✓ Crew successfully deleted{Colors.ENDC}\n")
    else:
        print(f"{Colors.FAIL}✗ Failed to create crew{Colors.ENDC}\n")


def test_error_cases():
    """Test error handling"""
    print_header("Error Handling Tests")

    # 1. Get non-existent crew
    print_request("GET", "/api/crews/nonexistent")
    response = requests.get(f"{BASE_URL}/crews/nonexistent")
    print_response(response)

    # 2. Create crew with invalid agent IDs
    print_request("POST", "/api/crews", {
        "name": "Invalid Crew",
        "agent_ids": ["invalid_agent_id"],
        "task_ids": [],
    })
    response = requests.post(f"{BASE_URL}/crews", json={
        "name": "Invalid Crew",
        "agent_ids": ["invalid_agent_id"],
        "task_ids": [],
    })
    print_response(response)

    # 3. Update non-existent crew
    print_request("PUT", "/api/crews/nonexistent", {"name": "Updated"})
    response = requests.put(f"{BASE_URL}/crews/nonexistent", json={"name": "Updated"})
    print_response(response)

    # 4. Delete non-existent crew
    print_request("DELETE", "/api/crews/nonexistent")
    response = requests.delete(f"{BASE_URL}/crews/nonexistent")
    print_response(response)


def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}CrewAI Studio - Crews API Tests{Colors.ENDC}")
    print(f"{Colors.BOLD}Base URL: {BASE_URL}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    try:
        # Test health check first
        test_health_check()

        # Test CRUD operations
        test_crews_crud()

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
