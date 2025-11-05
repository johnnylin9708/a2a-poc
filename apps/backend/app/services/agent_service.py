"""Agent service - business logic for agent management"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime
from app.models import Agent, AgentCreate, AgentResponse


class AgentService:
    """Agent management service"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.agents
    
    async def list_agents(self, skip: int = 0, limit: int = 100) -> List[AgentResponse]:
        """List all agents"""
        cursor = self.collection.find().skip(skip).limit(limit)
        agents = await cursor.to_list(length=limit)
        return [self._to_response(agent) for agent in agents]
    
    async def get_agent(self, token_id: int) -> Optional[AgentResponse]:
        """Get agent by token ID"""
        agent = await self.collection.find_one({"token_id": token_id})
        if not agent:
            return None
        return self._to_response(agent)
    
    async def discover_agents(
        self,
        capability: str,
        min_reputation: float = 0.0
    ) -> List[AgentResponse]:
        """Discover agents by capability"""
        query = {
            "agent_card.capabilities": capability,
            "is_active": True
        }
        
        cursor = self.collection.find(query)
        agents = await cursor.to_list(length=None)
        
        # Filter by reputation (would fetch from blockchain in production)
        # For now, return all matching agents
        return [self._to_response(agent) for agent in agents]
    
    async def register_agent(
        self,
        agent_data: AgentCreate,
        owner_address: str
    ) -> AgentResponse:
        """Register a new agent"""
        # In production, this would:
        # 1. Register on blockchain and get token_id
        # 2. Upload metadata to IPFS
        # 3. Store in database
        
        # For MVP, we'll generate a mock token_id
        existing_count = await self.collection.count_documents({})
        token_id = existing_count + 1000
        
        agent_dict = {
            "token_id": token_id,
            "owner_address": owner_address,
            "agent_card": {
                "name": agent_data.name,
                "description": agent_data.description,
                "capabilities": agent_data.capabilities,
                "endpoint": agent_data.endpoint,
                "version": agent_data.version,
                "image_url": agent_data.image_url,
            },
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        await self.collection.insert_one(agent_dict)
        return self._to_response(agent_dict)
    
    def _to_response(self, agent_dict: dict) -> AgentResponse:
        """Convert database document to API response"""
        return AgentResponse(
            token_id=agent_dict["token_id"],
            owner_address=agent_dict["owner_address"],
            name=agent_dict["agent_card"]["name"],
            description=agent_dict["agent_card"]["description"],
            capabilities=agent_dict["agent_card"]["capabilities"],
            endpoint=agent_dict["agent_card"]["endpoint"],
            reputation_score=0.0,  # Would fetch from blockchain
            feedback_count=0,  # Would fetch from blockchain
            is_active=agent_dict["is_active"],
            created_at=agent_dict["created_at"],
        )

