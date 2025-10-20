"""
Tools API Endpoints
CRUD operations for tools
"""
from fastapi import APIRouter, HTTPException, status
from bend.schemas.tool import (
    ToolCreate,
    ToolUpdate,
    ToolResponse,
    ToolListResponse,
    ToolValidationResponse
)
from bend.models.tool import ToolModel
from bend.storage.memory import storage

router = APIRouter()


@router.get("/", response_model=ToolListResponse)
async def list_tools():
    """Get all tools"""
    tools = [ToolResponse(**tool.to_dict()) for tool in storage.tools.values()]
    return ToolListResponse(tools=tools, total=len(tools))


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(tool_id: str):
    """Get a specific tool by ID"""
    tool = storage.tools.get(tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool with id '{tool_id}' not found"
        )
    return ToolResponse(**tool.to_dict())


@router.post("/", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(tool_data: ToolCreate):
    """Create a new tool"""
    # Create tool
    tool = ToolModel(
        name=tool_data.name,
        description=tool_data.description,
        parameters=tool_data.parameters,
        parameters_metadata=tool_data.parameters_metadata,
    )

    # Store tool
    storage.tools[tool.tool_id] = tool

    return ToolResponse(**tool.to_dict())


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(tool_id: str, tool_data: ToolUpdate):
    """Update an existing tool"""
    tool = storage.tools.get(tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool with id '{tool_id}' not found"
        )

    # Update fields if provided
    update_dict = tool_data.model_dump(exclude_unset=True)

    # Update fields
    for field, value in update_dict.items():
        if hasattr(tool, field):
            setattr(tool, field, value)

    return ToolResponse(**tool.to_dict())


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(tool_id: str):
    """Delete a tool"""
    if tool_id not in storage.tools:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool with id '{tool_id}' not found"
        )

    # Check if tool is used by any agents
    tool_in_use = False
    agents_using_tool = []
    for agent in storage.agents.values():
        if any(t.tool_id == tool_id for t in agent.tools):
            tool_in_use = True
            agents_using_tool.append(agent.role)

    if tool_in_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tool is used by agents: {', '.join(agents_using_tool)}. "
                   f"Remove tool from agents before deleting."
        )

    del storage.tools[tool_id]


@router.post("/{tool_id}/validate", response_model=ToolValidationResponse)
async def validate_tool(tool_id: str):
    """Validate a tool configuration"""
    tool = storage.tools.get(tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool with id '{tool_id}' not found"
        )

    # Validate tool
    validation = tool.validate()

    return ToolValidationResponse(
        is_valid=validation['is_valid'],
        errors=validation['errors'],
        warnings=validation['warnings']
    )
