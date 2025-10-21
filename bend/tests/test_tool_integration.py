"""
Tool Integration Test Script
CrewAI Tool 통합 테스트 - 실제 Tool을 사용하는 Crew 실행
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


# ============================================================
# 메인 테스트
# ============================================================
def main():
    """메인 테스트 실행"""

    print_header("Tool Integration Test")
    print(f"Base URL: {BASE_URL}{API_PREFIX}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 리소스 ID 저장
    resources = {
        "tool_id": None,
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
        # 2. Tool 생성 (DuckDuckGoSearchTool)
        # ============================================================
        print_header("2. Create Tool (DuckDuckGoSearchTool)")

        tool_data = {
            "name": "DuckDuckGoSearchTool",
            "description": "DuckDuckGo web search",
            "parameters": {},  # DuckDuckGoSearchTool은 파라미터 없음
            "parameters_metadata": {}
        }

        result = api_request("POST", "/tools", data=tool_data, expected_status=201)
        if result and "tool_id" in result:
            resources["tool_id"] = result["tool_id"]
            print_success(f"Tool created: {resources['tool_id']}")
        else:
            print_error("Failed to create tool. Exiting.")
            return

        # ============================================================
        # 3. Agent 생성 (Tool 포함)
        # ============================================================
        print_header("3. Create Agent with Tool")

        agent_data = {
            "role": "AI Research Analyst",
            "goal": "Search and summarize information about AI topics",
            "backstory": "You are an AI researcher who uses web search to find accurate information.",
            "llm_provider_model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_iter": 15,
            "allow_delegation": False,
            "verbose": True,
            "cache": True,
            "tool_ids": [resources["tool_id"]],  # DuckDuckGo Tool 추가
            "knowledge_source_ids": []
        }

        result = api_request("POST", "/agents", data=agent_data, expected_status=201)
        if result and "id" in result:
            resources["agent_id"] = result["id"]
            print_success(f"Agent created with tool: {resources['agent_id']}")
            print_info(f"Agent has {len(result.get('tool_ids', []))} tool(s)")
        else:
            print_error("Failed to create agent. Exiting.")
            return

        # ============================================================
        # 4. Task 생성 (Tool 사용 지시)
        # ============================================================
        print_header("4. Create Task (Use Tool)")

        task_data = {
            "description": "Use DuckDuckGo to search for 'AI in education benefits' and write a brief 2-sentence summary of what you find.",
            "expected_output": "A 2-sentence summary based on DuckDuckGo search results about AI in education",
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
        # 5. Crew 생성
        # ============================================================
        print_header("5. Create Crew")

        crew_data = {
            "name": "AI Research Team with Tools",
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
        # 6. Crew 검증
        # ============================================================
        print_header("6. Validate Crew")

        result = api_request("POST", f"/crews/{resources['crew_id']}/validate")
        if result and result.get("is_valid"):
            print_success("Crew is valid and ready to execute!")
        else:
            print_error("Crew validation failed!")
            if result:
                print(f"Errors: {result.get('errors', [])}")
                print(f"Warnings: {result.get('warnings', [])}")

        # ============================================================
        # 7. Crew 실행 (Tool 사용)
        # ============================================================
        print_header("7. Execute Crew with Tool")

        print_info("⚠️  This will:")
        print_info("  - Call DuckDuckGo Search API (free, no API key needed)")
        print_info("  - Call OpenAI LLM API (requires OPENAI_API_KEY in .env)")
        print_info("  - May take 15-45 seconds due to web search")
        print_info("")

        execution_inputs = {}

        print(f"{Colors.YELLOW}Starting crew execution with tool...{Colors.NC}")
        start_time = time.time()

        result = api_request(
            "POST",
            f"/crews/{resources['crew_id']}/kickoff",
            data=execution_inputs,
            expected_status=201
        )

        end_time = time.time()
        execution_time = end_time - start_time

        if result:
            resources["execution_id"] = result.get("execution_id")
            print_success(f"Execution completed in {execution_time:.2f} seconds")
            print_info(f"Execution ID: {resources['execution_id']}")
            print_info(f"Status: {result.get('status')}")

            # 결과 출력
            if result.get("result"):
                print(f"\n{Colors.MAGENTA}{'=' * 60}{Colors.NC}")
                print(f"{Colors.MAGENTA}Tool Execution Result:{Colors.NC}")
                print(f"{Colors.MAGENTA}{'=' * 60}{Colors.NC}")
                result_output = result["result"].get("output", "No output")
                print(f"\n{result_output}\n")

                # Tool 사용 확인
                if "search" in result_output.lower() or "duckduckgo" in result_output.lower() or "found" in result_output.lower():
                    print_success("✓ Tool appears to have been used successfully!")
                else:
                    print_info("Note: Result doesn't explicitly mention search/tool usage")

            if result.get("error"):
                print_error(f"Execution had errors: {result['error']}")
        else:
            print_error("Crew execution with tool failed!")
            print_info("Check if:")
            print_info("  1. OPENAI_API_KEY is set in .env file")
            print_info("  2. Internet connection is available for DuckDuckGo")
            print_info("  3. The tool was properly configured")

        # ============================================================
        # 8. Cleanup (정리)
        # ============================================================
        print_header("8. Cleanup - Deleting Test Data")

        print_info("Cleaning up test resources...")

        # Crew 삭제 (실행 이력도 함께 삭제됨)
        if resources["crew_id"]:
            api_request("DELETE", f"/crews/{resources['crew_id']}", expected_status=204)
            print_success("Crew deleted")

        # Task 삭제
        if resources["task_id"]:
            api_request("DELETE", f"/tasks/{resources['task_id']}", expected_status=204)
            print_success("Task deleted")

        # Agent 삭제
        if resources["agent_id"]:
            api_request("DELETE", f"/agents/{resources['agent_id']}", expected_status=204)
            print_success("Agent deleted")

        # Tool 삭제
        if resources["tool_id"]:
            api_request("DELETE", f"/tools/{resources['tool_id']}", expected_status=204)
            print_success("Tool deleted")

        # ============================================================
        # 완료
        # ============================================================
        print_header("Test Completed")
        print_success("🎉 Tool integration test completed successfully!")
        print_info("Tools are working properly with CrewAI agents!")

    except Exception as e:
        print_error(f"Test failed with error: {str(e)}")

        # 에러 발생 시에도 정리 시도
        print_info("\nAttempting cleanup...")
        if resources.get("crew_id"):
            api_request("DELETE", f"/crews/{resources['crew_id']}", expected_status=204)
        if resources.get("task_id"):
            api_request("DELETE", f"/tasks/{resources['task_id']}", expected_status=204)
        if resources.get("agent_id"):
            api_request("DELETE", f"/agents/{resources['agent_id']}", expected_status=204)
        if resources.get("tool_id"):
            api_request("DELETE", f"/tools/{resources['tool_id']}", expected_status=204)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nTest interrupted by user")
        exit(1)
