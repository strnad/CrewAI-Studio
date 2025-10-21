"""
WorkspaceMember Model
워크스페이스 멤버십 모델 - RBAC의 핵심
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from bend.database.connection import Base


class WorkspaceRole(str, enum.Enum):
    """워크스페이스 역할"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class WorkspaceMember(Base):
    """워크스페이스 멤버십 모델"""
    __tablename__ = "workspace_members"

    # Primary Key
    id = Column(String(12), primary_key=True)

    # Foreign Keys
    workspace_id = Column(
        String(12),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        String(12),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # 역할
    role = Column(
        SQLEnum(WorkspaceRole),
        default=WorkspaceRole.MEMBER,
        nullable=False,
        index=True
    )

    # 세부 권한 (커스터마이징 가능)
    permissions = Column(JSON, nullable=True)

    # 타임스탬프
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Unique constraint: 한 사용자는 한 워크스페이스에 한 번만 참여
    __table_args__ = (
        UniqueConstraint('workspace_id', 'user_id', name='unique_workspace_user'),
    )

    # Relationships
    workspace = relationship(
        "Workspace",
        back_populates="members"
    )
    user = relationship(
        "User",
        back_populates="workspace_memberships"
    )

    def __repr__(self):
        return f"<WorkspaceMember(workspace_id={self.workspace_id}, user_id={self.user_id}, role={self.role})>"

    def to_dict(self, include_user=False, include_workspace=False):
        """딕셔너리 변환"""
        data = {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "role": self.role.value if isinstance(self.role, WorkspaceRole) else self.role,
            "permissions": self.permissions,
            "joined_at": self.joined_at.isoformat()
        }

        if include_user and self.user:
            data["user"] = self.user.to_dict()

        if include_workspace and self.workspace:
            data["workspace"] = self.workspace.to_dict()

        return data

    def has_permission(self, action: str, resource=None) -> bool:
        """권한 체크"""
        role = self.role.value if isinstance(self.role, WorkspaceRole) else self.role

        # 읽기는 모든 역할 가능
        if action == "read":
            return True

        # 생성은 owner, admin, member 가능
        if action == "create":
            return role in ["owner", "admin", "member"]

        # 수정/삭제
        if action in ["update", "delete"]:
            # 본인 리소스인 경우
            if resource and hasattr(resource, "created_by"):
                if resource.created_by == self.user_id:
                    return role in ["owner", "admin", "member"]
            # 타인 리소스인 경우
            return role in ["owner", "admin"]

        # 크루 실행
        if action == "execute_crew":
            # 본인 크루 또는 공유된 크루
            if resource:
                if hasattr(resource, "created_by") and resource.created_by == self.user_id:
                    return role in ["owner", "admin", "member"]
                # 추가: is_shared 속성 체크 (필요시)
            return role in ["owner", "admin", "member"]

        # 멤버 관리
        if action == "manage_members":
            return role in ["owner", "admin"]

        # 워크스페이스 관리
        if action == "manage_workspace":
            return role == "owner"

        # 기본적으로 거부
        return False
