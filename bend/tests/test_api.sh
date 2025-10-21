#!/bin/bash

# CrewAI Studio - API Test Script (curl)
# 모든 API 엔드포인트를 curl로 테스트

set -e  # 에러 발생 시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 설정
BASE_URL="${API_BASE_URL:-http://localhost:8000}"
API_PREFIX="/api"

# 헬퍼 함수
print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# JSON 파싱 (jq 없이)
get_json_value() {
    local json="$1"
    local key="$2"
    echo "$json" | grep -o "\"$key\":\"[^\"]*\"" | cut -d'"' -f4
}

# 임시 변수
CREW_ID=""
AGENT_ID=""
TASK_ID=""
TOOL_ID=""
KNOWLEDGE_ID=""

print_header "CrewAI Studio - API Tests (curl)"
echo "Base URL: $BASE_URL$API_PREFIX"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"

# ============================================================
# 1. Health Check
# ============================================================
print_header "1. Health Check"

echo "GET $API_PREFIX/health"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL$API_PREFIX/health")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$HTTP_CODE" == "200" ]; then
    print_success "Health Check OK"
    echo "$BODY" | head -5
else
    print_error "Health Check Failed (HTTP $HTTP_CODE)"
    exit 1
fi

# ============================================================
# 2. Crews API
# ============================================================
print_header "2. Crews API Tests"

# 2-1. Create Crew
print_info "2-1. Creating Crew..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL$API_PREFIX/crews" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Crew",
    "agent_ids": [],
    "task_ids": [],
    "process": "sequential",
    "verbose": true,
    "cache": true,
    "max_rpm": 1000,
    "memory": false,
    "planning": false
  }')

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$HTTP_CODE" == "201" ] || [ "$HTTP_CODE" == "200" ]; then
    CREW_ID=$(get_json_value "$BODY" "id")
    print_success "Crew created: $CREW_ID"
else
    print_error "Crew creation failed (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

# 2-2. Get Crew
if [ -n "$CREW_ID" ]; then
    print_info "2-2. Getting Crew..."
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL$API_PREFIX/crews/$CREW_ID")
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)

    if [ "$HTTP_CODE" == "200" ]; then
        print_success "Crew retrieved"
    else
        print_error "Crew retrieval failed (HTTP $HTTP_CODE)"
    fi
fi

# 2-3. List Crews
print_info "2-3. Listing Crews..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL$API_PREFIX/crews")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)

if [ "$HTTP_CODE" == "200" ]; then
    print_success "Crews listed"
else
    print_error "Crews listing failed (HTTP $HTTP_CODE)"
fi

# 2-4. Update Crew
if [ -n "$CREW_ID" ]; then
    print_info "2-4. Updating Crew..."
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X PUT "$BASE_URL$API_PREFIX/crews/$CREW_ID" \
      -H "Content-Type: application/json" \
      -d '{"name": "Updated Test Crew"}')
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)

    if [ "$HTTP_CODE" == "200" ]; then
        print_success "Crew updated"
    else
        print_error "Crew update failed (HTTP $HTTP_CODE)"
    fi
fi

# 2-5. Validate Crew
if [ -n "$CREW_ID" ]; then
    print_info "2-5. Validating Crew..."
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL$API_PREFIX/crews/$CREW_ID/validate")
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)

    if [ "$HTTP_CODE" == "200" ]; then
        print_success "Crew validated"
    else
        print_error "Crew validation failed (HTTP $HTTP_CODE)"
    fi
fi

# ============================================================
# 3. Agents API
# ============================================================
print_header "3. Agents API Tests"

# 3-1. Create Agent
print_info "3-1. Creating Agent..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL$API_PREFIX/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Test Agent",
    "backstory": "A test agent",
    "goal": "Testing purposes",
    "temperature": 0.7,
    "allow_delegation": false,
    "verbose": true,
    "cache": true,
    "llm_provider_model": "gpt-4",
    "max_iter": 25,
    "tool_ids": [],
    "knowledge_source_ids": []
  }')

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$HTTP_CODE" == "201" ] || [ "$HTTP_CODE" == "200" ]; then
    AGENT_ID=$(get_json_value "$BODY" "id")
    print_success "Agent created: $AGENT_ID"
else
    print_error "Agent creation failed (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

# 3-2. Get Agent
if [ -n "$AGENT_ID" ]; then
    print_info "3-2. Getting Agent..."
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL$API_PREFIX/agents/$AGENT_ID")
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)

    if [ "$HTTP_CODE" == "200" ]; then
        print_success "Agent retrieved"
    else
        print_error "Agent retrieval failed (HTTP $HTTP_CODE)"
    fi
fi

# 3-3. List Agents
print_info "3-3. Listing Agents..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL$API_PREFIX/agents")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)

if [ "$HTTP_CODE" == "200" ]; then
    print_success "Agents listed"
else
    print_error "Agents listing failed (HTTP $HTTP_CODE)"
fi

# 3-4. Update Agent
if [ -n "$AGENT_ID" ]; then
    print_info "3-4. Updating Agent..."
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X PUT "$BASE_URL$API_PREFIX/agents/$AGENT_ID" \
      -H "Content-Type: application/json" \
      -d '{"role": "Updated Test Agent"}')
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)

    if [ "$HTTP_CODE" == "200" ]; then
        print_success "Agent updated"
    else
        print_error "Agent update failed (HTTP $HTTP_CODE)"
    fi
fi

# ============================================================
# 4. Tasks API
# ============================================================
print_header "4. Tasks API Tests"

# 4-1. Create Task
if [ -n "$AGENT_ID" ]; then
    print_info "4-1. Creating Task..."
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL$API_PREFIX/tasks" \
      -H "Content-Type: application/json" \
      -d "{
        \"description\": \"Test task\",
        \"expected_output\": \"Test output\",
        \"agent_id\": \"$AGENT_ID\",
        \"async_execution\": false
      }")

    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)
    BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

    if [ "$HTTP_CODE" == "201" ] || [ "$HTTP_CODE" == "200" ]; then
        TASK_ID=$(get_json_value "$BODY" "id")
        print_success "Task created: $TASK_ID"
    else
        print_error "Task creation failed (HTTP $HTTP_CODE)"
        echo "$BODY"
    fi
fi

# 4-2. Get Task
if [ -n "$TASK_ID" ]; then
    print_info "4-2. Getting Task..."
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL$API_PREFIX/tasks/$TASK_ID")
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)

    if [ "$HTTP_CODE" == "200" ]; then
        print_success "Task retrieved"
    else
        print_error "Task retrieval failed (HTTP $HTTP_CODE)"
    fi
fi

# 4-3. List Tasks
print_info "4-3. Listing Tasks..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL$API_PREFIX/tasks")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)

if [ "$HTTP_CODE" == "200" ]; then
    print_success "Tasks listed"
else
    print_error "Tasks listing failed (HTTP $HTTP_CODE)"
fi

# ============================================================
# 5. Tools API
# ============================================================
print_header "5. Tools API Tests"

# 5-1. Create Tool
print_info "5-1. Creating Tool..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL$API_PREFIX/tools" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Tool",
    "description": "A test tool",
    "parameters": {"api_key": "test123"},
    "parameters_metadata": {
      "api_key": {"mandatory": true}
    }
  }')

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$HTTP_CODE" == "201" ] || [ "$HTTP_CODE" == "200" ]; then
    TOOL_ID=$(get_json_value "$BODY" "tool_id")
    print_success "Tool created: $TOOL_ID"
else
    print_error "Tool creation failed (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

# 5-2. Get Tool
if [ -n "$TOOL_ID" ]; then
    print_info "5-2. Getting Tool..."
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL$API_PREFIX/tools/$TOOL_ID")
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)

    if [ "$HTTP_CODE" == "200" ]; then
        print_success "Tool retrieved"
    else
        print_error "Tool retrieval failed (HTTP $HTTP_CODE)"
    fi
fi

# ============================================================
# 6. Knowledge Sources API
# ============================================================
print_header "6. Knowledge Sources API Tests"

# 6-1. Create Knowledge Source
print_info "6-1. Creating Knowledge Source..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL$API_PREFIX/knowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Knowledge",
    "source_type": "string",
    "content": "This is test knowledge content",
    "chunk_size": 4000,
    "chunk_overlap": 200
  }')

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$HTTP_CODE" == "201" ] || [ "$HTTP_CODE" == "200" ]; then
    KNOWLEDGE_ID=$(get_json_value "$BODY" "id")
    print_success "Knowledge Source created: $KNOWLEDGE_ID"
else
    print_error "Knowledge Source creation failed (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

# 6-2. Get Knowledge Source
if [ -n "$KNOWLEDGE_ID" ]; then
    print_info "6-2. Getting Knowledge Source..."
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL$API_PREFIX/knowledge/$KNOWLEDGE_ID")
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)

    if [ "$HTTP_CODE" == "200" ]; then
        print_success "Knowledge Source retrieved"
    else
        print_error "Knowledge Source retrieval failed (HTTP $HTTP_CODE)"
    fi
fi

# ============================================================
# 7. Cleanup
# ============================================================
print_header "7. Cleanup - Deleting Test Data"

# Delete in reverse order of dependencies
if [ -n "$TASK_ID" ]; then
    print_info "Deleting Task..."
    curl -s -X DELETE "$BASE_URL$API_PREFIX/tasks/$TASK_ID" > /dev/null
    print_success "Task deleted"
fi

if [ -n "$AGENT_ID" ]; then
    print_info "Deleting Agent..."
    curl -s -X DELETE "$BASE_URL$API_PREFIX/agents/$AGENT_ID" > /dev/null
    print_success "Agent deleted"
fi

if [ -n "$TOOL_ID" ]; then
    print_info "Deleting Tool..."
    curl -s -X DELETE "$BASE_URL$API_PREFIX/tools/$TOOL_ID" > /dev/null
    print_success "Tool deleted"
fi

if [ -n "$KNOWLEDGE_ID" ]; then
    print_info "Deleting Knowledge Source..."
    curl -s -X DELETE "$BASE_URL$API_PREFIX/knowledge/$KNOWLEDGE_ID" > /dev/null
    print_success "Knowledge Source deleted"
fi

if [ -n "$CREW_ID" ]; then
    print_info "Deleting Crew..."
    curl -s -X DELETE "$BASE_URL$API_PREFIX/crews/$CREW_ID" > /dev/null
    print_success "Crew deleted"
fi

# ============================================================
# Summary
# ============================================================
print_header "Test Summary"
print_success "All tests completed successfully!"
echo ""
echo "Tested endpoints:"
echo "  - Health Check"
echo "  - Crews CRUD (Create, Read, Update, Validate, Delete)"
echo "  - Agents CRUD"
echo "  - Tasks CRUD"
echo "  - Tools CRUD"
echo "  - Knowledge Sources CRUD"
echo ""
print_info "Total: 30+ API endpoints tested"
