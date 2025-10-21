# RBAC 역할 체계 설계

## 역할 계층 구조

```
system_admin (crew_system)
  └── workspace_owner
      └── workspace_admin
          └── workspace_member
              └── workspace_viewer
```

## 1. system_admin (crew_system)

**최상위 시스템 관리자 계정**

### 권한:
- ✅ 모든 워크스페이스 접근 및 관리
- ✅ 모든 사용자 계정 관리 (생성, 수정, 삭제, 비활성화)
- ✅ 시스템 설정 및 글로벌 구성 변경
- ✅ 모든 크루 템플릿 관리 (public 템플릿 승인/거부)
- ✅ 시스템 통계 및 모니터링
- ✅ 워크스페이스 플랜 변경 (free, pro, enterprise)
- ✅ 백업 및 복구
- ✅ 감사 로그 조회

### 특징:
- 워크스페이스에 속하지 않음 (workspace_id = NULL)
- 단일 계정 또는 소수의 시스템 관리자만 가능
- 사용자 생성 시 자동으로 이 역할 부여 불가 (수동 설정 필요)

---

## 2. workspace_owner

**워크스페이스 소유자 (생성자)**

### 권한:
- ✅ 워크스페이스 설정 변경 (이름, 슬러그 등)
- ✅ 워크스페이스 삭제
- ✅ 멤버 초대, 역할 변경, 제거
- ✅ 워크스페이스 플랜 업그레이드 요청
- ✅ 소유권 이전
- ✅ 모든 리소스 CRUD (Agent, Crew, Task, Tool, Knowledge)
- ✅ 크루 템플릿 생성, 수정, 삭제
- ✅ 크루 실행 및 결과 조회
- ✅ 워크스페이스 통계 조회

### 특징:
- 워크스페이스당 1명만 존재
- 워크스페이스 생성 시 자동으로 owner가 됨
- 소유권 이전 가능

---

## 3. workspace_admin

**워크스페이스 관리자**

### 권한:
- ✅ 멤버 초대 및 제거 (owner 제외)
- ✅ member/viewer 역할 변경 가능
- ⛔ admin/owner 역할 변경 불가
- ✅ 모든 리소스 CRUD (Agent, Crew, Task, Tool, Knowledge)
- ✅ 크루 템플릿 생성, 수정, 삭제
- ✅ 크루 실행 및 결과 조회
- ✅ 워크스페이스 통계 조회
- ⛔ 워크스페이스 삭제 불가
- ⛔ 워크스페이스 설정 변경 불가

### 특징:
- 워크스페이스당 여러 명 가능
- owner가 지정

---

## 4. workspace_member

**워크스페이스 일반 멤버**

### 권한:
- ✅ 자신이 생성한 리소스 CRUD
- ✅ 공유된 리소스 읽기
- ✅ 크루 실행 (자신의 크루 또는 공유된 크루)
- ✅ 크루 템플릿 생성 (private/workspace)
- ✅ 자신의 크루 템플릿 수정/삭제
- ⛔ 다른 멤버의 리소스 수정/삭제 불가
- ⛔ 멤버 초대/제거 불가
- ⛔ 워크스페이스 설정 변경 불가

### 특징:
- 기본 작업 역할
- 초대 시 기본 역할

---

## 5. workspace_viewer

**읽기 전용 사용자**

### 권한:
- ✅ 워크스페이스 리소스 읽기
- ✅ 공유된 크루 템플릿 조회
- ✅ 크루 실행 결과 조회
- ⛔ 리소스 생성/수정/삭제 불가
- ⛔ 크루 실행 불가
- ⛔ 크루 템플릿 생성 불가

### 특징:
- 감사/모니터링 용도
- 외부 협력사, 클라이언트에게 부여

---

## 권한 매트릭스

| 작업 | system_admin | workspace_owner | workspace_admin | workspace_member | workspace_viewer |
|------|--------------|-----------------|-----------------|------------------|------------------|
| 워크스페이스 생성 | ✅ | ✅ | ⛔ | ⛔ | ⛔ |
| 워크스페이스 삭제 | ✅ | ✅ | ⛔ | ⛔ | ⛔ |
| 워크스페이스 설정 | ✅ | ✅ | ⛔ | ⛔ | ⛔ |
| 멤버 초대 | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| 멤버 제거 | ✅ | ✅ | ✅ (owner 제외) | ⛔ | ⛔ |
| 역할 변경 | ✅ | ✅ | ✅ (member/viewer만) | ⛔ | ⛔ |
| Agent 생성 | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Agent 수정 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Agent 수정 (타인) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| Agent 삭제 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Agent 삭제 (타인) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| Agent 조회 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Crew 생성 | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Crew 수정 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Crew 수정 (타인) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| Crew 삭제 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Crew 삭제 (타인) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| Crew 조회 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Crew 실행 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Crew 실행 (공유) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Task 생성 | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Task 수정 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Task 수정 (타인) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| Task 삭제 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Task 삭제 (타인) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| Task 조회 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Tool 생성 | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Tool 수정 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Tool 수정 (타인) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| Tool 삭제 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Tool 삭제 (타인) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| Tool 조회 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Knowledge 생성 | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Knowledge 수정 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Knowledge 수정 (타인) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| Knowledge 삭제 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Knowledge 삭제 (타인) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| Knowledge 조회 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Template 생성 (private) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Template 생성 (workspace) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Template 생성 (public) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Template 승인 (public) | ✅ | ⛔ | ⛔ | ⛔ | ⛔ |
| Template 수정 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Template 수정 (타인) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| Template 삭제 (자신) | ✅ | ✅ | ✅ | ✅ | ⛔ |
| Template 삭제 (타인) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| Template 조회 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 시스템 설정 | ✅ | ⛔ | ⛔ | ⛔ | ⛔ |
| 사용자 관리 (전체) | ✅ | ⛔ | ⛔ | ⛔ | ⛔ |
| 워크스페이스 관리 (전체) | ✅ | ⛔ | ⛔ | ⛔ | ⛔ |
| 감사 로그 조회 | ✅ | ✅ | ⛔ | ⛔ | ⛔ |
| 통계 조회 (워크스페이스) | ✅ | ✅ | ✅ | ⛔ | ⛔ |
| 통계 조회 (시스템 전체) | ✅ | ⛔ | ⛔ | ⛔ | ⛔ |

---

## 데이터베이스 저장 방식

### users 테이블
```sql
CREATE TABLE users (
    id VARCHAR(12) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_system_admin BOOLEAN DEFAULT FALSE,  -- crew_system 계정 여부
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- system_admin 계정 생성 예시
INSERT INTO users (id, email, password_hash, name, is_system_admin)
VALUES ('crew_system', 'admin@crewai.studio', '<hashed_password>', 'System Admin', TRUE);
```

### workspace_members 테이블
```sql
CREATE TABLE workspace_members (
    id VARCHAR(12) PRIMARY KEY,
    workspace_id VARCHAR(12) NOT NULL,
    user_id VARCHAR(12) NOT NULL,
    role ENUM('owner', 'admin', 'member', 'viewer') NOT NULL,
    permissions JSON,  -- 세부 권한 커스터마이징 가능
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (workspace_id, user_id)
);
```

---

## 권한 체크 로직 (Pseudo Code)

```python
def check_permission(user, workspace_id, action, resource=None):
    # 1. System Admin은 모든 권한 가짐
    if user.is_system_admin:
        return True

    # 2. 워크스페이스 멤버십 확인
    membership = get_membership(user.id, workspace_id)
    if not membership:
        return False

    role = membership.role

    # 3. 역할별 권한 체크
    if action == "read":
        return True  # 모든 역할이 읽기 가능

    if action in ["create"]:
        return role in ["owner", "admin", "member"]

    if action in ["update", "delete"]:
        # 본인 리소스인 경우
        if resource and resource.created_by == user.id:
            return role in ["owner", "admin", "member"]
        # 타인 리소스인 경우
        else:
            return role in ["owner", "admin"]

    if action == "manage_members":
        return role in ["owner", "admin"]

    if action == "manage_workspace":
        return role == "owner"

    if action == "execute_crew":
        # 본인 크루 또는 공유된 크루
        if resource and (resource.created_by == user.id or resource.is_shared):
            return role in ["owner", "admin", "member"]
        return False

    return False
```

---

## 초기 데이터 설정

### 1. System Admin 계정 생성
```python
from bend.database.models.user import User
from bend.utils.security import hash_password
from bend.utils.id_generator import generate_id

system_admin = User(
    id="crew_system",
    email="admin@crewai.studio",
    password_hash=hash_password("CHANGE_ME_IN_PRODUCTION"),
    name="System Admin",
    is_system_admin=True,
    is_active=True
)
db.add(system_admin)
db.commit()
```

### 2. 첫 워크스페이스 생성 시 Owner 자동 할당
```python
# 워크스페이스 생성
workspace = Workspace(
    id=generate_id(),
    name="My Workspace",
    slug="my-workspace",
    owner_id=current_user.id
)
db.add(workspace)

# Owner 멤버십 자동 생성
membership = WorkspaceMember(
    id=generate_id(),
    workspace_id=workspace.id,
    user_id=current_user.id,
    role="owner"
)
db.add(membership)
db.commit()
```

---

## 추가 고려사항

### 1. 역할 변경 제한
- owner → admin/member/viewer: 불가 (소유권 이전 먼저 필요)
- admin → owner: owner만 가능
- member/viewer → admin: owner/admin 가능

### 2. 멤버 제거 제한
- owner는 제거 불가 (소유권 이전 먼저 필요)
- 본인 스스로 제거 가능 (탈퇴)

### 3. 워크스페이스 삭제
- owner만 가능
- 모든 리소스 CASCADE DELETE
- 멤버십도 모두 삭제

### 4. Public 템플릿 승인
- system_admin만 가능
- 악의적/부적절한 템플릿 필터링
