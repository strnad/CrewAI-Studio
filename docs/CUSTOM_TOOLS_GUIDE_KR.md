# CrewAI Studio 커스텀 도구 개발 가이드

CrewAI Studio에서 신규 커스텀 도구를 개발하기 위한 완전한 가이드입니다.

---

## 📚 목차

1. [개요](#개요)
2. [아키텍처](#아키텍처)
3. [개발 단계](#개발-단계)
4. [실전 예제](#실전-예제)
5. [등록 및 통합](#등록-및-통합)
6. [베스트 프랙티스](#베스트-프랙티스)
7. [트러블슈팅](#트러블슈팅)

---

## 개요

### 커스텀 도구란?

CrewAI Studio의 커스텀 도구는 CrewAI Agent가 사용할 수 있는 **특수 기능**을 제공하는 모듈입니다.

**기본 제공 도구 vs 커스텀 도구**:

| 구분 | 기본 제공 도구 (crewai-tools) | 커스텀 도구 (app/tools/) |
|------|------------------------------|-------------------------|
| 위치 | crewai-tools 패키지 | `app/tools/` 디렉토리 |
| 수정 | 불가능 (외부 패키지) | 가능 (직접 개발) |
| 예시 | CSVSearchTool, PDFSearchTool | CustomApiTool, DuckDuckGoSearchTool |

### 현재 커스텀 도구 목록

```
app/tools/
├── CustomApiTool.py                   # REST API 호출
├── CustomCodeInterpreterTool.py       # 코드 실행 및 해석
├── CustomFileWriteTool.py             # 파일 쓰기/추가
├── DuckDuckGoSearchTool.py            # 웹 검색
├── ScrapeWebsiteToolEnhanced.py       # 웹 스크래핑 (향상)
└── ScrapflyScrapeWebsiteTool.py       # Scrapfly 기반 스크래핑
```

---

## 아키텍처

### 2-Layer 구조

CrewAI Studio의 커스텀 도구는 **2개의 레이어**로 구성됩니다:

```
┌─────────────────────────────────────────┐
│  Layer 2: Wrapper Class (my_tools.py)  │ ← Streamlit UI 통합
│  예: MyCustomApiTool                    │
└─────────────────────────────────────────┘
              ↓ wraps
┌─────────────────────────────────────────┐
│  Layer 1: Tool Implementation           │ ← 실제 로직
│  (app/tools/CustomApiTool.py)           │
│  예: CustomApiTool (BaseTool 상속)      │
└─────────────────────────────────────────┘
```

#### Layer 1: Tool Implementation (app/tools/*.py)

**역할**: 실제 도구의 비즈니스 로직 구현

**필수 요소**:
1. **Input Schema** (Pydantic BaseModel)
   - Agent가 도구에 전달할 파라미터 정의
2. **Tool Class** (BaseTool 상속)
   - `name`: 도구 이름
   - `description`: 도구 설명
   - `args_schema`: Input Schema 클래스
   - `_run()`: 실제 실행 로직

#### Layer 2: Wrapper Class (app/my_tools.py)

**역할**: Streamlit UI와 Tool을 연결하는 어댑터

**필수 요소**:
1. **MyTool 상속**
2. **parameters_metadata**: UI에서 입력받을 설정값 정의
3. **create_tool()**: Layer 1의 Tool 인스턴스 생성

---

## 개발 단계

### Step 1: 요구사항 정의

다음 질문에 답하세요:

1. **도구의 목적은?**
   - 예: "외부 REST API를 호출해서 데이터를 가져온다"

2. **Agent가 제공해야 할 입력은?**
   - 예: `endpoint`, `method`, `headers`, `body`

3. **도구가 반환할 출력은?**
   - 예: `{"status_code": 200, "response": {...}}`

4. **UI에서 미리 설정할 값은?**
   - 예: `base_url`, `default_headers`

---

### Step 2: Layer 1 구현 (Tool Implementation)

#### 2-1. Input Schema 정의

```python
from pydantic.v1 import BaseModel, Field
from typing import Optional

class YourToolInputSchema(BaseModel):
    """Agent가 도구를 호출할 때 전달하는 파라미터"""

    # 필수 파라미터
    query: str = Field(..., description="검색할 쿼리 문자열")

    # 선택 파라미터
    max_results: int = Field(5, description="최대 결과 개수")
    region: Optional[str] = Field(None, description="검색 지역")
```

**중요**: `pydantic.v1`을 사용해야 합니다 (CrewAI 호환성)

#### 2-2. Tool Class 구현

```python
from crewai.tools import BaseTool
from typing import Type, Optional, Any

class YourCustomTool(BaseTool):
    # 1. 필수 속성
    name: str = "Your Tool Name"
    description: str = "What your tool does in detail"
    args_schema: Type[BaseModel] = YourToolInputSchema

    # 2. 커스텀 속성 (optional, UI에서 설정)
    base_url: Optional[str] = None
    api_key: Optional[str] = None

    # 3. 초기화 메서드
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url
        self.api_key = api_key
        self._generate_description()  # 설명 자동 생성 (선택)

    # 4. 실행 메서드 (핵심!)
    def _run(self, query: str, max_results: int = 5, region: Optional[str] = None) -> Any:
        """
        실제 도구 로직 구현

        Args:
            query: Input Schema에서 정의한 파라미터들
            max_results: ...
            region: ...

        Returns:
            도구 실행 결과 (문자열, 딕셔너리, 리스트 등)
        """
        try:
            # 여기에 실제 로직 구현
            result = self._perform_task(query, max_results, region)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    # 5. Helper 메서드 (optional)
    def _perform_task(self, query, max_results, region):
        # 실제 작업 수행
        pass
```

---

### Step 3: Layer 2 구현 (Wrapper Class)

`app/my_tools.py` 파일에 추가:

```python
class MyYourCustomTool(MyTool):
    """
    UI와 연동하기 위한 Wrapper 클래스
    """

    def __init__(self, tool_id=None, base_url=None, api_key=None):
        # 1. UI에서 입력받을 파라미터 정의
        parameters = {
            'base_url': {'mandatory': True},   # 필수
            'api_key': {'mandatory': False}    # 선택
        }

        # 2. 부모 클래스 초기화
        super().__init__(
            tool_id,
            'YourCustomTool',                  # TOOL_CLASSES의 키와 일치해야 함
            t('tools.desc_your_custom_tool'),  # i18n 번역 키 (또는 직접 문자열)
            parameters,
            base_url=base_url,
            api_key=api_key
        )

    # 3. Tool 인스턴스 생성 메서드
    def create_tool(self) -> YourCustomTool:
        return YourCustomTool(
            base_url=self.parameters.get('base_url'),
            api_key=self.parameters.get('api_key')
        )
```

---

### Step 4: 도구 등록

`app/my_tools.py` 파일의 **맨 위** (import 섹션):

```python
# 기존 imports...
from tools.YourCustomTool import YourCustomTool
```

`app/my_tools.py` 파일의 **TOOL_CLASSES 딕셔너리**에 추가:

```python
TOOL_CLASSES = {
    # 기존 도구들...
    'CustomApiTool': MyCustomApiTool,
    'CustomFileWriteTool': MyCustomFileWriteTool,

    # 신규 도구 추가
    'YourCustomTool': MyYourCustomTool,  # ← 여기 추가!
}
```

---

### Step 5: 국제화 (i18n) 추가 (선택)

`app/i18n/en.json`:

```json
{
  "tools": {
    "desc_your_custom_tool": "Description of your custom tool"
  }
}
```

`app/i18n/kr.json`:

```json
{
  "tools": {
    "desc_your_custom_tool": "커스텀 도구에 대한 설명"
  }
}
```

---

## 실전 예제

### 예제 1: 간단한 도구 - 날씨 조회 도구

**요구사항**: OpenWeatherMap API를 사용해서 특정 도시의 날씨를 조회

#### Layer 1: `app/tools/WeatherTool.py`

```python
from crewai.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from typing import Type, Optional
import requests

class WeatherToolInputSchema(BaseModel):
    """날씨 조회 입력 스키마"""
    city: str = Field(..., description="조회할 도시 이름 (예: Seoul, Tokyo)")
    units: str = Field("metric", description="온도 단위 (metric, imperial, kelvin)")

class WeatherTool(BaseTool):
    name: str = "Weather Checker"
    description: str = "Checks current weather for a given city using OpenWeatherMap API"
    args_schema: Type[BaseModel] = WeatherToolInputSchema

    # UI에서 설정할 값
    api_key: Optional[str] = None

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self._generate_description()

    def _run(self, city: str, units: str = "metric") -> str:
        """날씨 조회 실행"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # 결과 포맷팅
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            humidity = data['main']['humidity']

            return f"Weather in {city}: {weather}, Temperature: {temp}°C, Humidity: {humidity}%"

        except Exception as e:
            return f"Error fetching weather: {str(e)}"
```

#### Layer 2: `app/my_tools.py`에 추가

```python
# Import 섹션에 추가
from tools.WeatherTool import WeatherTool

# 클래스 추가
class MyWeatherTool(MyTool):
    def __init__(self, tool_id=None, api_key=None):
        parameters = {
            'api_key': {'mandatory': True}
        }
        super().__init__(tool_id, 'WeatherTool',
                        'Check current weather for any city',
                        parameters, api_key=api_key)

    def create_tool(self) -> WeatherTool:
        return WeatherTool(api_key=self.parameters.get('api_key'))

# TOOL_CLASSES에 추가
TOOL_CLASSES = {
    # ...
    'WeatherTool': MyWeatherTool,
}
```

---

### 예제 2: 중급 - 데이터베이스 조회 도구

**요구사항**: PostgreSQL 데이터베이스에서 SQL 쿼리 실행

#### Layer 1: `app/tools/DatabaseQueryTool.py`

```python
from crewai.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from typing import Type, Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseQueryToolInputSchema(BaseModel):
    """데이터베이스 쿼리 입력 스키마"""
    query: str = Field(..., description="실행할 SQL 쿼리 (SELECT만 허용)")
    limit: int = Field(100, description="최대 결과 개수")

class DatabaseQueryTool(BaseTool):
    name: str = "Database Query Tool"
    description: str = "Execute SELECT queries on PostgreSQL database and return results"
    args_schema: Type[BaseModel] = DatabaseQueryToolInputSchema

    # UI에서 설정
    connection_string: str

    def __init__(self, connection_string: str, **kwargs):
        super().__init__(**kwargs)
        self.connection_string = connection_string
        self._generate_description()

    def _run(self, query: str, limit: int = 100) -> str:
        """SQL 쿼리 실행"""
        try:
            # 보안: SELECT만 허용
            if not query.strip().upper().startswith('SELECT'):
                return "Error: Only SELECT queries are allowed"

            # LIMIT 추가
            if 'LIMIT' not in query.upper():
                query = f"{query} LIMIT {limit}"

            # DB 연결
            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # 쿼리 실행
            cursor.execute(query)
            results = cursor.fetchall()

            # 정리
            cursor.close()
            conn.close()

            # 결과 포맷팅
            if not results:
                return "Query returned no results"

            return self._format_results(results)

        except Exception as e:
            return f"Database error: {str(e)}"

    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """결과를 읽기 쉬운 형태로 변환"""
        output = f"Found {len(results)} rows:\n\n"

        for i, row in enumerate(results, 1):
            output += f"Row {i}:\n"
            for key, value in row.items():
                output += f"  {key}: {value}\n"
            output += "\n"

        return output
```

#### Layer 2: `app/my_tools.py`에 추가

```python
from tools.DatabaseQueryTool import DatabaseQueryTool

class MyDatabaseQueryTool(MyTool):
    def __init__(self, tool_id=None, connection_string=None):
        parameters = {
            'connection_string': {'mandatory': True}
        }
        super().__init__(tool_id, 'DatabaseQueryTool',
                        'Execute SELECT queries on PostgreSQL database',
                        parameters, connection_string=connection_string)

    def create_tool(self) -> DatabaseQueryTool:
        return DatabaseQueryTool(
            connection_string=self.parameters.get('connection_string')
        )

TOOL_CLASSES = {
    # ...
    'DatabaseQueryTool': MyDatabaseQueryTool,
}
```

---

### 예제 3: 고급 - 가변 Input Schema 도구

**요구사항**: 파일 경로가 고정되면 Input Schema에서 제외

#### Layer 1: `app/tools/FlexibleFileTool.py`

```python
from crewai.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from typing import Type, Optional

# 2가지 Input Schema 정의
class FixedFileInputSchema(BaseModel):
    """파일 경로가 고정된 경우"""
    content: str = Field(..., description="파일에 쓸 내용")

class FlexibleFileInputSchema(BaseModel):
    """파일 경로를 Agent가 지정하는 경우"""
    filepath: str = Field(..., description="파일 경로")
    content: str = Field(..., description="파일에 쓸 내용")

class FlexibleFileTool(BaseTool):
    name: str = "Flexible File Writer"
    description: str = "Write content to a file (flexible or fixed path)"
    args_schema: Type[BaseModel] = FlexibleFileInputSchema

    # 고정 파일 경로 (optional)
    fixed_filepath: Optional[str] = None

    def __init__(self, fixed_filepath: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.fixed_filepath = fixed_filepath

        # 파일 경로가 고정되면 Schema 변경
        if fixed_filepath:
            self.args_schema = FixedFileInputSchema

        self._generate_description()

    def _run(self, content: str, filepath: Optional[str] = None) -> str:
        """파일 쓰기 실행"""
        try:
            # 파일 경로 결정
            target_path = self.fixed_filepath or filepath

            if not target_path:
                return "Error: No filepath specified"

            # 파일 쓰기
            with open(target_path, 'w') as f:
                f.write(content)

            return f"Successfully wrote to {target_path}"

        except Exception as e:
            return f"File write error: {str(e)}"
```

#### Layer 2: `app/my_tools.py`에 추가

```python
from tools.FlexibleFileTool import FlexibleFileTool

class MyFlexibleFileTool(MyTool):
    def __init__(self, tool_id=None, fixed_filepath=None):
        parameters = {
            'fixed_filepath': {'mandatory': False}
        }
        super().__init__(tool_id, 'FlexibleFileTool',
                        'Write content to a file (flexible or fixed path)',
                        parameters, fixed_filepath=fixed_filepath)

    def create_tool(self) -> FlexibleFileTool:
        return FlexibleFileTool(
            fixed_filepath=self.parameters.get('fixed_filepath') if self.parameters.get('fixed_filepath') else None
        )

TOOL_CLASSES = {
    # ...
    'FlexibleFileTool': MyFlexibleFileTool,
}
```

---

## 등록 및 통합

### 체크리스트

- [ ] **Layer 1 파일 생성**: `app/tools/YourTool.py`
  - [ ] Input Schema 정의 (pydantic.v1 사용)
  - [ ] BaseTool 상속
  - [ ] `name`, `description`, `args_schema` 설정
  - [ ] `_run()` 메서드 구현

- [ ] **Layer 2 등록**: `app/my_tools.py`
  - [ ] Import 추가 (파일 상단)
  - [ ] Wrapper 클래스 생성 (MyTool 상속)
  - [ ] `create_tool()` 메서드 구현
  - [ ] `TOOL_CLASSES` 딕셔너리에 추가

- [ ] **i18n 추가** (선택)
  - [ ] `app/i18n/en.json`
  - [ ] `app/i18n/kr.json`

- [ ] **테스트**
  - [ ] Streamlit UI에서 도구 선택 가능한지 확인
  - [ ] Agent에서 도구 실행 테스트

---

## 베스트 프랙티스

### 1. Input Schema 설계

**DO ✅**:
```python
class GoodInputSchema(BaseModel):
    query: str = Field(..., description="명확하고 구체적인 설명")
    max_results: int = Field(10, ge=1, le=100, description="1-100 사이의 값")
```

**DON'T ❌**:
```python
class BadInputSchema(BaseModel):
    q: str  # 설명 없음, 파라미터 이름 불명확
    n: int = 10  # 범위 제한 없음
```

### 2. 에러 처리

**DO ✅**:
```python
def _run(self, query: str) -> str:
    try:
        result = self._perform_task(query)
        return result
    except ValueError as e:
        return f"Invalid input: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
```

**DON'T ❌**:
```python
def _run(self, query: str) -> str:
    result = self._perform_task(query)  # 에러 처리 없음
    return result
```

### 3. 보안

**DO ✅**:
```python
def _run(self, filepath: str) -> str:
    # 경로 검증
    if '..' in filepath or filepath.startswith('/'):
        return "Invalid filepath"

    full_path = os.path.join(self.base_folder, filepath)

    # 경로 벗어남 방지
    if not full_path.startswith(os.path.abspath(self.base_folder)):
        return "Access denied"
```

**DON'T ❌**:
```python
def _run(self, filepath: str) -> str:
    with open(filepath, 'r') as f:  # 경로 검증 없음
        return f.read()
```

### 4. 반환값 포맷

**DO ✅**:
```python
def _run(self, query: str) -> str:
    results = self._search(query)

    # 사람이 읽기 쉬운 형태
    output = "Search Results:\n\n"
    for i, result in enumerate(results, 1):
        output += f"{i}. {result['title']}\n"
        output += f"   {result['description']}\n\n"

    return output
```

**DON'T ❌**:
```python
def _run(self, query: str) -> str:
    results = self._search(query)
    return str(results)  # 딕셔너리를 그냥 문자열로 변환
```

### 5. 필수 파라미터 검증

**DO ✅**:
```python
class MyCustomTool(MyTool):
    def __init__(self, tool_id=None, api_key=None):
        parameters = {
            'api_key': {'mandatory': True}  # 필수로 지정
        }
        super().__init__(tool_id, 'CustomTool', 'Description', parameters, api_key=api_key)
```

### 6. Pydantic 버전 주의

**DO ✅**:
```python
from pydantic.v1 import BaseModel, Field  # v1 사용
```

**DON'T ❌**:
```python
from pydantic import BaseModel, Field  # v2는 CrewAI와 호환 안됨
```

### 7. Type Annotation

**DO ✅**:
```python
from typing import Type

class CustomTool(BaseTool):
    args_schema: Type[BaseModel] = CustomInputSchema  # 타입 어노테이션 필수
```

**DON'T ❌**:
```python
class CustomTool(BaseTool):
    args_schema = CustomInputSchema  # Pydantic v2 에러 발생
```

---

## 트러블슈팅

### 문제 1: "Field 'args_schema' defined on a base class was overridden"

**원인**: Pydantic v2 호환성 문제

**해결**:
```python
# 변경 전 ❌
class CustomTool(BaseTool):
    args_schema = CustomInputSchema

# 변경 후 ✅
from typing import Type

class CustomTool(BaseTool):
    args_schema: Type[BaseModel] = CustomInputSchema
```

---

### 문제 2: "ModuleNotFoundError: No module named 'pydantic.v1'"

**원인**: pydantic v1이 설치되지 않음

**해결**:
```bash
pip install 'pydantic<2.0.0'
# 또는
pip install pydantic==1.10.13
```

---

### 문제 3: 도구가 UI에 나타나지 않음

**체크리스트**:

1. `app/my_tools.py` **Import 섹션** 확인:
   ```python
   from tools.YourTool import YourTool
   ```

2. **Wrapper 클래스** 작성 확인:
   ```python
   class MyYourTool(MyTool):
       # ...
   ```

3. **TOOL_CLASSES** 딕셔너리 등록 확인:
   ```python
   TOOL_CLASSES = {
       # ...
       'YourTool': MyYourTool,
   }
   ```

4. **Streamlit 재시작**:
   ```bash
   # Ctrl+C로 중지 후 재실행
   streamlit run app/app.py
   ```

---

### 문제 4: "Tool execution failed"

**디버깅**:

1. **_run() 메서드에 print 추가**:
   ```python
   def _run(self, query: str) -> str:
       print(f"[DEBUG] Query: {query}")  # 입력값 확인
       try:
           result = self._perform_task(query)
           print(f"[DEBUG] Result: {result}")  # 결과 확인
           return result
       except Exception as e:
           print(f"[ERROR] {e}")  # 에러 확인
           return f"Error: {str(e)}"
   ```

2. **터미널 로그 확인**:
   - Streamlit을 실행한 터미널에서 에러 메시지 확인

---

### 문제 5: Input Schema가 Agent에 전달되지 않음

**원인**: Input Schema 정의 누락 또는 잘못된 타입

**해결**:
```python
# 필수 요소 확인
class YourInputSchema(BaseModel):
    param: str = Field(..., description="설명 필수!")  # description 필수!

class YourTool(BaseTool):
    args_schema: Type[BaseModel] = YourInputSchema  # 타입 어노테이션 필수!
```

---

## 부록: 실제 코드 예제 참고

### 참고할 만한 기존 도구

| 도구 | 파일 위치 | 특징 |
|------|----------|------|
| **CustomApiTool** | `app/tools/CustomApiTool.py` | REST API 호출 기본 패턴 |
| **CustomFileWriteTool** | `app/tools/CustomFileWriteTool.py` | 가변 Input Schema 패턴 |
| **DuckDuckGoSearchTool** | `app/tools/DuckDuckGoSearchTool.py` | 외부 라이브러리 통합 |
| **ScrapeWebsiteToolEnhanced** | `app/tools/ScrapeWebsiteToolEnhanced.py` | 복잡한 로직 + 여러 Helper 메서드 |

### 추가 학습 자료

- **CrewAI 공식 문서**: https://docs.crewai.com/core-concepts/Tools/
- **Pydantic v1 문서**: https://docs.pydantic.dev/1.10/
- **BaseTool 소스코드**: https://github.com/joaomdmoura/crewAI/blob/main/src/crewai/tools/base_tool.py

---

## 마치며

이 가이드를 따라 새로운 커스텀 도구를 개발하시면 됩니다.

**개발 흐름 요약**:
1. 요구사항 정의
2. Layer 1 구현 (Input Schema + Tool Class)
3. Layer 2 구현 (Wrapper Class)
4. 등록 (import + TOOL_CLASSES)
5. 테스트 및 디버깅

**질문이나 이슈가 있다면**:
- 기존 도구 코드 참고
- CrewAI 공식 문서 확인
- GitHub Issues에서 유사 사례 검색

Happy Coding! 🚀
