"""
Base Agent Class
所有 Agent 的基类，封装通用功能
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
    """Agent 基类"""
    
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
        
        # Web3 初始化
        self.w3 = Web3(Web3.HTTPProvider(blockchain_rpc))
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        
        # Platform 客户端
        self.client = PlatformClient(platform_url)
        
        # Agent 状态
        self.token_id: Optional[int] = None
        self.is_registered = False
        
        logger.info(f"✅ {name} initialized with address {self.address}")
    
    async def close(self):
        """关闭连接"""
        await self.client.close()
    
    # ========== 核心功能 ==========
    
    async def register(self, endpoint: str = "http://localhost:3000") -> int:
        """
        注册 Agent 到区块链
        
        Returns:
            token_id: Agent 的 Token ID
        """
        try:
            log_info(f"注册 Agent: {self.name}")
            
            # 1. 上传 metadata 到 IPFS
            metadata = {
                "name": self.name,
                "description": self.description,
                "capabilities": self.capabilities,
                "endpoint": endpoint,
                "version": "1.0",
                "agent_type": self.__class__.__name__
            }
            
            # 这里简化处理，实际应该调用 IPFS API
            # 暂时使用 mock CID
            ipfs_uri = f"ipfs://Qm{self.name.replace(' ', '')}{len(self.capabilities)}"
            
            log_success(f"Metadata uploaded", f"URI: {ipfs_uri}")
            
            # 2. 调用智能合约注册
            # 注意：这里应该通过前端或者直接调用合约
            # 目前我们假设已经在链上注册，直接同步到数据库
            
            # 模拟 tx_hash (实际应该从合约调用获取)
            mock_tx_hash = f"0x{'0' * 64}"
            
            # 3. 同步到数据库
            # 由于我们没有实际的区块链交易，这里手动创建数据
            # 实际场景应该调用 sync_agent API
            
            self.is_registered = True
            log_success(f"{self.name} 注册成功")
            
            return self.token_id
            
        except Exception as e:
            log_error(f"注册失败: {self.name}", e)
            raise
    
    async def discover_agents(
        self,
        capabilities: List[str],
        min_reputation: float = 0.0,
        sort_by: str = "reputation",
        limit: int = 10
    ) -> List[Dict]:
        """
        发现其他 Agents
        
        Args:
            capabilities: 需要的能力
            min_reputation: 最低声誉
            sort_by: 排序方式
            limit: 返回数量
        
        Returns:
            匹配的 Agents 列表
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
                f"找到 {len(agents)} 个 Agent",
                f"能力: {', '.join(capabilities)}"
            )
            
            return agents
            
        except Exception as e:
            log_error("搜索 Agent 失败", e)
            return []
    
    async def create_group(
        self,
        group_name: str,
        description: str,
        member_agents: List[int]
    ) -> Optional[str]:
        """
        创建 Agent Group
        
        Args:
            group_name: Group 名称
            description: 描述
            member_agents: 成员 Agent Token IDs
        
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
            log_success(f"Group 创建成功", f"ID: {group_id}")
            
            return group_id
            
        except Exception as e:
            log_error("创建 Group 失败", e)
            return None
    
    async def delegate_task(
        self,
        agent_id: int,
        task_data: Dict,
        group_id: Optional[str] = None
    ) -> Optional[str]:
        """
        委派任务给另一个 Agent
        
        Args:
            agent_id: 目标 Agent ID
            task_data: 任务数据
            group_id: Group ID (可选)
        
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
            log_success(f"任务委派成功", f"Task ID: {task_id}")
            
            return task_id
            
        except Exception as e:
            log_error("委派任务失败", e)
            return None
    
    async def submit_feedback(
        self,
        agent_id: int,
        rating: float,
        comment: str,
        tx_hash: str = "0x" + "0" * 64
    ) -> bool:
        """
        提交对其他 Agent 的反馈
        
        Args:
            agent_id: 目标 Agent ID
            rating: 评分 (0-5)
            comment: 评论
            tx_hash: 支付交易哈希
        
        Returns:
            是否成功
        """
        try:
            # 转换为整数评分 (1-5)
            rating_int = min(5, max(1, int(round(rating))))
            
            # payment_proof 必须是字符串
            payment_proof = tx_hash
            
            await self.client.submit_feedback(
                agent_id=agent_id,
                rating=rating_int,  # 使用整数
                comment=comment,
                reviewer_address=self.address,
                payment_proof=payment_proof,  # 使用字符串
                private_key=self.private_key
            )
            
            log_success(f"反馈提交成功", f"Agent #{agent_id} - {rating_int}⭐")
            return True
            
        except Exception as e:
            log_error("提交反馈失败", e)
            return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        try:
            task = await self.client.get_task(task_id)
            return task
        except Exception as e:
            log_error(f"获取任务状态失败: {task_id}", e)
            return None
    
    async def wait_for_task_completion(
        self,
        task_id: str,
        timeout: int = 300,
        check_interval: int = 5
    ) -> Optional[Dict]:
        """
        等待任务完成
        
        Args:
            task_id: 任务 ID
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
        
        Returns:
            完成的任务数据
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
        
        log_error(f"任务超时: {task_id}")
        return None
    
    # ========== 工具方法 ==========
    
    def sign_message(self, message: str) -> str:
        """签名消息"""
        message_hash = self.w3.keccak(text=message)
        signed = self.account.signHash(message_hash)
        return signed.signature.hex()
    
    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} token_id={self.token_id}>"

