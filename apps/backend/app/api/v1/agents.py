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


@router.get("/search/advanced", response_model=dict)
async def advanced_search_agents(
    query: Optional[str] = None,
    capabilities: Optional[str] = None,  # comma-separated
    tags: Optional[str] = None,  # comma-separated
    min_reputation: float = 0.0,
    max_reputation: float = 5.0,
    min_tasks: int = 0,
    is_active: bool = True,
    sort_by: str = "reputation",  # reputation, tasks, recent
    limit: int = 20,
    offset: int = 0
):
    """
    Advanced agent search with multiple filters (Phase 3)
    
    - Full-text search on name and description
    - Multiple capabilities filtering
    - Tags filtering
    - Reputation range
    - Task count filtering
    - Multiple sort options
    """
    try:
        from app.database import get_agents_collection
        
        agents_collection = get_agents_collection()
        
        # Build MongoDB query
        mongo_query = {"is_active": is_active}
        
        # Full-text search
        if query:
            mongo_query["$or"] = [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        
        # Capabilities filter
        if capabilities:
            caps_list = [c.strip() for c in capabilities.split(",")]
            mongo_query["capabilities"] = {"$in": caps_list}
        
        # Tags filter
        if tags:
            tags_list = [t.strip() for t in tags.split(",")]
            mongo_query["tags"] = {"$in": tags_list}
        
        # Reputation range
        mongo_query["reputation_score"] = {
            "$gte": min_reputation * 100,  # Scaled by 100
            "$lte": max_reputation * 100
        }
        
        # Task count filter
        if min_tasks > 0:
            mongo_query["total_tasks"] = {"$gte": min_tasks}
        
        # Sort options
        sort_field = {
            "reputation": ("reputation_score", -1),
            "tasks": ("total_tasks", -1),
            "recent": ("created_at", -1)
        }.get(sort_by, ("reputation_score", -1))
        
        # Execute query
        total = await agents_collection.count_documents(mongo_query)
        cursor = agents_collection.find(mongo_query).sort(*sort_field).skip(offset).limit(limit)
        agents = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id
        for agent in agents:
            agent.pop("_id", None)
        
        return {
            "agents": agents,
            "total": total,
            "limit": limit,
            "offset": offset,
            "query": query,
            "filters": {
                "capabilities": capabilities,
                "tags": tags,
                "reputation_range": [min_reputation, max_reputation],
                "min_tasks": min_tasks
            }
        }
        
    except Exception as e:
        logger.error(f"Failed advanced search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed advanced search: {str(e)}"
        )


@router.get("/recommendations/{agent_id}", response_model=dict)
async def get_agent_recommendations(
    agent_id: int,
    limit: int = 10
):
    """
    Get recommended agents based on similarity (Phase 3)
    
    Uses collaborative filtering based on:
    - Similar capabilities
    - Similar reputation tier
    - Task completion patterns
    """
    try:
        from app.database import get_agents_collection
        
        agents_collection = get_agents_collection()
        
        # Get source agent
        source_agent = await agents_collection.find_one({"token_id": agent_id})
        if not source_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        # Find similar agents
        similar_query = {
            "token_id": {"$ne": agent_id},
            "is_active": True,
            "capabilities": {"$in": source_agent["capabilities"]}
        }
        
        # Get agents with similar reputation tier
        rep_score = source_agent.get("reputation_score", 0)
        rep_range = 50  # ±0.5 stars
        similar_query["reputation_score"] = {
            "$gte": max(0, rep_score - rep_range),
            "$lte": min(500, rep_score + rep_range)
        }
        
        cursor = agents_collection.find(similar_query).sort("reputation_score", -1).limit(limit)
        recommendations = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id
        for agent in recommendations:
            agent.pop("_id", None)
        
        return {
            "source_agent_id": agent_id,
            "recommendations": recommendations,
            "total": len(recommendations),
            "based_on": {
                "capabilities": source_agent["capabilities"],
                "reputation_tier": rep_score / 100
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/leaderboard/top", response_model=dict)
async def get_top_agents(
    category: Optional[str] = None,
    min_feedback: int = 5,
    limit: int = 20
):
    """
    Get top-rated agents leaderboard (Phase 3)
    
    - Overall top agents or by category
    - Minimum feedback threshold for credibility
    """
    try:
        from app.database import get_agents_collection
        
        agents_collection = get_agents_collection()
        
        query = {
            "is_active": True,
            "feedback_count": {"$gte": min_feedback}
        }
        
        if category:
            query["capabilities"] = category
        
        cursor = agents_collection.find(query).sort([
            ("reputation_score", -1),
            ("feedback_count", -1)
        ]).limit(limit)
        
        top_agents = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id and add rank
        for idx, agent in enumerate(top_agents, 1):
            agent.pop("_id", None)
            agent["rank"] = idx
        
        return {
            "leaderboard": top_agents,
            "total": len(top_agents),
            "category": category,
            "min_feedback_threshold": min_feedback
        }
        
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get leaderboard: {str(e)}"
        )


@router.get("/stats/global", response_model=dict)
async def get_global_stats():
    """
    Get global ecosystem statistics (Phase 3)
    
    - Total agents
    - Active agents  
    - Total tasks
    - Average reputation
    """
    try:
        from app.database import get_agents_collection, get_tasks_collection
        
        agents_collection = get_agents_collection()
        tasks_collection = get_tasks_collection()
        
        # Agent stats
        total_agents = await agents_collection.count_documents({})
        active_agents = await agents_collection.count_documents({"is_active": True})
        
        # Task stats
        total_tasks = await tasks_collection.count_documents({})
        completed_tasks = await tasks_collection.count_documents({"status": "completed"})
        
        # Average reputation
        pipeline = [
            {"$match": {"feedback_count": {"$gt": 0}}},
            {"$group": {
                "_id": None,
                "avg_reputation": {"$avg": "$reputation_score"},
                "total_feedback": {"$sum": "$feedback_count"}
            }}
        ]
        cursor = agents_collection.aggregate(pipeline)
        results = await cursor.to_list(length=1)
        
        avg_rep = 0
        total_feedback = 0
        if results:
            avg_rep = results[0].get("avg_reputation", 0) / 100  # Scale back to 0-5
            total_feedback = results[0].get("total_feedback", 0)
        
        return {
            "agents": {
                "total": total_agents,
                "active": active_agents,
                "inactive": total_agents - active_agents
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            "reputation": {
                "average": round(avg_rep, 2),
                "total_feedback": total_feedback
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get global stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get global stats: {str(e)}"
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

