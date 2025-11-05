"""
设置演示数据
创建必要的 Agents 用于演示
"""

import asyncio
import sys
import os

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web3 import Web3
from eth_account import Account
import httpx
from rich.console import Console
from rich.panel import Panel

console = Console()

# 演示账户私钥（Hardhat 测试账户）
DEMO_ACCOUNTS = [
    {
        "name": "PM Agent",
        "description": "AI Project Manager specialized in team coordination and task delegation",
        "capabilities": ["project-management", "team-coordination", "task-planning"],
        "private_key": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
        "endpoint": "http://localhost:3000"
    },
    {
        "name": "Frontend Expert",
        "description": "Senior Frontend Developer with expertise in React and TypeScript",
        "capabilities": ["react", "typescript", "ui-design", "responsive-design"],
        "private_key": "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
        "endpoint": "http://localhost:3001"
    },
    {
        "name": "Backend Master",
        "description": "Expert Backend Developer specializing in Python and FastAPI",
        "capabilities": ["python", "fastapi", "database", "api-design", "mongodb"],
        "private_key": "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
        "endpoint": "http://localhost:3002"
    }
]

PLATFORM_URL = "http://localhost:8000"
BLOCKCHAIN_RPC = "http://localhost:8545"


async def check_platform_health():
    """检查平台是否运行"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PLATFORM_URL}/health", timeout=5.0)
            return response.status_code == 200
    except Exception:
        return False


async def upload_to_ipfs(metadata: dict) -> str:
    """上传元数据到 IPFS（或使用 mock）"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PLATFORM_URL}/api/v1/ipfs/upload",
                json=metadata,
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("ipfs_uri", "")
    except Exception as e:
        console.print(f"[yellow]⚠️  IPFS upload warning: {e}[/yellow]")
    
    # Fallback: 生成 mock CID
    import hashlib
    import json
    data_str = json.dumps(metadata, sort_keys=True)
    mock_cid = hashlib.sha256(data_str.encode()).hexdigest()[:46]
    return f"ipfs://Qm{mock_cid}"


async def register_agent_on_blockchain(agent_data: dict, w3: Web3) -> str:
    """在区块链上注册 Agent"""
    
    # 加载合约 ABI（简化版）
    # 实际应该从 artifacts 加载
    contract_address = w3.to_checksum_address("0x5FbDB2315678afecb367f032d93F642f64180aa3")
    
    # 简化的 ABI - 只包含 registerAgent 函数
    contract_abi = [
        {
            "inputs": [
                {"internalType": "string", "name": "name", "type": "string"},
                {"internalType": "string", "name": "description", "type": "string"},
                {"internalType": "string[]", "name": "capabilities", "type": "string[]"},
                {"internalType": "string", "name": "endpoint", "type": "string"},
                {"internalType": "string", "name": "metadataURI", "type": "string"}
            ],
            "name": "registerAgent",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
    
    try:
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
        # 准备账户
        account = Account.from_key(agent_data["private_key"])
        
        # 上传 metadata
        metadata = {
            "name": agent_data["name"],
            "description": agent_data["description"],
            "capabilities": agent_data["capabilities"],
            "endpoint": agent_data["endpoint"],
            "version": "1.0"
        }
        
        ipfs_uri = await upload_to_ipfs(metadata)
        console.print(f"  📦 Metadata URI: {ipfs_uri}")
        
        # 构建交易
        nonce = w3.eth.get_transaction_count(account.address)
        
        txn = contract.functions.registerAgent(
            agent_data["name"],
            agent_data["description"],
            agent_data["capabilities"],
            agent_data["endpoint"],
            ipfs_uri
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 3000000,  # 增加 gas limit
            'gasPrice': w3.eth.gas_price
        })
        
        # 签名交易
        signed_txn = w3.eth.account.sign_transaction(txn, agent_data["private_key"])
        
        # 发送交易
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        console.print(f"  ⏳ 等待交易确认... TX: {tx_hash.hex()}")
        
        # 等待交易确认
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if tx_receipt['status'] == 1:
            console.print(f"  ✅ 区块链注册成功")
            return tx_hash.hex()
        else:
            console.print(f"  ❌ 交易失败")
            return None
            
    except Exception as e:
        console.print(f"  ❌ 区块链注册失败: {e}")
        return None


async def sync_to_database(tx_hash: str) -> dict:
    """同步 Agent 到数据库"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PLATFORM_URL}/api/v1/agents/sync",
                json={"tx_hash": tx_hash},
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                console.print(f"  ✅ 数据库同步成功 (Token ID: {data.get('token_id')})")
                return data
            else:
                console.print(f"  ❌ 数据库同步失败: {response.text}")
                return None
                
    except Exception as e:
        console.print(f"  ❌ 同步失败: {e}")
        return None


async def manually_create_agent(agent_data: dict) -> dict:
    """手动创建 Agent（绕过区块链，直接插入数据库）"""
    try:
        # 生成 mock token_id
        import random
        token_id = random.randint(1, 1000)
        
        # 准备 Agent 数据
        from datetime import datetime, timezone
        account = Account.from_key(agent_data["private_key"])
        
        agent_doc = {
            "token_id": token_id,
            "name": agent_data["name"],
            "description": agent_data["description"],
            "capabilities": agent_data["capabilities"],
            "endpoint": agent_data["endpoint"],
            "metadata_uri": await upload_to_ipfs({
                "name": agent_data["name"],
                "description": agent_data["description"],
                "capabilities": agent_data["capabilities"]
            }),
            "owner_address": account.address,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "reputation_score": 450,  # 4.5 stars * 100
            "feedback_count": 10,
            "total_tasks": 50,
            "completed_tasks": 47,
            "failed_tasks": 3
        }
        
        # 直接插入数据库
        console.print(f"  📝 手动创建 Agent (Token ID: {token_id})")
        
        try:
            # 通过 API 插入（模拟 sync 后的结果）
            # 实际上我们直接操作 MongoDB 会更可靠
            from motor.motor_asyncio import AsyncIOMotorClient
            
            mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
            db = mongo_client.a2a_ecosystem
            
            # 检查是否已存在相同 token_id
            existing = await db.agents.find_one({"token_id": token_id})
            if existing:
                # 如果存在，使用不同的 token_id
                token_id = random.randint(1000, 9999)
                agent_doc["token_id"] = token_id
            
            # 插入到数据库
            await db.agents.insert_one(agent_doc)
            
            console.print(f"  ✅ Agent 已保存到数据库 (Token ID: {token_id})")
            
            mongo_client.close()
            
            return agent_doc
            
        except Exception as db_error:
            console.print(f"  ⚠️  数据库插入失败: {db_error}")
            console.print(f"  ℹ️  Agent 数据已准备，但未保存到数据库")
            return agent_doc
            
    except Exception as e:
        console.print(f"  ❌ 创建失败: {e}")
        return None


async def setup_demo_agents():
    """设置演示 Agents"""
    
    console.print(Panel.fit(
        "[bold cyan]A2A Demo Data Setup[/bold cyan]\n\n"
        "准备创建演示 Agents...",
        border_style="cyan"
    ))
    
    # 1. 检查平台健康
    console.print("\n[bold]1. 检查平台状态[/bold]")
    if not await check_platform_health():
        console.print("[bold red]❌ 平台未运行！[/bold red]")
        console.print("\n请先启动平台:")
        console.print("  [dim]cd /Users/johnnylin/Documents/a2a-poc[/dim]")
        console.print("  [dim]pnpm dev[/dim]")
        return
    
    console.print("✅ 平台运行正常\n")
    
    # 2. 初始化 Web3
    console.print("[bold]2. 连接区块链[/bold]")
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC))
    
    if not w3.is_connected():
        console.print("[bold red]❌ 区块链未连接！[/bold red]")
        console.print("\n请确保 Hardhat 节点正在运行")
        return
    
    console.print(f"✅ 已连接到区块链 (Chain ID: {w3.eth.chain_id})\n")
    
    # 3. 注册 Agents
    console.print("[bold]3. 注册演示 Agents[/bold]\n")
    
    registered_agents = []
    
    for idx, agent_data in enumerate(DEMO_ACCOUNTS, 1):
        console.print(f"[bold cyan]Agent {idx}/{len(DEMO_ACCOUNTS)}: {agent_data['name']}[/bold cyan]")
        
        # 方法 1: 尝试在区块链上注册
        tx_hash = await register_agent_on_blockchain(agent_data, w3)
        
        if tx_hash:
            # 同步到数据库
            agent = await sync_to_database(tx_hash)
            if agent:
                # 添加 name 字段（从原始数据）
                agent['name'] = agent_data['name']
                registered_agents.append(agent)
        else:
            # 方法 2: 手动创建（用于演示）
            console.print("  ⚠️  区块链注册失败，使用手动创建模式")
            agent = await manually_create_agent(agent_data)
            if agent:
                registered_agents.append(agent)
        
        console.print()
    
    # 4. 总结
    console.print(Panel.fit(
        f"[bold green]✨ 设置完成！[/bold green]\n\n"
        f"已创建 {len(registered_agents)} 个演示 Agents:\n"
        + "\n".join([
            f"  • {a['name']} (Token ID: {a['token_id']})"
            for a in registered_agents
        ]) +
        f"\n\n[dim]现在可以运行演示:[/dim]\n"
        f"[cyan]python scenarios/demo_todo_app.py[/cyan]",
        border_style="green"
    ))


if __name__ == "__main__":
    try:
        asyncio.run(setup_demo_agents())
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  设置已取消[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]❌ 设置失败: {e}[/bold red]")
        import traceback
        traceback.print_exc()

