"""
Users API Endpoints
사용자 관련 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from bend.database.connection import get_db
from bend.services.user_service import UserService
from typing import Optional

router = APIRouter(prefix="/users", tags=["users"])


# Request/Response Models
class UserRegisterRequest(BaseModel):
    """회원가입 요청"""
    email: EmailStr
    password: str
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "name": "John Doe"
            }
        }


class UserLoginRequest(BaseModel):
    """로그인 요청"""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class UserUpdateRequest(BaseModel):
    """사용자 정보 업데이트 요청"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Updated",
                "email": "newemail@example.com"
            }
        }


class UserResponse(BaseModel):
    """사용자 응답"""
    id: str
    email: str
    name: str
    system_role: str  # "system_admin" or "regular_user"
    status: str       # "active", "inactive", "suspended"
    email_verified: bool
    last_login_at: Optional[str]
    created_at: str
    updated_at: str


# API Endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    사용자 회원가입

    - **email**: 이메일 주소 (고유값)
    - **password**: 비밀번호 (8자 이상 권장)
    - **name**: 사용자 이름
    """
    service = UserService(db)

    try:
        user = service.register_user(
            email=request.email,
            password=request.password,
            name=request.name
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=UserResponse)
def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    사용자 로그인

    - **email**: 이메일 주소
    - **password**: 비밀번호
    """
    service = UserService(db)

    user = service.authenticate(
        email=request.email,
        password=request.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    사용자 조회

    - **user_id**: 사용자 ID
    """
    service = UserService(db)
    user = service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    request: UserUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    사용자 정보 업데이트

    - **user_id**: 사용자 ID
    - **name**: 변경할 이름 (선택)
    - **email**: 변경할 이메일 (선택)
    """
    service = UserService(db)

    try:
        user = service.update_user(
            user_id=user_id,
            name=request.name,
            email=request.email
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {user_id}"
            )

        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    사용자 삭제

    - **user_id**: 사용자 ID
    """
    service = UserService(db)

    if not service.delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}"
        )

    return None
