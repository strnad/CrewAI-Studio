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

## 👥 작성자
- 수정 일자: 2025-10-20
- 환경: WSL2 Ubuntu + Conda (hfcrewai)
- 목적: LangChain 1.0 호환 및 Pydantic v2 호환성 확보
