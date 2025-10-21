# 데이터베이스 마이그레이션 플랜

## 목표
기존 단일 테넌트 시스템을 멀티테넌트 시스템으로 마이그레이션

## 마이그레이션 전략

### Phase 1: 새로운 테이블 생성 (사용자, 워크스페이스, 권한)
### Phase 2: 기존 테이블에 멀티테넌트 컬럼 추가
### Phase 3: 데이터 마이그레이션
### Phase 4: 제약조건 및 인덱스 추가
### Phase 5: 검증 및 롤백 계획

---

## Phase 1: 새로운 테이블 생성

### 1.1. users 테이블
```sql
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(12) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_system_admin BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 1.2. workspaces 테이블
```sql
CREATE TABLE IF NOT EXISTS workspaces (
    id VARCHAR(12) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NULL,
    owner_id VARCHAR(12) NOT NULL,
    plan VARCHAR(20) DEFAULT 'free',
    max_members INT DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    settings JSON NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_owner_id (owner_id),
    INDEX idx_slug (slug),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 1.3. workspace_members 테이블
```sql
CREATE TABLE IF NOT EXISTS workspace_members (
    id VARCHAR(12) PRIMARY KEY,
    workspace_id VARCHAR(12) NOT NULL,
    user_id VARCHAR(12) NOT NULL,
    role ENUM('owner', 'admin', 'member', 'viewer') NOT NULL DEFAULT 'member',
    permissions JSON NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_workspace_user (workspace_id, user_id),
    INDEX idx_workspace_id (workspace_id),
    INDEX idx_user_id (user_id),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 1.4. crew_templates 테이블
```sql
CREATE TABLE IF NOT EXISTS crew_templates (
    id VARCHAR(12) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    category VARCHAR(50) NULL,
    template_data JSON NOT NULL,
    visibility ENUM('private', 'workspace', 'public') DEFAULT 'private',
    workspace_id VARCHAR(12) NULL,
    created_by VARCHAR(12) NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    use_count INT DEFAULT 0,
    rating_avg DECIMAL(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,
    tags JSON NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_workspace_id (workspace_id),
    INDEX idx_created_by (created_by),
    INDEX idx_visibility (visibility),
    INDEX idx_category (category),
    INDEX idx_is_approved (is_approved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 1.5. template_favorites 테이블
```sql
CREATE TABLE IF NOT EXISTS template_favorites (
    id VARCHAR(12) PRIMARY KEY,
    template_id VARCHAR(12) NOT NULL,
    user_id VARCHAR(12) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES crew_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_template_user (template_id, user_id),
    INDEX idx_template_id (template_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## Phase 2: 기존 테이블에 컬럼 추가

### 2.1. agents 테이블
```sql
-- 1. 워크스페이스 컬럼 추가 (NULL 허용)
ALTER TABLE agents
ADD COLUMN workspace_id VARCHAR(12) NULL AFTER id,
ADD COLUMN created_by VARCHAR(12) NULL AFTER workspace_id;

-- 2. 인덱스 추가
ALTER TABLE agents
ADD INDEX idx_workspace_id (workspace_id),
ADD INDEX idx_created_by (created_by);

-- 3. 외래키 제약조건 추가 (데이터 마이그레이션 후)
-- ALTER TABLE agents
-- ADD CONSTRAINT fk_agents_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
-- ADD CONSTRAINT fk_agents_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;
```

### 2.2. crews 테이블
```sql
-- 1. 워크스페이스 컬럼 추가 (NULL 허용)
ALTER TABLE crews
ADD COLUMN workspace_id VARCHAR(12) NULL AFTER id,
ADD COLUMN created_by VARCHAR(12) NULL AFTER workspace_id;

-- 2. 인덱스 추가
ALTER TABLE crews
ADD INDEX idx_workspace_id (workspace_id),
ADD INDEX idx_created_by (created_by);

-- 3. 외래키 제약조건 추가 (데이터 마이그레이션 후)
-- ALTER TABLE crews
-- ADD CONSTRAINT fk_crews_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
-- ADD CONSTRAINT fk_crews_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;
```

### 2.3. tasks 테이블
```sql
-- 1. 워크스페이스 컬럼 추가 (NULL 허용)
ALTER TABLE tasks
ADD COLUMN workspace_id VARCHAR(12) NULL AFTER id,
ADD COLUMN created_by VARCHAR(12) NULL AFTER workspace_id;

-- 2. 인덱스 추가
ALTER TABLE tasks
ADD INDEX idx_workspace_id (workspace_id),
ADD INDEX idx_created_by (created_by);

-- 3. 외래키 제약조건 추가 (데이터 마이그레이션 후)
-- ALTER TABLE tasks
-- ADD CONSTRAINT fk_tasks_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
-- ADD CONSTRAINT fk_tasks_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;
```

### 2.4. tools 테이블
```sql
-- 1. 워크스페이스 컬럼 추가 (NULL 허용)
ALTER TABLE tools
ADD COLUMN workspace_id VARCHAR(12) NULL AFTER tool_id,
ADD COLUMN created_by VARCHAR(12) NULL AFTER workspace_id;

-- 2. 인덱스 추가
ALTER TABLE tools
ADD INDEX idx_workspace_id (workspace_id),
ADD INDEX idx_created_by (created_by);

-- 3. 외래키 제약조건 추가 (데이터 마이그레이션 후)
-- ALTER TABLE tools
-- ADD CONSTRAINT fk_tools_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
-- ADD CONSTRAINT fk_tools_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;
```

### 2.5. knowledge_sources 테이블
```sql
-- 1. 워크스페이스 컬럼 추가 (NULL 허용)
ALTER TABLE knowledge_sources
ADD COLUMN workspace_id VARCHAR(12) NULL AFTER id,
ADD COLUMN created_by VARCHAR(12) NULL AFTER workspace_id;

-- 2. 인덱스 추가
ALTER TABLE knowledge_sources
ADD INDEX idx_workspace_id (workspace_id),
ADD INDEX idx_created_by (created_by);

-- 3. 외래키 제약조건 추가 (데이터 마이그레이션 후)
-- ALTER TABLE knowledge_sources
-- ADD CONSTRAINT fk_knowledge_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
-- ADD CONSTRAINT fk_knowledge_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;
```

### 2.6. crew_runs 테이블
```sql
-- 1. 실행자 컬럼 추가 (NULL 허용)
ALTER TABLE crew_runs
ADD COLUMN executed_by VARCHAR(12) NULL AFTER crew_id;

-- 2. 인덱스 추가
ALTER TABLE crew_runs
ADD INDEX idx_executed_by (executed_by);

-- 3. 외래키 제약조건 추가 (데이터 마이그레이션 후)
-- ALTER TABLE crew_runs
-- ADD CONSTRAINT fk_crew_runs_executed_by FOREIGN KEY (executed_by) REFERENCES users(id) ON DELETE SET NULL;
```

---

## Phase 3: 데이터 마이그레이션

### 3.1. 시스템 관리자 계정 생성
```python
from bend.database.models.user import User
from bend.utils.security import hash_password
from datetime import datetime

# System Admin 계정 생성
system_admin = User(
    id="crew_system",
    email="admin@crewai.studio",
    password_hash=hash_password("ChangeMe123!"),  # 반드시 변경 필요
    name="System Admin",
    is_system_admin=True,
    is_active=True,
    email_verified=True,
    created_at=datetime.utcnow()
)
db.add(system_admin)
db.commit()
```

### 3.2. 기본 워크스페이스 생성
```python
from bend.database.models.workspace import Workspace
from bend.utils.id_generator import generate_id

# 기존 데이터를 위한 기본 워크스페이스 생성
default_workspace = Workspace(
    id=generate_id(),
    name="Default Workspace",
    slug="default",
    description="기존 데이터를 위한 기본 워크스페이스",
    owner_id="crew_system",
    plan="enterprise",
    max_members=999,
    is_active=True
)
db.add(default_workspace)
db.commit()

default_workspace_id = default_workspace.id
```

### 3.3. 기존 리소스에 워크스페이스 할당
```sql
-- 모든 기존 Agent를 기본 워크스페이스에 할당
UPDATE agents
SET workspace_id = :default_workspace_id,
    created_by = 'crew_system'
WHERE workspace_id IS NULL;

-- 모든 기존 Crew를 기본 워크스페이스에 할당
UPDATE crews
SET workspace_id = :default_workspace_id,
    created_by = 'crew_system'
WHERE workspace_id IS NULL;

-- 모든 기존 Task를 기본 워크스페이스에 할당
UPDATE tasks
SET workspace_id = :default_workspace_id,
    created_by = 'crew_system'
WHERE workspace_id IS NULL;

-- 모든 기존 Tool을 기본 워크스페이스에 할당
UPDATE tools
SET workspace_id = :default_workspace_id,
    created_by = 'crew_system'
WHERE workspace_id IS NULL;

-- 모든 기존 Knowledge Source를 기본 워크스페이스에 할당
UPDATE knowledge_sources
SET workspace_id = :default_workspace_id,
    created_by = 'crew_system'
WHERE workspace_id IS NULL;

-- 모든 기존 Crew Run에 실행자 할당
UPDATE crew_runs
SET executed_by = 'crew_system'
WHERE executed_by IS NULL;
```

### 3.4. Workspace Member 생성 (System Admin)
```python
from bend.database.models.workspace_member import WorkspaceMember

# System Admin을 기본 워크스페이스의 Owner로 추가
membership = WorkspaceMember(
    id=generate_id(),
    workspace_id=default_workspace_id,
    user_id="crew_system",
    role="owner"
)
db.add(membership)
db.commit()
```

---

## Phase 4: 제약조건 및 NOT NULL 변경

### 4.1. 외래키 제약조건 추가
```sql
-- agents 테이블
ALTER TABLE agents
ADD CONSTRAINT fk_agents_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_agents_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- crews 테이블
ALTER TABLE crews
ADD CONSTRAINT fk_crews_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_crews_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- tasks 테이블
ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_tasks_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- tools 테이블
ALTER TABLE tools
ADD CONSTRAINT fk_tools_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_tools_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- knowledge_sources 테이블
ALTER TABLE knowledge_sources
ADD CONSTRAINT fk_knowledge_workspace FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_knowledge_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- crew_runs 테이블
ALTER TABLE crew_runs
ADD CONSTRAINT fk_crew_runs_executed_by FOREIGN KEY (executed_by) REFERENCES users(id) ON DELETE SET NULL;
```

### 4.2. workspace_id를 NOT NULL로 변경 (선택사항)
```sql
-- 프로덕션 환경에서 모든 리소스가 워크스페이스를 가져야 한다면:
-- ALTER TABLE agents MODIFY workspace_id VARCHAR(12) NOT NULL;
-- ALTER TABLE crews MODIFY workspace_id VARCHAR(12) NOT NULL;
-- ALTER TABLE tasks MODIFY workspace_id VARCHAR(12) NOT NULL;
-- ALTER TABLE tools MODIFY workspace_id VARCHAR(12) NOT NULL;
-- ALTER TABLE knowledge_sources MODIFY workspace_id VARCHAR(12) NOT NULL;

-- 주의: created_by는 NULL 허용 유지 (사용자 삭제 시 SET NULL)
```

---

## Phase 5: 검증

### 5.1. 데이터 무결성 검증
```sql
-- 1. 모든 리소스가 워크스페이스를 가지고 있는지 확인
SELECT
    'agents' as table_name,
    COUNT(*) as total,
    SUM(CASE WHEN workspace_id IS NULL THEN 1 ELSE 0 END) as null_count
FROM agents
UNION ALL
SELECT 'crews', COUNT(*), SUM(CASE WHEN workspace_id IS NULL THEN 1 ELSE 0 END) FROM crews
UNION ALL
SELECT 'tasks', COUNT(*), SUM(CASE WHEN workspace_id IS NULL THEN 1 ELSE 0 END) FROM tasks
UNION ALL
SELECT 'tools', COUNT(*), SUM(CASE WHEN workspace_id IS NULL THEN 1 ELSE 0 END) FROM tools
UNION ALL
SELECT 'knowledge_sources', COUNT(*), SUM(CASE WHEN workspace_id IS NULL THEN 1 ELSE 0 END) FROM knowledge_sources;

-- 2. 외래키 무결성 확인 (고아 레코드 없는지)
SELECT COUNT(*) as orphaned_agents
FROM agents a
WHERE a.workspace_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM workspaces w WHERE w.id = a.workspace_id);

-- 3. 워크스페이스 멤버십 확인
SELECT
    w.name as workspace_name,
    COUNT(DISTINCT wm.user_id) as member_count,
    SUM(CASE WHEN wm.role = 'owner' THEN 1 ELSE 0 END) as owner_count
FROM workspaces w
LEFT JOIN workspace_members wm ON w.id = wm.workspace_id
GROUP BY w.id, w.name;

-- 4. System Admin 확인
SELECT id, email, name, is_system_admin, is_active
FROM users
WHERE is_system_admin = TRUE;
```

### 5.2. 성능 검증
```sql
-- 인덱스 사용 확인
EXPLAIN SELECT * FROM agents WHERE workspace_id = 'xxx';
EXPLAIN SELECT * FROM crews WHERE created_by = 'yyy';

-- 조인 성능 확인
EXPLAIN SELECT
    a.*,
    w.name as workspace_name,
    u.name as creator_name
FROM agents a
JOIN workspaces w ON a.workspace_id = w.id
LEFT JOIN users u ON a.created_by = u.id
WHERE w.id = 'xxx';
```

---

## Phase 6: 롤백 계획

### 6.1. 백업
```bash
# 마이그레이션 전 전체 데이터베이스 백업
mysqldump -u root -p crewai_studio > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql

# 또는 특정 테이블만 백업
mysqldump -u root -p crewai_studio \
  agents crews tasks tools knowledge_sources crew_runs \
  > backup_tables_before_migration.sql
```

### 6.2. 롤백 스크립트
```sql
-- 1. 외래키 제약조건 제거
ALTER TABLE agents DROP FOREIGN KEY fk_agents_workspace;
ALTER TABLE agents DROP FOREIGN KEY fk_agents_created_by;
ALTER TABLE crews DROP FOREIGN KEY fk_crews_workspace;
ALTER TABLE crews DROP FOREIGN KEY fk_crews_created_by;
ALTER TABLE tasks DROP FOREIGN KEY fk_tasks_workspace;
ALTER TABLE tasks DROP FOREIGN KEY fk_tasks_created_by;
ALTER TABLE tools DROP FOREIGN KEY fk_tools_workspace;
ALTER TABLE tools DROP FOREIGN KEY fk_tools_created_by;
ALTER TABLE knowledge_sources DROP FOREIGN KEY fk_knowledge_workspace;
ALTER TABLE knowledge_sources DROP FOREIGN KEY fk_knowledge_created_by;
ALTER TABLE crew_runs DROP FOREIGN KEY fk_crew_runs_executed_by;

-- 2. 추가된 컬럼 제거
ALTER TABLE agents DROP COLUMN workspace_id, DROP COLUMN created_by;
ALTER TABLE crews DROP COLUMN workspace_id, DROP COLUMN created_by;
ALTER TABLE tasks DROP COLUMN workspace_id, DROP COLUMN created_by;
ALTER TABLE tools DROP COLUMN workspace_id, DROP COLUMN created_by;
ALTER TABLE knowledge_sources DROP COLUMN workspace_id, DROP COLUMN created_by;
ALTER TABLE crew_runs DROP COLUMN executed_by;

-- 3. 새로운 테이블 삭제
DROP TABLE IF EXISTS template_favorites;
DROP TABLE IF EXISTS crew_templates;
DROP TABLE IF EXISTS workspace_members;
DROP TABLE IF EXISTS workspaces;
DROP TABLE IF EXISTS users;
```

---

## 실행 순서

### 개발 환경
1. ✅ Phase 1: 새 테이블 생성
2. ✅ Phase 2: 기존 테이블에 컬럼 추가
3. ✅ Phase 3: 데이터 마이그레이션
4. ✅ Phase 4: 제약조건 추가
5. ✅ Phase 5: 검증
6. ✅ 애플리케이션 코드 업데이트 및 테스트

### 프로덕션 환경
1. ✅ 백업 (Phase 6.1)
2. ✅ 유지보수 모드 활성화
3. ✅ Phase 1 ~ 5 실행
4. ✅ 검증 (Phase 5)
5. ✅ 애플리케이션 배포
6. ✅ 유지보수 모드 해제
7. ✅ 모니터링

---

## 추정 소요 시간

| Phase | 예상 시간 | 비고 |
|-------|----------|------|
| Phase 1 | 10분 | 새 테이블 생성 |
| Phase 2 | 5분 | 컬럼 추가 |
| Phase 3 | 15분 | 데이터 마이그레이션 |
| Phase 4 | 5분 | 제약조건 추가 |
| Phase 5 | 10분 | 검증 |
| **Total** | **45분** | 다운타임 포함 |

## 다운타임 최소화 전략

### 무중단 마이그레이션 (선택사항)
1. Phase 1-2를 먼저 실행 (서비스 운영 중)
2. 애플리케이션을 이중 쓰기 모드로 업데이트 (workspace_id NULL 허용)
3. Phase 3 데이터 마이그레이션 (백그라운드)
4. 검증 후 Phase 4 실행
5. 애플리케이션 최종 업데이트 (workspace_id 필수)

이 방식으로 다운타임을 5분 이내로 줄일 수 있습니다.
