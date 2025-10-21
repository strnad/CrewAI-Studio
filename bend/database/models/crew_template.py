"""
CrewTemplate Model
크루 템플릿 모델 - 재사용 가능한 크루 설정
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from bend.database.connection import Base


class TemplateVisibility(str, enum.Enum):
    """템플릿 공개 범위"""
    PRIVATE = "private"         # 본인만
    WORKSPACE = "workspace"     # 워크스페이스 멤버
    PUBLIC = "public"           # 모든 사용자 (승인 필요)


class CrewTemplate(Base):
    """크루 템플릿 모델"""
    __tablename__ = "crew_templates"

    # Primary Key
    id = Column(String(12), primary_key=True)

    # 기본 정보
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True, index=True)

    # 템플릿 데이터 (JSON)
    # crew 설정, agents, tasks 등 모든 정보 포함
    template_data = Column(JSON, nullable=False)

    # 공개 범위
    visibility = Column(
        SQLEnum(TemplateVisibility),
        default=TemplateVisibility.PRIVATE,
        nullable=False,
        index=True
    )

    # 소속 및 생성자
    workspace_id = Column(
        String(12),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    created_by = Column(
        String(12),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # 승인 상태 (public 템플릿만 해당)
    is_approved = Column(Boolean, default=False, nullable=False, index=True)

    # 사용 통계
    use_count = Column(Integer, default=0, nullable=False)
    rating_avg = Column(DECIMAL(3, 2), default=0.00, nullable=False)
    rating_count = Column(Integer, default=0, nullable=False)

    # 태그 (검색용)
    tags = Column(JSON, nullable=True)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    workspace = relationship(
        "Workspace",
        back_populates="templates"
    )
    creator = relationship(
        "User",
        back_populates="created_templates"
    )
    favorites = relationship(
        "TemplateFavorite",
        back_populates="template",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<CrewTemplate(id={self.id}, name={self.name}, visibility={self.visibility})>"

    def to_dict(self, include_template_data=True, include_creator=False):
        """딕셔너리 변환"""
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "visibility": self.visibility.value if isinstance(self.visibility, TemplateVisibility) else self.visibility,
            "workspace_id": self.workspace_id,
            "created_by": self.created_by,
            "is_approved": self.is_approved,
            "use_count": self.use_count,
            "rating_avg": float(self.rating_avg) if self.rating_avg else 0.0,
            "rating_count": self.rating_count,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

        if include_template_data:
            data["template_data"] = self.template_data

        if include_creator and self.creator:
            data["creator"] = {
                "id": self.creator.id,
                "name": self.creator.name,
                "email": self.creator.email
            }

        return data

    def can_access(self, user_id: str, workspace_id: str = None) -> bool:
        """접근 권한 체크"""
        # 생성자는 항상 접근 가능
        if self.created_by == user_id:
            return True

        # Private: 생성자만
        if self.visibility == TemplateVisibility.PRIVATE:
            return False

        # Workspace: 같은 워크스페이스 멤버
        if self.visibility == TemplateVisibility.WORKSPACE:
            return self.workspace_id == workspace_id

        # Public: 승인된 경우 누구나
        if self.visibility == TemplateVisibility.PUBLIC:
            return self.is_approved

        return False
