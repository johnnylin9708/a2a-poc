"""Agent endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import AgentCreate, AgentResponse
from app.services.agent_service import AgentService
from app.core.database import get_database

router = APIRouter()


def get_agent_service(db=Depends(get_database)) -> AgentService:
    """Dependency injection for AgentService"""
    return AgentService(db)


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    service: AgentService = Depends(get_agent_service)
):
    """List all agents"""
    agents = await service.list_agents(skip=skip, limit=limit)
    return agents


@router.get("/{token_id}", response_model=AgentResponse)
async def get_agent(
    token_id: int,
    service: AgentService = Depends(get_agent_service)
):
    """Get agent by token ID"""
    agent = await service.get_agent(token_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/discover", response_model=List[AgentResponse])
async def discover_agents(
    capability: str,
    min_reputation: float = 0.0,
    service: AgentService = Depends(get_agent_service)
):
    """Discover agents by capability"""
    agents = await service.discover_agents(
        capability=capability,
        min_reputation=min_reputation
    )
    return agents


@router.post("/", response_model=AgentResponse, status_code=201)
async def register_agent(
    agent_data: AgentCreate,
    owner_address: str,
    service: AgentService = Depends(get_agent_service)
):
    """Register a new agent (will also register on blockchain)"""
    agent = await service.register_agent(agent_data, owner_address)
    return agent

