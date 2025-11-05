"""
Setup Demo Data
Create necessary Agents for demonstration
"""

import asyncio
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web3 import Web3
from eth_account import Account
import httpx
from rich.console import Console
from rich.panel import Panel

console = Console()

# Demo account private keys (Hardhat test accounts)
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
    """Check if platform is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PLATFORM_URL}/health", timeout=5.0)
            return response.status_code == 200
    except Exception:
        return False


async def upload_to_ipfs(metadata: dict) -> str:
    """Upload metadata to IPFS (or use mock)"""
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
    
    # Fallback: Generate mock CID
    import hashlib
    import json
    data_str = json.dumps(metadata, sort_keys=True)
    mock_cid = hashlib.sha256(data_str.encode()).hexdigest()[:46]
    return f"ipfs://Qm{mock_cid}"


async def register_agent_on_blockchain(agent_data: dict, w3: Web3) -> str:
    """Register Agent on blockchain"""
    
    # Load contract ABI (simplified version)
    # Should load from artifacts in production
    contract_address = w3.to_checksum_address("0x5FbDB2315678afecb367f032d93F642f64180aa3")
    
    # Simplified ABI - only includes registerAgent function
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
        
        # Prepare account
        account = Account.from_key(agent_data["private_key"])
        
        # Upload metadata
        metadata = {
            "name": agent_data["name"],
            "description": agent_data["description"],
            "capabilities": agent_data["capabilities"],
            "endpoint": agent_data["endpoint"],
            "version": "1.0"
        }
        
        ipfs_uri = await upload_to_ipfs(metadata)
        console.print(f"  📦 Metadata URI: {ipfs_uri}")
        
        # Build transaction
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
            'gas': 3000000,  # Increased gas limit
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(txn, agent_data["private_key"])
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        console.print(f"  ⏳ Waiting for transaction confirmation... TX: {tx_hash.hex()}")
        
        # Wait for transaction confirmation
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if tx_receipt['status'] == 1:
            console.print(f"  ✅ Blockchain registration successful")
            return tx_hash.hex()
        else:
            console.print(f"  ❌ Transaction failed")
            return None
            
    except Exception as e:
        console.print(f"  ❌ Blockchain registration failed: {e}")
        return None


async def sync_to_database(tx_hash: str) -> dict:
    """Sync Agent to database"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PLATFORM_URL}/api/v1/agents/sync",
                json={"tx_hash": tx_hash},
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                console.print(f"  ✅ Database sync successful (Token ID: {data.get('token_id')})")
                return data
            else:
                console.print(f"  ❌ Database sync failed: {response.text}")
                return None
                
    except Exception as e:
        console.print(f"  ❌ Sync failed: {e}")
        return None


async def manually_create_agent(agent_data: dict) -> dict:
    """Manually create Agent (bypass blockchain, insert directly to database)"""
    try:
        # Generate mock token_id
        import random
        token_id = random.randint(1, 1000)
        
        # Prepare Agent data
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
        
        # Insert directly to database
        console.print(f"  📝 Manually creating Agent (Token ID: {token_id})")
        
        try:
            # Insert via API (simulating sync result)
            # Actually, directly operating MongoDB would be more reliable
            from motor.motor_asyncio import AsyncIOMotorClient
            
            mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
            db = mongo_client.a2a_ecosystem
            
            # Check if same token_id already exists
            existing = await db.agents.find_one({"token_id": token_id})
            if existing:
                # If exists, use different token_id
                token_id = random.randint(1000, 9999)
                agent_doc["token_id"] = token_id
            
            # Insert to database
            await db.agents.insert_one(agent_doc)
            
            console.print(f"  ✅ Agent saved to database (Token ID: {token_id})")
            
            mongo_client.close()
            
            return agent_doc
            
        except Exception as db_error:
            console.print(f"  ⚠️  Database insertion failed: {db_error}")
            console.print(f"  ℹ️  Agent data prepared but not saved to database")
            return agent_doc
            
    except Exception as e:
        console.print(f"  ❌ Creation failed: {e}")
        return None


async def setup_demo_agents():
    """Setup demo Agents"""
    
    console.print(Panel.fit(
        "[bold cyan]A2A Demo Data Setup[/bold cyan]\n\n"
        "Preparing to create demo Agents...",
        border_style="cyan"
    ))
    
    # 1. Check platform health
    console.print("\n[bold]1. Check Platform Status[/bold]")
    if not await check_platform_health():
        console.print("[bold red]❌ Platform not running![/bold red]")
        console.print("\nPlease start the platform first:")
        console.print("  [dim]cd /Users/johnnylin/Documents/a2a-poc[/dim]")
        console.print("  [dim]pnpm dev[/dim]")
        return
    
    console.print("✅ Platform running normally\n")
    
    # 2. Initialize Web3
    console.print("[bold]2. Connect to Blockchain[/bold]")
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC))
    
    if not w3.is_connected():
        console.print("[bold red]❌ Blockchain not connected![/bold red]")
        console.print("\nPlease ensure Hardhat node is running")
        return
    
    console.print(f"✅ Connected to blockchain (Chain ID: {w3.eth.chain_id})\n")
    
    # 3. Register Agents
    console.print("[bold]3. Register Demo Agents[/bold]\n")
    
    registered_agents = []
    
    for idx, agent_data in enumerate(DEMO_ACCOUNTS, 1):
        console.print(f"[bold cyan]Agent {idx}/{len(DEMO_ACCOUNTS)}: {agent_data['name']}[/bold cyan]")
        
        # Method 1: Try registering on blockchain
        tx_hash = await register_agent_on_blockchain(agent_data, w3)
        
        if tx_hash:
            # Sync to database
            agent = await sync_to_database(tx_hash)
            if agent:
                # Add name field (from original data)
                agent['name'] = agent_data['name']
                registered_agents.append(agent)
        else:
            # Method 2: Manual creation (for demo)
            console.print("  ⚠️  Blockchain registration failed, using manual creation mode")
            agent = await manually_create_agent(agent_data)
            if agent:
                registered_agents.append(agent)
        
        console.print()
    
    # 4. Summary
    console.print(Panel.fit(
        f"[bold green]✨ Setup Complete![/bold green]\n\n"
        f"Created {len(registered_agents)} demo Agents:\n"
        + "\n".join([
            f"  • {a['name']} (Token ID: {a['token_id']})"
            for a in registered_agents
        ]) +
        f"\n\n[dim]Now you can run the demo:[/dim]\n"
        f"[cyan]python scenarios/demo_todo_app.py[/cyan]",
        border_style="green"
    ))


if __name__ == "__main__":
    try:
        asyncio.run(setup_demo_agents())
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Setup cancelled[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Setup failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()
