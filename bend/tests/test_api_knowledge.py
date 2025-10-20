"""
Knowledge Sources API Test Script
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


def test_knowledge_sources_crud():
    """Test Knowledge Sources CRUD operations"""
    print_header("Knowledge Sources CRUD Operations")

    # 1. Create a string-based knowledge source
    print_request("POST", "/api/knowledge", {
        "name": "AI Research Knowledge",
        "source_type": "string",
        "content": "Artificial Intelligence is the simulation of human intelligence by machines.",
        "metadata": {"category": "research"},
        "chunk_size": 4000,
        "chunk_overlap": 200
    })

    response = requests.post(f"{BASE_URL}/knowledge", json={
        "name": "AI Research Knowledge",
        "source_type": "string",
        "content": "Artificial Intelligence is the simulation of human intelligence by machines.",
        "metadata": {"category": "research"},
        "chunk_size": 4000,
        "chunk_overlap": 200
    })
    print_response(response)

    if response.status_code == 201:
        ks_id = response.json()['id']
        print(f"{Colors.OKGREEN}✓ Created knowledge source with ID: {ks_id}{Colors.ENDC}\n")

        # 2. Get the created knowledge source
        print_request("GET", f"/api/knowledge/{ks_id}")
        response = requests.get(f"{BASE_URL}/knowledge/{ks_id}")
        print_response(response)

        # 3. List all knowledge sources
        print_request("GET", "/api/knowledge")
        response = requests.get(f"{BASE_URL}/knowledge")
        print_response(response)

        # 4. Update the knowledge source
        print_request("PUT", f"/api/knowledge/{ks_id}", {
            "name": "Updated AI Research Knowledge",
            "chunk_size": 5000
        })
        response = requests.put(f"{BASE_URL}/knowledge/{ks_id}", json={
            "name": "Updated AI Research Knowledge",
            "chunk_size": 5000
        })
        print_response(response)

        # 5. Validate the knowledge source
        print_request("POST", f"/api/knowledge/{ks_id}/validate")
        response = requests.post(f"{BASE_URL}/knowledge/{ks_id}/validate")
        print_response(response)

        validation = response.json()
        if not validation['is_valid']:
            print(f"{Colors.WARNING}⚠ Validation warnings/errors:{Colors.ENDC}")
            for error in validation['errors']:
                print(f"  {Colors.FAIL}✗ {error}{Colors.ENDC}")
            for warning in validation['warnings']:
                print(f"  {Colors.WARNING}⚠ {warning}{Colors.ENDC}")
            print()

        # 6. Delete the knowledge source
        print_request("DELETE", f"/api/knowledge/{ks_id}")
        response = requests.delete(f"{BASE_URL}/knowledge/{ks_id}")
        print(f"\n{Colors.OKGREEN}Status: {response.status_code} {response.reason}{Colors.ENDC}\n")

        # 7. Verify deletion
        print_request("GET", f"/api/knowledge/{ks_id}")
        response = requests.get(f"{BASE_URL}/knowledge/{ks_id}")
        print_response(response)

        if response.status_code == 404:
            print(f"{Colors.OKGREEN}✓ Knowledge source successfully deleted{Colors.ENDC}\n")
    else:
        print(f"{Colors.FAIL}✗ Failed to create knowledge source{Colors.ENDC}\n")


def test_invalid_source_type():
    """Test knowledge source creation with invalid source type"""
    print_header("Test: Invalid Source Type")

    print_request("POST", "/api/knowledge", {
        "name": "Invalid Knowledge Source",
        "source_type": "invalid_type",
        "content": "Some content"
    })

    response = requests.post(f"{BASE_URL}/knowledge", json={
        "name": "Invalid Knowledge Source",
        "source_type": "invalid_type",
        "content": "Some content"
    })
    print_response(response)

    if response.status_code == 400:
        print(f"{Colors.OKGREEN}✓ Correctly rejected invalid source_type{Colors.ENDC}\n")
    else:
        print(f"{Colors.FAIL}✗ Should have rejected invalid source_type{Colors.ENDC}\n")


def test_string_source_without_content():
    """Test string-based knowledge source without content"""
    print_header("Test: String Source Without Content")

    # Create knowledge source without content
    ks_response = requests.post(f"{BASE_URL}/knowledge", json={
        "name": "Empty String Source",
        "source_type": "string",
        "content": "",  # Empty content
        "chunk_size": 4000,
        "chunk_overlap": 200
    })

    if ks_response.status_code == 201:
        ks_id = ks_response.json()['id']
        print(f"{Colors.OKGREEN}✓ Created knowledge source: {ks_id}{Colors.ENDC}\n")

        # Validate (should fail)
        print_request("POST", f"/api/knowledge/{ks_id}/validate")
        response = requests.post(f"{BASE_URL}/knowledge/{ks_id}/validate")
        print_response(response)

        validation = response.json()
        if not validation['is_valid']:
            print(f"{Colors.OKGREEN}✓ Correctly detected missing content{Colors.ENDC}\n")
        else:
            print(f"{Colors.FAIL}✗ Should have detected missing content{Colors.ENDC}\n")

        # Clean up
        requests.delete(f"{BASE_URL}/knowledge/{ks_id}")
        print(f"{Colors.OKBLUE}Cleaned up test knowledge source{Colors.ENDC}\n")


def test_knowledge_source_deletion_with_agent_dependency():
    """Test knowledge source deletion when used by an agent"""
    print_header("Test: Knowledge Source Deletion with Agent Dependency")

    # 1. Create a knowledge source
    ks_response = requests.post(f"{BASE_URL}/knowledge", json={
        "name": "Test Knowledge",
        "source_type": "string",
        "content": "Test content for agent dependency",
        "chunk_size": 4000,
        "chunk_overlap": 200
    })

    if ks_response.status_code == 201:
        ks_id = ks_response.json()['id']
        print(f"{Colors.OKGREEN}✓ Created knowledge source: {ks_id}{Colors.ENDC}\n")

        # 2. Create an agent using this knowledge source
        agent_response = requests.post(f"{BASE_URL}/agents", json={
            "role": "Test Agent",
            "backstory": "Testing knowledge source dependency",
            "goal": "Test validation",
            "llm_provider_model": "openai/gpt-4o-mini",
            "tool_ids": [],
            "knowledge_source_ids": [ks_id]
        })

        if agent_response.status_code == 201:
            agent_id = agent_response.json()['id']
            print(f"{Colors.OKGREEN}✓ Created agent: {agent_id}{Colors.ENDC}\n")

            # 3. Try to delete the knowledge source (should fail)
            print_request("DELETE", f"/api/knowledge/{ks_id}")
            response = requests.delete(f"{BASE_URL}/knowledge/{ks_id}")
            print_response(response)

            if response.status_code == 400:
                print(f"{Colors.OKGREEN}✓ Correctly prevented deletion (knowledge source in use by agent){Colors.ENDC}\n")
            else:
                print(f"{Colors.FAIL}✗ Should have prevented deletion{Colors.ENDC}\n")

            # Clean up
            requests.delete(f"{BASE_URL}/agents/{agent_id}")
            requests.delete(f"{BASE_URL}/knowledge/{ks_id}")
            print(f"{Colors.OKBLUE}Cleaned up test data{Colors.ENDC}\n")


def test_knowledge_source_deletion_with_crew_dependency():
    """Test knowledge source deletion when used by a crew"""
    print_header("Test: Knowledge Source Deletion with Crew Dependency")

    # 1. Create a knowledge source
    ks_response = requests.post(f"{BASE_URL}/knowledge", json={
        "name": "Test Knowledge for Crew",
        "source_type": "string",
        "content": "Test content for crew dependency",
        "chunk_size": 4000,
        "chunk_overlap": 200
    })

    if ks_response.status_code == 201:
        ks_id = ks_response.json()['id']
        print(f"{Colors.OKGREEN}✓ Created knowledge source: {ks_id}{Colors.ENDC}\n")

        # 2. Create a crew using this knowledge source
        crew_response = requests.post(f"{BASE_URL}/crews", json={
            "name": "Test Crew",
            "agent_ids": [],
            "task_ids": [],
            "process": "sequential",
            "verbose": True,
            "cache": True,
            "max_rpm": 1000,
            "memory": False,
            "planning": False,
            "knowledge_source_ids": [ks_id]
        })

        if crew_response.status_code == 201:
            crew_id = crew_response.json()['id']
            print(f"{Colors.OKGREEN}✓ Created crew: {crew_id}{Colors.ENDC}\n")

            # 3. Try to delete the knowledge source (should fail)
            print_request("DELETE", f"/api/knowledge/{ks_id}")
            response = requests.delete(f"{BASE_URL}/knowledge/{ks_id}")
            print_response(response)

            if response.status_code == 400:
                print(f"{Colors.OKGREEN}✓ Correctly prevented deletion (knowledge source in use by crew){Colors.ENDC}\n")
            else:
                print(f"{Colors.FAIL}✗ Should have prevented deletion{Colors.ENDC}\n")

            # Clean up
            requests.delete(f"{BASE_URL}/crews/{crew_id}")
            requests.delete(f"{BASE_URL}/knowledge/{ks_id}")
            print(f"{Colors.OKBLUE}Cleaned up test data{Colors.ENDC}\n")


def test_error_cases():
    """Test error handling"""
    print_header("Error Handling Tests")

    # 1. Get non-existent knowledge source
    print_request("GET", "/api/knowledge/nonexistent")
    response = requests.get(f"{BASE_URL}/knowledge/nonexistent")
    print_response(response)

    # 2. Update non-existent knowledge source
    print_request("PUT", "/api/knowledge/nonexistent", {"name": "Updated"})
    response = requests.put(f"{BASE_URL}/knowledge/nonexistent", json={"name": "Updated"})
    print_response(response)

    # 3. Delete non-existent knowledge source
    print_request("DELETE", "/api/knowledge/nonexistent")
    response = requests.delete(f"{BASE_URL}/knowledge/nonexistent")
    print_response(response)

    # 4. Validate non-existent knowledge source
    print_request("POST", "/api/knowledge/nonexistent/validate")
    response = requests.post(f"{BASE_URL}/knowledge/nonexistent/validate")
    print_response(response)


def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}CrewAI Studio - Knowledge Sources API Tests{Colors.ENDC}")
    print(f"{Colors.BOLD}Base URL: {BASE_URL}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    try:
        # Test health check first
        test_health_check()

        # Test CRUD operations
        test_knowledge_sources_crud()

        # Test invalid source type
        test_invalid_source_type()

        # Test string source without content
        test_string_source_without_content()

        # Test knowledge source deletion with agent dependency
        test_knowledge_source_deletion_with_agent_dependency()

        # Test knowledge source deletion with crew dependency
        test_knowledge_source_deletion_with_crew_dependency()

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
