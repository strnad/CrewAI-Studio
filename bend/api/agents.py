"""
Agents API Endpoints
CRUD operations for agents
"""
from fastapi import APIRouter, HTTPException, status
from bend.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentListResponse,
    AgentValidationResponse
)
from bend.models.agent import AgentModel
from bend.storage.memory import storage

router = APIRouter()


@router.get("/", response_model=AgentListResponse)
async def list_agents():
    """Get all agents"""
    agents = [AgentResponse(**agent.to_dict()) for agent in storage.agents.values()]
    return AgentListResponse(agents=agents, total=len(agents))


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get a specific agent by ID"""
    agent = storage.agents.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id '{agent_id}' not found"
        )
    return AgentResponse(**agent.to_dict())


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_data: AgentCreate):
    """Create a new agent"""
    # Resolve tools from storage
    tools = []
    for tool_id in agent_data.tool_ids:
        tool = storage.tools.get(tool_id)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tool with id '{tool_id}' not found"
            )
        tools.append(tool)

    # Validate knowledge source IDs
    for ks_id in agent_data.knowledge_source_ids:
        if ks_id not in storage.knowledge_sources:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Knowledge source with id '{ks_id}' not found"
            )

    # Create agent
    agent = AgentModel(
        role=agent_data.role,
        backstory=agent_data.backstory,
        goal=agent_data.goal,
        temperature=agent_data.temperature,
        allow_delegation=agent_data.allow_delegation,
        verbose=agent_data.verbose,
        cache=agent_data.cache,
        llm_provider_model=agent_data.llm_provider_model,
        max_iter=agent_data.max_iter,
        tools=tools,
        knowledge_source_ids=agent_data.knowledge_source_ids,
    )

    # Store agent
    storage.agents[agent.id] = agent

    return AgentResponse(**agent.to_dict())


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent_data: AgentUpdate):
    """Update an existing agent"""
    agent = storage.agents.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id '{agent_id}' not found"
        )

    # Update fields if provided
    update_dict = agent_data.model_dump(exclude_unset=True)

    # Handle tool_ids if provided
    if 'tool_ids' in update_dict:
        tools = []
        for tool_id in update_dict['tool_ids']:
            tool = storage.tools.get(tool_id)
            if not tool:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tool with id '{tool_id}' not found"
                )
            tools.append(tool)
        agent.tools = tools
        del update_dict['tool_ids']

    # Handle knowledge_source_ids if provided
    if 'knowledge_source_ids' in update_dict:
        for ks_id in update_dict['knowledge_source_ids']:
            if ks_id not in storage.knowledge_sources:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Knowledge source with id '{ks_id}' not found"
                )
        agent.knowledge_source_ids = update_dict['knowledge_source_ids']
        del update_dict['knowledge_source_ids']

    # Update remaining fields
    for field, value in update_dict.items():
        if hasattr(agent, field):
            setattr(agent, field, value)

    return AgentResponse(**agent.to_dict())


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str):
    """Delete an agent"""
    if agent_id not in storage.agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id '{agent_id}' not found"
        )

    # Check if agent is used by any crews
    agent_in_use = False
    crews_using_agent = []
    for crew in storage.crews.values():
        if any(a.id == agent_id for a in crew.agents):
            agent_in_use = True
            crews_using_agent.append(crew.name)

    if agent_in_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent is used by crews: {', '.join(crews_using_agent)}. "
                   f"Remove agent from crews before deleting."
        )

    del storage.agents[agent_id]


@router.post("/{agent_id}/validate", response_model=AgentValidationResponse)
async def validate_agent(agent_id: str):
    """Validate an agent configuration"""
    agent = storage.agents.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id '{agent_id}' not found"
        )

    # Validate agent
    validation = agent.validate()

    return AgentValidationResponse(
        is_valid=validation['is_valid'],
        errors=validation['errors'],
        warnings=validation['warnings']
    )
