# CrewAI Studio - Backend API

FastAPI 기반 REST API 백엔드

## 기술 스택

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **Keycloak** - Authentication (예정)

## 디렉토리 구조

```
bend/
├── main.py              # FastAPI 엔트리포인트
├── config.py            # 설정 관리
├── requirements.txt     # Python 의존성
├── api/                 # API 라우터
│   └── health.py       # 헬스체크 엔드포인트
├── models/              # 도메인 모델
├── schemas/             # Pydantic 스키마
├── services/            # 비즈니스 로직
├── database/            # 데이터베이스
│   ├── connection.py   # DB 연결 관리
│   └── repositories/   # Repository 패턴
└── tests/               # 테스트

```

## 설치 및 실행

### 1. 의존성 설치

```bash
cd bend
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 루트 디렉토리에 생성:

```env
# Database
DB_URL=sqlite:///crewai.db

# Security
SECRET_KEY=your-secret-key-here

# Keycloak (선택)
KEYCLOAK_ENABLED=false
KEYCLOAK_SERVER_URL=http://localhost:8080
KEYCLOAK_REALM=crewai
KEYCLOAK_CLIENT_ID=crewai-api
KEYCLOAK_CLIENT_SECRET=your-client-secret
```

### 3. 서버 실행

**개발 모드:**
```bash
python main.py
# 또는
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**프로덕션 모드:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 문서

서버 실행 후 다음 URL에서 API 문서 확인:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## API 엔드포인트

### 헬스체크

- `GET /` - 루트 엔드포인트 (API 정보)
- `GET /api/health` - 기본 헬스체크
- `GET /api/health/detailed` - 상세 헬스체크 (DB 포함)
- `GET /api/version` - 버전 정보

### 향후 추가 예정

- `POST /api/crews` - 크루 생성
- `GET /api/crews` - 크루 목록
- `GET /api/agents` - 에이전트 목록
- `POST /api/execute` - 크루 실행
- 기타 CRUD 엔드포인트

## 개발 가이드

### 새 API 엔드포인트 추가

1. `api/` 폴더에 라우터 파일 생성 (예: `crews.py`)
2. `main.py`에 라우터 등록
3. `schemas/` 폴더에 요청/응답 스키마 정의
4. `services/` 폴더에 비즈니스 로직 작성

### 테스트 실행

```bash
pytest
# 또는 커버리지와 함께
pytest --cov=bend
```

## 모노레포 구조

이 프로젝트는 모노레포 구조를 사용합니다:

```
CrewAI-Studio/
├── bend/        # 백엔드 (현재)
├── frnt/        # 프론트엔드 (예정)
├── app/         # 기존 Streamlit (점진적 전환)
└── shared/      # 공유 코드
```

## Keycloak 통합 (예정)

향후 Keycloak을 통한 인증/인가 추가 예정:

- OAuth 2.0 / OIDC
- Role-based access control
- SSO (Single Sign-On)

## 라이선스

기존 프로젝트 라이선스 준수
