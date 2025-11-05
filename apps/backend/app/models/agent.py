"""Agent models"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AgentCard(BaseModel):
    """Agent Card - describes agent capabilities and metadata"""
    name: str
    description: str
    capabilities: List[str]
    endpoint: str
    version: str = "1.0.0"
    image_url: Optional[str] = None
    metadata_uri: Optional[str] = None


class Agent(BaseModel):
    """Agent model"""
    token_id: int
    owner_address: str
    agent_card: AgentCard
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "token_id": 123,
                "owner_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "agent_card": {
                    "name": "PM Agent",
                    "description": "Project management agent specialized in Agile methodology",
                    "capabilities": ["project-management", "task-planning", "team-coordination"],
                    "endpoint": "https://api.example.com/agents/pm",
                    "version": "1.0.0"
                },
                "is_active": True
            }
        }


class AgentCreate(BaseModel):
    """Agent creation request"""
    name: str
    description: str
    capabilities: List[str]
    endpoint: str
    version: str = "1.0.0"
    image_url: Optional[str] = None


class AgentUpdate(BaseModel):
    """Agent update request"""
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class AgentResponse(BaseModel):
    """Agent API response"""
    token_id: int
    owner_address: str
    name: str
    description: str
    capabilities: List[str]
    endpoint: str
    reputation_score: float = 0.0
    feedback_count: int = 0
    is_active: bool
    created_at: datetime

