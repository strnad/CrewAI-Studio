"""
Agents API Endpoints
CRUD operations for agents
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from bend.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentListResponse,
    AgentValidationResponse
)
from bend.services import AgentService
from bend.database.connection import get_db_session

router = APIRouter()


@router.get("/", response_model=AgentListResponse)
async def list_agents(db: Session = Depends(get_db_session)):
    """Get all agents"""
    service = AgentService(db)
    agents_list = service.list_agents()
    agents = [AgentResponse(**agent.to_dict()) for agent in agents_list]
    return AgentListResponse(agents=agents, total=len(agents))


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: Session = Depends(get_db_session)):
    """Get a specific agent by ID"""
    service = AgentService(db)
    agent = service.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id '{agent_id}' not found"
        )
    return AgentResponse(**agent.to_dict())


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db_session)):
    """Create a new agent"""
    service = AgentService(db)
    try:
        agent = service.create_agent(
            role=agent_data.role,
            backstory=agent_data.backstory,
            goal=agent_data.goal,
            llm_provider_model=agent_data.llm_provider_model,
            tool_ids=agent_data.tool_ids,
            knowledge_source_ids=agent_data.knowledge_source_ids,
            temperature=agent_data.temperature,
            max_iter=agent_data.max_iter,
            allow_delegation=agent_data.allow_delegation,
            verbose=agent_data.verbose,
            cache=agent_data.cache
        )
        return AgentResponse(**agent.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent_data: AgentUpdate, db: Session = Depends(get_db_session)):
    """Update an existing agent"""
    service = AgentService(db)
    try:
        update_dict = agent_data.model_dump(exclude_unset=True)
        agent = service.update_agent(agent_id, **update_dict)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with id '{agent_id}' not found"
            )
        return AgentResponse(**agent.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str, db: Session = Depends(get_db_session)):
    """Delete an agent"""
    service = AgentService(db)
    try:
        success = service.delete_agent(agent_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with id '{agent_id}' not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{agent_id}/validate", response_model=AgentValidationResponse)
async def validate_agent(agent_id: str, db: Session = Depends(get_db_session)):
    """Validate an agent configuration"""
    service = AgentService(db)
    try:
        validation = service.validate_agent(agent_id)
        return AgentValidationResponse(
            is_valid=validation['is_valid'],
            errors=validation['errors'],
            warnings=validation['warnings']
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
