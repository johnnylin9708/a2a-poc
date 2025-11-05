"""Group models"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime


class GroupCreate(BaseModel):
    """Group creation request"""
    name: str
    description: str
    initial_agents: List[int] = []


class Group(BaseModel):
    """Group model"""
    group_id: str
    name: str
    description: str
    admin_address: str
    member_agents: List[int]
    collaboration_rules: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "group_id": "grp_123456",
                "name": "Development Team",
                "description": "Full-stack development team",
                "admin_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "member_agents": [123, 456, 789],
                "collaboration_rules": {
                    "task_timeout": 3600,
                    "max_retries": 3,
                    "require_validation": False
                }
            }
        }


class GroupResponse(BaseModel):
    """Group API response"""
    group_id: str
    name: str
    description: str
    admin_address: str
    member_count: int
    created_at: datetime

