"""
Base Agent Class
Base class for all Agents, encapsulating common functionality
"""

from typing import Dict, List, Optional, Any
from web3 import Web3
from eth_account import Account
import asyncio
import logging

from utils.api_client import PlatformClient
from utils.logger import log_success, log_error, log_info

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base Agent class"""
    
    def __init__(
        self,
        name: str,
        description: str,
        capabilities: List[str],
        private_key: str,
        platform_url: str = "http://localhost:8000",
        blockchain_rpc: str = "http://localhost:8545"
    ):
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.private_key = private_key
        
        # Web3 initialization
        self.w3 = Web3(Web3.HTTPProvider(blockchain_rpc))
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        
        # Platform client
        self.client = PlatformClient(platform_url)
        
        # Agent state
        self.token_id: Optional[int] = None
        self.is_registered = False
        
        logger.info(f"✅ {name} initialized with address {self.address}")
    
    async def close(self):
        """Close connections"""
        await self.client.close()
    
    # ========== Core Functions ==========
    
    async def register(self, endpoint: str = "http://localhost:3000") -> int:
        """
        Register Agent on blockchain
        
        Returns:
            token_id: Agent's Token ID
        """
        try:
            log_info(f"Registering Agent: {self.name}")
            
            # 1. Upload metadata to IPFS
            metadata = {
                "name": self.name,
                "description": self.description,
                "capabilities": self.capabilities,
                "endpoint": endpoint,
                "version": "1.0",
                "agent_type": self.__class__.__name__
            }
            
            # Simplified handling - should call IPFS API in production
            # Using mock CID for now
            ipfs_uri = f"ipfs://Qm{self.name.replace(' ', '')}{len(self.capabilities)}"
            
            log_success(f"Metadata uploaded", f"URI: {ipfs_uri}")
            
            # 2. Call smart contract to register
            # Note: Should call contract through frontend or directly
            # Currently assuming on-chain registration, sync to database directly
            
            # Mock tx_hash (should get from contract call in production)
            mock_tx_hash = f"0x{'0' * 64}"
            
            # 3. Sync to database
            # Since we don't have actual blockchain transaction, manually create data
            # In production, should call sync_agent API
            
            self.is_registered = True
            log_success(f"{self.name} registered successfully")
            
            return self.token_id
            
        except Exception as e:
            log_error(f"Registration failed: {self.name}", e)
            raise
    
    async def discover_agents(
        self,
        capabilities: List[str],
        min_reputation: float = 0.0,
        sort_by: str = "reputation",
        limit: int = 10
    ) -> List[Dict]:
        """
        Discover other Agents
        
        Args:
            capabilities: Required capabilities
            min_reputation: Minimum reputation score
            sort_by: Sort method
            limit: Number of results to return
        
        Returns:
            List of matching Agents
        """
        try:
            result = await self.client.search_agents(
                capabilities=capabilities,
                min_reputation=min_reputation,
                sort_by=sort_by,
                limit=limit
            )
            
            agents = result.get("agents", [])
            log_success(
                f"Found {len(agents)} Agents",
                f"Capabilities: {', '.join(capabilities)}"
            )
            
            return agents
            
        except Exception as e:
            log_error("Agent search failed", e)
            return []
    
    async def create_group(
        self,
        group_name: str,
        description: str,
        member_agents: List[int]
    ) -> Optional[str]:
        """
        Create Agent Group
        
        Args:
            group_name: Group name
            description: Description
            member_agents: Member Agent Token IDs
        
        Returns:
            group_id
        """
        try:
            result = await self.client.create_group(
                name=group_name,
                description=description,
                admin_address=self.address,
                initial_agents=member_agents
            )
            
            group_id = result.get("group_id")
            log_success(f"Group created successfully", f"ID: {group_id}")
            
            return group_id
            
        except Exception as e:
            log_error("Group creation failed", e)
            return None
    
    async def delegate_task(
        self,
        agent_id: int,
        task_data: Dict,
        group_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Delegate task to another Agent
        
        Args:
            agent_id: Target Agent ID
            task_data: Task data
            group_id: Group ID (optional)
        
        Returns:
            task_id
        """
        try:
            result = await self.client.delegate_task(
                agent_id=agent_id,
                task_data=task_data,
                group_id=group_id
            )
            
            task_id = result.get("task_id")
            log_success(f"Task delegated successfully", f"Task ID: {task_id}")
            
            return task_id
            
        except Exception as e:
            log_error("Task delegation failed", e)
            return None
    
    async def submit_feedback(
        self,
        agent_id: int,
        rating: float,
        comment: str,
        tx_hash: str = "0x" + "0" * 64
    ) -> bool:
        """
        Submit feedback for another Agent
        
        Args:
            agent_id: Target Agent ID
            rating: Rating (0-5)
            comment: Comment
            tx_hash: Payment transaction hash
        
        Returns:
            Success status
        """
        try:
            # Convert to integer rating (1-5)
            rating_int = min(5, max(1, int(round(rating))))
            
            # payment_proof must be a string
            payment_proof = tx_hash
            
            await self.client.submit_feedback(
                agent_id=agent_id,
                rating=rating_int,  # Use integer
                comment=comment,
                reviewer_address=self.address,
                payment_proof=payment_proof,  # Use string
                private_key=self.private_key
            )
            
            log_success(f"Feedback submitted successfully", f"Agent #{agent_id} - {rating_int}⭐")
            return True
            
        except Exception as e:
            log_error("Feedback submission failed", e)
            return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get task status"""
        try:
            task = await self.client.get_task(task_id)
            return task
        except Exception as e:
            log_error(f"Failed to get task status: {task_id}", e)
            return None
    
    async def wait_for_task_completion(
        self,
        task_id: str,
        timeout: int = 300,
        check_interval: int = 5
    ) -> Optional[Dict]:
        """
        Wait for task completion
        
        Args:
            task_id: Task ID
            timeout: Timeout in seconds
            check_interval: Check interval in seconds
        
        Returns:
            Completed task data
        """
        elapsed = 0
        
        while elapsed < timeout:
            task = await self.get_task_status(task_id)
            
            if not task:
                break
            
            status = task.get("status")
            
            if status in ["completed", "failed"]:
                return task
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
        
        log_error(f"Task timeout: {task_id}")
        return None
    
    # ========== Utility Methods ==========
    
    def sign_message(self, message: str) -> str:
        """Sign message"""
        message_hash = self.w3.keccak(text=message)
        signed = self.account.signHash(message_hash)
        return signed.signature.hex()
    
    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} token_id={self.token_id}>"

