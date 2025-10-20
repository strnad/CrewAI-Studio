# CrewAI Studio 수정 내역 (Modification Log)

## 🗓️ 2025-10-20

### 📦 패키지 업그레이드

#### embedchain 업그레이드
- **변경 전**: `embedchain==0.0.18`
- **변경 후**: `embedchain==0.1.128`
- **이유**: LangChain 1.0.0과의 호환성 문제 해결
  - 오래된 API `langchain.docstore.document` 사용으로 인한 ModuleNotFoundError 발생
  - LangChain Core 0.3.79와 호환되는 최신 버전으로 업그레이드

#### 연쇄 다운그레이드된 패키지들
```
langchain: 1.0.0 → 0.3.27
langchain-core: 1.0.0 → 0.3.79
langchain-community: 0.4 → 0.3.31
langchain-openai: 1.0.0 → 0.2.14
langchain-groq: 1.0.0 → 0.3.8
langchain-anthropic: 1.0.0 → 0.3.22
langchain-ollama: 1.0.0 → 0.3.10
chromadb: 설치 → 0.5.23
```

**📌 중요**: embedchain 0.1.128이 langchain 0.3.x를 요구하여 모든 langchain 관련 패키지가 0.3.x로 다운그레이드됨

---

### 🔧 코드 수정 (Pydantic v2 호환성)

CrewAI와 Pydantic v2 호환을 위한 타입 어노테이션 추가

#### 1. `app/tools/CustomApiTool.py`
**파일 위치**: `/app/tools/CustomApiTool.py:1,17`

**수정 내용**:
```python
# 변경 전
from typing import Optional, Dict, Any
class CustomApiTool(BaseTool):
    args_schema = CustomApiToolInputSchema

# 변경 후
from typing import Optional, Dict, Any, Type
class CustomApiTool(BaseTool):
    args_schema: Type[BaseModel] = CustomApiToolInputSchema
```

**에러 메시지**:
```
PydanticUserError: Field 'args_schema' defined on a base class was overridden by a
non-annotated attribute. All field definitions, including overrides, require a type
annotation.
```

---

#### 2. `app/tools/CustomFileWriteTool.py`
**파일 위치**: `/app/tools/CustomFileWriteTool.py:1,18`

**수정 내용**:
```python
# 변경 전
from typing import Optional, Dict, Any
class CustomFileWriteTool(BaseTool):
    args_schema = CustomFileWriteToolInputSchema

# 변경 후
from typing import Optional, Dict, Any, Type
class CustomFileWriteTool(BaseTool):
    args_schema: Type[BaseModel] = CustomFileWriteToolInputSchema
```

---

#### 3. `app/tools/ScrapeWebsiteToolEnhanced.py`
**파일 위치**: `/app/tools/ScrapeWebsiteToolEnhanced.py:24`

**상태**: ✅ 이미 올바르게 구현됨
```python
class ScrapeWebsiteToolEnhanced(BaseTool):
    args_schema: Type[BaseModel] = ScrapeWebsiteToolEnhancedSchema
```

---

## 📋 환경 정보

### 개발 환경
- **Python**: 3.11.13
- **Conda 환경**: `hfcrewai`
- **작업 디렉토리**: `/mnt/c/data/300.Workspaces/CrewAI-Studio`

### 주요 의존성 버전
```
streamlit: (설치됨)
crewai: (설치됨)
langchain: 0.3.27
langchain-core: 0.3.79
pydantic: 2.12.x
embedchain: 0.1.128
```

---

## 🐛 해결된 문제들

### 1. LangChain API 호환성 문제 (embedchain)
**증상**: `ModuleNotFoundError: No module named 'langchain.docstore'`

**근본 원인**:
- embedchain 0.0.18이 제거된 LangChain API 사용
- LangChain 1.0.0에서 `langchain.docstore.document`가 `langchain_core.documents`로 이동

**해결 방법**: embedchain을 0.1.128로 업그레이드하여 최신 LangChain API 사용

---

### 2. LangChain 통합 패키지 버전 충돌
**증상**: `ImportError: cannot import name 'content' from 'langchain_core.messages'`

**근본 원인**:
- embedchain 0.1.128이 langchain 0.3.x 의존성 요구
- langchain-groq 1.0.0이 langchain-core 1.0.0의 API 사용
- langchain-core가 0.3.79로 다운그레이드되면서 1.0.0 API 제거됨

**해결 방법**:
```bash
pip install 'langchain-groq<1.0.0' 'langchain-anthropic<1.0.0' 'langchain-ollama<1.0.0'
```
- langchain-groq: 1.0.0 → 0.3.8
- langchain-anthropic: 1.0.0 → 0.3.22
- langchain-ollama: 1.0.0 → 0.3.10

---

### 3. Pydantic v2 타입 어노테이션 문제
**증상**: `PydanticUserError: Field 'args_schema' defined on a base class was overridden`

**근본 원인**:
- Pydantic v2는 모든 필드 오버라이드에 타입 어노테이션 필수
- CrewAI BaseTool이 `args_schema` 필드를 정의하고 있음
- 자식 클래스에서 타입 없이 오버라이드하면 에러 발생

**해결 방법**: `args_schema: Type[BaseModel] = ...` 형태로 타입 어노테이션 추가

---

## 🔜 예정된 작업

### Phase 1: embedchain → LlamaIndex 마이그레이션
- [ ] LlamaIndex 패키지 설치
- [ ] CSVSearchToolEnhanced.py 리팩토링
- [ ] Knowledge source 시스템 업데이트
- [ ] 테스트 및 검증

### Phase 2: 국제화(i18n) 구현
- [ ] i18n 인프라 구축 (JSON 기반)
- [ ] 한글 번역 파일 생성
- [ ] UI 텍스트 국제화 적용
- [ ] 언어 선택 UI 추가

### Phase 3: UI 테마 개선
- [ ] 색상 스키마 선택
- [ ] config.toml 업데이트
- [ ] 추가 스타일링

---

## 📝 참고사항

### 코드 변경 원칙
1. **최소한의 변경**: 기존 기능 유지하면서 호환성만 수정
2. **타입 안전성**: 모든 오버라이드에 명시적 타입 어노테이션 추가
3. **하위 호환성**: 기존 API 인터페이스 유지

### 테스트 방법
```bash
cd /mnt/c/data/300.Workspaces/CrewAI-Studio
streamlit run app/app.py
```

---

## 🚀 REST API 백엔드 전환 (모노레포 구조)

### Phase 1: FastAPI 기본 구조 생성 ✅

**작업 일시**: 2025-10-20

**새로 생성된 파일**:
```
bend/                           # 백엔드 디렉토리
├── main.py                     # FastAPI 엔트리포인트
├── config.py                   # 설정 관리 (Keycloak 준비)
├── requirements.txt            # 백엔드 의존성
├── run.py                      # 개발 서버 실행 스크립트
├── README.md                   # 백엔드 문서
├── .gitignore                  # Git 제외 파일
│
├── api/
│   └── health.py              # 헬스체크 API 엔드포인트
│
└── database/
    └── connection.py          # DB 연결 관리 (SQLAlchemy)
```

**기술 스택**:
- FastAPI 0.104+
- SQLAlchemy 2.0+
- Pydantic 2.0+
- Uvicorn (ASGI server)
- Python-Jose (JWT, Keycloak 준비)

**주요 기능**:
- ✅ CORS 설정 (Streamlit 연동 준비)
- ✅ Rate Limiting (slowapi)
- ✅ 데이터베이스 연결 (SQLite/PostgreSQL 지원)
- ✅ API 자동 문서화 (Swagger UI, ReDoc)
- ✅ Keycloak/OIDC 설정 준비 (환경변수)

**API 엔드포인트**:
- `GET /` - 루트 엔드포인트 (API 정보)
- `GET /api/health` - 기본 헬스체크
- `GET /api/health/detailed` - 상세 헬스체크 (DB 포함)
- `GET /api/version` - 버전 정보

**실행 방법**:
```bash
cd bend
python run.py
# 또는
uvicorn main:app --reload
```

---

### Phase 2-1: Crew 도메인 모델 분리 ✅

**작업 일시**: 2025-10-20

**새로 생성된 파일**:
- `bend/models/crew.py` - 순수 도메인 모델
- `bend/schemas/crew.py` - Pydantic API 스키마

**주요 변경사항**:

#### 1. `bend/models/crew.py`
**설계 철학**: Streamlit 의존성을 완전히 제거한 순수 비즈니스 로직

```python
@dataclass
class CrewModel:
    """Streamlit 없는 순수 도메인 모델"""
    id: str
    name: str
    agents: List[Any]
    tasks: List[Any]
    process: Process
    # ... 기타 필드
```

**제거된 UI 관련 코드**:
- ❌ `import streamlit as st`
- ❌ `from streamlit import session_state as ss`
- ❌ `draw()` 메서드 (UI 렌더링)
- ❌ `set_editable()` 메서드
- ❌ `update_*()` 메서드들 (UI 상태 업데이트)
- ❌ `edit_key`, `tasks_order_key` (세션 상태 키)

**추가된 기능**:
- ✅ `validate()` - 에러/경고 딕셔너리 반환
- ✅ `to_dict()` - 직렬화
- ✅ `from_dict()` - 역직렬화 (with registries)
- ✅ `get_crewai_crew()` - CrewAI 인스턴스 변환

**검증 로직 개선**:
```python
# 변경 전 (my_crew.py)
def is_valid(self, show_warning=False):
    if len(self.agents) == 0:
        if show_warning:
            st.warning("...")
        return False

# 변경 후 (crew.py)
def validate(self) -> Dict[str, List[str]]:
    errors = []
    warnings = []
    if len(self.agents) == 0:
        errors.append(f"Crew '{self.name}' has no agents")
    return {'errors': errors, 'warnings': warnings, 'is_valid': len(errors) == 0}
```

#### 2. `bend/schemas/crew.py`
**Pydantic 기반 API 요청/응답 스키마**:

```python
class CrewCreate(BaseModel):
    """크루 생성 요청"""
    name: str
    agent_ids: List[str]
    task_ids: List[str]
    # ... 기타 필드

class CrewUpdate(BaseModel):
    """크루 수정 요청 (모든 필드 optional)"""
    name: Optional[str] = None
    # ...

class CrewResponse(BaseModel):
    """크루 조회 응답"""
    id: str
    name: str
    created_at: str
    # ...

class CrewExecutionRequest(BaseModel):
    """크루 실행 요청"""
    crew_id: str
    inputs: dict = {}
```

**기존 코드 유지**:
- ✅ `app/my_crew.py` - Streamlit UI에서 계속 사용
- ✅ 기존 기능 100% 호환 유지

---

## 📦 모노레포 구조

```
CrewAI-Studio/
├── bend/              # 🆕 백엔드 (FastAPI REST API)
├── app/               # 기존 Streamlit 프론트엔드 (점진적 전환 예정)
├── frnt/              # (예정) 새 프론트엔드 (React/Vue)
└── shared/            # (예정) 공유 코드
```

---

## 🔜 다음 작업 (Phase 2 계속)

### Phase 2-2: Agent 도메인 모델 분리
- [ ] `app/my_agent.py` → `bend/models/agent.py`
- [ ] `bend/schemas/agent.py` 생성

### Phase 2-3: Task 도메인 모델 분리
- [ ] `app/my_task.py` → `bend/models/task.py`
- [ ] `bend/schemas/task.py` 생성

### Phase 2-4: Tool 도메인 모델 분리
- [ ] `app/my_tools.py` → `bend/models/tool.py`
- [ ] `bend/schemas/tool.py` 생성

### Phase 2-5: Knowledge 도메인 모델 분리
- [ ] `app/my_knowledge_source.py` → `bend/models/knowledge.py`
- [ ] `bend/schemas/knowledge.py` 생성

### Phase 3: API 엔드포인트 구현
- [ ] Crews CRUD API
- [ ] Agents CRUD API
- [ ] Tasks CRUD API
- [ ] Tools CRUD API
- [ ] Knowledge CRUD API
- [ ] Execution API (WebSocket)

### Phase 4: 비즈니스 로직 분리
- [ ] Service 레이어 구현
- [ ] Repository 패턴 적용

### Phase 5: 인증 및 보안
- [ ] Keycloak/OIDC 통합
- [ ] JWT 토큰 검증
- [ ] Role-based access control

### Phase 6: 프론트엔드 연동
- [ ] Streamlit UI를 REST API 클라이언트로 변경
- [ ] (선택) React/Vue 새 프론트엔드

### Phase 7: 배포 및 최적화
- [ ] Docker 컨테이너화
- [ ] docker-compose 멀티 서비스
- [ ] 성능 최적화 및 캐싱

---

## 👥 작성자
- 수정 일자: 2025-10-20
- 환경: WSL2 Ubuntu + Conda (hfcrewai)
- 목적: LangChain 1.0 호환 및 Pydantic v2 호환성 확보 / REST API 백엔드 구축
