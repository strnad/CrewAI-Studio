"""
Workspaces API Endpoints
워크스페이스 관련 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from bend.database.connection import get_db
from bend.services.workspace_service import WorkspaceService
from typing import Optional, List

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


# Request/Response Models
class WorkspaceCreateRequest(BaseModel):
    """워크스페이스 생성 요청"""
    name: str
    owner_id: str
    description: Optional[str] = None
    slug: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "My Workspace",
                "owner_id": "U_1234567890",
                "description": "This is my workspace",
                "slug": "my-workspace"
            }
        }


class WorkspaceUpdateRequest(BaseModel):
    """워크스페이스 업데이트 요청"""
    name: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Workspace",
                "description": "Updated description"
            }
        }


class WorkspaceResponse(BaseModel):
    """워크스페이스 응답"""
    id: str
    name: str
    slug: str
    description: Optional[str]
    owner_id: str
    plan: str
    max_members: int
    is_active: bool
    settings: Optional[dict]
    created_at: str
    updated_at: str
    members: Optional[List[dict]] = None
    member_count: Optional[int] = None


# API Endpoints
@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    request: WorkspaceCreateRequest,
    db: Session = Depends(get_db)
):
    """
    워크스페이스 생성

    - **name**: 워크스페이스 이름
    - **owner_id**: 소유자 User ID
    - **description**: 설명 (선택)
    - **slug**: URL slug (선택, 없으면 자동 생성)
    """
    service = WorkspaceService(db)

    try:
        workspace = service.create_workspace(
            name=request.name,
            owner_id=request.owner_id,
            description=request.description,
            slug=request.slug
        )
        return workspace
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[WorkspaceResponse])
def list_user_workspaces(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    사용자가 속한 워크스페이스 목록 조회

    - **user_id**: 사용자 ID (query parameter)
    """
    service = WorkspaceService(db)
    workspaces = service.get_user_workspaces(user_id)
    return workspaces


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """
    워크스페이스 조회

    - **workspace_id**: 워크스페이스 ID
    """
    service = WorkspaceService(db)
    workspace = service.get_workspace_by_id(workspace_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace not found: {workspace_id}"
        )

    return workspace


@router.get("/slug/{slug}", response_model=WorkspaceResponse)
def get_workspace_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Slug로 워크스페이스 조회

    - **slug**: 워크스페이스 slug
    """
    service = WorkspaceService(db)
    workspace = service.get_workspace_by_slug(slug)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace not found: {slug}"
        )

    return workspace


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: str,
    request: WorkspaceUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    워크스페이스 정보 업데이트

    - **workspace_id**: 워크스페이스 ID
    - **name**: 변경할 이름 (선택)
    - **description**: 변경할 설명 (선택)
    - **slug**: 변경할 slug (선택)
    - **is_active**: 활성화 상태 (선택)
    """
    service = WorkspaceService(db)

    try:
        workspace = service.update_workspace(
            workspace_id=workspace_id,
            name=request.name,
            description=request.description,
            slug=request.slug,
            is_active=request.is_active
        )

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace not found: {workspace_id}"
            )

        return workspace
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """
    워크스페이스 삭제

    - **workspace_id**: 워크스페이스 ID
    """
    service = WorkspaceService(db)

    if not service.delete_workspace(workspace_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace not found: {workspace_id}"
        )

    return None
