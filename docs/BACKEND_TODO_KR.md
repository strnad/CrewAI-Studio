# 백엔드 개발 TODO 리스트

**작업 위치**: `/bend` 디렉토리

---

## ✅ 완료된 작업 (회사에서)

### Phase 1: FastAPI 기본 구조 ✅
- [x] FastAPI 애플리케이션 설정 (`main.py`)
- [x] CORS 설정
- [x] Rate Limiting (slowapi)
- [x] 기본 헬스체크 API (`/api/health`)
- [x] API 자동 문서화 (Swagger UI, ReDoc)
- [x] Keycloak/OIDC 설정 준비 (환경변수)

### Phase 2: 도메인 모델 분리 ✅
- [x] Crew 도메인 모델 (`bend/models/crew.py`)
- [x] Agent 도메인 모델 (`bend/models/agent.py`)
- [x] Task 도메인 모델 (`bend/models/task.py`)
- [x] Tool 도메인 모델 (`bend/models/tool.py`)
- [x] Knowledge Source 도메인 모델 (`bend/models/knowledge.py`)
- [x] Pydantic 스키마 (`bend/schemas/`)

### Phase 3: CRUD API 엔드포인트 ✅
- [x] Crews CRUD API (6 endpoints)
- [x] Agents CRUD API (6 endpoints)
- [x] Tasks CRUD API (6 endpoints)
- [x] Tools CRUD API (6 endpoints)
- [x] Knowledge Sources CRUD API (6 endpoints)
- **총 30개 API 엔드포인트 구현 완료!**

### Phase 4: 데이터베이스 레이어 ✅
- [x] SQLAlchemy ORM 모델 (`bend/database/models/`)
  - [x] CrewModel
  - [x] AgentModel
  - [x] TaskModel
  - [x] ToolModel
  - [x] KnowledgeSourceModel
- [x] Repository 패턴 (`bend/database/repositories/`)
  - [x] BaseRepository
  - [x] CrewRepository
  - [x] AgentRepository
  - [x] TaskRepository
  - [x] ToolRepository
  - [x] KnowledgeSourceRepository
- [x] Service 레이어 (`bend/services/`)
  - [x] CrewService
  - [x] AgentService
  - [x] TaskService
  - [x] ToolService
  - [x] KnowledgeSourceService
- [x] Alembic 마이그레이션 설정
- [x] PostgreSQL 연동

### 추가 완료 작업
- [x] 로깅 시스템 (`bend/logger/`)
  - [x] 기본 로거
  - [x] Discord 웹훅 연동
- [x] 테스트 스크립트 (`bend/tests/`)

---

## 🚧 남은 작업 (우선순위 순)

### Phase 5: 핵심 비즈니스 로직 구현 🔥 **[우선순위: 최상]**

#### 5-1. Crew 실행 API ⭐⭐⭐⭐⭐
**목표**: Agent가 실제로 작업을 수행할 수 있도록 Crew 실행 기능 구현

```python
# 구현 필요 API
POST /api/crews/{crew_id}/kickoff       # Crew 실행 시작
POST /api/crews/{crew_id}/stop          # 실행 중단
GET  /api/crews/{crew_id}/status        # 실행 상태 조회
GET  /api/crews/{crew_id}/result        # 실행 결과 조회
```

**작업 내용**:
- [ ] CrewAI 실행 엔진 통합
- [ ] 비동기 작업 처리 (Celery 또는 BackgroundTasks)
- [ ] 실행 상태 관리 (pending, running, completed, failed)
- [ ] 실행 결과 저장 (DB)
- [ ] 에러 핸들링 및 로깅

**예상 소요 시간**: 2-3일

---

#### 5-2. 실행 히스토리 관리 ⭐⭐⭐⭐
**목표**: Crew 실행 이력 저장 및 조회

```python
# 구현 필요 API
GET  /api/crews/{crew_id}/executions           # 실행 이력 목록
GET  /api/crews/{crew_id}/executions/{exec_id} # 특정 실행 상세
DELETE /api/crews/{crew_id}/executions/{exec_id} # 이력 삭제
```

**작업 내용**:
- [ ] ExecutionHistory ORM 모델 생성
- [ ] ExecutionHistoryRepository 구현
- [ ] ExecutionHistoryService 구현
- [ ] API 엔드포인트 구현
- [ ] 페이지네이션 지원

**예상 소요 시간**: 1-2일

---

#### 5-3. WebSocket 지원 (실시간 로그) ⭐⭐⭐⭐
**목표**: Crew 실행 중 실시간 로그 스트리밍

```python
# 구현 필요 WebSocket 엔드포인트
WS /api/crews/{crew_id}/executions/{exec_id}/logs
```

**작업 내용**:
- [ ] FastAPI WebSocket 엔드포인트 구현
- [ ] CrewAI 로그 캡처 및 스트리밍
- [ ] 클라이언트 연결 관리
- [ ] 에러 핸들링

**예상 소요 시간**: 1-2일

---

### Phase 6: 인증 및 보안 ⭐⭐⭐

#### 6-1. Keycloak/OIDC 통합
**목표**: 사용자 인증 및 권한 관리

**작업 내용**:
- [ ] Keycloak 서버 설정
- [ ] FastAPI 미들웨어 구현
- [ ] JWT 토큰 검증
- [ ] 사용자 정보 추출 및 저장

**참고 파일**: `bend/config.py` (이미 환경변수 준비됨)

**예상 소요 시간**: 2-3일

---

#### 6-2. Role-Based Access Control (RBAC)
**목표**: 역할 기반 권한 제어

**작업 내용**:
- [ ] 역할 정의 (admin, user, viewer)
- [ ] Permission 데코레이터 구현
- [ ] API 엔드포인트에 권한 검증 추가
- [ ] 소유권 검증 (본인 데이터만 수정 가능)

**예상 소요 시간**: 1-2일

---

#### 6-3. API 키 관리 (선택)
**목표**: Programmatic API 접근을 위한 API 키 발급

**작업 내용**:
- [ ] ApiKey ORM 모델
- [ ] API 키 생성/삭제 API
- [ ] API 키 검증 미들웨어
- [ ] Rate limiting per API key

**예상 소요 시간**: 1일

---

### Phase 7: 프론트엔드 연동 ⭐⭐⭐

#### 7-1. Streamlit UI → REST API 클라이언트 전환
**목표**: 기존 Streamlit 앱이 백엔드 API를 호출하도록 수정

**작업 내용**:
- [ ] `app/` 디렉토리에 API 클라이언트 라이브러리 추가
- [ ] 기존 세션 상태 → API 호출로 변경
- [ ] 인증 토큰 관리
- [ ] 에러 핸들링 UI

**예상 소요 시간**: 3-5일

---

#### 7-2. React/Vue 새 프론트엔드 (선택)
**목표**: 현대적인 SPA 프론트엔드 구축

**작업 내용**:
- [ ] 프론트엔드 프로젝트 생성 (`frnt/`)
- [ ] API 통합 (axios/fetch)
- [ ] 인증 플로우 구현
- [ ] Crew 관리 UI
- [ ] 실시간 로그 표시 (WebSocket)

**예상 소요 시간**: 2-3주 (대규모)

---

### Phase 8: 배포 및 최적화 ⭐⭐

#### 8-1. Docker 컨테이너화
**목표**: 각 서비스를 Docker 컨테이너로 패키징

**작업 내용**:
- [ ] `bend/Dockerfile` 생성 (FastAPI)
- [ ] `app/Dockerfile` 생성 (Streamlit, 선택)
- [ ] `frnt/Dockerfile` 생성 (React/Vue, 선택)
- [ ] 멀티 스테이지 빌드 최적화

**예상 소요 시간**: 1일

---

#### 8-2. docker-compose 멀티 서비스
**목표**: 전체 스택을 한 번에 실행

**작업 내용**:
- [ ] `docker-compose.yml` 생성
  - [ ] bend (FastAPI)
  - [ ] postgres
  - [ ] redis (선택, 캐싱용)
  - [ ] nginx (선택, 리버스 프록시)
- [ ] 네트워크 설정
- [ ] 볼륨 설정 (데이터 영속성)
- [ ] 환경변수 관리 (`.env`)

**예상 소요 시간**: 1일

---

#### 8-3. 성능 최적화 및 캐싱
**목표**: 응답 속도 개선 및 DB 부하 감소

**작업 내용**:
- [ ] Redis 캐싱 추가
  - [ ] Crew/Agent/Task 조회 캐싱
  - [ ] 실행 상태 캐싱
- [ ] DB 쿼리 최적화
  - [ ] Eager loading (N+1 문제 해결)
  - [ ] 인덱스 추가
- [ ] API 응답 압축 (gzip)
- [ ] Connection pooling 최적화

**예상 소요 시간**: 1-2일

---

### Phase 9: 추가 기능 (선택) ⭐

#### 9-1. 파일 업로드 관리
**목표**: Knowledge Source 파일 업로드 지원

**작업 내용**:
- [ ] File Upload API (`POST /api/files`)
- [ ] 파일 저장소 (S3 또는 로컬)
- [ ] 파일 타입 검증
- [ ] 업로드 진행률 표시

**예상 소요 시간**: 1일

---

#### 9-2. 스케줄링 (Cron Jobs)
**목표**: 정기적인 Crew 실행

**작업 내용**:
- [ ] APScheduler 통합
- [ ] 스케줄 관리 API
- [ ] Cron 표현식 검증
- [ ] 스케줄 이력 관리

**예상 소요 시간**: 1-2일

---

#### 9-3. 알림 시스템
**목표**: Crew 실행 완료 시 알림

**작업 내용**:
- [ ] 이메일 알림 (SMTP)
- [ ] Slack/Discord 웹훅
- [ ] 알림 설정 관리 API

**예상 소요 시간**: 1일

---

#### 9-4. 통계 및 분석 대시보드
**목표**: Crew 실행 통계 제공

**작업 내용**:
- [ ] 실행 성공률 통계 API
- [ ] 평균 실행 시간 API
- [ ] 도구 사용 빈도 API
- [ ] 시계열 데이터 집계

**예상 소요 시간**: 1-2일

---

#### 9-5. Import/Export 기능
**목표**: Crew 설정 백업 및 공유

**작업 내용**:
- [ ] Export API (JSON/YAML)
- [ ] Import API
- [ ] 템플릿 라이브러리

**예상 소요 시간**: 1일

---

## 📊 우선순위 요약

### 🔥 즉시 착수 (핵심 기능)
1. **Crew 실행 API** (Phase 5-1) - 2-3일
2. **실행 히스토리 관리** (Phase 5-2) - 1-2일
3. **WebSocket 실시간 로그** (Phase 5-3) - 1-2일

**→ 총 4-7일 소요 (1주일 내)**

### ⚡ 다음 단계 (보안 및 연동)
4. **Keycloak 인증** (Phase 6-1) - 2-3일
5. **RBAC** (Phase 6-2) - 1-2일
6. **Streamlit API 클라이언트 전환** (Phase 7-1) - 3-5일

**→ 총 6-10일 소요 (2주 내)**

### 🚀 배포 준비
7. **Docker 컨테이너화** (Phase 8-1) - 1일
8. **docker-compose** (Phase 8-2) - 1일
9. **성능 최적화** (Phase 8-3) - 1-2일

**→ 총 3-4일 소요 (1주일 내)**

### 🎯 선택 기능 (나중에)
- 파일 업로드 관리
- 스케줄링
- 알림 시스템
- 통계 대시보드
- Import/Export

---

## 🎯 추천 작업 순서 (최소 MVP)

### Week 1: 핵심 기능
- [ ] Day 1-2: Crew 실행 API 구현
- [ ] Day 3: 실행 히스토리 관리
- [ ] Day 4: WebSocket 실시간 로그
- [ ] Day 5: 통합 테스트

### Week 2: 보안 및 프론트엔드
- [ ] Day 1-2: Keycloak 인증 통합
- [ ] Day 3: RBAC 구현
- [ ] Day 4-5: Streamlit → API 클라이언트 전환

### Week 3: 배포 준비
- [ ] Day 1: Docker 컨테이너화
- [ ] Day 2: docker-compose 설정
- [ ] Day 3: 성능 최적화
- [ ] Day 4-5: 통합 테스트 및 버그 수정

**→ 총 3주 내에 배포 가능한 MVP 완성!**

---

## 📝 기술 스택 정리

### 현재 사용 중
- **Backend Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL + pgvector
- **Migration**: Alembic
- **Validation**: Pydantic 2.0+
- **Logging**: Python logging + Discord webhook
- **API Docs**: Swagger UI, ReDoc

### 추가 필요 (Phase 5+)
- **Task Queue**: Celery + Redis (또는 FastAPI BackgroundTasks)
- **WebSocket**: FastAPI WebSocket
- **Auth**: Keycloak + python-jose
- **Caching**: Redis (선택)
- **File Storage**: AWS S3 또는 로컬 파일 시스템
- **Scheduler**: APScheduler (선택)
- **Container**: Docker + docker-compose

---

## 🔍 현재 프로젝트 구조

```
bend/
├── alembic/                    # DB 마이그레이션
├── api/                        # API 엔드포인트 ✅
│   ├── agents.py
│   ├── crews.py
│   ├── health.py
│   ├── knowledge.py
│   ├── tasks.py
│   └── tools.py
├── core/                       # 핵심 설정
├── database/                   # 데이터베이스 레이어 ✅
│   ├── models/                 # ORM 모델
│   └── repositories/           # Repository 패턴
├── logger/                     # 로깅 시스템 ✅
├── models/                     # 도메인 모델 ✅
├── schemas/                    # Pydantic 스키마 ✅
├── services/                   # Service 레이어 ✅
├── storage/                    # In-memory 저장소 (임시)
├── scripts/                    # 유틸리티 스크립트
├── tests/                      # 테스트 ✅
├── config.py                   # 설정
├── main.py                     # FastAPI 엔트리포인트 ✅
└── run.py                      # 개발 서버 실행 ✅
```

---

## ⚠️ 주의사항

1. **Phase 5 (Crew 실행 API)는 필수!**
   - 현재는 CRUD만 있고 실제 실행 기능이 없음
   - 이것 없이는 백엔드가 의미가 없음

2. **Keycloak 없이도 개발 가능**
   - 일단 인증 없이 개발 후 나중에 추가 가능
   - 개발 환경에서는 인증 건너뛰기 옵션 제공

3. **Streamlit vs 새 프론트엔드**
   - MVP는 기존 Streamlit 수정으로 충분
   - React/Vue는 장기 프로젝트

4. **성능 최적화는 마지막에**
   - 먼저 기능 완성 후 프로파일링
   - 실제 병목 지점 확인 후 최적화

---

## 📚 참고 문서

- **FastAPI WebSocket**: https://fastapi.tiangolo.com/advanced/websockets/
- **Celery + FastAPI**: https://fastapi.tiangolo.com/tutorial/background-tasks/
- **Keycloak Python**: https://github.com/marcospereirampj/python-keycloak
- **Docker 멀티 스테이지**: https://docs.docker.com/build/building/multi-stage/

---

**작성일**: 2025-10-21
**작성자**: AI Assistant
**프로젝트**: CrewAI Studio Backend
