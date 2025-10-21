"""
간단한 Tool 생성 테스트
"""
import requests

BASE_URL = "http://localhost:8000/api"

# Tool 생성
tool_data = {
    "name": "DuckDuckGoSearchTool",
    "description": "DuckDuckGo web search",
    "parameters": {},
    "parameters_metadata": {}
}

print("1. Tool 생성...")
response = requests.post(f"{BASE_URL}/tools", json=tool_data)
print(f"Status: {response.status_code}")
tool = response.json()
print(f"Tool ID: {tool['tool_id']}")
print(f"Tool Name: {tool['name']}\n")

tool_id = tool['tool_id']

# Tool 조회
print("2. Tool 조회...")
response = requests.get(f"{BASE_URL}/tools/{tool_id}")
print(f"Status: {response.status_code}")
print(f"Retrieved: {response.json()['name']}\n")

# Tool 삭제
print("3. Tool 삭제...")
response = requests.delete(f"{BASE_URL}/tools/{tool_id}")
print(f"Status: {response.status_code}")

print("\n✓ 테스트 완료!")
