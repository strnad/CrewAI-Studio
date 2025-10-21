"""
User Repository
User 모델에 대한 데이터베이스 작업
"""
from sqlalchemy.orm import Session
from bend.database.models.user import User
from typing import Optional, List


class UserRepository:
    """User 저장소"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        """사용자 생성"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """모든 사용자 조회"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def update(self, user: User) -> User:
        """사용자 정보 업데이트"""
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: str) -> bool:
        """사용자 삭제"""
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

    def exists_by_email(self, email: str) -> bool:
        """이메일 존재 여부 확인"""
        return self.db.query(User).filter(User.email == email).count() > 0
