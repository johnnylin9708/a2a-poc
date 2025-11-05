"""
Agent Management Service for registration, discovery, and matching
"""

from typing import List, Dict, Optional
import logging
from datetime import datetime
import uuid

from app.database import get_agents_collection, get_tasks_collection
from app.services.blockchain import blockchain_service
from app.services.ipfs_service import ipfs_service
from app.services.a2a_handler import a2a_handler

logger = logging.getLogger(__name__)


class AgentManagementService:
    """Service for managing agents"""
    
    def __init__(self):
        self._agents_collection = None
        self._tasks_collection = None
        logger.info("✅ Agent Management Service initialized")
    
    @property
    def agents_collection(self):
        """Lazy loading of agents collection"""
        if self._agents_collection is None:
            self._agents_collection = get_agents_collection()
        return self._agents_collection
    
    @property
    def tasks_collection(self):
        """Lazy loading of tasks collection"""
        if self._tasks_collection is None:
            self._tasks_collection = get_tasks_collection()
        return self._tasks_collection
    
    async def register_agent(
        self,
        name: str,
        description: str,
        capabilities: List[str],
        endpoint: str,
        metadata: Optional[Dict],
        owner_address: str,
        private_key: str
    ) -> Dict:
        """
        Register a new agent
        
        1. Upload metadata to IPFS
        2. Register on blockchain (mint NFT)
        3. Store in MongoDB for fast queries
        
        Returns:
            Agent information including token_id
        """
        try:
            # Prepare metadata for IPFS
            full_metadata = {
                "name": name,
                "description": description,
                "capabilities": capabilities,
                "endpoint": endpoint,
                "version": "1.0",
                "created_at": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            
            # Upload to IPFS
            logger.info("📤 Uploading metadata to IPFS...")
            metadata_uri = await ipfs_service.upload_json(full_metadata)
            logger.info(f"✅ Metadata uploaded: {metadata_uri}")
            
            # Register on blockchain
            logger.info("📝 Registering on blockchain...")
            token_id = await blockchain_service.register_agent(
                name=name,
                description=description,
                capabilities=capabilities,
                endpoint=endpoint,
                metadata_uri=metadata_uri,
                owner_address=owner_address,
                private_key=private_key
            )
            logger.info(f"✅ Agent registered with Token ID: {token_id}")
            
            # Store in MongoDB for fast queries
            agent_doc = {
                "token_id": token_id,
                "name": name,
                "description": description,
                "capabilities": capabilities,
                "endpoint": endpoint,
                "metadata_uri": metadata_uri,
                "owner_address": owner_address,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True,
                "reputation_score": 0.0,
                "feedback_count": 0,
                "total_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0
            }
            
            await self.agents_collection.insert_one(agent_doc)
            logger.info(f"✅ Agent stored in database")
            
            return {
                "token_id": token_id,
                "name": name,
                "endpoint": endpoint,
                "metadata_uri": metadata_uri,
                "tx_hash": "0x..."  # Would come from blockchain
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to register agent: {e}")
            raise
    
    async def discover_agents(
        self,
        capability: Optional[str] = None,
        min_reputation: float = 0.0,
        is_active: bool = True,
        limit: int = 20,
        offset: int = 0
    ) -> Dict:
        """
        Discover agents based on criteria
        
        Returns:
            Dictionary with agents array and metadata
        """
        try:
            # Build query
            query = {"is_active": is_active}
            
            if capability:
                query["capabilities"] = capability
            
            if min_reputation > 0:
                query["reputation_score"] = {"$gte": min_reputation}
            
            # Get total count
            total = await self.agents_collection.count_documents(query)
            
            # Get agents with pagination
            cursor = self.agents_collection.find(query).skip(offset).limit(limit)
            agents = await cursor.to_list(length=limit)
            
            # Convert MongoDB docs to response format
            agent_list = []
            for agent in agents:
                agent_list.append({
                    "token_id": agent["token_id"],
                    "name": agent["name"],
                    "description": agent["description"],
                    "capabilities": agent["capabilities"],
                    "endpoint": agent["endpoint"],
                    "metadata_uri": agent["metadata_uri"],
                    "owner_address": agent["owner_address"],
                    "created_at": agent["created_at"],
                    "is_active": agent["is_active"],
                    "reputation_score": agent.get("reputation_score", 0.0),
                    "feedback_count": agent.get("feedback_count", 0)
                })
            
            logger.info(f"✅ Found {len(agent_list)} agents (total: {total})")
            
            return {
                "agents": agent_list,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to discover agents: {e}")
            raise
    
    async def get_agent(self, token_id: int) -> Optional[Dict]:
        """Get agent by token ID"""
        try:
            agent = await self.agents_collection.find_one({"token_id": token_id})
            
            if not agent:
                return None
            
            # Get fresh reputation from blockchain
            rep_score, feedback_count = await blockchain_service.get_reputation_score(token_id)
            
            # Update cache
            await self.agents_collection.update_one(
                {"token_id": token_id},
                {
                    "$set": {
                        "reputation_score": rep_score,
                        "feedback_count": feedback_count,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            agent["reputation_score"] = rep_score
            agent["feedback_count"] = feedback_count
            
            return agent
            
        except Exception as e:
            logger.error(f"❌ Failed to get agent: {e}")
            return None
    
    async def match_agent_for_task(
        self,
        required_capability: str,
        min_reputation: float = 3.0,
        exclude_agents: Optional[List[int]] = None
    ) -> Optional[Dict]:
        """
        Find best matching agent for a task
        
        Returns:
            Best matching agent or None
        """
        try:
            query = {
                "capabilities": required_capability,
                "is_active": True,
                "reputation_score": {"$gte": min_reputation}
            }
            
            if exclude_agents:
                query["token_id"] = {"$nin": exclude_agents}
            
            # Sort by reputation descending
            cursor = self.agents_collection.find(query).sort("reputation_score", -1).limit(1)
            agents = await cursor.to_list(length=1)
            
            if agents:
                logger.info(f"✅ Matched agent {agents[0]['token_id']} for capability {required_capability}")
                return agents[0]
            
            logger.warning(f"⚠️ No agent found for capability {required_capability}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to match agent: {e}")
            return None
    
    async def delegate_task(
        self,
        agent_id: int,
        task: Dict
    ) -> Dict:
        """
        Delegate a task to an agent via A2A protocol
        
        Returns:
            Task execution result
        """
        try:
            # Get agent details
            agent = await self.get_agent(agent_id)
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            
            # Create task record
            task_id = str(uuid.uuid4())
            task_doc = {
                "task_id": task_id,
                "agent_id": agent_id,
                "agent_name": agent["name"],
                "task_data": task,
                "status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await self.tasks_collection.insert_one(task_doc)
            
            # Send task via A2A protocol
            logger.info(f"📤 Delegating task to agent {agent_id} at {agent['endpoint']}")
            result = await a2a_handler.send_task(agent["endpoint"], task)
            
            # Update task status
            await self.tasks_collection.update_one(
                {"task_id": task_id},
                {
                    "$set": {
                        "status": "in_progress",
                        "started_at": datetime.utcnow(),
                        "result": result
                    }
                }
            )
            
            # Update agent stats
            await self.agents_collection.update_one(
                {"token_id": agent_id},
                {"$inc": {"total_tasks": 1}}
            )
            
            logger.info(f"✅ Task {task_id} delegated successfully")
            
            return {
                "task_id": task_id,
                "agent_id": agent_id,
                "agent_name": agent["name"],
                "status": "in_progress",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to delegate task: {e}")
            raise
    
    async def update_agent_stats(
        self,
        agent_id: int,
        task_status: str
    ):
        """Update agent task statistics"""
        try:
            update = {}
            if task_status == "completed":
                update["$inc"] = {"completed_tasks": 1}
            elif task_status == "failed":
                update["$inc"] = {"failed_tasks": 1}
            
            if update:
                await self.agents_collection.update_one(
                    {"token_id": agent_id},
                    update
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to update agent stats: {e}")


# Create singleton instance
agent_manager = AgentManagementService()

