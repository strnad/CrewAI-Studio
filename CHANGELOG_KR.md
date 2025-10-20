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

### Phase 2-2: Agent 도메인 모델 분리 ✅

**작업 일시**: 2025-10-20

**새로 생성된 파일**:
- `bend/models/agent.py` - 순수 도메인 모델
- `bend/schemas/agent.py` - Pydantic API 스키마

**주요 변경사항**:

#### 1. `bend/models/agent.py`
**설계 철학**: Streamlit 의존성을 완전히 제거한 순수 비즈니스 로직

```python
@dataclass
class AgentModel:
    """Streamlit 없는 순수 도메인 모델"""
    id: str
    role: str
    backstory: str
    goal: str
    temperature: float
    allow_delegation: bool
    verbose: bool
    cache: bool
    llm_provider_model: str
    max_iter: int
    tools: List[Any]
    knowledge_source_ids: List[str]
```

**제거된 UI 관련 코드**:
- ❌ `import streamlit as st`
- ❌ `from streamlit import session_state as ss`
- ❌ `draw()` 메서드 (UI 렌더링)
- ❌ `set_editable()` 메서드
- ❌ `delete()` 메서드 (UI 상태 업데이트)
- ❌ `edit_key`, `edit` 프로퍼티 (세션 상태 키)

**추가된 기능**:
- ✅ `validate(available_llm_models)` - 에러/경고 딕셔너리 반환
- ✅ `validate_llm_provider_model(available_models)` - LLM 모델 검증
- ✅ `to_dict()` - 직렬화
- ✅ `from_dict()` - 역직렬화 (with registries)
- ✅ `get_crewai_agent()` - CrewAI Agent 인스턴스 변환

**검증 로직 개선**:
```python
# 변경 전 (my_agent.py)
def is_valid(self, show_warning=False):
    for tool in self.tools:
        if not tool.is_valid(show_warning=show_warning):
            if show_warning:
                st.warning(t('agents.warning_tool_invalid', tool_name=tool.name))
            return False
    return True

# 변경 후 (agent.py)
def validate(self, available_llm_models=None) -> Dict[str, Any]:
    errors = []
    warnings = []
    if not self.role or not self.role.strip():
        errors.append(f"Agent '{self.id}' has no role defined")
    # ... 추가 검증 로직
    for tool in self.tools:
        tool_validation = tool.validate()
        if not tool_validation.get('is_valid', False):
            errors.append(f"Agent '{self.id}' has invalid tool '{tool.name}'")
    return {'errors': errors, 'warnings': warnings, 'is_valid': len(errors) == 0}
```

#### 2. `bend/schemas/agent.py`
**Pydantic 기반 API 요청/응답 스키마**:

```python
class AgentCreate(BaseModel):
    """에이전트 생성 요청"""
    role: str = Field(..., min_length=1, max_length=500)
    backstory: str
    goal: str
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    llm_provider_model: str
    tool_ids: List[str] = Field(default_factory=list)
    # ... 기타 필드

class AgentUpdate(BaseModel):
    """에이전트 수정 요청 (모든 필드 optional)"""
    role: Optional[str] = None
    # ...

class AgentResponse(BaseModel):
    """에이전트 조회 응답"""
    id: str
    role: str
    created_at: str
    # ...

class AgentValidationResponse(BaseModel):
    """에이전트 검증 응답"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
```

**기존 코드 유지**:
- ✅ `app/my_agent.py` - Streamlit UI에서 계속 사용
- ✅ 기존 기능 100% 호환 유지

---

### Phase 2-3: Task 도메인 모델 분리 ✅

**작업 일시**: 2025-10-20

**새로 생성된 파일**:
- `bend/models/task.py` - 순수 도메인 모델
- `bend/schemas/task.py` - Pydantic API 스키마

**주요 변경사항**:

#### 1. `bend/models/task.py`
**설계 철학**: Streamlit 의존성을 완전히 제거한 순수 비즈니스 로직

```python
@dataclass
class TaskModel:
    """Streamlit 없는 순수 도메인 모델"""
    id: str
    description: str
    expected_output: str
    agent: Optional[Any]  # AgentModel reference
    async_execution: bool
    context_from_async_tasks_ids: Optional[List[str]]
    context_from_sync_tasks_ids: Optional[List[str]]
    created_at: str
```

**제거된 UI 관련 코드**:
- ❌ `import streamlit as st`
- ❌ `from streamlit import session_state as ss`
- ❌ `draw()` 메서드 (UI 렌더링)
- ❌ `set_editable()` 메서드
- ❌ `delete()` 메서드 (UI 상태 업데이트)
- ❌ `edit_key`, `edit` 프로퍼티 (세션 상태 키)

**추가된 기능**:
- ✅ `validate()` - 에러/경고 딕셔너리 반환
- ✅ `to_dict()` - 직렬화
- ✅ `from_dict()` - 역직렬화 (with agent registry)
- ✅ `get_crewai_task()` - CrewAI Task 인스턴스 변환 (개선)

**검증 로직 개선**:
```python
# 변경 전 (my_task.py)
def is_valid(self, show_warning=False):
    if not self.agent:
        if show_warning:
            st.warning(t('tasks.warning_no_agent', description=self.description))
        return False
    if not self.agent.is_valid(show_warning):
        return False
    return True

# 변경 후 (task.py)
def validate(self) -> Dict[str, Any]:
    errors = []
    warnings = []
    if not self.description or not self.description.strip():
        errors.append(f"Task '{self.id}' has no description")
    if not self.agent:
        errors.append(f"Task '{self.description[:50]}...' has no agent assigned")
    else:
        agent_validation = self.agent.validate()
        if not agent_validation.get('is_valid', False):
            errors.append(f"Task has invalid agent: {agent_validation.get('errors', [])}")
    if self.async_execution and not self.context_from_async_tasks_ids:
        warnings.append(f"Task is async but has no context tasks defined")
    return {'errors': errors, 'warnings': warnings, 'is_valid': len(errors) == 0}
```

#### 2. `bend/schemas/task.py`
**Pydantic 기반 API 요청/응답 스키마**:

```python
class TaskCreate(BaseModel):
    """작업 생성 요청"""
    description: str = Field(..., min_length=1)
    expected_output: str = Field(..., min_length=1)
    agent_id: str
    async_execution: bool = Field(default=False)
    context_from_async_tasks_ids: Optional[List[str]] = None
    context_from_sync_tasks_ids: Optional[List[str]] = None

class TaskUpdate(BaseModel):
    """작업 수정 요청 (모든 필드 optional)"""
    description: Optional[str] = None
    # ...

class TaskResponse(BaseModel):
    """작업 조회 응답"""
    id: str
    description: str
    agent_id: str
    created_at: str
    # ...

class TaskValidationResponse(BaseModel):
    """작업 검증 응답"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
```

**기존 코드 유지**:
- ✅ `app/my_task.py` - Streamlit UI에서 계속 사용
- ✅ 기존 기능 100% 호환 유지

---

### Phase 2-4: Tool 도메인 모델 분리 ✅

**작업 일시**: 2025-10-20

**새로 생성된 파일**:
- `bend/models/tool.py` - 순수 도메인 모델 (베이스 클래스)
- `bend/schemas/tool.py` - Pydantic API 스키마

**주요 변경사항**:

#### 1. `bend/models/tool.py`
**설계 철학**: Streamlit 의존성을 제거한 베이스 Tool 모델

```python
@dataclass
class ToolModel:
    """베이스 Tool 도메인 모델"""
    tool_id: str
    name: str
    description: str
    parameters: Dict[str, Any]
    parameters_metadata: Dict[str, Dict[str, Any]]

    def create_tool(self):
        """서브클래스에서 구현"""
        raise NotImplementedError
```

**제거된 UI 관련 코드**:
- ❌ `import streamlit as st`
- ❌ `st.warning()` 호출 (검증 경고)

**추가된 기능**:
- ✅ `validate()` - 에러/경고 딕셔너리 반환
- ✅ `to_dict()` - 직렬화
- ✅ `from_dict()` - 역직렬화
- ✅ `get_parameters()`, `set_parameters()` - 파라미터 관리
- ✅ `is_parameter_mandatory()` - 필수 파라미터 확인

**검증 로직 개선**:
```python
# 변경 전 (my_tools.py)
def is_valid(self, show_warning=False):
    for param_name, metadata in self.parameters_metadata.items():
        if metadata['mandatory'] and not self.parameters.get(param_name):
            if show_warning:
                st.warning(t('tools.warning_parameter_mandatory',
                           param_name=param_name, tool_name=self.name))
            return False
    return True

# 변경 후 (tool.py)
def validate(self) -> Dict[str, Any]:
    errors = []
    warnings = []
    for param_name, metadata in self.parameters_metadata.items():
        if metadata.get('mandatory', False) and not self.parameters.get(param_name):
            errors.append(f"Parameter '{param_name}' is mandatory for tool '{self.name}'")
    if not self.name:
        errors.append("Tool has no name defined")
    return {'errors': errors, 'warnings': warnings, 'is_valid': len(errors) == 0}
```

**29개 Tool 서브클래스 처리**:
- 📝 `app/my_tools.py`의 29개 서브클래스는 Streamlit UI에서 계속 사용
- 🔄 Phase 3 API 구현 시, 필요하면 bend/models/에 Streamlit 없는 버전 생성 예정
- ✅ 베이스 ToolModel은 공통 기능 (검증, 직렬화) 제공

#### 2. `bend/schemas/tool.py`
**Pydantic 기반 API 요청/응답 스키마**:

```python
class ToolCreate(BaseModel):
    """도구 생성 요청"""
    name: str = Field(..., min_length=1, max_length=255)
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    parameters_metadata: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

class ToolUpdate(BaseModel):
    """도구 수정 요청 (모든 필드 optional)"""
    name: Optional[str] = None
    # ...

class ToolResponse(BaseModel):
    """도구 조회 응답"""
    tool_id: str
    name: str
    description: str
    parameters: Dict[str, Any]
    # ...

class ToolTypeInfo(BaseModel):
    """사용 가능한 도구 타입 정보"""
    name: str
    description: str
    required_parameters: List[str]
    optional_parameters: List[str]

class ToolTypesListResponse(BaseModel):
    """도구 타입 목록 응답 (29개 도구 정보)"""
    tool_types: List[ToolTypeInfo]
    total: int
```

**기존 코드 유지**:
- ✅ `app/my_tools.py` - Streamlit UI 및 29개 서브클래스 계속 사용
- ✅ 기존 기능 100% 호환 유지

---

### Phase 2-5: Knowledge 도메인 모델 분리 ✅

**작업 일시**: 2025-10-20

**새로 생성된 파일**:
- `bend/models/knowledge.py` - 순수 도메인 모델
- `bend/schemas/knowledge.py` - Pydantic API 스키마

**주요 변경사항**:

#### 1. `bend/models/knowledge.py`
**설계 철학**: Streamlit 의존성을 완전히 제거한 순수 비즈니스 로직

```python
@dataclass
class KnowledgeSourceModel:
    """Streamlit 없는 순수 도메인 모델"""
    id: str
    name: str
    source_type: str  # string, text_file, pdf, csv, excel, json, docling
    source_path: str  # For file-based sources
    content: str  # For string-based sources
    metadata: Dict[str, Any]
    chunk_size: int
    chunk_overlap: int
    created_at: str
```

**제거된 UI 관련 코드**:
- ❌ `import streamlit as st`
- ❌ `from streamlit import session_state as ss`
- ❌ `draw()` 메서드 (UI 렌더링, 파일 업로더)
- ❌ `set_editable()` 메서드
- ❌ `delete()` 메서드 (UI 상태 업데이트)
- ❌ `edit_key`, `edit` 프로퍼티 (세션 상태 키)

**추가된 기능**:
- ✅ `validate(knowledge_base_path)` - 에러/경고 딕셔너리 반환
- ✅ `find_file(file_path, knowledge_base_path)` - 파일 경로 검증 (개선)
- ✅ `to_dict()` - 직렬화
- ✅ `from_dict()` - 역직렬화
- ✅ `get_crewai_knowledge_source(knowledge_base_path)` - CrewAI 인스턴스 변환 (개선)

**검증 로직 개선**:
```python
# 변경 전 (my_knowledge_source.py)
def is_valid(self, show_warning=False):
    if self.source_type == "string" and not self.content:
        if show_warning:
            st.warning(t('knowledge.warning_no_content', name=self.name))
        return False
    if self.source_type != "string" and not self.source_path:
        if show_warning:
            st.warning(t('knowledge.warning_no_path', name=self.name))
        return False
    # ... 파일 검증
    return True

# 변경 후 (knowledge.py)
def validate(self, knowledge_base_path="knowledge") -> Dict[str, Any]:
    errors = []
    warnings = []
    if self.source_type == "string" and not self.content:
        errors.append(f"Knowledge source '{self.name}' (type: string) has no content")
    if self.source_type not in ["string", "docling"] and not self.source_path:
        errors.append(f"Knowledge source '{self.name}' has no source path")
    else:
        actual_path = self.find_file(self.source_path, knowledge_base_path)
        if not actual_path:
            errors.append(f"File not found at '{self.source_path}'")
    if self.chunk_overlap >= self.chunk_size:
        errors.append(f"chunk_overlap must be less than chunk_size")
    return {'errors': errors, 'warnings': warnings, 'is_valid': len(errors) == 0}
```

**지원하는 Knowledge Source 타입** (7가지):
1. **string**: 문자열 기반 지식 소스
2. **text_file**: 텍스트 파일 (.txt)
3. **pdf**: PDF 문서
4. **csv**: CSV 파일
5. **excel**: Excel 파일 (.xlsx, .xls)
6. **json**: JSON 파일
7. **docling**: Docling 기반 소스

#### 2. `bend/schemas/knowledge.py`
**Pydantic 기반 API 요청/응답 스키마**:

```python
class KnowledgeSourceCreate(BaseModel):
    """지식 소스 생성 요청"""
    name: str = Field(..., min_length=1, max_length=255)
    source_type: str  # string, text_file, pdf, csv, excel, json, docling
    source_path: str = Field(default="")
    content: str = Field(default="")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunk_size: int = Field(default=4000, ge=100, le=8000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)

class KnowledgeSourceUpdate(BaseModel):
    """지식 소스 수정 요청 (모든 필드 optional)"""
    name: Optional[str] = None
    # ...

class KnowledgeSourceResponse(BaseModel):
    """지식 소스 조회 응답"""
    id: str
    name: str
    source_type: str
    created_at: str
    # ...

class KnowledgeSourceTypeInfo(BaseModel):
    """지원하는 지식 소스 타입 정보"""
    type: str
    display_name: str
    requires_file: bool
    supported_extensions: List[str]

class KnowledgeSourceTypesListResponse(BaseModel):
    """지식 소스 타입 목록 응답 (7개 타입 정보)"""
    source_types: List[KnowledgeSourceTypeInfo]
    total: int
```

**기존 코드 유지**:
- ✅ `app/my_knowledge_source.py` - Streamlit UI에서 계속 사용
- ✅ 기존 기능 100% 호환 유지

---

### Phase 3: API 엔드포인트 구현

#### Phase 3-1: Crews CRUD API ✅

**작업 일시**: 2025-10-20

**새로 생성된 파일**:
- `bend/api/crews.py` - Crews CRUD API 엔드포인트
- `bend/storage/memory.py` - In-memory 저장소 (개발용)
- `bend/tests/test_api_crews.py` - Python 기반 API 테스트 스크립트
- `bend/tests/README.md` - 테스트 사용 가이드

**구현된 API 엔드포인트**:
```
GET    /api/crews              # 모든 Crew 조회
GET    /api/crews/{crew_id}    # 특정 Crew 조회
POST   /api/crews              # Crew 생성
PUT    /api/crews/{crew_id}    # Crew 수정
DELETE /api/crews/{crew_id}    # Crew 삭제
POST   /api/crews/{crew_id}/validate  # Crew 검증
```

**주요 기능**:
- ✅ CRUD 전체 작업 (Create, Read, Update, Delete)
- ✅ Crew 검증 API (validate() 메서드 활용)
- ✅ Agent/Task 참조 검증 (404, 400 에러 처리)
- ✅ Process 타입 지원 (sequential, hierarchical)
- ✅ Manager LLM/Agent 지원
- ✅ Knowledge Source 참조
- ✅ In-memory 저장소 (Phase 4에서 DB로 변경 예정)

**테스트 스크립트** (`test_api_crews.py`):
- ✅ 컬러 출력 (성공/실패 구분)
- ✅ Health Check 테스트
- ✅ CRUD 전체 플로우 테스트
- ✅ 에러 케이스 테스트 (404, 400)
- ✅ 검증 API 테스트

**실행 방법**:
```bash
# 서버 실행
cd bend
python run.py

# 테스트 실행 (다른 터미널)
python bend/tests/test_api_crews.py
```

**API 문서**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

#### Phase 3-2: Agents CRUD API ✅

**작업 일시**: 2025-10-20

**새로 생성된 파일**:
- `bend/api/agents.py` - Agents CRUD API 엔드포인트
- `bend/tests/test_api_agents.py` - Python 기반 API 테스트 스크립트

**구현된 API 엔드포인트**:
```
GET    /api/agents              # 모든 Agent 조회
GET    /api/agents/{agent_id}   # 특정 Agent 조회
POST   /api/agents              # Agent 생성
PUT    /api/agents/{agent_id}   # Agent 수정
DELETE /api/agents/{agent_id}   # Agent 삭제
POST   /api/agents/{agent_id}/validate  # Agent 검증
```

**주요 기능**:
- ✅ CRUD 전체 작업 (Create, Read, Update, Delete)
- ✅ Agent 검증 API (validate() 메서드 활용)
- ✅ Tool 참조 검증 (404, 400 에러 처리)
- ✅ Knowledge Source 참조 검증
- ✅ LLM 설정 지원 (provider/model, temperature)
- ✅ Crew 의존성 검사 (사용 중인 Agent 삭제 방지)
- ✅ In-memory 저장소 연동

**테스트 스크립트** (`test_api_agents.py`):
- ✅ 컬러 출력 (성공/실패 구분)
- ✅ Health Check 테스트
- ✅ CRUD 전체 플로우 테스트
- ✅ 에러 케이스 테스트 (404, 400)
- ✅ 검증 API 테스트
- ✅ Tool ID 검증 테스트
- ✅ Crew 의존성 검증 테스트

**실행 방법**:
```bash
# 서버 실행
cd bend
python run.py

# 테스트 실행 (다른 터미널)
python bend/tests/test_api_agents.py
```

**API 문서**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

#### Phase 3-3: Tasks CRUD API ✅

**작업 일시**: 2025-10-20

**새로 생성된 파일**:
- `bend/api/tasks.py` - Tasks CRUD API 엔드포인트
- `bend/tests/test_api_tasks.py` - Python 기반 API 테스트 스크립트

**구현된 API 엔드포인트**:
```
GET    /api/tasks              # 모든 Task 조회
GET    /api/tasks/{task_id}    # 특정 Task 조회
POST   /api/tasks              # Task 생성
PUT    /api/tasks/{task_id}    # Task 수정
DELETE /api/tasks/{task_id}    # Task 삭제
POST   /api/tasks/{task_id}/validate  # Task 검증
```

**주요 기능**:
- ✅ CRUD 전체 작업 (Create, Read, Update, Delete)
- ✅ Task 검증 API (validate() 메서드 활용)
- ✅ Agent ID 참조 검증 (404, 400 에러 처리)
- ✅ Context Task 참조 검증 (async/sync)
- ✅ Context로 사용 중인 Task 삭제 방지
- ✅ Crew 의존성 검사 (사용 중인 Task 삭제 방지)
- ✅ Async/Sync 실행 모드 지원
- ✅ In-memory 저장소 연동

**테스트 스크립트** (`test_api_tasks.py`):
- ✅ 컬러 출력 (성공/실패 구분)
- ✅ Health Check 테스트
- ✅ CRUD 전체 플로우 테스트
- ✅ 에러 케이스 테스트 (404, 400)
- ✅ 검증 API 테스트
- ✅ Agent ID 검증 테스트
- ✅ Context Task 참조 테스트
- ✅ Context 사용 중인 Task 삭제 방지 테스트
- ✅ Crew 의존성 검증 테스트

**실행 방법**:
```bash
# 서버 실행
cd bend
python run.py

# 테스트 실행 (다른 터미널)
python bend/tests/test_api_tasks.py
```

**API 문서**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

#### Phase 3-4: Tools CRUD API ✅

**작업 일시**: 2025-10-20

**새로 생성된 파일**:
- `bend/api/tools.py` - Tools CRUD API 엔드포인트
- `bend/tests/test_api_tools.py` - Python 기반 API 테스트 스크립트

**구현된 API 엔드포인트**:
```
GET    /api/tools              # 모든 Tool 조회
GET    /api/tools/{tool_id}    # 특정 Tool 조회
POST   /api/tools              # Tool 생성
PUT    /api/tools/{tool_id}    # Tool 수정
DELETE /api/tools/{tool_id}    # Tool 삭제
POST   /api/tools/{tool_id}/validate  # Tool 검증
```

**주요 기능**:
- ✅ CRUD 전체 작업 (Create, Read, Update, Delete)
- ✅ Tool 검증 API (validate() 메서드 활용)
- ✅ 필수 파라미터 검증 (parameters_metadata 활용)
- ✅ Agent 의존성 검사 (사용 중인 Tool 삭제 방지)
- ✅ 파라미터 메타데이터 관리
- ✅ In-memory 저장소 연동

**테스트 스크립트** (`test_api_tools.py`):
- ✅ 컬러 출력 (성공/실패 구분)
- ✅ Health Check 테스트
- ✅ CRUD 전체 플로우 테스트
- ✅ 에러 케이스 테스트 (404, 400)
- ✅ 검증 API 테스트
- ✅ 필수 파라미터 누락 테스트
- ✅ Agent 의존성 검증 테스트

**실행 방법**:
```bash
# 서버 실행
cd bend
python run.py

# 테스트 실행 (다른 터미널)
python bend/tests/test_api_tools.py
```

**API 문서**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

#### Phase 3-5: Knowledge Sources CRUD API
- [ ] Knowledge Sources CRUD API 엔드포인트
- [ ] 테스트 스크립트

---

### Phase 4: 비즈니스 로직 분리
- [ ] Service 레이어 구현
- [ ] Repository 패턴 적용
- [ ] Database 연동 (SQLAlchemy)

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
