"""
Platform API Client
封装所有与 A2A 平台的 HTTP 交互
"""

import httpx
from typing import Dict, List, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


class PlatformClient:
    """A2A Platform API Client"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    # ========== Agent APIs ==========
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_agent(self, agent_id: int) -> Dict:
        """获取 Agent 详情"""
        response = await self.client.get(f"{self.base_url}/api/v1/agents/{agent_id}")
        response.raise_for_status()
        return response.json()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def list_agents(self, limit: int = 20, offset: int = 0, is_active: bool = True) -> Dict:
        """列出所有 Agents"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/agents/",  # 添加结尾斜杠
            params={"limit": limit, "offset": offset, "is_active": is_active}
        )
        response.raise_for_status()
        return response.json()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_agents(
        self,
        capabilities: Optional[List[str]] = None,
        min_reputation: float = 0.0,
        max_reputation: float = 5.0,
        min_tasks: int = 0,
        sort_by: str = "reputation",
        limit: int = 20
    ) -> Dict:
        """高级搜索 Agents"""
        params = {
            "min_reputation": min_reputation,
            "max_reputation": max_reputation,
            "min_tasks": min_tasks,
            "sort_by": sort_by,
            "limit": limit
        }
        
        if capabilities:
            params["capabilities"] = ",".join(capabilities)
        
        response = await self.client.get(
            f"{self.base_url}/api/v1/agents/search/advanced",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def sync_agent(self, tx_hash: str) -> Dict:
        """同步 Agent 到数据库"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/agents/sync",
            json={"tx_hash": tx_hash}
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Group APIs ==========
    
    async def create_group(
        self,
        name: str,
        description: str,
        admin_address: str,
        initial_agents: List[int]
    ) -> Dict:
        """创建 Group"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/groups/",  # 添加结尾斜杠
            json={
                "name": name,
                "description": description,
                "admin_address": admin_address,
                "initial_agents": initial_agents
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_group(self, group_id: str) -> Dict:
        """获取 Group 详情"""
        response = await self.client.get(f"{self.base_url}/api/v1/groups/{group_id}")
        response.raise_for_status()
        return response.json()
    
    async def add_agent_to_group(self, group_id: str, agent_id: int) -> Dict:
        """添加 Agent 到 Group"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/groups/{group_id}/add-agent",
            json={"agent_id": agent_id}
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Task APIs ==========
    
    async def delegate_task(
        self,
        agent_id: int,
        task_data: Dict,
        group_id: Optional[str] = None
    ) -> Dict:
        """委派任务"""
        # 确保 task_data 包含所有必需字段
        if group_id:
            task_data["group_id"] = group_id
        
        # agent_id 作为查询参数，task_data 作为 JSON body
        response = await self.client.post(
            f"{self.base_url}/api/v1/tasks/delegate",
            params={"agent_id": agent_id},  # 查询参数
            json=task_data  # JSON body
        )
        response.raise_for_status()
        return response.json()
    
    async def get_task(self, task_id: str) -> Dict:
        """获取任务详情"""
        response = await self.client.get(f"{self.base_url}/api/v1/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
    
    async def list_tasks(
        self,
        agent_id: Optional[int] = None,
        group_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> Dict:
        """列出任务"""
        params = {"limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        if group_id:
            params["group_id"] = group_id
        if status:
            params["status"] = status
        
        response = await self.client.get(
            f"{self.base_url}/api/v1/tasks/",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def update_task_status(
        self,
        task_id: str,
        status: str,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ) -> Dict:
        """更新任务状态"""
        payload = {"status": status}
        if result:
            payload["result"] = result
        if error:
            payload["error"] = error
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/tasks/{task_id}/status",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Reputation APIs ==========
    
    async def submit_feedback(
        self,
        agent_id: int,
        rating: int,  # 必须是整数 1-5
        comment: str,
        reviewer_address: str,
        payment_proof: str,  # 必须是字符串（tx hash）
        private_key: str = None
    ) -> Dict:
        """提交反馈"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/reputation/feedback",
            json={
                "agent_id": agent_id,
                "rating": rating,
                "comment": comment,
                "reviewer_address": reviewer_address,
                "payment_proof": payment_proof,
                "private_key": private_key or "0x" + "0" * 64  # 使用提供的或 mock key
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_reputation(self, agent_id: int) -> Dict:
        """获取声誉"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/reputation/{agent_id}"
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Analytics APIs ==========
    
    async def get_ecosystem_health(self) -> Dict:
        """获取生态健康"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/analytics/ecosystem/health"
        )
        response.raise_for_status()
        return response.json()
    
    async def get_trending_agents(self, days: int = 7, limit: int = 10) -> Dict:
        """获取趋势 Agents"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/analytics/agents/trending",
            params={"days": days, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Helper Methods ==========
    
    async def health_check(self) -> bool:
        """检查平台健康状态"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

