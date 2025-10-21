#!/bin/bash

# Crews API 상세 테스트

set -e

# 색상
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_URL="${API_BASE_URL:-http://localhost:8000}"
API_PREFIX="/api"

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
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

print_header "Crews API Tests"

# 1. Health Check
print_info "1. Health Check"
curl -s "$BASE_URL$API_PREFIX/health" | head -3
echo ""

# 2. List all crews (initial)
print_info "2. List all crews (should be empty or have existing crews)"
curl -s "$BASE_URL$API_PREFIX/crews" | python3 -m json.tool 2>/dev/null || echo "No crews found"
echo ""

# 3. Create new crew
print_info "3. Creating new crew..."
RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/crews" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marketing Team",
    "agent_ids": [],
    "task_ids": [],
    "process": "sequential",
    "verbose": true,
    "cache": true,
    "max_rpm": 1000,
    "memory": false,
    "planning": false,
    "knowledge_source_ids": []
  }')

CREW_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -n "$CREW_ID" ]; then
    print_success "Crew created with ID: $CREW_ID"
    echo "$RESPONSE" | python3 -m json.tool
else
    print_error "Failed to create crew"
    echo "$RESPONSE"
    exit 1
fi
echo ""

# 4. Get specific crew
print_info "4. Getting crew by ID: $CREW_ID"
curl -s "$BASE_URL$API_PREFIX/crews/$CREW_ID" | python3 -m json.tool
echo ""

# 5. Update crew
print_info "5. Updating crew name..."
curl -s -X PUT "$BASE_URL$API_PREFIX/crews/$CREW_ID" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Marketing Team", "verbose": false}' | python3 -m json.tool
print_success "Crew updated"
echo ""

# 6. Validate crew
print_info "6. Validating crew..."
curl -s -X POST "$BASE_URL$API_PREFIX/crews/$CREW_ID/validate" | python3 -m json.tool
echo ""

# 7. List all crews (should show our crew)
print_info "7. List all crews (should include new crew)"
curl -s "$BASE_URL$API_PREFIX/crews" | python3 -m json.tool
echo ""

# 8. Test error cases
print_info "8. Testing error cases..."

print_info "8-1. Get non-existent crew (should return 404)"
curl -s "$BASE_URL$API_PREFIX/crews/non-existent-id" | python3 -m json.tool
echo ""

print_info "8-2. Create crew with missing required fields (should return 400)"
curl -s -X POST "$BASE_URL$API_PREFIX/crews" \
  -H "Content-Type: application/json" \
  -d '{"agent_ids": []}' | python3 -m json.tool
echo ""

# 9. Delete crew
print_info "9. Deleting crew..."
curl -s -X DELETE "$BASE_URL$API_PREFIX/crews/$CREW_ID"
print_success "Crew deleted: $CREW_ID"
echo ""

# 10. Verify deletion
print_info "10. Verifying deletion (should return 404)"
curl -s "$BASE_URL$API_PREFIX/crews/$CREW_ID" | python3 -m json.tool
echo ""

print_header "Tests Completed"
print_success "All Crews API tests finished!"
