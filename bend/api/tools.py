"""
Tools API Endpoints
CRUD operations for tools
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from bend.schemas.tool import (
    ToolCreate,
    ToolUpdate,
    ToolResponse,
    ToolListResponse,
    ToolValidationResponse
)
from bend.services import ToolService
from bend.database.connection import get_db_session

router = APIRouter()


@router.get("/", response_model=ToolListResponse)
async def list_tools(db: Session = Depends(get_db_session)):
    """Get all tools"""
    service = ToolService(db)
    tools_list = service.list_tools()
    tools = [ToolResponse(**tool.to_dict()) for tool in tools_list]
    return ToolListResponse(tools=tools, total=len(tools))


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(tool_id: str, db: Session = Depends(get_db_session)):
    """Get a specific tool by ID"""
    service = ToolService(db)
    tool = service.get_tool(tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool with id '{tool_id}' not found"
        )
    return ToolResponse(**tool.to_dict())


@router.post("/", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(tool_data: ToolCreate, db: Session = Depends(get_db_session)):
    """Create a new tool"""
    service = ToolService(db)
    try:
        tool = service.create_tool(
            name=tool_data.name,
            description=tool_data.description,
            parameters=tool_data.parameters,
            parameters_metadata=tool_data.parameters_metadata
        )
        return ToolResponse(**tool.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(tool_id: str, tool_data: ToolUpdate, db: Session = Depends(get_db_session)):
    """Update an existing tool"""
    service = ToolService(db)
    try:
        update_dict = tool_data.model_dump(exclude_unset=True)
        tool = service.update_tool(tool_id, **update_dict)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool with id '{tool_id}' not found"
            )
        return ToolResponse(**tool.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(tool_id: str, db: Session = Depends(get_db_session)):
    """Delete a tool"""
    service = ToolService(db)
    try:
        success = service.delete_tool(tool_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool with id '{tool_id}' not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{tool_id}/validate", response_model=ToolValidationResponse)
async def validate_tool(tool_id: str, db: Session = Depends(get_db_session)):
    """Validate a tool configuration"""
    service = ToolService(db)
    try:
        validation = service.validate_tool(tool_id)
        return ToolValidationResponse(
            is_valid=validation['is_valid'],
            errors=validation['errors'],
            warnings=validation['warnings']
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
