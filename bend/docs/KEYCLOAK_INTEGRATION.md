# Keycloak 통합 전략

## 개요

현재 자체 구현된 RBAC 시스템과 Keycloak IAM 솔루션의 통합 전략을 제시합니다.

## Keycloak 장점

### 1. 엔터프라이즈급 인증/인가
- **SSO (Single Sign-On)**: 여러 애플리케이션 간 단일 로그인
- **소셜 로그인**: Google, GitHub, Facebook 등 OAuth2 통합
- **MFA (Multi-Factor Authentication)**: 2단계 인증 기본 제공
- **Password Policies**: 비밀번호 정책 자동 적용

### 2. 표준 프로토콜 지원
- **OpenID Connect (OIDC)**: 인증 표준
- **OAuth 2.0**: 인가 표준
- **SAML 2.0**: 엔터프라이즈 SSO

### 3. 관리 편의성
- **Admin Console**: 웹 기반 관리 UI
- **User Federation**: LDAP, Active Directory 연동
- **Audit Logging**: 감사 로그 자동 기록

---

## 통합 시나리오 비교

### Option 1: Keycloak 완전 통합 (추천 ⭐)

**구조:**
```
[Frontend] → [Keycloak] → [Backend API]
                ↓
        [JWT Token + Roles]
```

**역할 관리:**
- **Keycloak Realm Roles**: system_admin
- **Keycloak Client Roles**: workspace_owner, workspace_admin, workspace_member, workspace_viewer
- **Custom Attributes**: workspace_id 매핑

**장점:**
- ✅ 표준 OAuth2/OIDC 사용
- ✅ SSO, MFA 기본 제공
- ✅ 사용자 관리 UI 제공
- ✅ 감사 로그 자동 기록
- ✅ 엔터프라이즈 기능 완비

**단점:**
- ⚠️ Keycloak 서버 운영 필요
- ⚠️ 학습 곡선 존재
- ⚠️ 인프라 복잡도 증가

**구현 방식:**
```python
# 1. Keycloak에서 JWT 토큰 받기
# 2. 백엔드에서 토큰 검증
# 3. 토큰에서 roles 추출
# 4. WorkspaceMember 매핑 (선택적)
```

---

### Option 2: Hybrid 방식 (인증만 Keycloak)

**구조:**
```
[Frontend] → [Keycloak] → [Backend API]
                ↓              ↓
        [JWT Token]    [WorkspaceMember DB]
```

**역할 관리:**
- **Keycloak**: 사용자 인증만 담당 (user_id, email)
- **자체 DB**: WorkspaceMember 테이블로 워크스페이스 권한 관리

**장점:**
- ✅ 인증은 Keycloak의 강력한 기능 활용
- ✅ 워크스페이스 권한은 세밀하게 커스터마이징 가능
- ✅ 기존 설계한 RBAC 모델 그대로 사용
- ✅ Keycloak 의존도 낮음

**단점:**
- ⚠️ 권한 관리 로직 직접 구현 필요
- ⚠️ 이중 관리 (Keycloak + DB)

**구현 방식:**
```python
# 1. Keycloak에서 user_id만 받기
# 2. WorkspaceMember 테이블에서 역할 조회
# 3. 권한 체크는 기존 로직 사용
```

---

### Option 3: 자체 구현 (Keycloak 없음)

**구조:**
```
[Frontend] → [Backend API]
                ↓
        [User DB + JWT]
```

**역할 관리:**
- **자체 DB**: User, WorkspaceMember 테이블

**장점:**
- ✅ 인프라 단순함
- ✅ 완전한 커스터마이징 가능
- ✅ Keycloak 의존성 없음

**단점:**
- ❌ SSO, MFA 직접 구현 필요
- ❌ 보안 취약점 발생 가능성
- ❌ 엔터프라이즈 기능 부족

---

## 추천: Option 1 (Keycloak 완전 통합)

### 이유
1. **프로덕션 환경**: SSO, MFA 필수
2. **엔터프라이즈 판매**: Keycloak은 대기업에서 선호
3. **보안**: 검증된 솔루션 사용
4. **개발 속도**: 인증/인가 직접 구현 불필요

---

## Keycloak 통합 구현 가이드

### 1. Keycloak 설정

#### 1.1. Realm 생성
```
Realm Name: crewai-studio
```

#### 1.2. Client 생성
```yaml
Client ID: crewai-studio-backend
Client Protocol: openid-connect
Access Type: confidential
Valid Redirect URIs: http://localhost:8000/*
Web Origins: *
```

#### 1.3. Realm Roles 정의
```
- system_admin
```

#### 1.4. Client Roles 정의 (crewai-studio-backend)
```
- workspace_owner
- workspace_admin
- workspace_member
- workspace_viewer
```

#### 1.5. Custom User Attributes
```
- workspace_id: 사용자의 현재 워크스페이스
- workspaces: 참여 중인 워크스페이스 목록 (JSON)
```

---

### 2. 백엔드 통합

#### 2.1. 필요 라이브러리
```bash
pip install python-keycloak PyJWT cryptography
```

#### 2.2. Keycloak 설정 파일
```python
# bend/config/keycloak_config.py
KEYCLOAK_SERVER_URL = "http://localhost:8080"
KEYCLOAK_REALM = "crewai-studio"
KEYCLOAK_CLIENT_ID = "crewai-studio-backend"
KEYCLOAK_CLIENT_SECRET = "your-client-secret"
```

#### 2.3. JWT 토큰 검증 미들웨어
```python
# bend/middleware/auth_middleware.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from keycloak import KeycloakOpenID

security = HTTPBearer()

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM,
    client_secret_key=KEYCLOAK_CLIENT_SECRET
)

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        # Keycloak 공개키로 토큰 검증
        KEYCLOAK_PUBLIC_KEY = (
            "-----BEGIN PUBLIC KEY-----\n"
            + keycloak_openid.public_key()
            + "\n-----END PUBLIC KEY-----"
        )

        options = {"verify_signature": True, "verify_aud": False, "exp": True}
        decoded_token = jwt.decode(
            token,
            KEYCLOAK_PUBLIC_KEY,
            algorithms=["RS256"],
            options=options
        )

        return decoded_token
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### 2.4. 권한 체크 함수
```python
# bend/middleware/permission_middleware.py
def check_workspace_permission(
    token_data: dict,
    workspace_id: str,
    required_role: str
) -> bool:
    """
    Keycloak 토큰에서 워크스페이스 권한 체크

    Args:
        token_data: 디코딩된 JWT 토큰
        workspace_id: 확인할 워크스페이스 ID
        required_role: 필요한 역할 (owner, admin, member, viewer)

    Returns:
        bool: 권한 있으면 True
    """
    # 1. System Admin 체크
    realm_roles = token_data.get("realm_access", {}).get("roles", [])
    if "system_admin" in realm_roles:
        return True

    # 2. Client Roles 체크
    client_roles = token_data.get("resource_access", {}).get(
        KEYCLOAK_CLIENT_ID, {}
    ).get("roles", [])

    # 3. Workspace 매핑 체크 (Custom Attribute)
    user_workspaces = token_data.get("workspaces", {})
    user_role_in_workspace = user_workspaces.get(workspace_id)

    if not user_role_in_workspace:
        return False

    # 4. 역할 계층 체크
    role_hierarchy = {
        "workspace_owner": 4,
        "workspace_admin": 3,
        "workspace_member": 2,
        "workspace_viewer": 1
    }

    user_level = role_hierarchy.get(user_role_in_workspace, 0)
    required_level = role_hierarchy.get(required_role, 0)

    return user_level >= required_level
```

#### 2.5. FastAPI Dependency
```python
# bend/dependencies/auth_dependencies.py
from fastapi import Depends, HTTPException

def get_current_user(token_data: dict = Depends(verify_token)):
    """현재 사용자 정보 반환"""
    user_id = token_data.get("sub")
    email = token_data.get("email")
    name = token_data.get("name")

    return {
        "id": user_id,
        "email": email,
        "name": name,
        "roles": token_data.get("realm_access", {}).get("roles", [])
    }

def require_workspace_access(
    required_role: str = "workspace_viewer"
):
    """워크스페이스 접근 권한 체크 데코레이터"""
    def dependency(
        workspace_id: str,
        token_data: dict = Depends(verify_token)
    ):
        if not check_workspace_permission(token_data, workspace_id, required_role):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {required_role}"
            )
        return token_data
    return dependency
```

#### 2.6. API 엔드포인트 예시
```python
# bend/api/agents.py
from fastapi import APIRouter, Depends
from bend.dependencies.auth_dependencies import get_current_user, require_workspace_access

router = APIRouter()

@router.post("/workspaces/{workspace_id}/agents")
async def create_agent(
    workspace_id: str,
    agent_data: AgentCreate,
    current_user: dict = Depends(get_current_user),
    _: dict = Depends(require_workspace_access("workspace_member"))
):
    """
    Agent 생성 (workspace_member 이상 권한 필요)
    """
    agent = Agent(
        **agent_data.dict(),
        workspace_id=workspace_id,
        created_by=current_user["id"]
    )
    db.add(agent)
    db.commit()
    return agent.to_dict()

@router.get("/workspaces/{workspace_id}/agents")
async def list_agents(
    workspace_id: str,
    current_user: dict = Depends(get_current_user),
    _: dict = Depends(require_workspace_access("workspace_viewer"))
):
    """
    Agent 목록 조회 (workspace_viewer 이상 권한 필요)
    """
    agents = db.query(Agent).filter(Agent.workspace_id == workspace_id).all()
    return [agent.to_dict() for agent in agents]
```

---

### 3. 프론트엔드 통합

#### 3.1. Keycloak JavaScript Adapter
```html
<!-- index.html -->
<script src="http://localhost:8080/js/keycloak.js"></script>
```

```javascript
// auth.js
const keycloak = new Keycloak({
  url: 'http://localhost:8080',
  realm: 'crewai-studio',
  clientId: 'crewai-studio-frontend'
});

keycloak.init({ onLoad: 'login-required' }).then(authenticated => {
  if (authenticated) {
    // 로그인 성공
    const token = keycloak.token;
    const refreshToken = keycloak.refreshToken;

    // API 요청 시 토큰 사용
    fetch('http://localhost:8000/api/agents', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  }
});

// 토큰 자동 갱신
setInterval(() => {
  keycloak.updateToken(70).then(refreshed => {
    if (refreshed) {
      console.log('Token refreshed');
    }
  });
}, 60000);
```

---

### 4. 데이터베이스 스키마 조정

#### Option A: Keycloak 사용자 ID 동기화
```python
# User 테이블의 id를 Keycloak user_id와 동기화
class User(Base):
    __tablename__ = "users"

    # Keycloak의 sub (user_id) 사용
    id = Column(String(36), primary_key=True)  # UUID 형식

    # Keycloak에서 가져온 정보 캐싱
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)

    # Keycloak 동기화 정보
    keycloak_id = Column(String(36), unique=True, nullable=False)
    last_sync_at = Column(DateTime, default=datetime.utcnow)
```

#### Option B: WorkspaceMember만 유지
```python
# User 테이블 삭제하고 WorkspaceMember만 사용
class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(String(12), primary_key=True)
    workspace_id = Column(String(12), ForeignKey("workspaces.id"))

    # Keycloak user_id 직접 참조
    keycloak_user_id = Column(String(36), nullable=False, index=True)

    role = Column(Enum(WorkspaceRole), nullable=False)
    permissions = Column(JSON, nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
```

---

### 5. Keycloak Custom User Attribute 매핑

#### 5.1. User Attribute Mapper 생성
```
Keycloak Admin Console → Clients → crewai-studio-backend → Mappers
→ Create Protocol Mapper

Mapper Type: User Attribute
Name: workspaces
User Attribute: workspaces
Token Claim Name: workspaces
Claim JSON Type: JSON
Add to ID token: ON
Add to access token: ON
Add to userinfo: ON
```

#### 5.2. JWT 토큰 예시
```json
{
  "sub": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "email": "user@example.com",
  "name": "John Doe",
  "realm_access": {
    "roles": []
  },
  "resource_access": {
    "crewai-studio-backend": {
      "roles": ["workspace_member"]
    }
  },
  "workspaces": {
    "WS_abc123": "workspace_owner",
    "WS_def456": "workspace_member"
  }
}
```

---

## 마이그레이션 전략

### 단계별 전환

#### Phase 1: Keycloak 설치 및 설정
```bash
# Docker Compose로 Keycloak 설치
docker-compose up -d keycloak
```

#### Phase 2: 기존 사용자 마이그레이션
```python
# bend/scripts/migrate_users_to_keycloak.py
from keycloak import KeycloakAdmin

keycloak_admin = KeycloakAdmin(
    server_url=KEYCLOAK_SERVER_URL,
    realm_name=KEYCLOAK_REALM,
    client_id=KEYCLOAK_CLIENT_ID,
    client_secret_key=KEYCLOAK_CLIENT_SECRET
)

# 기존 User 테이블에서 Keycloak으로 마이그레이션
users = db.query(User).all()
for user in users:
    keycloak_admin.create_user({
        "email": user.email,
        "username": user.email,
        "firstName": user.name.split()[0],
        "lastName": user.name.split()[-1] if len(user.name.split()) > 1 else "",
        "enabled": user.is_active,
        "emailVerified": user.email_verified,
        "attributes": {
            "old_user_id": user.id
        }
    })
```

#### Phase 3: WorkspaceMember 매핑 업데이트
```python
# Keycloak user_id로 WorkspaceMember 업데이트
for workspace_member in db.query(WorkspaceMember).all():
    old_user = db.query(User).filter(User.id == workspace_member.user_id).first()
    keycloak_user = keycloak_admin.get_users({"email": old_user.email})[0]

    workspace_member.keycloak_user_id = keycloak_user["id"]
    db.commit()
```

#### Phase 4: API 엔드포인트 업데이트
```python
# 모든 API에 Keycloak 인증 적용
# FastAPI Dependency로 전역 적용 가능
```

---

## Keycloak Docker Compose 설정

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres-keycloak:
    image: postgres:15
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: keycloak
    volumes:
      - keycloak_postgres_data:/var/lib/postgresql/data
    networks:
      - crewai-network

  keycloak:
    image: quay.io/keycloak/keycloak:23.0
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres-keycloak:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: keycloak
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin
    ports:
      - "8080:8080"
    command:
      - start-dev
    depends_on:
      - postgres-keycloak
    networks:
      - crewai-network

volumes:
  keycloak_postgres_data:

networks:
  crewai-network:
    driver: bridge
```

---

## 비용 및 리소스

### Keycloak 서버 리소스
- **최소**: 512MB RAM, 1 CPU
- **권장**: 2GB RAM, 2 CPU
- **대규모**: 4GB+ RAM, 4+ CPU

### 개발 시간 추정
- **Keycloak 설정**: 1-2일
- **백엔드 통합**: 3-5일
- **프론트엔드 통합**: 2-3일
- **마이그레이션 및 테스트**: 2-3일
- **Total**: 8-13일

---

## 결론

### ✅ Keycloak 통합 추천
- **프로덕션 환경**: 필수
- **엔터프라이즈 판매**: 강력히 추천
- **스타트업 초기**: Option 2 (Hybrid) 사용 후 나중에 완전 통합

### 통합 가능성: ⭐⭐⭐⭐⭐ (5/5)
현재 설계한 RBAC 시스템은 Keycloak과 완벽하게 호환됩니다.
