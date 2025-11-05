#!/usr/bin/env python3
"""
测试链上反馈提交
使用 Hardhat mock account 提交真实的区块链交易
"""

import asyncio
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from utils.api_client import PlatformClient

console = Console()

# Hardhat 测试账户
TEST_ACCOUNTS = {
    "account0": {
        "address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "private_key": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    },
    "account1": {
        "address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
        "private_key": "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
    }
}


async def test_onchain_feedback():
    """测试链上反馈提交"""
    
    console.print("\n[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]")
    console.print("[bold cyan]  测试链上反馈提交[/bold cyan]")
    console.print("[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]\n")
    
    client = PlatformClient()
    
    try:
        # 1. 获取一个 Agent
        console.print("[bold]1. 查找测试 Agent[/bold]")
        agents_data = await client.list_agents(limit=5)
        agents = agents_data.get("agents", [])
        
        if not agents:
            console.print("[red]❌ 没有可用的 Agent[/red]")
            return
        
        test_agent = agents[0]
        console.print(f"✅ 找到 Agent: {test_agent['name']} (ID: {test_agent['token_id']})")
        console.print()
        
        # 2. 准备反馈数据
        console.print("[bold]2. 准备反馈数据[/bold]")
        account = TEST_ACCOUNTS["account1"]  # 使用 account1 作为评价者
        
        feedback_data = {
            "agent_id": test_agent['token_id'],
            "rating": 5,  # 必须是整数 1-5
            "comment": "Excellent work on the demo! Great performance.",
            "reviewer_address": account["address"],
            "payment_proof": "0x" + "a" * 64,  # Mock payment proof (32 bytes)
            "private_key": account["private_key"]
        }
        
        console.print(f"  Agent ID: {feedback_data['agent_id']}")
        console.print(f"  Rating: {feedback_data['rating']} ⭐")
        console.print(f"  Comment: {feedback_data['comment']}")
        console.print(f"  Reviewer: {account['address'][:10]}...")
        console.print()
        
        # 3. 提交反馈到链上
        console.print("[bold]3. 提交反馈到区块链[/bold]")
        console.print("⏳ 等待交易确认...")
        
        try:
            result = await client.submit_feedback(**feedback_data)
            
            console.print(f"[green]✅ 反馈已成功提交到区块链！[/green]")
            console.print(f"   Message: {result.get('message', 'N/A')}")
            console.print()
            
        except Exception as e:
            error_msg = str(e)
            console.print(f"[red]❌ 提交失败: {error_msg}[/red]")
            
            # 提供调试信息
            if "500" in error_msg or "Internal Server Error" in error_msg:
                console.print("\n[yellow]可能的原因:[/yellow]")
                console.print("  1. Reputation Registry 合约未部署")
                console.print("  2. 合约地址配置错误")
                console.print("  3. Gas 不足")
                console.print("\n[cyan]解决方案:[/cyan]")
                console.print("  1. 检查合约部署: cd apps/contracts && pnpm hardhat run scripts/deploy.ts --network localhost")
                console.print("  2. 检查后端配置: apps/backend/.env")
                console.print("  3. 查看后端日志了解详细错误")
            
            return
        
        # 4. 验证结果
        console.print("[bold]4. 验证链上数据[/bold]")
        
        try:
            reputation_data = await client.get_reputation(test_agent['token_id'])
            
            console.print(f"✅ 当前声誉数据:")
            console.print(f"   平均评分: {reputation_data.get('average_rating', 0):.2f} ⭐")
            console.print(f"   反馈数量: {reputation_data.get('feedback_count', 0)}")
            console.print(f"   声誉等级: {reputation_data.get('reputation_tier', 'N/A')}")
            
        except Exception as e:
            console.print(f"[yellow]⚠️  无法获取声誉数据: {e}[/yellow]")
        
        console.print()
        console.print("[bold green]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold green]")
        console.print("[bold green]  测试完成！✨[/bold green]")
        console.print("[bold green]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold green]")
        console.print()
        
    except Exception as e:
        console.print(f"\n[bold red]测试失败: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        
    finally:
        await client.close()


async def check_contracts():
    """检查合约是否已部署"""
    console.print("\n[bold]检查合约部署状态[/bold]")
    
    try:
        from web3 import Web3
        
        w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
        
        if not w3.is_connected():
            console.print("[red]❌ 无法连接到区块链[/red]")
            return False
        
        console.print(f"✅ 已连接到区块链 (Chain ID: {w3.eth.chain_id})")
        
        # 检查合约地址配置
        import os
        from dotenv import load_dotenv
        
        env_path = Path(__file__).parent.parent / "apps" / "backend" / ".env"
        load_dotenv(env_path)
        
        identity_addr = os.getenv("IDENTITY_REGISTRY_ADDRESS")
        reputation_addr = os.getenv("REPUTATION_REGISTRY_ADDRESS")
        
        console.print(f"Identity Registry: {identity_addr or '[red]未配置[/red]'}")
        console.print(f"Reputation Registry: {reputation_addr or '[red]未配置[/red]'}")
        
        if not reputation_addr:
            console.print("\n[yellow]⚠️  Reputation Registry 地址未配置[/yellow]")
            console.print("[cyan]请运行: cd apps/contracts && pnpm hardhat run scripts/deploy.ts --network localhost[/cyan]")
            return False
        
        # 检查合约是否存在
        code = w3.eth.get_code(Web3.to_checksum_address(reputation_addr))
        if code == b'' or code == b'0x':
            console.print("[red]❌ Reputation Registry 合约不存在[/red]")
            return False
        
        console.print("✅ Reputation Registry 合约已部署")
        console.print()
        return True
        
    except Exception as e:
        console.print(f"[red]❌ 检查失败: {e}[/red]")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="测试链上反馈提交")
    parser.add_argument("--check-contracts", action="store_true", help="只检查合约状态")
    
    args = parser.parse_args()
    
    try:
        if args.check_contracts:
            asyncio.run(check_contracts())
        else:
            # 先检查合约
            if asyncio.run(check_contracts()):
                asyncio.run(test_onchain_feedback())
            else:
                console.print("\n[red]请先部署合约或检查配置[/red]")
                sys.exit(1)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]测试已取消[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]错误: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

