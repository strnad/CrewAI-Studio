"""
Workspace Repository
워크스페이스 데이터 접근 레이어
"""
from sqlalchemy.orm import Session
from bend.database.models.workspace import Workspace
from typing import Optional, List


class WorkspaceRepository:
    """Workspace CRUD Repository"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, workspace: Workspace) -> Workspace:
        """워크스페이스 생성"""
        self.db.add(workspace)
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def get_by_id(self, workspace_id: str) -> Optional[Workspace]:
        """ID로 워크스페이스 조회"""
        return self.db.query(Workspace).filter(Workspace.id == workspace_id).first()

    def get_by_slug(self, slug: str) -> Optional[Workspace]:
        """Slug로 워크스페이스 조회"""
        return self.db.query(Workspace).filter(Workspace.slug == slug).first()

    def get_by_owner(self, owner_id: str) -> List[Workspace]:
        """소유자 ID로 워크스페이스 목록 조회"""
        return self.db.query(Workspace).filter(Workspace.owner_id == owner_id).all()

    def get_all(self) -> List[Workspace]:
        """모든 워크스페이스 조회"""
        return self.db.query(Workspace).all()

    def update(self, workspace: Workspace) -> Workspace:
        """워크스페이스 업데이트"""
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def delete(self, workspace_id: str) -> bool:
        """워크스페이스 삭제"""
        workspace = self.get_by_id(workspace_id)
        if workspace:
            self.db.delete(workspace)
            self.db.commit()
            return True
        return False

    def exists_by_slug(self, slug: str) -> bool:
        """Slug 존재 여부 확인"""
        return self.db.query(Workspace).filter(Workspace.slug == slug).count() > 0

    def count_members(self, workspace_id: str) -> int:
        """워크스페이스 멤버 수 조회"""
        from bend.database.models.workspace_member import WorkspaceMember
        return self.db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id
        ).count()
