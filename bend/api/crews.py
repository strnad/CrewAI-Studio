"""
Crews API Endpoints
CRUD operations for Crew management
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from bend.schemas.crew import (
    CrewCreate,
    CrewUpdate,
    CrewResponse,
    CrewListResponse,
    CrewValidationResponse
)
from bend.models.crew import CrewModel
from bend.storage.memory import storage

router = APIRouter()


@router.get("/", response_model=CrewListResponse)
async def list_crews():
    """Get all crews"""
    crews = [
        CrewResponse(**crew.to_dict())
        for crew in storage.crews.values()
    ]
    return CrewListResponse(crews=crews, total=len(crews))


@router.get("/{crew_id}", response_model=CrewResponse)
async def get_crew(crew_id: str):
    """Get a specific crew by ID"""
    crew = storage.crews.get(crew_id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crew with id '{crew_id}' not found"
        )
    return CrewResponse(**crew.to_dict())


@router.post("/", response_model=CrewResponse, status_code=status.HTTP_201_CREATED)
async def create_crew(crew_data: CrewCreate):
    """Create a new crew"""
    # Resolve agents from storage
    agents = []
    for agent_id in crew_data.agent_ids:
        agent = storage.agents.get(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent with id '{agent_id}' not found"
            )
        agents.append(agent)

    # Resolve tasks from storage
    tasks = []
    for task_id in crew_data.task_ids:
        task = storage.tasks.get(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Task with id '{task_id}' not found"
            )
        tasks.append(task)

    # Resolve manager agent if specified
    manager_agent = None
    if crew_data.manager_agent_id:
        manager_agent = storage.agents.get(crew_data.manager_agent_id)
        if not manager_agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Manager agent with id '{crew_data.manager_agent_id}' not found"
            )

    # Create crew model
    crew = CrewModel(
        name=crew_data.name,
        agents=agents,
        tasks=tasks,
        process=crew_data.process,
        verbose=crew_data.verbose,
        cache=crew_data.cache,
        max_rpm=crew_data.max_rpm,
        memory=crew_data.memory,
        planning=crew_data.planning,
        manager_llm=crew_data.manager_llm,
        manager_agent=manager_agent,
        planning_llm=crew_data.planning_llm,
        knowledge_source_ids=crew_data.knowledge_source_ids,
    )

    # Store crew
    storage.crews[crew.id] = crew

    return CrewResponse(**crew.to_dict())


@router.put("/{crew_id}", response_model=CrewResponse)
async def update_crew(crew_id: str, crew_data: CrewUpdate):
    """Update an existing crew"""
    crew = storage.crews.get(crew_id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crew with id '{crew_id}' not found"
        )

    # Update fields if provided
    if crew_data.name is not None:
        crew.name = crew_data.name

    if crew_data.agent_ids is not None:
        agents = []
        for agent_id in crew_data.agent_ids:
            agent = storage.agents.get(agent_id)
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Agent with id '{agent_id}' not found"
                )
            agents.append(agent)
        crew.agents = agents

    if crew_data.task_ids is not None:
        tasks = []
        for task_id in crew_data.task_ids:
            task = storage.tasks.get(task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Task with id '{task_id}' not found"
                )
            tasks.append(task)
        crew.tasks = tasks

    if crew_data.process is not None:
        crew.process = crew_data.process

    if crew_data.verbose is not None:
        crew.verbose = crew_data.verbose

    if crew_data.cache is not None:
        crew.cache = crew_data.cache

    if crew_data.max_rpm is not None:
        crew.max_rpm = crew_data.max_rpm

    if crew_data.memory is not None:
        crew.memory = crew_data.memory

    if crew_data.planning is not None:
        crew.planning = crew_data.planning

    if crew_data.manager_llm is not None:
        crew.manager_llm = crew_data.manager_llm

    if crew_data.manager_agent_id is not None:
        manager_agent = storage.agents.get(crew_data.manager_agent_id)
        if not manager_agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Manager agent with id '{crew_data.manager_agent_id}' not found"
            )
        crew.manager_agent = manager_agent

    if crew_data.planning_llm is not None:
        crew.planning_llm = crew_data.planning_llm

    if crew_data.knowledge_source_ids is not None:
        crew.knowledge_source_ids = crew_data.knowledge_source_ids

    return CrewResponse(**crew.to_dict())


@router.delete("/{crew_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crew(crew_id: str):
    """Delete a crew"""
    if crew_id not in storage.crews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crew with id '{crew_id}' not found"
        )

    del storage.crews[crew_id]
    return None


@router.post("/{crew_id}/validate", response_model=CrewValidationResponse)
async def validate_crew(crew_id: str):
    """Validate a crew configuration"""
    crew = storage.crews.get(crew_id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crew with id '{crew_id}' not found"
        )

    validation = crew.validate()
    return CrewValidationResponse(
        is_valid=validation['is_valid'],
        errors=validation['errors'],
        warnings=validation['warnings']
    )
