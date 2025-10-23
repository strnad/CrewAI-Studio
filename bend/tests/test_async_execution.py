"""
Async Crew Execution Test Script
비동기 Crew 실행 및 Stop 기능 테스트
"""
import requests
import json
import time
from datetime import datetime


# ============================================================
# 설정
# ============================================================
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api"

# 색상 코드
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'


# ============================================================
# 헬퍼 함수
# ============================================================
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


def print_response(response: requests.Response):
    """응답 출력"""
    status_color = Colors.GREEN if response.status_code < 300 else Colors.RED
    print(f"{status_color}Status: {response.status_code}{Colors.NC}")

    try:
        body = response.json()
        print(f"{Colors.CYAN}Response:{Colors.NC}")
        print(json.dumps(body, indent=2, ensure_ascii=False))
    except:
        print(f"{Colors.CYAN}Response:{Colors.NC}")
        print(response.text[:500])


def api_request(method: str, endpoint: str, data=None, expected_status=200):
    """API 요청"""
    url = f"{BASE_URL}{API_PREFIX}{endpoint}"

    print(f"\n{Colors.CYAN}{method} {API_PREFIX}{endpoint}{Colors.NC}")

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

        if response.status_code == expected_status:
            print_success(f"Expected status {expected_status} ✓")
            return response.json() if response.text else None
        else:
            print_error(f"Expected {expected_status}, got {response.status_code}")
            return None

    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to {BASE_URL}")
        print_info("Make sure the server is running: cd bend && python run.py")
        return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None


def poll_execution_status(crew_id: str, run_id: str, max_wait: int = 60, interval: float = 2.0):
    """
    실행 상태를 폴링하여 완료 대기

    Args:
        crew_id: Crew ID
        run_id: Execution run ID
        max_wait: 최대 대기 시간 (초)
        interval: 폴링 간격 (초)

    Returns:
        Final status or None
    """
    print_info(f"Polling execution status (max {max_wait}s, interval {interval}s)...")

    start_time = time.time()
    while time.time() - start_time < max_wait:
        result = api_request(
            "GET",
            f"/crews/{crew_id}/runs/{run_id}"
        )

        if not result:
            print_error("Failed to get execution status")
            return None

        status = result.get("status")
        elapsed = time.time() - start_time

        print(f"{Colors.YELLOW}[{elapsed:.1f}s] Status: {status}{Colors.NC}")

        # 완료 상태 체크
        if status in ["completed", "failed", "cancelled"]:
            return result

        # 대기
        time.sleep(interval)

    print_error(f"Timeout waiting for execution to complete ({max_wait}s)")
    return None


# ============================================================
# 메인 테스트
# ============================================================
def main():
    """메인 테스트 실행"""

    print_header("Async Crew Execution & Stop Test")
    print(f"Base URL: {BASE_URL}{API_PREFIX}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 리소스 ID 저장
    resources = {
        "agent_id": None,
        "task_id": None,
        "crew_id": None,
        "execution_id": None
    }

    try:
        # ============================================================
        # 1. Health Check
        # ============================================================
        print_header("1. Health Check")
        result = api_request("GET", "/health")
        if not result:
            print_error("Health check failed. Exiting.")
            return

        # ============================================================
        # 2. Agent 생성
        # ============================================================
        print_header("2. Create Agent")

        agent_data = {
            "role": "AI Content Writer",
            "goal": "Write engaging and informative content",
            "backstory": "You are an experienced content writer with expertise in AI and technology.",
            "llm_provider_model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_iter": 15,
            "allow_delegation": False,
            "verbose": True,
            "cache": True,
            "tool_ids": [],
            "knowledge_source_ids": []
        }

        result = api_request("POST", "/agents", data=agent_data, expected_status=201)
        if result and "id" in result:
            resources["agent_id"] = result["id"]
            print_success(f"Agent created: {resources['agent_id']}")
        else:
            print_error("Failed to create agent. Exiting.")
            return

        # ============================================================
        # 3. Task 생성
        # ============================================================
        print_header("3. Create Task")

        task_data = {
            "description": "Write a short paragraph (2-3 sentences) about the benefits of AI in education.",
            "expected_output": "A concise paragraph highlighting key benefits of AI in education",
            "agent_id": resources["agent_id"],
            "async_execution": False
        }

        result = api_request("POST", "/tasks", data=task_data, expected_status=201)
        if result and "id" in result:
            resources["task_id"] = result["id"]
            print_success(f"Task created: {resources['task_id']}")
        else:
            print_error("Failed to create task. Exiting.")
            return

        # ============================================================
        # 4. Crew 생성
        # ============================================================
        print_header("4. Create Crew")

        crew_data = {
            "name": "Async Test Crew",
            "agent_ids": [resources["agent_id"]],
            "task_ids": [resources["task_id"]],
            "process": "sequential",
            "verbose": True,
            "cache": True,
            "max_rpm": 1000,
            "memory": False,
            "planning": False,
            "knowledge_source_ids": []
        }

        result = api_request("POST", "/crews", data=crew_data, expected_status=201)
        if result and "id" in result:
            resources["crew_id"] = result["id"]
            print_success(f"Crew created: {resources['crew_id']}")
        else:
            print_error("Failed to create crew. Exiting.")
            return

        # ============================================================
        # 5. 비동기 Crew 실행 테스트
        # ============================================================
        print_header("5. Test Async Crew Execution")

        print_info("⚠️  Testing async execution - should return immediately with 'pending' status")
        print_info("")

        execution_inputs = {}

        print(f"{Colors.YELLOW}Starting async crew execution...{Colors.NC}")
        start_time = time.time()

        result = api_request(
            "POST",
            f"/crews/{resources['crew_id']}/kickoff",
            data=execution_inputs,
            expected_status=201
        )

        end_time = time.time()
        response_time = end_time - start_time

        if result:
            resources["execution_id"] = result.get("execution_id")
            print_success(f"Execution started (response in {response_time:.2f}s)")
            print_info(f"Execution ID: {resources['execution_id']}")

            status = result.get("status")
            print_info(f"Initial Status: {status}")

            # 비동기 실행이면 즉시 'pending' 상태로 반환되어야 함
            if status == "pending":
                print_success("✓ Async execution working correctly (status: pending)")
            else:
                print_error(f"✗ Expected 'pending' status, got '{status}'")

            # 응답이 2초 이내면 비동기로 판단
            if response_time < 2.0:
                print_success(f"✓ Fast response ({response_time:.2f}s < 2s) - async confirmed")
            else:
                print_error(f"✗ Slow response ({response_time:.2f}s) - might be synchronous")

        else:
            print_error("Crew execution failed!")
            return

        # ============================================================
        # 6. 실행 상태 폴링 및 완료 대기
        # ============================================================
        print_header("6. Poll Execution Status Until Completion")

        final_result = poll_execution_status(
            resources['crew_id'],
            resources['execution_id'],
            max_wait=120,  # 2분 대기
            interval=2.0
        )

        if final_result:
            final_status = final_result.get("status")
            print_success(f"Execution completed with status: {final_status}")

            # 결과 출력
            if final_result.get("result"):
                print(f"\n{Colors.MAGENTA}{'=' * 60}{Colors.NC}")
                print(f"{Colors.MAGENTA}Execution Result:{Colors.NC}")
                print(f"{Colors.MAGENTA}{'=' * 60}{Colors.NC}")
                result_output = final_result["result"].get("output", "No output")
                print(f"\n{result_output}\n")

            if final_result.get("error"):
                print_error(f"Execution had errors: {final_result['error']}")
        else:
            print_error("Failed to get final execution status")

        # ============================================================
        # 7. Stop 기능 테스트 (새로운 실행 시작)
        # ============================================================
        print_header("7. Test Stop Functionality")

        print_info("Starting another execution to test stop...")

        result = api_request(
            "POST",
            f"/crews/{resources['crew_id']}/kickoff",
            data={},
            expected_status=201
        )

        if result:
            stop_execution_id = result.get("execution_id")
            print_success(f"Test execution started: {stop_execution_id}")

            # 약간 대기 (실행이 시작되도록)
            print_info("Waiting 3 seconds before stopping...")
            time.sleep(3)

            # Stop 요청
            print_info(f"Sending stop request...")
            stop_result = api_request(
                "POST",
                f"/crews/{resources['crew_id']}/runs/{stop_execution_id}/stop"
            )

            if stop_result:
                stopped_status = stop_result.get("status")
                print_success(f"Stop request succeeded - Status: {stopped_status}")

                if stopped_status == "cancelled":
                    print_success("✓ Stop functionality working correctly")
                else:
                    print_error(f"✗ Expected 'cancelled' status, got '{stopped_status}'")
            else:
                print_error("Stop request failed")

        # ============================================================
        # 8. 실행 이력 조회
        # ============================================================
        print_header("8. Get Execution History")

        result = api_request(
            "GET",
            f"/crews/{resources['crew_id']}/runs"
        )

        if result and isinstance(result, list):
            print_success(f"Found {len(result)} execution(s) in history")

            # 각 실행의 상태 출력
            for i, run in enumerate(result, 1):
                print(f"  {i}. ID: {run.get('execution_id')}, Status: {run.get('status')}")

        # ============================================================
        # 9. Cleanup (정리)
        # ============================================================
        print_header("9. Cleanup - Deleting Test Data")

        print_info("Cleaning up test resources...")

        # Crew 삭제 먼저 (실행 이력도 함께 삭제됨, CASCADE DELETE)
        if resources["crew_id"]:
            api_request("DELETE", f"/crews/{resources['crew_id']}", expected_status=204)
            print_success("Crew deleted (including execution history)")

        # Task 삭제
        if resources["task_id"]:
            api_request("DELETE", f"/tasks/{resources['task_id']}", expected_status=204)
            print_success("Task deleted")

        # Agent 삭제
        if resources["agent_id"]:
            api_request("DELETE", f"/agents/{resources['agent_id']}", expected_status=204)
            print_success("Agent deleted")

        # ============================================================
        # 완료
        # ============================================================
        print_header("Test Completed")
        print_success("🎉 All async execution tests completed!")
        print_info("Summary:")
        print_info("  ✓ Async execution (immediate response)")
        print_info("  ✓ Status polling (pending → running → completed)")
        print_info("  ✓ Stop functionality (cancelled)")
        print_info("  ✓ Execution history")

    except Exception as e:
        print_error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

        # 에러 발생 시에도 정리 시도
        print_info("\nAttempting cleanup...")
        if resources.get("crew_id"):
            api_request("DELETE", f"/crews/{resources['crew_id']}", expected_status=204)
        if resources.get("task_id"):
            api_request("DELETE", f"/tasks/{resources['task_id']}", expected_status=204)
        if resources.get("agent_id"):
            api_request("DELETE", f"/agents/{resources['agent_id']}", expected_status=204)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nTest interrupted by user")
        exit(1)
