"""
Workspace API Tests
curl-style 테스트 스크립트
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def print_success(message):
    print(f"✓ {message}")

def print_error(message):
    print(f"✗ {message}")

def print_info(message):
    print(f"ℹ {message}")

print("\n=== Workspaces API Tests ===\n")

# Test 사용자 생성 (워크스페이스 테스트용)
print_info("0. 테스트 사용자 생성")

user1_data = {
    "email": "workspace_owner@example.com",
    "password": "password123",
    "name": "Workspace Owner"
}
response = requests.post(f"{BASE_URL}/users/register", json=user1_data)
if response.status_code == 201:
    owner_id = response.json()["id"]
    print_success(f"Test user created: {owner_id}")
else:
    print_error(f"Failed to create test user: {response.status_code}")
    exit(1)

print()

# 1. 워크스페이스 생성 (slug 자동 생성)
print_info("1. 워크스페이스 생성 (slug 자동 생성)")
workspace_data = {
    "name": "My Test Workspace",
    "owner_id": owner_id,
    "description": "This is a test workspace"
}
response = requests.post(f"{BASE_URL}/workspaces/", json=workspace_data)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    workspace = response.json()
    workspace_id = workspace["id"]
    workspace_slug = workspace["slug"]
    print_success(f"Workspace created: {workspace_id} (slug: {workspace_slug})")
    print(json.dumps(workspace, indent=2))
else:
    print_error(f"Workspace creation failed: {response.status_code}")
    print(response.text)
    exit(1)

print()

# 2. 워크스페이스 생성 (커스텀 slug)
print_info("2. 워크스페이스 생성 (커스텀 slug)")
workspace_data2 = {
    "name": "Marketing Team",
    "owner_id": owner_id,
    "description": "Marketing team workspace",
    "slug": "marketing-team"
}
response = requests.post(f"{BASE_URL}/workspaces/", json=workspace_data2)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    workspace2 = response.json()
    workspace2_id = workspace2["id"]
    print_success(f"Workspace created with custom slug: {workspace2['slug']}")
else:
    print_error(f"Failed: {response.status_code}")

print()

# 3. 워크스페이스 조회 (ID로)
print_info(f"3. 워크스페이스 조회 (Get by ID): {workspace_id}")
response = requests.get(f"{BASE_URL}/workspaces/{workspace_id}")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print_success("Workspace retrieved")
    print(json.dumps(response.json(), indent=2))
else:
    print_error(f"Failed: {response.status_code}")

print()

# 4. 워크스페이스 조회 (slug로)
print_info(f"4. 워크스페이스 조회 (Get by slug): {workspace_slug}")
response = requests.get(f"{BASE_URL}/workspaces/slug/{workspace_slug}")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print_success("Workspace retrieved by slug")
    print(json.dumps(response.json(), indent=2))
else:
    print_error(f"Failed: {response.status_code}")

print()

# 5. 사용자의 워크스페이스 목록 조회
print_info("5. 사용자의 워크스페이스 목록 조회")
response = requests.get(f"{BASE_URL}/workspaces/", params={"user_id": owner_id})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    workspaces = response.json()
    print_success(f"User workspaces retrieved: {len(workspaces)} workspaces")
    for ws in workspaces:
        print(f"  - {ws['name']} ({ws['slug']})")
else:
    print_error(f"Failed: {response.status_code}")

print()

# 6. 워크스페이스 업데이트
print_info("6. 워크스페이스 업데이트")
update_data = {
    "name": "Updated Test Workspace",
    "description": "This workspace has been updated"
}
response = requests.put(f"{BASE_URL}/workspaces/{workspace_id}", json=update_data)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print_success("Workspace updated")
    updated = response.json()
    print(f"  New name: {updated['name']}")
    print(f"  New description: {updated['description']}")
else:
    print_error(f"Failed: {response.status_code}")

print()

# 7. 중복 slug로 생성 시도 (Expected: 400)
print_info("7. 중복 slug로 생성 시도 (Expected: 400)")
duplicate_data = {
    "name": "Another Workspace",
    "owner_id": owner_id,
    "slug": workspace_slug
}
response = requests.post(f"{BASE_URL}/workspaces/", json=duplicate_data)
print(f"Status: {response.status_code}")
if response.status_code == 400:
    print_success("Correctly rejected duplicate slug")
    print(json.dumps(response.json(), indent=2))
else:
    print_error(f"Unexpected status: {response.status_code}")

print()

# 8. 존재하지 않는 워크스페이스 조회 (Expected: 404)
print_info("8. 존재하지 않는 워크스페이스 조회 (Expected: 404)")
response = requests.get(f"{BASE_URL}/workspaces/WS_nonexistent")
print(f"Status: {response.status_code}")
if response.status_code == 404:
    print_success("Correctly returned 404 for nonexistent workspace")
else:
    print_error(f"Unexpected status: {response.status_code}")

print()

# 9. 워크스페이스 삭제
print_info(f"9. 워크스페이스 삭제 (Delete): {workspace_id}")
response = requests.delete(f"{BASE_URL}/workspaces/{workspace_id}")
print(f"Status: {response.status_code}")
if response.status_code == 204:
    print_success(f"Workspace deleted: {workspace_id}")
else:
    print_error(f"Failed: {response.status_code}")

print()

# 10. 삭제된 워크스페이스 조회 (Expected: 404)
print_info("10. 삭제된 워크스페이스 조회 (Expected: 404)")
response = requests.get(f"{BASE_URL}/workspaces/{workspace_id}")
print(f"Status: {response.status_code}")
if response.status_code == 404:
    print_success("Correctly returned 404 for deleted workspace")
else:
    print_error(f"Unexpected status: {response.status_code}")

print()

# Cleanup: 두 번째 워크스페이스 삭제
print_info("Cleanup: 두 번째 워크스페이스 삭제")
response = requests.delete(f"{BASE_URL}/workspaces/{workspace2_id}")
if response.status_code == 204:
    print_success("Cleanup successful")

# Cleanup: 테스트 사용자 삭제
response = requests.delete(f"{BASE_URL}/users/{owner_id}")

print("\n=== Tests Completed ===\n")
print_success("🎉 All Workspaces API tests finished!")
