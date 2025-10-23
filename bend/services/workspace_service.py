"""
Workspace Service
워크스페이스 비즈니스 로직
"""
from sqlalchemy.orm import Session
from bend.database.models.workspace import Workspace
from bend.database.models.workspace_member import WorkspaceMember, WorkspaceRole
from bend.database.repositories.workspace_repository import WorkspaceRepository
from bend.utils.id_generator import generate_workspace_id
from typing import Optional, Dict, List
from datetime import datetime
import re


class WorkspaceService:
    """Workspace 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = WorkspaceRepository(db)

    def create_workspace(
        self,
        name: str,
        owner_id: str,
        description: Optional[str] = None,
        slug: Optional[str] = None
    ) -> Dict:
        """
        워크스페이스 생성

        Args:
            name: 워크스페이스 이름
            owner_id: 소유자 User ID
            description: 설명 (선택)
            slug: URL slug (선택, 없으면 자동 생성)

        Returns:
            Dict: 생성된 워크스페이스 정보

        Raises:
            ValueError: slug가 이미 존재하는 경우
        """
        # Slug 생성 또는 검증
        if not slug:
            slug = self._generate_slug(name)
        else:
            slug = self._sanitize_slug(slug)

        # Slug 중복 체크
        if self.repository.exists_by_slug(slug):
            raise ValueError(f"Slug already exists: {slug}")

        # Workspace 생성
        workspace = Workspace(
            id=generate_workspace_id(),
            name=name,
            slug=slug,
            description=description,
            owner_id=owner_id,
            plan="free",
            max_members=5,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        created_workspace = self.repository.create(workspace)

        # 소유자를 OWNER 권한으로 멤버에 추가
        self._add_owner_as_member(created_workspace.id, owner_id)

        return created_workspace.to_dict(include_members=True)

    def get_workspace_by_id(self, workspace_id: str) -> Optional[Dict]:
        """ID로 워크스페이스 조회"""
        workspace = self.repository.get_by_id(workspace_id)
        return workspace.to_dict(include_members=True) if workspace else None

    def get_workspace_by_slug(self, slug: str) -> Optional[Dict]:
        """Slug로 워크스페이스 조회"""
        workspace = self.repository.get_by_slug(slug)
        return workspace.to_dict(include_members=True) if workspace else None

    def get_user_workspaces(self, user_id: str) -> List[Dict]:
        """
        사용자가 속한 모든 워크스페이스 조회
        (소유자 + 멤버로 속한 워크스페이스)
        """
        # 소유한 워크스페이스
        owned = self.repository.get_by_owner(user_id)

        # 멤버로 속한 워크스페이스
        member_workspaces = self.db.query(Workspace).join(
            WorkspaceMember,
            WorkspaceMember.workspace_id == Workspace.id
        ).filter(
            WorkspaceMember.user_id == user_id
        ).all()

        # 중복 제거 (소유자이면서 멤버인 경우)
        all_workspaces = {ws.id: ws for ws in owned + member_workspaces}.values()

        return [ws.to_dict() for ws in all_workspaces]

    def update_workspace(
        self,
        workspace_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        slug: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict]:
        """워크스페이스 정보 업데이트"""
        workspace = self.repository.get_by_id(workspace_id)

        if not workspace:
            return None

        if name:
            workspace.name = name

        if description is not None:
            workspace.description = description

        if slug:
            sanitized_slug = self._sanitize_slug(slug)
            if sanitized_slug != workspace.slug:
                if self.repository.exists_by_slug(sanitized_slug):
                    raise ValueError(f"Slug already exists: {sanitized_slug}")
                workspace.slug = sanitized_slug

        if is_active is not None:
            workspace.is_active = is_active

        workspace.updated_at = datetime.utcnow()
        updated_workspace = self.repository.update(workspace)

        return updated_workspace.to_dict(include_members=True)

    def delete_workspace(self, workspace_id: str) -> bool:
        """워크스페이스 삭제"""
        return self.repository.delete(workspace_id)

    def _generate_slug(self, name: str) -> str:
        """이름에서 slug 자동 생성"""
        # 소문자 변환
        slug = name.lower()
        # 특수문자 제거, 공백을 하이픈으로
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')

        # 중복 시 숫자 추가
        original_slug = slug
        counter = 1
        while self.repository.exists_by_slug(slug):
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug

    def _sanitize_slug(self, slug: str) -> str:
        """Slug 정리 (소문자, 영숫자와 하이픈만)"""
        slug = slug.lower()
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')

    def _add_owner_as_member(self, workspace_id: str, owner_id: str):
        """워크스페이스 생성 시 소유자를 OWNER 권한으로 멤버에 추가"""
        from bend.utils.id_generator import generate_id

        member = WorkspaceMember(
            id=generate_id("WM_", 10),
            workspace_id=workspace_id,
            user_id=owner_id,
            role=WorkspaceRole.OWNER,
            joined_at=datetime.utcnow()
        )

        self.db.add(member)
        self.db.commit()
