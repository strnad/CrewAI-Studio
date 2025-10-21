"""
Crews API 전용 테스트 스크립트
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

# 색상
class C:
    G = '\033[0;32m'  # Green
    R = '\033[0;31m'  # Red
    Y = '\033[1;33m'  # Yellow
    B = '\033[0;34m'  # Blue
    N = '\033[0m'     # No Color

def header(text):
    print(f"\n{C.B}{'='*50}{C.N}")
    print(f"{C.B}{text}{C.N}")
    print(f"{C.B}{'='*50}{C.N}\n")

def success(text):
    print(f"{C.G}✓ {text}{C.N}")

def error(text):
    print(f"{C.R}✗ {text}{C.N}")

def info(text):
    print(f"{C.Y}→ {text}{C.N}")

def show_response(resp):
    """응답 출력"""
    print(f"Status: {resp.status_code}")
    try:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except:
        print(resp.text)

header("Crews API Tests")
print(f"Base URL: {BASE_URL}")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

crew_id = None

try:
    # 1. Health Check
    info("1. Health Check")
    r = requests.get(f"{BASE_URL}/health")
    show_response(r)
    if r.status_code == 200:
        success("Health OK")
    else:
        error("Health Failed")

    # 2. List Crews (initial)
    info("\n2. List All Crews (initial)")
    r = requests.get(f"{BASE_URL}/crews")
    show_response(r)

    # 3. Create Crew
    info("\n3. Create New Crew")
    crew_data = {
        "name": "Marketing Team",
        "agent_ids": [],
        "task_ids": [],
        "process": "sequential",
        "verbose": True,
        "cache": True,
        "max_rpm": 1000,
        "memory": False,
        "planning": False
    }

    r = requests.post(f"{BASE_URL}/crews", json=crew_data)
    show_response(r)

    if r.status_code in [200, 201]:
        crew_id = r.json().get("id")
        success(f"Crew Created: {crew_id}")
    else:
        error("Crew Creation Failed")

    # 4. Get Crew by ID
    if crew_id:
        info(f"\n4. Get Crew by ID: {crew_id}")
        r = requests.get(f"{BASE_URL}/crews/{crew_id}")
        show_response(r)
        if r.status_code == 200:
            success("Crew Retrieved")
        else:
            error("Crew Retrieval Failed")

    # 5. Update Crew
    if crew_id:
        info(f"\n5. Update Crew: {crew_id}")
        r = requests.put(
            f"{BASE_URL}/crews/{crew_id}",
            json={"name": "Updated Marketing Team", "verbose": False}
        )
        show_response(r)
        if r.status_code == 200:
            success("Crew Updated")
        else:
            error("Crew Update Failed")

    # 6. Validate Crew
    if crew_id:
        info(f"\n6. Validate Crew: {crew_id}")
        r = requests.post(f"{BASE_URL}/crews/{crew_id}/validate")
        show_response(r)
        if r.status_code == 200:
            success("Crew Validated")
        else:
            error("Crew Validation Failed")

    # 7. List Crews (should include our crew)
    info("\n7. List All Crews (should include new crew)")
    r = requests.get(f"{BASE_URL}/crews")
    show_response(r)

    # 8. Error Cases
    header("Error Cases")

    info("8-1. Get Non-existent Crew (404)")
    r = requests.get(f"{BASE_URL}/crews/non-existent-id")
    if r.status_code == 404:
        success("Correctly returned 404")
    else:
        error(f"Expected 404, got {r.status_code}")
    show_response(r)

    info("\n8-2. Create Crew with Missing Fields (422)")
    r = requests.post(f"{BASE_URL}/crews", json={"agent_ids": []})
    if r.status_code == 422:
        success("Correctly returned 422")
    else:
        error(f"Expected 422, got {r.status_code}")
    show_response(r)

    # 9. Delete Crew
    if crew_id:
        info(f"\n9. Delete Crew: {crew_id}")
        r = requests.delete(f"{BASE_URL}/crews/{crew_id}")
        if r.status_code in [200, 204]:
            success("Crew Deleted")
        else:
            error("Crew Deletion Failed")
        print(f"Status: {r.status_code}")

        # 10. Verify Deletion
        info(f"\n10. Verify Deletion (should return 404)")
        r = requests.get(f"{BASE_URL}/crews/{crew_id}")
        if r.status_code == 404:
            success("Correctly returned 404 after deletion")
        else:
            error(f"Expected 404, got {r.status_code}")
        show_response(r)

    header("Tests Completed")
    success("All Crews API tests finished!")

except requests.exceptions.ConnectionError:
    error(f"\nCould not connect to {BASE_URL}")
    info("Make sure the server is running:")
    info("  cd bend && python run.py")
except Exception as e:
    error(f"\nError: {str(e)}")
