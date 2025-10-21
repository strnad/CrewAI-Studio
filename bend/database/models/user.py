"""
User Model
사용자 계정 모델
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from bend.database.connection import Base


class UserRole(str, enum.Enum):
    """글로벌 사용자 역할"""
    SYSTEM_ADMIN = "system_admin"  # 최상위 시스템 관리자
    REGULAR_USER = "regular_user"  # 일반 사용자


class UserStatus(str, enum.Enum):
    """사용자 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    # Primary Key
    id = Column(String(12), primary_key=True)

    # 기본 정보
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)

    # 역할 및 상태 정보 (일관된 enum 사용)
    system_role = Column(SQLEnum(UserRole), default=UserRole.REGULAR_USER, nullable=False, index=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False, index=True)
    email_verified = Column(Boolean, default=False, nullable=False)

    # 활동 추적
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    # 소유한 워크스페이스 (owner로서)
    owned_workspaces = relationship(
        "Workspace",
        back_populates="owner",
        cascade="all, delete-orphan",
        foreign_keys="Workspace.owner_id"
    )

    # 멤버로 속한 워크스페이스
    workspace_memberships = relationship(
        "WorkspaceMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # 생성한 리소스들
    created_agents = relationship(
        "Agent",
        back_populates="creator",
        foreign_keys="Agent.created_by",
        cascade="all, delete-orphan"
    )
    created_crews = relationship(
        "Crew",
        back_populates="creator",
        foreign_keys="Crew.created_by",
        cascade="all, delete-orphan"
    )
    created_tasks = relationship(
        "Task",
        back_populates="creator",
        foreign_keys="Task.created_by",
        cascade="all, delete-orphan"
    )
    created_tools = relationship(
        "Tool",
        back_populates="creator",
        foreign_keys="Tool.created_by",
        cascade="all, delete-orphan"
    )
    created_knowledge_sources = relationship(
        "KnowledgeSource",
        back_populates="creator",
        foreign_keys="KnowledgeSource.created_by",
        cascade="all, delete-orphan"
    )

    # 크루 템플릿
    created_templates = relationship(
        "CrewTemplate",
        back_populates="creator",
        cascade="all, delete-orphan"
    )
    favorite_templates = relationship(
        "TemplateFavorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # 크루 실행 기록
    executed_crew_runs = relationship(
        "CrewRun",
        back_populates="executor",
        foreign_keys="CrewRun.executed_by"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"

    def to_dict(self):
        """딕셔너리 변환 (비밀번호 제외)"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "system_role": self.system_role.value if isinstance(self.system_role, UserRole) else self.system_role,
            "status": self.status.value if isinstance(self.status, UserStatus) else self.status,
            "email_verified": self.email_verified,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def is_system_admin(self) -> bool:
        """시스템 관리자 여부 확인 (헬퍼 메서드)"""
        return self.system_role == UserRole.SYSTEM_ADMIN

    def is_active(self) -> bool:
        """활성 사용자 여부 확인 (헬퍼 메서드)"""
        return self.status == UserStatus.ACTIVE
