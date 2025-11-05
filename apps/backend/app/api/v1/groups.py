"""
Group Management API endpoints
"""

from fastapi import APIRouter, HTTPException, status
import logging
import uuid
from datetime import datetime

from app.schemas.group import (
    GroupCreateRequest,
    GroupAddAgentRequest,
    GroupTaskRequest,
    GroupResponse,
    GroupTaskResponse
)
from app.database import get_groups_collection
from app.services.agent_manager import agent_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(request: GroupCreateRequest):
    """
    Create a new agent group
    
    Groups allow multiple agents to collaborate on tasks
    """
    try:
        groups_collection = get_groups_collection()
        
        # Verify all initial agents exist
        for agent_id in request.initial_agents:
            agent = await agent_manager.get_agent(agent_id)
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent {agent_id} not found"
                )
        
        group_id = str(uuid.uuid4())
        
        # Default collaboration rules
        default_rules = {
            "task_timeout": 3600,
            "max_retries": 3,
            "require_validation": False,
            "auto_feedback": True
        }
        
        group_doc = {
            "group_id": group_id,
            "name": request.name,
            "description": request.description,
            "admin_address": request.admin_address,
            "member_agents": request.initial_agents,
            "collaboration_rules": request.collaboration_rules or default_rules,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await groups_collection.insert_one(group_doc)
        
        logger.info(f"✅ Group created: {group_id}")
        
        group_doc.pop("_id", None)
        return group_doc
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create group: {str(e)}"
        )


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(group_id: str):
    """Get group details"""
    try:
        groups_collection = get_groups_collection()
        group = await groups_collection.find_one({"group_id": group_id})
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found"
            )
        
        group.pop("_id", None)
        return group
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get group: {str(e)}"
        )


@router.post("/{group_id}/add-agent", response_model=dict)
async def add_agent_to_group(group_id: str, request: GroupAddAgentRequest):
    """Add an agent to a group"""
    try:
        groups_collection = get_groups_collection()
        
        # Verify agent exists
        agent = await agent_manager.get_agent(request.agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {request.agent_id} not found"
            )
        
        # Update group
        result = await groups_collection.update_one(
            {"group_id": group_id},
            {
                "$addToSet": {"member_agents": request.agent_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found"
            )
        
        logger.info(f"✅ Agent {request.agent_id} added to group {group_id}")
        
        return {"message": "Agent added to group successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add agent to group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add agent to group: {str(e)}"
        )


@router.post("/{group_id}/tasks", response_model=GroupTaskResponse)
async def delegate_task_to_group(group_id: str, request: GroupTaskRequest):
    """
    Delegate a task to a group
    
    The system will find the best matching agent in the group
    based on capability and reputation
    """
    try:
        groups_collection = get_groups_collection()
        
        # Get group
        group = await groups_collection.find_one({"group_id": group_id})
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found"
            )
        
        # Find best agent in group for this capability
        best_agent = None
        best_reputation = 0.0
        
        for agent_id in group["member_agents"]:
            agent = await agent_manager.get_agent(agent_id)
            
            if agent and request.required_capability in agent["capabilities"]:
                reputation = agent.get("reputation_score", 0.0)
                
                if reputation > best_reputation:
                    best_agent = agent
                    best_reputation = reputation
        
        if not best_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No agent in group has capability: {request.required_capability}"
            )
        
        # Delegate task to best agent
        task = {
            "title": request.title,
            "description": request.description,
            "priority": request.priority,
            "deadline": request.deadline.isoformat() if request.deadline else None,
            "budget": request.budget,
            "metadata": request.metadata
        }
        
        result = await agent_manager.delegate_task(best_agent["token_id"], task)
        
        return {
            "task_id": result["task_id"],
            "group_id": group_id,
            "assigned_agent_id": best_agent["token_id"],
            "agent_name": best_agent["name"],
            "status": result["status"],
            "created_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delegate task to group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delegate task to group: {str(e)}"
        )


@router.post("/{group_id}/remove-agent", response_model=dict)
async def remove_agent_from_group(group_id: str, request: GroupAddAgentRequest):
    """Remove an agent from a group"""
    try:
        groups_collection = get_groups_collection()
        
        # Update group
        result = await groups_collection.update_one(
            {"group_id": group_id},
            {
                "$pull": {"member_agents": request.agent_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found"
            )
        
        logger.info(f"✅ Agent {request.agent_id} removed from group {group_id}")
        
        return {"message": "Agent removed from group successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove agent from group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove agent from group: {str(e)}"
        )


@router.get("/", response_model=dict)
async def list_groups(limit: int = 20, offset: int = 0):
    """List all groups"""
    try:
        groups_collection = get_groups_collection()
        
        total = await groups_collection.count_documents({})
        
        cursor = groups_collection.find({}).skip(offset).limit(limit)
        groups = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id
        for group in groups:
            group.pop("_id", None)
        
        return {
            "groups": groups,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to list groups: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list groups: {str(e)}"
        )

