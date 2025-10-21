"""
TemplateFavorite Model
크루 템플릿 즐겨찾기 모델
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from bend.database.connection import Base


class TemplateFavorite(Base):
    """템플릿 즐겨찾기 모델"""
    __tablename__ = "template_favorites"

    # Primary Key
    id = Column(String(12), primary_key=True)

    # Foreign Keys
    template_id = Column(
        String(12),
        ForeignKey("crew_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        String(12),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Unique constraint: 한 사용자는 한 템플릿을 한 번만 즐겨찾기 가능
    __table_args__ = (
        UniqueConstraint('template_id', 'user_id', name='unique_template_user'),
    )

    # Relationships
    template = relationship(
        "CrewTemplate",
        back_populates="favorites"
    )
    user = relationship(
        "User",
        back_populates="favorite_templates"
    )

    def __repr__(self):
        return f"<TemplateFavorite(template_id={self.template_id}, user_id={self.user_id})>"

    def to_dict(self):
        """딕셔너리 변환"""
        return {
            "id": self.id,
            "template_id": self.template_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat()
        }
