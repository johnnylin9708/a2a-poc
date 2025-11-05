"""
Agent API endpoints
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional
import logging

from app.schemas.agent import (
    AgentRegisterRequest,
    AgentUpdateRequest,
    AgentCardResponse,
    AgentDiscoveryRequest,
    AgentDiscoveryResponse,
    AgentStatusResponse
)
from app.services.agent_manager import agent_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_agent(request: AgentRegisterRequest):
    """
    Register a new agent
    
    - Uploads metadata to IPFS
    - Mints ERC-721 NFT on blockchain
    - Stores agent info in database
    """
    try:
        result = await agent_manager.register_agent(
            name=request.name,
            description=request.description,
            capabilities=request.capabilities,
            endpoint=str(request.endpoint),
            metadata=request.metadata,
            owner_address=request.owner_address,
            private_key=request.private_key
        )
        return result
    except Exception as e:
        logger.error(f"Failed to register agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register agent: {str(e)}"
        )


@router.post("/discover", response_model=AgentDiscoveryResponse)
async def discover_agents(request: AgentDiscoveryRequest):
    """
    Discover agents based on criteria
    
    - Search by capability
    - Filter by reputation
    - Filter by active status
    """
    try:
        result = await agent_manager.discover_agents(
            capability=request.capability,
            min_reputation=request.min_reputation,
            is_active=request.is_active,
            limit=request.limit,
            offset=request.offset
        )
        return result
    except Exception as e:
        logger.error(f"Failed to discover agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to discover agents: {str(e)}"
        )


@router.get("/{agent_id}", response_model=dict)
async def get_agent(agent_id: int):
    """
    Get agent details by token ID
    
    Returns agent card with current reputation and stats
    """
    try:
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        # Remove MongoDB _id field
        agent.pop("_id", None)
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}"
        )


@router.get("/{agent_id}/status", response_model=dict)
async def get_agent_status(agent_id: int):
    """
    Get agent status information
    
    Returns task statistics and current status
    """
    try:
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        return {
            "token_id": agent["token_id"],
            "is_active": agent["is_active"],
            "last_seen": agent.get("updated_at"),
            "total_tasks": agent.get("total_tasks", 0),
            "completed_tasks": agent.get("completed_tasks", 0),
            "failed_tasks": agent.get("failed_tasks", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.post("/{agent_id}/delegate-task", response_model=dict)
async def delegate_task_to_agent(agent_id: int, task: dict):
    """
    Delegate a task to a specific agent
    
    Sends task via A2A protocol
    """
    try:
        result = await agent_manager.delegate_task(agent_id, task)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to delegate task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delegate task: {str(e)}"
        )


@router.get("/", response_model=dict)
async def list_agents(
    limit: int = 20,
    offset: int = 0,
    is_active: Optional[bool] = None
):
    """
    List all agents with pagination
    """
    try:
        query_params = {
            "limit": limit,
            "offset": offset
        }
        
        if is_active is not None:
            query_params["is_active"] = is_active
        
        result = await agent_manager.discover_agents(**query_params)
        return result
        
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.post("/sync", response_model=dict)
async def sync_agent_from_blockchain(request: dict):
    """
    Sync agent from blockchain to database
    
    Called after agent registration transaction is confirmed
    """
    try:
        from app.services.blockchain import blockchain_service
        from app.database import get_agents_collection
        from datetime import datetime
        
        tx_hash = request.get("tx_hash")
        if not tx_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tx_hash is required"
            )
        
        # Get transaction receipt
        tx_receipt = blockchain_service.w3.eth.get_transaction_receipt(tx_hash)
        
        # Extract token ID from logs
        event_signature_hash = blockchain_service.w3.keccak(text="AgentRegistered(uint256,string,address,string)")
        token_id = None
        
        for log in tx_receipt['logs']:
            if log['topics'][0] == event_signature_hash:
                token_id = int(log['topics'][1].hex(), 16)
                break
        
        if not token_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AgentRegistered event not found in transaction"
            )
        
        # Get agent card from blockchain
        agent_card = await blockchain_service.get_agent_card(token_id)
        
        # Get reputation
        rep_score, feedback_count = await blockchain_service.get_reputation_score(token_id)
        
        # Save to database
        agents_collection = get_agents_collection()
        agent_doc = {
            "token_id": token_id,
            "name": agent_card["name"],
            "description": agent_card["description"],
            "capabilities": agent_card["capabilities"],
            "endpoint": agent_card["endpoint"],
            "metadata_uri": agent_card["metadata_uri"],
            "owner_address": agent_card["owner_address"],
            "created_at": datetime.fromtimestamp(int(agent_card["created_at"])),
            "updated_at": datetime.utcnow(),
            "is_active": agent_card["is_active"],
            "reputation_score": rep_score,
            "feedback_count": feedback_count,
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0
        }
        
        # Upsert (update if exists, insert if not)
        await agents_collection.update_one(
            {"token_id": token_id},
            {"$set": agent_doc},
            upsert=True
        )
        
        logger.info(f"✅ Agent {token_id} synced to database")
        
        return {
            "message": "Agent synced successfully",
            "token_id": token_id,
            "agent": agent_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync agent: {str(e)}"
        )

