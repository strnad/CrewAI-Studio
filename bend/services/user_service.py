"""
User Service
사용자 비즈니스 로직
"""
from sqlalchemy.orm import Session
from bend.database.models.user import User, UserRole, UserStatus
from bend.database.repositories.user_repository import UserRepository
from bend.utils.id_generator import generate_user_id
from bend.utils.security import hash_password, verify_password
from typing import Optional, Dict
from datetime import datetime


class UserService:
    """User 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def register_user(
        self,
        email: str,
        password: str,
        name: str
    ) -> Dict:
        """
        사용자 회원가입

        Args:
            email: 이메일
            password: 비밀번호 (평문)
            name: 이름

        Returns:
            Dict: 생성된 사용자 정보

        Raises:
            ValueError: 이메일이 이미 존재하는 경우
        """
        # 이메일 중복 체크
        if self.repository.exists_by_email(email):
            raise ValueError(f"Email already exists: {email}")

        # 비밀번호 해싱
        password_hash = hash_password(password)

        # User 생성
        user = User(
            id=generate_user_id(),
            email=email,
            password_hash=password_hash,
            name=name,
            system_role=UserRole.REGULAR_USER,
            status=UserStatus.ACTIVE,
            email_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        created_user = self.repository.create(user)

        return created_user.to_dict()

    def authenticate(self, email: str, password: str) -> Optional[Dict]:
        """
        사용자 인증 (로그인)

        Args:
            email: 이메일
            password: 비밀번호 (평문)

        Returns:
            Optional[Dict]: 인증 성공 시 사용자 정보, 실패 시 None
        """
        user = self.repository.get_by_email(email)

        if not user:
            return None

        if user.status != UserStatus.ACTIVE:
            return None

        if not verify_password(password, user.password_hash):
            return None

        # 마지막 로그인 시간 업데이트
        user.last_login_at = datetime.utcnow()
        self.repository.update(user)

        return user.to_dict()

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """ID로 사용자 조회"""
        user = self.repository.get_by_id(user_id)
        return user.to_dict() if user else None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """이메일로 사용자 조회"""
        user = self.repository.get_by_email(email)
        return user.to_dict() if user else None

    def update_user(
        self,
        user_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None
    ) -> Optional[Dict]:
        """사용자 정보 업데이트"""
        user = self.repository.get_by_id(user_id)

        if not user:
            return None

        if name:
            user.name = name

        if email and email != user.email:
            if self.repository.exists_by_email(email):
                raise ValueError(f"Email already exists: {email}")
            user.email = email
            user.email_verified = False  # 이메일 변경 시 재인증 필요

        user.updated_at = datetime.utcnow()
        updated_user = self.repository.update(user)

        return updated_user.to_dict()

    def delete_user(self, user_id: str) -> bool:
        """사용자 삭제"""
        return self.repository.delete(user_id)
