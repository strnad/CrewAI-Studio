"""
CrewAI Studio - API 전체 테스트 스크립트
모든 API 엔드포인트를 테스트합니다.
"""
import requests
import sys
from datetime import datetime
from typing import Optional, Dict, Any

# 색상 코드
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color

# 설정
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api"

# 테스트 결과 저장
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}

# 생성된 리소스 ID 저장
resources = {
    "crew_id": None,
    "agent_id": None,
    "task_id": None,
    "tool_id": None,
    "knowledge_id": None
}


def print_header(text: str):
    """헤더 출력"""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")


def print_success(text: str):
    """성공 메시지"""
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")


def print_error(text: str):
    """에러 메시지"""
    print(f"{Colors.RED}✗ {text}{Colors.NC}")


def print_info(text: str):
    """정보 메시지"""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.NC}")


def print_response(response: requests.Response, show_body: bool = True):
    """응답 정보 출력"""
    status_color = Colors.GREEN if response.status_code < 300 else Colors.RED
    print(f"{status_color}Status: {response.status_code}{Colors.NC}")

    if show_body:
        try:
            body = response.json()
            import json
            print(f"{Colors.CYAN}Response:{Colors.NC}")
            print(json.dumps(body, indent=2, ensure_ascii=False))
        except:
            print(f"{Colors.CYAN}Response:{Colors.NC}")
            print(response.text[:500])


def test_request(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    expected_status: int = 200,
    description: str = ""
) -> Optional[Dict[str, Any]]:
    """API 요청 테스트"""
    url = f"{BASE_URL}{API_PREFIX}{endpoint}"

    print(f"\n{Colors.CYAN}{method} {API_PREFIX}{endpoint}{Colors.NC}")
    if description:
        print(f"{Colors.MAGENTA}→ {description}{Colors.NC}")

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            print_error(f"Unknown method: {method}")
            return None

        print_response(response)

        # 상태 코드 검증
        if response.status_code == expected_status:
            print_success(f"Expected status {expected_status} ✓")
            test_results["passed"] += 1
            return response.json() if response.text else None
        else:
            print_error(f"Expected {expected_status}, got {response.status_code}")
            test_results["failed"] += 1
            test_results["errors"].append({
                "endpoint": endpoint,
                "expected": expected_status,
                "actual": response.status_code
            })
            return None

    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to {BASE_URL}")
        print_info("Make sure the server is running: cd bend && python run.py")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        test_results["failed"] += 1
        return None


def main():
    """메인 테스트 실행"""
    print_header("CrewAI Studio - API Tests")
    print(f"Base URL: {BASE_URL}{API_PREFIX}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ============================================================
    # 1. Health Check
    # ============================================================
    print_header("1. Health Check")
    test_request("GET", "/health", description="Basic health check")

    # ============================================================
    # 2. Crews API
    # ============================================================
    print_header("2. Crews API Tests")

    # 2-1. Create Crew
    crew_data = {
        "name": "Test Crew",
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

    result = test_request(
        "POST", "/crews",
        data=crew_data,
        expected_status=201,
        description="Create new crew"
    )

    if result and "id" in result:
        resources["crew_id"] = result["id"]
        print_info(f"Created Crew ID: {resources['crew_id']}")

    # 2-2. Get Crew
    if resources["crew_id"]:
        test_request(
            "GET", f"/crews/{resources['crew_id']}",
            description="Get crew by ID"
        )

    # 2-3. List Crews
    test_request("GET", "/crews", description="List all crews")

    # 2-4. Update Crew
    if resources["crew_id"]:
        test_request(
            "PUT", f"/crews/{resources['crew_id']}",
            data={"name": "Updated Test Crew"},
            description="Update crew name"
        )

    # 2-5. Validate Crew
    if resources["crew_id"]:
        test_request(
            "POST", f"/crews/{resources['crew_id']}/validate",
            description="Validate crew"
        )

    # 2-6. Execute Crew (will be tested after agents and tasks are created)
    # Placeholder - will test after creating agents and tasks

    # ============================================================
    # 3. Agents API
    # ============================================================
    print_header("3. Agents API Tests")

    # 3-1. Create Agent
    agent_data = {
        "role": "Test Agent",
        "backstory": "A test agent for API testing",
        "goal": "Test all API endpoints",
        "temperature": 0.7,
        "allow_delegation": False,
        "verbose": True,
        "cache": True,
        "llm_provider_model": "gpt-4",
        "max_iter": 25,
        "tool_ids": [],
        "knowledge_source_ids": []
    }

    result = test_request(
        "POST", "/agents",
        data=agent_data,
        expected_status=201,
        description="Create new agent"
    )

    if result and "id" in result:
        resources["agent_id"] = result["id"]
        print_info(f"Created Agent ID: {resources['agent_id']}")

    # 3-2. Get Agent
    if resources["agent_id"]:
        test_request(
            "GET", f"/agents/{resources['agent_id']}",
            description="Get agent by ID"
        )

    # 3-3. List Agents
    test_request("GET", "/agents", description="List all agents")

    # 3-4. Update Agent
    if resources["agent_id"]:
        test_request(
            "PUT", f"/agents/{resources['agent_id']}",
            data={"role": "Updated Test Agent"},
            description="Update agent role"
        )

    # 3-5. Validate Agent
    if resources["agent_id"]:
        test_request(
            "POST", f"/agents/{resources['agent_id']}/validate",
            description="Validate agent"
        )

    # ============================================================
    # 4. Tasks API
    # ============================================================
    print_header("4. Tasks API Tests")

    # 4-1. Create Task
    if resources["agent_id"]:
        task_data = {
            "description": "Test task for API testing",
            "expected_output": "API test results",
            "agent_id": resources["agent_id"],
            "async_execution": False
        }

        result = test_request(
            "POST", "/tasks",
            data=task_data,
            expected_status=201,
            description="Create new task"
        )

        if result and "id" in result:
            resources["task_id"] = result["id"]
            print_info(f"Created Task ID: {resources['task_id']}")

    # 4-2. Get Task
    if resources["task_id"]:
        test_request(
            "GET", f"/tasks/{resources['task_id']}",
            description="Get task by ID"
        )

    # 4-3. List Tasks
    test_request("GET", "/tasks", description="List all tasks")

    # 4-4. Update Task
    if resources["task_id"]:
        test_request(
            "PUT", f"/tasks/{resources['task_id']}",
            data={"description": "Updated test task"},
            description="Update task description"
        )

    # 4-5. Validate Task
    if resources["task_id"]:
        test_request(
            "POST", f"/tasks/{resources['task_id']}/validate",
            description="Validate task"
        )

    # ============================================================
    # 5. Tools API
    # ============================================================
    print_header("5. Tools API Tests")

    # 5-1. Create Tool
    tool_data = {
        "name": "Test Tool",
        "description": "A test tool for API testing",
        "parameters": {"api_key": "test123"},
        "parameters_metadata": {
            "api_key": {"mandatory": True}
        }
    }

    result = test_request(
        "POST", "/tools",
        data=tool_data,
        expected_status=201,
        description="Create new tool"
    )

    if result and "tool_id" in result:
        resources["tool_id"] = result["tool_id"]
        print_info(f"Created Tool ID: {resources['tool_id']}")

    # 5-2. Get Tool
    if resources["tool_id"]:
        test_request(
            "GET", f"/tools/{resources['tool_id']}",
            description="Get tool by ID"
        )

    # 5-3. List Tools
    test_request("GET", "/tools", description="List all tools")

    # 5-4. Update Tool
    if resources["tool_id"]:
        test_request(
            "PUT", f"/tools/{resources['tool_id']}",
            data={"name": "Updated Test Tool"},
            description="Update tool name"
        )

    # 5-5. Validate Tool
    if resources["tool_id"]:
        test_request(
            "POST", f"/tools/{resources['tool_id']}/validate",
            description="Validate tool"
        )

    # ============================================================
    # 6. Knowledge Sources API
    # ============================================================
    print_header("6. Knowledge Sources API Tests")

    # 6-1. Create Knowledge Source
    knowledge_data = {
        "name": "Test Knowledge",
        "source_type": "string",
        "content": "This is test knowledge content for API testing",
        "chunk_size": 4000,
        "chunk_overlap": 200
    }

    result = test_request(
        "POST", "/knowledge",
        data=knowledge_data,
        expected_status=201,
        description="Create new knowledge source"
    )

    if result and "id" in result:
        resources["knowledge_id"] = result["id"]
        print_info(f"Created Knowledge ID: {resources['knowledge_id']}")

    # 6-2. Get Knowledge Source
    if resources["knowledge_id"]:
        test_request(
            "GET", f"/knowledge/{resources['knowledge_id']}",
            description="Get knowledge source by ID"
        )

    # 6-3. List Knowledge Sources
    test_request("GET", "/knowledge", description="List all knowledge sources")

    # 6-4. Update Knowledge Source
    if resources["knowledge_id"]:
        test_request(
            "PUT", f"/knowledge/{resources['knowledge_id']}",
            data={"name": "Updated Test Knowledge"},
            description="Update knowledge source name"
        )

    # 6-5. Validate Knowledge Source
    if resources["knowledge_id"]:
        test_request(
            "POST", f"/knowledge/{resources['knowledge_id']}/validate",
            description="Validate knowledge source"
        )

    # ============================================================
    # 7. Crew Execution API Tests (NEW)
    # ============================================================
    print_header("7. Crew Execution API Tests")

    # Update crew with agent and task for execution test
    if resources["crew_id"] and resources["agent_id"] and resources["task_id"]:
        test_request(
            "PUT", f"/crews/{resources['crew_id']}",
            data={
                "agent_ids": [resources["agent_id"]],
                "task_ids": [resources["task_id"]]
            },
            description="Update crew with agent and task for execution"
        )

    # 7-1. Execute Crew (kickoff)
    # Note: This will likely fail if OPENAI_API_KEY is not set
    # But we test the endpoint structure is correct
    if resources["crew_id"]:
        print_info("\n⚠️  Note: Crew execution may fail if LLM API keys are not configured")
        print_info("    This test validates endpoint structure, not execution success")

        result = test_request(
            "POST", f"/crews/{resources['crew_id']}/kickoff",
            data={"query": "Test execution"},
            expected_status=201,
            description="Execute crew (kickoff) - may fail without API keys"
        )

        if result and "execution_id" in result:
            resources["execution_id"] = result["execution_id"]
            print_info(f"Execution ID: {resources['execution_id']}")
            print_info(f"Execution Status: {result.get('status', 'unknown')}")

    # 7-2. Get Execution Status
    if resources["crew_id"] and resources.get("execution_id"):
        test_request(
            "GET", f"/crews/{resources['crew_id']}/runs/{resources['execution_id']}",
            description="Get execution status"
        )

    # 7-3. Get Execution History
    if resources["crew_id"]:
        test_request(
            "GET", f"/crews/{resources['crew_id']}/runs",
            description="Get crew execution history"
        )

    # ============================================================
    # 8. Error Cases
    # ============================================================
    print_header("8. Error Cases Tests")

    # 8-1. Get non-existent resource
    test_request(
        "GET", "/crews/non-existent-id",
        expected_status=404,
        description="Get non-existent crew (should return 404)"
    )

    # 8-2. Create with missing required fields
    test_request(
        "POST", "/crews",
        data={"agent_ids": []},  # Missing 'name'
        expected_status=422,
        description="Create crew with missing fields (should return 422)"
    )

    # ============================================================
    # 9. Cleanup
    # ============================================================
    print_header("9. Cleanup - Deleting Test Data")

    # Delete in reverse order of dependencies
    if resources["task_id"]:
        test_request(
            "DELETE", f"/tasks/{resources['task_id']}",
            expected_status=204,
            description="Delete test task"
        )

    if resources["agent_id"]:
        test_request(
            "DELETE", f"/agents/{resources['agent_id']}",
            expected_status=204,
            description="Delete test agent"
        )

    if resources["tool_id"]:
        test_request(
            "DELETE", f"/tools/{resources['tool_id']}",
            expected_status=204,
            description="Delete test tool"
        )

    if resources["knowledge_id"]:
        test_request(
            "DELETE", f"/knowledge/{resources['knowledge_id']}",
            expected_status=204,
            description="Delete test knowledge source"
        )

    if resources["crew_id"]:
        test_request(
            "DELETE", f"/crews/{resources['crew_id']}",
            expected_status=204,
            description="Delete test crew"
        )

    # ============================================================
    # Summary
    # ============================================================
    print_header("Test Summary")

    total = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total * 100) if total > 0 else 0

    print(f"Total Tests: {total}")
    print_success(f"Passed: {test_results['passed']}")

    if test_results["failed"] > 0:
        print_error(f"Failed: {test_results['failed']}")
        print(f"\n{Colors.RED}Failed Tests:{Colors.NC}")
        for error in test_results["errors"]:
            print(f"  - {error['endpoint']}: Expected {error['expected']}, got {error['actual']}")
    else:
        print_success("Failed: 0")

    print(f"\nPass Rate: {pass_rate:.1f}%")

    if test_results["failed"] == 0:
        print_success("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print_error("\n❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nTests interrupted by user")
        sys.exit(1)
