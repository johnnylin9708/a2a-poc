"""
Group Pydantic schemas for request/response validation
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class GroupCreateRequest(BaseModel):
    """Request body for creating a group"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    admin_address: str = Field(..., description="Ethereum address of admin")
    initial_agents: List[int] = Field(default=[], description="Initial agent token IDs")
    collaboration_rules: Optional[Dict] = Field(default=None)


class GroupAddAgentRequest(BaseModel):
    """Request body for adding agent to group"""
    agent_id: int = Field(..., gt=0)


class GroupTaskRequest(BaseModel):
    """Request body for delegating task to group"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=1000)
    required_capability: str
    priority: int = Field(default=1, ge=1, le=5)
    deadline: Optional[datetime] = None
    budget: Optional[float] = None
    metadata: Optional[Dict] = None


class GroupResponse(BaseModel):
    """Group response"""
    group_id: str
    name: str
    description: str
    admin_address: str
    member_agents: List[int]
    collaboration_rules: Dict
    created_at: datetime
    updated_at: datetime


class GroupTaskResponse(BaseModel):
    """Response for task delegation"""
    task_id: str
    group_id: str
    assigned_agent_id: int
    agent_name: str
    status: str
    created_at: datetime

