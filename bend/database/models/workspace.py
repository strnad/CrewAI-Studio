"""
Workspace Model
워크스페이스 모델 - 멀티테넌시의 핵심
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from bend.database.connection import Base


class Workspace(Base):
    """워크스페이스 모델"""
    __tablename__ = "workspaces"

    # Primary Key
    id = Column(String(12), primary_key=True)

    # 기본 정보
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # 소유자
    owner_id = Column(String(12), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 플랜 및 제한
    plan = Column(String(20), default="free", nullable=False)  # free, pro, enterprise
    max_members = Column(Integer, default=5, nullable=False)

    # 상태
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # 설정 (JSON)
    settings = Column(JSON, nullable=True)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    # 소유자
    owner = relationship(
        "User",
        back_populates="owned_workspaces",
        foreign_keys=[owner_id]
    )

    # 멤버
    members = relationship(
        "WorkspaceMember",
        back_populates="workspace",
        cascade="all, delete-orphan"
    )

    # 리소스들
    agents = relationship(
        "Agent",
        back_populates="workspace",
        cascade="all, delete-orphan"
    )
    crews = relationship(
        "Crew",
        back_populates="workspace",
        cascade="all, delete-orphan"
    )
    tasks = relationship(
        "Task",
        back_populates="workspace",
        cascade="all, delete-orphan"
    )
    tools = relationship(
        "Tool",
        back_populates="workspace",
        cascade="all, delete-orphan"
    )
    knowledge_sources = relationship(
        "KnowledgeSource",
        back_populates="workspace",
        cascade="all, delete-orphan"
    )

    # 크루 템플릿
    templates = relationship(
        "CrewTemplate",
        back_populates="workspace",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Workspace(id={self.id}, name={self.name}, slug={self.slug})>"

    def to_dict(self, include_members=False):
        """딕셔너리 변환"""
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "owner_id": self.owner_id,
            "plan": self.plan,
            "max_members": self.max_members,
            "is_active": self.is_active,
            "settings": self.settings,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

        if include_members:
            data["members"] = [m.to_dict() for m in self.members]
            data["member_count"] = len(self.members)

        return data
