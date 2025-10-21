"""
Users API Test Script
사용자 API 테스트 (curl 방식)
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

print_header("Users API Tests")

user_id = None

try:
    # 1. 회원가입 (Register)
    print_info("1. 회원가입 (Register)")
    register_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/users/register", json=register_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 201:
        user = response.json()
        user_id = user["id"]
        print_success(f"User registered: {user_id}")
        print(json.dumps(user, indent=2))
    else:
        print_error(f"Registration failed: {response.status_code}")
        print(response.text)

    # 2. 로그인 (Login)
    print_info("2. 로그인 (Login)")
    login_data = {
        "email": "test@example.com",
        "password": "securepassword123"
    }
    response = requests.post(f"{BASE_URL}/users/login", json=login_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        user = response.json()
        print_success("Login successful")
        print(json.dumps(user, indent=2))
    else:
        print_error(f"Login failed: {response.status_code}")
        print(response.text)

    # 3. 사용자 조회 (Get User)
    if user_id:
        print_info(f"3. 사용자 조회 (Get User): {user_id}")
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print_success("User retrieved")
            print(json.dumps(response.json(), indent=2))
        else:
            print_error(f"Failed: {response.status_code}")
            print(response.text)

    # 4. 사용자 정보 업데이트 (Update User)
    if user_id:
        print_info("4. 사용자 정보 업데이트 (Update User)")
        update_data = {
            "name": "Updated Test User"
        }
        response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print_success("User updated")
            print(json.dumps(response.json(), indent=2))
        else:
            print_error(f"Failed: {response.status_code}")
            print(response.text)

    # 5. 잘못된 비밀번호로 로그인 (Negative Test)
    print_info("5. 잘못된 비밀번호로 로그인 (Expected: 401)")
    wrong_login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/users/login", json=wrong_login_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 401:
        print_success("Correctly rejected invalid password")
    else:
        print_error(f"Unexpected status: {response.status_code}")

    # 6. 존재하지 않는 사용자 조회 (Negative Test)
    print_info("6. 존재하지 않는 사용자 조회 (Expected: 404)")
    response = requests.get(f"{BASE_URL}/users/nonexistent_id")
    print(f"Status: {response.status_code}")

    if response.status_code == 404:
        print_success("Correctly returned 404 for nonexistent user")
    else:
        print_error(f"Unexpected status: {response.status_code}")

    # 7. 이메일 중복 테스트 (Negative Test)
    print_info("7. 이메일 중복 회원가입 (Expected: 400)")
    duplicate_data = {
        "email": "test@example.com",  # 이미 등록된 이메일
        "password": "anotherpassword",
        "name": "Another User"
    }
    response = requests.post(f"{BASE_URL}/users/register", json=duplicate_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 400:
        print_success("Correctly rejected duplicate email")
        print(json.dumps(response.json(), indent=2))
    else:
        print_error(f"Unexpected status: {response.status_code}")

    # 8. 사용자 삭제 (Delete User)
    if user_id:
        print_info("8. 사용자 삭제 (Delete User)")
        response = requests.delete(f"{BASE_URL}/users/{user_id}")
        print(f"Status: {response.status_code}")

        if response.status_code == 204:
            print_success(f"User deleted: {user_id}")
        else:
            print_error(f"Failed: {response.status_code}")
            print(response.text)

    # 9. 삭제된 사용자 조회 (Negative Test)
    if user_id:
        print_info("9. 삭제된 사용자 조회 (Expected: 404)")
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        print(f"Status: {response.status_code}")

        if response.status_code == 404:
            print_success("Correctly returned 404 for deleted user")
        else:
            print_error(f"Unexpected status: {response.status_code}")

    print_header("Tests Completed")
    print_success("🎉 All Users API tests finished!")

except Exception as e:
    print_error(f"Test failed: {str(e)}")
    # Cleanup
    if user_id:
        try:
            requests.delete(f"{BASE_URL}/users/{user_id}")
            print_info("Cleanup: User deleted")
        except:
            pass
