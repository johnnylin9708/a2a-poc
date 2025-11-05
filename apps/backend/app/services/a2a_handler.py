"""
A2A Protocol Handler for Agent-to-Agent communication
"""

from typing import Dict, Any, Optional
import httpx
import logging
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class A2AProtocolHandler:
    """Handler for A2A Protocol operations"""
    
    def __init__(self):
        self.protocol_version = settings.A2A_PROTOCOL_VERSION
        self.default_timeout = settings.A2A_DEFAULT_TIMEOUT
        logger.info(f"✅ A2A Protocol Handler initialized (v{self.protocol_version})")
    
    async def send_task(
        self,
        endpoint: str,
        task: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send task to an agent via A2A protocol
        
        Args:
            endpoint: Agent's A2A endpoint
            task: Task details
            timeout: Request timeout in seconds
            
        Returns:
            Response from agent
        """
        if timeout is None:
            timeout = self.default_timeout
        
        try:
            headers = {
                "Content-Type": "application/json",
                "A2A-Protocol-Version": self.protocol_version,
                "User-Agent": f"A2A-Ecosystem/{self.protocol_version}"
            }
            
            payload = {
                "protocol_version": self.protocol_version,
                "task": task,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{endpoint}/tasks",
                    json=payload,
                    headers=headers,
                    timeout=float(timeout)
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"✅ Task sent to {endpoint}")
                return result
                
        except httpx.TimeoutException:
            logger.error(f"⏱️ Timeout sending task to {endpoint}")
            raise Exception(f"Agent at {endpoint} timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error from {endpoint}: {e.response.status_code}")
            raise Exception(f"Agent returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"❌ Failed to send task to {endpoint}: {e}")
            raise
    
    async def get_agent_status(self, endpoint: str) -> Dict[str, Any]:
        """
        Get agent status via A2A protocol
        
        Args:
            endpoint: Agent's A2A endpoint
            
        Returns:
            Agent status information
        """
        try:
            headers = {
                "A2A-Protocol-Version": self.protocol_version,
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{endpoint}/status",
                    headers=headers,
                    timeout=float(self.default_timeout)
                )
                
                response.raise_for_status()
                status = response.json()
                
                logger.info(f"✅ Got status from {endpoint}")
                return status
                
        except Exception as e:
            logger.error(f"❌ Failed to get status from {endpoint}: {e}")
            raise
    
    async def discover_capabilities(self, endpoint: str) -> Dict[str, Any]:
        """
        Discover agent capabilities via A2A protocol
        
        Args:
            endpoint: Agent's A2A endpoint
            
        Returns:
            Agent capability information
        """
        try:
            headers = {
                "A2A-Protocol-Version": self.protocol_version,
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{endpoint}/capabilities",
                    headers=headers,
                    timeout=float(self.default_timeout)
                )
                
                response.raise_for_status()
                capabilities = response.json()
                
                logger.info(f"✅ Discovered capabilities from {endpoint}")
                return capabilities
                
        except Exception as e:
            logger.error(f"❌ Failed to discover capabilities from {endpoint}: {e}")
            raise
    
    async def send_message(
        self,
        endpoint: str,
        message: Dict[str, Any],
        message_type: str = "notification"
    ) -> Dict[str, Any]:
        """
        Send message to an agent
        
        Args:
            endpoint: Agent's A2A endpoint
            message: Message content
            message_type: Type of message (notification, query, command)
            
        Returns:
            Response from agent
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "A2A-Protocol-Version": self.protocol_version,
                "A2A-Message-Type": message_type
            }
            
            payload = {
                "protocol_version": self.protocol_version,
                "message_type": message_type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{endpoint}/messages",
                    json=payload,
                    headers=headers,
                    timeout=float(self.default_timeout)
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"✅ Message sent to {endpoint}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Failed to send message to {endpoint}: {e}")
            raise
    
    async def check_endpoint_availability(self, endpoint: str) -> bool:
        """
        Check if an agent endpoint is available
        
        Args:
            endpoint: Agent's A2A endpoint
            
        Returns:
            True if available, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{endpoint}/health",
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception:
            return False


# Create singleton instance
a2a_handler = A2AProtocolHandler()

