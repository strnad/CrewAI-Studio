# Alembic Database Migration Guide

## 개요

Alembic을 사용하여 데이터베이스 스키마 변경을 버전 관리합니다.

## 설정 완료 사항

✅ Alembic 초기화 완료
✅ 모든 ORM 모델 등록 (Tool, KnowledgeSource, Agent, Task, Crew)
✅ 현재 스키마를 baseline migration으로 생성
✅ Database 버전을 head로 stamp

## 주요 명령어

### 1. 현재 Migration 상태 확인
```bash
cd /mnt/c/data/300.Workspaces/CrewAI-Studio
./bend/scripts/alembic_wrapper.sh current
```

### 2. Migration 히스토리 확인
```bash
./bend/scripts/alembic_wrapper.sh history
```

### 3. 새로운 Migration 생성 (Auto-generate)
```bash
# ORM 모델을 변경한 후 실행
./bend/scripts/alembic_wrapper.sh revision --autogenerate -m "설명 메시지"
```

### 4. Migration 적용 (Upgrade)
```bash
# 최신 버전으로 업그레이드
./bend/scripts/alembic_wrapper.sh upgrade head

# 특정 버전으로 업그레이드
./bend/scripts/alembic_wrapper.sh upgrade <revision_id>
```

### 5. Migration 롤백 (Downgrade)
```bash
# 이전 버전으로 롤백
./bend/scripts/alembic_wrapper.sh downgrade -1

# 특정 버전으로 롤백
./bend/scripts/alembic_wrapper.sh downgrade <revision_id>
```

## 워크플로우 예시

### ORM 모델 변경 시

1. **모델 수정**: `bend/database/models/*.py` 파일 수정
2. **Migration 생성**:
   ```bash
   ./bend/scripts/alembic_wrapper.sh revision --autogenerate -m "Add new column to Agent"
   ```
3. **Migration 파일 검토**: `bend/alembic/versions/` 에서 생성된 파일 확인
4. **Migration 적용**:
   ```bash
   ./bend/scripts/alembic_wrapper.sh upgrade head
   ```

### 프로덕션 배포 시

1. **개발 환경에서 Migration 생성 및 테스트**
2. **Git에 커밋**: Migration 파일을 버전 관리에 포함
3. **프로덕션 서버에서 적용**:
   ```bash
   git pull
   ./bend/scripts/alembic_wrapper.sh upgrade head
   ```

## 현재 상태

- **Current Revision**: `799f20a37e7e` (Initial schema with all models)
- **Database**: PostgreSQL (wsl_db)
- **Tables**: 12개 (5 entity + 7 association tables)

## 주의사항

⚠️ **프로덕션 데이터베이스**:
- Migration 적용 전 항상 백업
- Downgrade 스크립트도 함께 테스트
- 큰 테이블 변경 시 실행 시간 고려

⚠️ **Auto-generate 한계**:
- 컬럼명 변경은 감지 못함 (drop + add로 인식)
- 데이터 마이그레이션은 수동 작성 필요
- 생성된 Migration 파일 항상 검토 필요

## 트러블슈팅

### "Target database is not up to date" 에러
```bash
# 현재 상태 확인
./bend/scripts/alembic_wrapper.sh current

# Head로 업그레이드
./bend/scripts/alembic_wrapper.sh upgrade head
```

### "Can't locate revision" 에러
```bash
# Migration 파일이 존재하는지 확인
ls -la bend/alembic/versions/

# 강제로 head 버전 설정 (주의!)
./bend/scripts/alembic_wrapper.sh stamp head
```
