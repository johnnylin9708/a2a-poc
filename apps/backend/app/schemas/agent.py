"""
Agent Pydantic schemas for request/response validation
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class AgentCapability(BaseModel):
    """Agent capability"""
    name: str
    description: Optional[str] = None
    version: Optional[str] = None


class AgentRegisterRequest(BaseModel):
    """Request body for agent registration"""
    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    description: str = Field(..., max_length=500, description="Agent description")
    capabilities: List[str] = Field(..., min_items=1, description="List of capabilities")
    endpoint: HttpUrl = Field(..., description="A2A protocol endpoint")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")
    owner_address: str = Field(..., description="Ethereum address of owner")
    private_key: str = Field(..., description="Private key for signing (stored securely)")


class AgentUpdateRequest(BaseModel):
    """Request body for agent update"""
    description: Optional[str] = Field(None, max_length=500)
    capabilities: Optional[List[str]] = Field(None, min_items=1)
    metadata: Optional[dict] = None


class AgentCardResponse(BaseModel):
    """Agent card response"""
    token_id: int
    name: str
    description: str
    capabilities: List[str]
    endpoint: str
    metadata_uri: str
    owner_address: str
    created_at: datetime
    is_active: bool
    reputation_score: Optional[float] = None
    feedback_count: Optional[int] = None


class AgentDiscoveryRequest(BaseModel):
    """Request body for agent discovery"""
    capability: Optional[str] = None
    min_reputation: float = Field(default=0.0, ge=0.0, le=5.0)
    is_active: bool = True
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class AgentDiscoveryResponse(BaseModel):
    """Response for agent discovery"""
    agents: List[AgentCardResponse]
    total: int
    limit: int
    offset: int


class AgentStatusResponse(BaseModel):
    """Agent status response"""
    token_id: int
    is_active: bool
    last_seen: Optional[datetime] = None
    total_tasks: int
    completed_tasks: int
    failed_tasks: int

