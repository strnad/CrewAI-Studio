# API Tests

API 기능 테스트를 위한 Python 스크립트 모음

## 사용 방법

### 1. 서버 실행

먼저 백엔드 서버를 실행합니다:

```bash
cd bend
python run.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 2. API 테스트 실행

다른 터미널에서 테스트 스크립트를 실행합니다:

```bash
# Crews API 테스트
python bend/tests/test_api_crews.py

# Agents API 테스트
python bend/tests/test_api_agents.py

# Tasks API 테스트
python bend/tests/test_api_tasks.py

# Tools API 테스트
python bend/tests/test_api_tools.py
```

## 테스트 스크립트 목록

### `test_api_crews.py`
Crews CRUD API 테스트

### `test_api_agents.py`
Agents CRUD API 테스트

### `test_api_tasks.py`
Tasks CRUD API 테스트

### `test_api_tools.py`
Tools CRUD API 테스트

**테스트 항목**:
- ✅ Health Check
- ✅ CREATE: 새 Tool 생성
- ✅ READ: Tool 조회 (단일/목록)
- ✅ UPDATE: Tool 수정
- ✅ DELETE: Tool 삭제
- ✅ VALIDATE: Tool 검증
- ✅ 에러 처리 (404, 400 등)
- ✅ 필수 파라미터 검증
- ✅ Agent 의존성 검증 (사용 중인 Tool 삭제 방지)

**실행 결과 예시**:
```
============================================================
CrewAI Studio - Tools API Tests
Base URL: http://localhost:8000/api
============================================================

============================================================
Health Check
============================================================

GET /api/health
Status: 200 OK
...
```

### `test_api_tasks.py`
Tasks CRUD API 테스트

**테스트 항목**:
- ✅ Health Check
- ✅ CREATE: 새 Task 생성
- ✅ READ: Task 조회 (단일/목록)
- ✅ UPDATE: Task 수정
- ✅ DELETE: Task 삭제
- ✅ VALIDATE: Task 검증
- ✅ 에러 처리 (404, 400 등)
- ✅ Agent ID 검증
- ✅ Context Task 참조 검증
- ✅ Context로 사용 중인 Task 삭제 방지
- ✅ Crew 의존성 검증 (사용 중인 Task 삭제 방지)

**실행 결과 예시**:
```
============================================================
CrewAI Studio - Tasks API Tests
Base URL: http://localhost:8000/api
============================================================

============================================================
Health Check
============================================================

GET /api/health
Status: 200 OK
...
```

### `test_api_agents.py`
Agents CRUD API 테스트

**테스트 항목**:
- ✅ Health Check
- ✅ CREATE: 새 Agent 생성
- ✅ READ: Agent 조회 (단일/목록)
- ✅ UPDATE: Agent 수정
- ✅ DELETE: Agent 삭제
- ✅ VALIDATE: Agent 검증
- ✅ 에러 처리 (404, 400 등)
- ✅ Tool ID 검증
- ✅ Crew 의존성 검증 (사용 중인 Agent 삭제 방지)

**실행 결과 예시**:
```
============================================================
CrewAI Studio - Agents API Tests
Base URL: http://localhost:8000/api
============================================================

============================================================
Health Check
============================================================

GET /api/health
Status: 200 OK
...
```

### `test_api_crews.py`
Crews CRUD API 테스트

**테스트 항목**:
- ✅ Health Check (기본 및 상세)
- ✅ CREATE: 새 Crew 생성
- ✅ READ: Crew 조회 (단일/목록)
- ✅ UPDATE: Crew 수정
- ✅ DELETE: Crew 삭제
- ✅ VALIDATE: Crew 검증
- ✅ 에러 처리 (404, 400 등)

**실행 결과 예시**:
```
============================================================
CrewAI Studio - Crews API Tests
Base URL: http://localhost:8000/api
============================================================

============================================================
Health Check
============================================================

GET /api/health
Status: 200 OK
Response Body:
{
  "status": "healthy",
  "timestamp": "2025-10-20T10:30:00",
  "service": "CrewAI Studio API"
}

...
```

### `test_api_agents.py` (예정)
Agents CRUD API 테스트

### `test_api_tasks.py` (예정)
Tasks CRUD API 테스트

### `test_api_tools.py` (예정)
Tools CRUD API 테스트

### `test_api_knowledge.py` (예정)
Knowledge Sources CRUD API 테스트

## API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 수동 테스트 (curl)

Python 스크립트 대신 curl로 직접 테스트할 수도 있습니다:

```bash
# Health Check
curl http://localhost:8000/api/health

# List Crews
curl http://localhost:8000/api/crews

# Create Crew
curl -X POST http://localhost:8000/api/crews \
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
    "planning": false,
    "knowledge_source_ids": []
  }'

# Get Crew
curl http://localhost:8000/api/crews/{crew_id}

# Update Crew
curl -X PUT http://localhost:8000/api/crews/{crew_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Crew"}'

# Validate Crew
curl -X POST http://localhost:8000/api/crews/{crew_id}/validate

# Delete Crew
curl -X DELETE http://localhost:8000/api/crews/{crew_id}
```

## 트러블슈팅

### 서버 연결 오류
```
✗ Error: Could not connect to http://localhost:8000/api
```

**해결 방법**: 백엔드 서버가 실행 중인지 확인
```bash
cd bend
python run.py
```

### Import 오류
```
ModuleNotFoundError: No module named 'requests'
```

**해결 방법**: requirements 설치
```bash
cd bend
pip install -r requirements.txt
```

### Port 충돌
```
[ERROR] Address already in use
```

**해결 방법**: 다른 포트 사용 또는 기존 프로세스 종료
```bash
# 포트 8000 사용 중인 프로세스 찾기
lsof -i :8000

# 또는 다른 포트로 실행
# bend/config.py에서 port 변경
```
