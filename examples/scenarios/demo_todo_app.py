#!/usr/bin/env python3
"""
完整演示: PM Agent 自动组建团队开发 Todo List App

展示功能:
1. PM Agent 自动搜索合适的开发者
2. 自动创建 Group
3. 自动委派任务
4. 监控任务进度
5. 自动评价和支付
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import argparse

from agents.pm_agent import PMAgent
from utils.api_client import PlatformClient
from utils.logger import log_section, log_success, log_error, log_info

console = Console()


# 项目需求
TODO_APP_REQUIREMENTS = {
    "name": "Todo List App",
    "description": """
一个现代化的 Todo List 应用，帮助用户管理日常任务。

核心功能:
- 用户注册和登录
- 任务 CRUD 操作
- 任务分类和标签
- 截止日期提醒
- 任务优先级
- 统计和分析

技术栈:
- Frontend: React + TypeScript + TailwindCSS
- Backend: FastAPI + MongoDB
- 部署: Docker + Nginx
""",
    "required_capabilities": {
        "frontend": ["react", "typescript", "ui-design"],
        "backend": ["python", "fastapi", "database"]
    },
    "min_reputation": 0.0,  # 降低到 0.0 以匹配新注册的 Agents
    "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
    "budget": 0.5  # ETH
}


async def check_prerequisites():
    """检查前置条件"""
    console.print("[bold]检查前置条件...[/bold]\n")
    
    # 检查平台
    client = PlatformClient()
    
    try:
        if not await client.health_check():
            raise Exception("平台未运行")
        log_success("平台运行正常", "http://localhost:8000")
        
        # 检查是否有可用的 Agents
        agents_data = await client.list_agents(limit=5)
        agent_count = len(agents_data.get("agents", []))
        
        if agent_count < 2:
            log_error(
                f"Agent 数量不足 (当前: {agent_count}, 需要: 至少 2 个)",
                Exception("请先运行 setup_demo_data.py")
            )
            console.print("\n运行以下命令设置演示数据:")
            console.print("  [cyan]python scenarios/setup_demo_data.py[/cyan]\n")
            return False
        
        log_success(f"找到 {agent_count} 个可用 Agents")
        
        return True
        
    except Exception as e:
        log_error("前置条件检查失败", e)
        return False
    finally:
        await client.close()


async def run_demo(fast_mode: bool = False):
    """运行完整演示"""
    
    # 显示欢迎信息
    console.print()
    console.print(Panel.fit(
        "[bold cyan]A2A Agent Ecosystem Demo[/bold cyan]\n\n"
        "[bold]场景:[/bold] PM Agent 自动组建团队开发 Todo List App\n\n"
        "[dim]本演示将展示 AI Agents 如何自主协作完成项目[/dim]",
        border_style="cyan",
        title="🚀 Demo Start"
    ))
    console.print()
    
    # 检查前置条件
    if not await check_prerequisites():
        return
    
    console.print()
    input("按 Enter 继续...")
    console.print()
    
    # 初始化 PM Agent
    log_section("初始化 PM Agent")
    
    pm_agent = PMAgent(
        name="PM Agent",
        private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    )
    
    log_success("PM Agent 已启动")
    log_info(f"地址: {pm_agent.address}")
    console.print()
    
    if not fast_mode:
        await asyncio.sleep(1)
    
    try:
        # 显示项目需求
        log_section("项目需求")
        console.print(Panel(
            f"""[bold cyan]{TODO_APP_REQUIREMENTS['name']}[/bold cyan]

{TODO_APP_REQUIREMENTS['description']}

[bold]预算:[/bold] {TODO_APP_REQUIREMENTS['budget']} ETH
[bold]截止日期:[/bold] {TODO_APP_REQUIREMENTS['deadline'][:10]}
""",
            border_style="cyan"
        ))
        console.print()
        
        if not fast_mode:
            input("按 Enter 开始自动化流程...")
            console.print()
        
        # 🚀 启动项目（核心演示）
        with console.status("[bold green]PM Agent 正在工作中...[/bold green]"):
            if not fast_mode:
                await asyncio.sleep(1)
        
        result = await pm_agent.start_project(TODO_APP_REQUIREMENTS)
        
        # 显示项目摘要
        console.print()
        log_section("项目执行摘要")
        
        summary = await pm_agent.get_project_summary()
        
        console.print(Panel(
            f"""[bold green]✨ 项目完成！[/bold green]

[bold]团队组成:[/bold]
{chr(10).join([f"  • {m['role']}: {m['name']} (Token ID: {m['token_id']})" for m in summary['team_members']])}

[bold]Group ID:[/bold] {summary['group_id']}
[bold]任务数量:[/bold] {summary['active_tasks']}
[bold]项目状态:[/bold] ✅ 已完成

[dim]所有任务已委派并完成，团队成员已获得评价[/dim]
""",
            border_style="green",
            title="📊 Project Summary"
        ))
        
        # 显示后续步骤
        console.print()
        log_section("后续步骤")
        console.print("""
1. 查看 Analytics Dashboard:
   [cyan]http://localhost:5173/analytics[/cyan]

2. 查看 Groups:
   [cyan]http://localhost:5173/groups[/cyan]

3. 查看 API 文档:
   [cyan]http://localhost:8000/docs[/cyan]

4. 检查数据库:
   [dim]mongosh a2a_ecosystem[/dim]
   [dim]db.agents.find().pretty()[/dim]
   [dim]db.groups.find().pretty()[/dim]
   [dim]db.tasks.find().pretty()[/dim]
""")
        
        # 成功完成
        console.print()
        console.print(Panel.fit(
            "[bold green]🎉 Demo 完成！[/bold green]\n\n"
            "[bold]展示了以下功能:[/bold]\n"
            "  ✅ Agent 自动搜索和发现\n"
            "  ✅ 自动组建协作 Group\n"
            "  ✅ 自动委派任务\n"
            "  ✅ 任务监控和管理\n"
            "  ✅ 自动评价和反馈\n\n"
            "[dim]这就是真正的 Agent 自主协作生态！[/dim]",
            border_style="green"
        ))
        
    except Exception as e:
        log_error("Demo 执行失败", e)
        import traceback
        traceback.print_exc()
    finally:
        await pm_agent.close()


async def quick_status_check():
    """快速状态检查"""
    console.print("[bold]快速状态检查[/bold]\n")
    
    client = PlatformClient()
    
    try:
        # 检查 Agents
        agents_data = await client.list_agents(limit=10)
        agents = agents_data.get("agents", [])
        console.print(f"✅ Agents: {len(agents)}")
        
        # 检查 Groups
        try:
            groups_response = await client.client.get(f"{client.base_url}/api/v1/groups")
            groups_data = groups_response.json()
            groups = groups_data.get("groups", [])
            console.print(f"✅ Groups: {len(groups)}")
        except:
            console.print("⚠️  Groups: 无法获取")
        
        # 检查 Tasks
        tasks_data = await client.list_tasks(limit=10)
        tasks = tasks_data.get("tasks", [])
        console.print(f"✅ Tasks: {len(tasks)}")
        
        console.print()
        
        if len(agents) > 0:
            console.print("[bold]可用 Agents:[/bold]")
            for agent in agents[:5]:
                rep = agent.get("reputation_score", 0) / 100
                console.print(f"  • {agent['name']} (Token ID: {agent['token_id']}, {rep:.1f}⭐)")
        
    except Exception as e:
        log_error("状态检查失败", e)
    finally:
        await client.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="A2A Agent Demo - Todo App")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="快速模式（跳过等待）"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="只显示状态"
    )
    
    args = parser.parse_args()
    
    try:
        if args.status:
            asyncio.run(quick_status_check())
        else:
            asyncio.run(run_demo(fast_mode=args.fast))
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Demo 已取消[/yellow]")
    except Exception as e:
        console.print(f"\n\n[bold red]❌ Demo 失败: {e}[/bold red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

