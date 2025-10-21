# API Tests

API 기능 테스트를 위한 Python 스크립트 모음

## 🚀 빠른 시작

### 1. 서버 실행

먼저 백엔드 서버를 실행합니다:

```bash
cd bend
python run.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 2. API 테스트 실행

#### 📦 전체 API 테스트 (권장)

**모든 API 엔드포인트를 한 번에 테스트:**

```bash
# 전체 테스트 실행
python bend/tests/run_all_tests.py
```

**출력 예시:**
```
============================================================
CrewAI Studio - API Tests
============================================================
Base URL: http://localhost:8000/api
Time: 2025-10-21 10:30:00

============================================================
1. Health Check
============================================================

GET /api/health
Status: 200
Response:
{
  "status": "healthy",
  "timestamp": "2025-10-21T10:30:00"
}
✓ Expected status 200 ✓

... (생략)

============================================================
Test Summary
============================================================
Total Tests: 45
✓ Passed: 45
✓ Failed: 0

Pass Rate: 100.0%

✓ 🎉 All tests passed!
```

#### 🎯 개별 API 테스트

**특정 API만 테스트:**

```bash
# Crews API만 테스트
python bend/tests/test_crews_only.py

# 🆕 Crew 실행 기능 테스트 (End-to-End)
python bend/tests/test_crew_execution.py

# 기존 Python 스크립트 (상세 로그)
python bend/tests/test_api_crews.py
python bend/tests/test_api_agents.py
python bend/tests/test_api_tasks.py
python bend/tests/test_api_tools.py
python bend/tests/test_api_knowledge.py

# 통합 테스트
python bend/tests/test_api_integration.py
```

## 🆕 새로운 기능: Crew 실행 API

**Phase 5-1: CrewAI 엔진 통합 완료**

이제 Crew를 실제로 실행할 수 있습니다! 새로운 API 엔드포인트:

### POST /api/crews/{crew_id}/kickoff
Crew를 실행하고 결과를 반환합니다.

**요청 예시**:
```bash
curl -X POST http://localhost:8000/api/crews/{crew_id}/kickoff \
  -H "Content-Type: application/json" \
  -d '{"query": "Write a blog post about AI"}'
```

**응답 예시**:
```json
{
  "execution_id": "CR_12345678",
  "crew_id": "C_87654321",
  "status": "completed",
  "started_at": "2025-10-21T10:30:00",
  "completed_at": "2025-10-21T10:30:05",
  "result": {
    "output": "Here is your blog post about AI..."
  },
  "error": null
}
```

### GET /api/crews/{crew_id}/runs/{run_id}
특정 실행 상태 조회

### GET /api/crews/{crew_id}/runs
Crew의 실행 이력 조회 (최대 10개)

**테스트 참고사항**:
- ⚠️ Crew 실행은 LLM API 키가 필요합니다 (.env 파일에 설정)
- 테스트 스크립트는 엔드포인트 구조를 검증하며, API 키가 없으면 실행이 실패할 수 있습니다
- 정상 실행을 위해 `.env` 파일에 `OPENAI_API_KEY` 또는 다른 LLM provider API 키를 설정하세요

## 테스트 스크립트 목록

### 🆕 `test_crew_execution.py` (새로운 End-to-End 테스트)
**Crew 실행 기능 전체 테스트 - 실제 LLM 호출 포함**

**테스트 시나리오**:
1. ✅ Health Check
2. ✅ Agent 생성 (AI Content Writer)
3. ✅ Task 생성 (AI 관련 콘텐츠 작성)
4. ✅ Crew 생성 (Agent + Task 포함)
5. ✅ Crew 검증
6. ✅ **Crew 실행 (kickoff)** - 실제 LLM API 호출
7. ✅ 실행 상태 조회
8. ✅ 실행 이력 조회
9. ✅ Cleanup (리소스 삭제)

**실행 결과 예시**:
```
============================================================
CrewAI Execution Test
============================================================
Base URL: http://localhost:8000/api
Time: 2025-10-21 14:30:00

============================================================
1. Health Check
============================================================

GET /api/health
Status: 200
...

============================================================
6. Execute Crew (Kickoff)
============================================================

⚠️  This will call the LLM API (requires API key in .env)
⚠️  This may take 10-30 seconds depending on the model

Starting crew execution...
POST /api/crews/C_12345678/kickoff
Status: 201
Response:
{
  "execution_id": "CR_87654321",
  "crew_id": "C_12345678",
  "status": "completed",
  "started_at": "2025-10-21T14:30:10",
  "completed_at": "2025-10-21T14:30:25",
  "result": {
    "output": "AI in education offers transformative benefits..."
  }
}
✓ Expected status 201 ✓
✓ Execution completed in 15.42 seconds
ℹ Execution ID: CR_87654321
ℹ Status: completed

============================================================
Execution Result:
============================================================

AI in education offers transformative benefits including
personalized learning experiences tailored to individual
student needs, automated grading systems that save educators
valuable time, and intelligent tutoring systems that provide
24/7 support to learners worldwide.

...

============================================================
Test Completed
============================================================
✓ 🎉 All tests completed successfully!
ℹ Crew execution is working properly!
```

**주의사항**:
- ⚠️ 이 테스트는 실제 LLM API를 호출합니다
- ⚠️ `.env` 파일에 `OPENAI_API_KEY` 또는 다른 LLM provider API 키가 필요합니다
- ⚠️ API 사용량이 발생할 수 있습니다 (약 500-1000 토큰)
- ⚠️ 실행 시간: 10-30초 정도 소요됩니다

**API 키 설정**:
```bash
# .env 파일 생성 또는 수정
cd bend
echo "OPENAI_API_KEY=sk-your-api-key-here" >> .env

# 또는 다른 provider 사용
echo "GROQ_API_KEY=your-groq-key" >> .env
echo "ANTHROPIC_API_KEY=your-anthropic-key" >> .env
```

---

### `test_api_crews.py`
Crews CRUD API 테스트

### `test_api_agents.py`
Agents CRUD API 테스트

### `test_api_tasks.py`
Tasks CRUD API 테스트

### `test_api_knowledge.py`
Knowledge Sources CRUD API 테스트

**테스트 항목**:
- ✅ Health Check
- ✅ CREATE: 새 Knowledge Source 생성
- ✅ READ: Knowledge Source 조회 (단일/목록)
- ✅ UPDATE: Knowledge Source 수정
- ✅ DELETE: Knowledge Source 삭제
- ✅ VALIDATE: Knowledge Source 검증
- ✅ 에러 처리 (404, 400 등)
- ✅ 잘못된 source_type 검증
- ✅ String 타입 content 누락 검증
- ✅ Agent 의존성 검증 (사용 중인 Knowledge Source 삭제 방지)
- ✅ Crew 의존성 검증 (사용 중인 Knowledge Source 삭제 방지)

**실행 결과 예시**:
```
============================================================
CrewAI Studio - Knowledge Sources API Tests
Base URL: http://localhost:8000/api
============================================================

============================================================
Health Check
============================================================

GET /api/health
Status: 200 OK
...
```

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
