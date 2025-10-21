"""
Crews API 상세 테스트
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
    print(f"\n{Colors.BLUE}=== {text} ==={Colors.NC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.NC}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.NC}")

print_header("Crews API Tests")

crew_id = None

try:
    # 1. Health Check
    print_info("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}\n")

    # 2. List all crews (initial)
    print_info("2. List all crews (초기 상태)")
    response = requests.get(f"{BASE_URL}/crews")
    print(json.dumps(response.json(), indent=2))

    # 3. Create new crew
    print_info("3. Creating new crew...")
    crew_data = {
        "name": "Marketing Team",
        "agent_ids": [],
        "task_ids": [],
        "process": "sequential",
        "verbose": True,
        "cache": True,
        "max_rpm": 1000,
        "memory": False,
        "planning": False,
        "knowledge_source_ids": []
    }
    response = requests.post(f"{BASE_URL}/crews", json=crew_data)

    if response.status_code == 201:
        crew_id = response.json()["id"]
        print_success(f"Crew created: {crew_id}")
        print(json.dumps(response.json(), indent=2))
    else:
        print_error(f"Failed: {response.status_code}")
        print(response.text)
        exit(1)

    # 4. Get specific crew
    print_info(f"4. Getting crew by ID: {crew_id}")
    response = requests.get(f"{BASE_URL}/crews/{crew_id}")
    print(json.dumps(response.json(), indent=2))

    # 5. Update crew
    print_info("5. Updating crew name...")
    response = requests.put(
        f"{BASE_URL}/crews/{crew_id}",
        json={"name": "Updated Marketing Team", "verbose": False}
    )
    print(json.dumps(response.json(), indent=2))
    print_success("Crew updated")

    # 6. Validate crew
    print_info("6. Validating crew...")
    response = requests.post(f"{BASE_URL}/crews/{crew_id}/validate")
    print(json.dumps(response.json(), indent=2))

    # 7. List all crews (should show our crew)
    print_info("7. List all crews (생성된 crew 포함)")
    response = requests.get(f"{BASE_URL}/crews")
    print(json.dumps(response.json(), indent=2))

    # 8. Test error cases
    print_info("8. Testing error cases...")

    print_info("8-1. Get non-existent crew (404 예상)")
    response = requests.get(f"{BASE_URL}/crews/non-existent-id")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

    print_info("8-2. Create crew with missing fields (400 예상)")
    response = requests.post(f"{BASE_URL}/crews", json={"agent_ids": []})
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

    # 9. Delete crew
    print_info("9. Deleting crew...")
    response = requests.delete(f"{BASE_URL}/crews/{crew_id}")
    print_success(f"Crew deleted: {crew_id}")
    print(f"Status: {response.status_code}")

    # 10. Verify deletion
    print_info("10. Verifying deletion (404 예상)")
    response = requests.get(f"{BASE_URL}/crews/{crew_id}")
    print(f"Status: {response.status_code}")

    print_header("Tests Completed")
    print_success("🎉 All Crews API tests finished!")

except Exception as e:
    print_error(f"Test failed: {str(e)}")
    # Cleanup
    if crew_id:
        try:
            requests.delete(f"{BASE_URL}/crews/{crew_id}")
            print_info("Cleanup: Crew deleted")
        except:
            pass
