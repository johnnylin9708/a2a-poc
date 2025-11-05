#!/usr/bin/env python3
"""
Complete Demo: PM Agent Automatically Forms Team to Develop Todo List App

Demonstrates:
1. PM Agent automatically searches for suitable developers
2. Automatically creates Group
3. Automatically delegates tasks
4. Monitors task progress
5. Automatically evaluates and provides feedback
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import argparse

from agents.pm_agent import PMAgent
from utils.api_client import PlatformClient
from utils.logger import log_section, log_success, log_error, log_info

console = Console()


# Project requirements
TODO_APP_REQUIREMENTS = {
    "name": "Todo List App",
    "description": """
A modern Todo List application to help users manage daily tasks.

Core Features:
- User registration and login
- Task CRUD operations
- Task categories and tags
- Deadline reminders
- Task priority levels
- Statistics and analytics

Tech Stack:
- Frontend: React + TypeScript + TailwindCSS
- Backend: FastAPI + MongoDB
- Deployment: Docker + Nginx
""",
    "required_capabilities": {
        "frontend": ["react", "typescript", "ui-design"],
        "backend": ["python", "fastapi", "database"]
    },
    "min_reputation": 0.0,  # Lowered to 0.0 to match newly registered Agents
    "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
    "budget": 0.5  # ETH
}


async def check_prerequisites():
    """Check prerequisites"""
    console.print("[bold]Checking prerequisites...[/bold]\n")
    
    # Check platform
    client = PlatformClient()
    
    try:
        if not await client.health_check():
            raise Exception("Platform not running")
        log_success("Platform is running", "http://localhost:8000")
        
        # Check if there are available Agents
        agents_data = await client.list_agents(limit=5)
        agent_count = len(agents_data.get("agents", []))
        
        if agent_count < 2:
            log_error(
                f"Insufficient Agents (current: {agent_count}, required: at least 2)",
                Exception("Please run setup_demo_data.py first")
            )
            console.print("\nRun the following command to setup demo data:")
            console.print("  [cyan]python scenarios/setup_demo_data.py[/cyan]\n")
            return False
        
        log_success(f"Found {agent_count} available Agents")
        
        return True
        
    except Exception as e:
        log_error("Prerequisites check failed", e)
        return False
    finally:
        await client.close()


async def run_demo(fast_mode: bool = False):
    """Run complete demo"""
    
    # Display welcome message
    console.print()
    console.print(Panel.fit(
        "[bold cyan]A2A Agent Ecosystem Demo[/bold cyan]\n\n"
        "[bold]Scenario:[/bold] PM Agent automatically forms team to develop Todo List App\n\n"
        "[dim]This demo shows how AI Agents autonomously collaborate to complete a project[/dim]",
        border_style="cyan",
        title="🚀 Demo Start"
    ))
    console.print()
    
    # Check prerequisites
    if not await check_prerequisites():
        return
    
    console.print()
    if not fast_mode:
        input("Press Enter to continue...")
    console.print()
    
    # Initialize PM Agent
    log_section("Initialize PM Agent")
    
    pm_agent = PMAgent(
        name="PM Agent",
        private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    )
    
    log_success("PM Agent started")
    log_info(f"Address: {pm_agent.address}")
    console.print()
    
    if not fast_mode:
        await asyncio.sleep(1)
    
    try:
        # Display project requirements
        log_section("Project Requirements")
        console.print(Panel(
            f"""[bold cyan]{TODO_APP_REQUIREMENTS['name']}[/bold cyan]

{TODO_APP_REQUIREMENTS['description']}

[bold]Budget:[/bold] {TODO_APP_REQUIREMENTS['budget']} ETH
[bold]Deadline:[/bold] {TODO_APP_REQUIREMENTS['deadline'][:10]}
""",
            border_style="cyan"
        ))
        console.print()
        
        if not fast_mode:
            input("Press Enter to start automated workflow...")
            console.print()
        
        # 🚀 Start project (core demo)
        with console.status("[bold green]PM Agent is working...[/bold green]"):
            if not fast_mode:
                await asyncio.sleep(1)
        
        result = await pm_agent.start_project(TODO_APP_REQUIREMENTS)
        
        # Display project summary
        console.print()
        log_section("Project Execution Summary")
        
        summary = await pm_agent.get_project_summary()
        
        console.print(Panel(
            f"""[bold green]✨ Project Completed![/bold green]

[bold]Team Composition:[/bold]
{chr(10).join([f"  • {m['role']}: {m['name']} (Token ID: {m['token_id']})" for m in summary['team_members']])}

[bold]Group ID:[/bold] {summary['group_id']}
[bold]Task Count:[/bold] {summary['active_tasks']}
[bold]Project Status:[/bold] ✅ Completed

[dim]All tasks have been delegated and completed, team members have received evaluations[/dim]
""",
            border_style="green",
            title="📊 Project Summary"
        ))
        
        # Display next steps
        console.print()
        log_section("Next Steps")
        console.print("""
1. View Analytics Dashboard:
   [cyan]http://localhost:5173/analytics[/cyan]

2. View Groups:
   [cyan]http://localhost:5173/groups[/cyan]

3. View API Documentation:
   [cyan]http://localhost:8000/docs[/cyan]

4. Check database:
   [dim]mongosh a2a_ecosystem[/dim]
   [dim]db.agents.find().pretty()[/dim]
   [dim]db.groups.find().pretty()[/dim]
   [dim]db.tasks.find().pretty()[/dim]
""")
        
        # Success completion
        console.print()
        console.print(Panel.fit(
            "[bold green]🎉 Demo Completed![/bold green]\n\n"
            "[bold]Demonstrated Features:[/bold]\n"
            "  ✅ Automatic agent search and discovery\n"
            "  ✅ Automatic collaboration group formation\n"
            "  ✅ Automatic task delegation\n"
            "  ✅ Task monitoring and management\n"
            "  ✅ Automatic evaluation and feedback\n\n"
            "[dim]This is true agent autonomous collaboration ecosystem![/dim]",
            border_style="green"
        ))
        
    except Exception as e:
        log_error("Demo execution failed", e)
        import traceback
        traceback.print_exc()
    finally:
        await pm_agent.close()


async def quick_status_check():
    """Quick status check"""
    console.print("[bold]Quick Status Check[/bold]\n")
    
    client = PlatformClient()
    
    try:
        # Check Agents
        agents_data = await client.list_agents(limit=10)
        agents = agents_data.get("agents", [])
        console.print(f"✅ Agents: {len(agents)}")
        
        # Check Groups
        try:
            groups_response = await client.client.get(f"{client.base_url}/api/v1/groups")
            groups_data = groups_response.json()
            groups = groups_data.get("groups", [])
            console.print(f"✅ Groups: {len(groups)}")
        except:
            console.print("⚠️  Groups: Unable to fetch")
        
        # Check Tasks
        tasks_data = await client.list_tasks(limit=10)
        tasks = tasks_data.get("tasks", [])
        console.print(f"✅ Tasks: {len(tasks)}")
        
        console.print()
        
        if len(agents) > 0:
            console.print("[bold]Available Agents:[/bold]")
            for agent in agents[:5]:
                rep = agent.get("reputation_score", 0) / 100
                console.print(f"  • {agent['name']} (Token ID: {agent['token_id']}, {rep:.1f}⭐)")
        
    except Exception as e:
        log_error("Status check failed", e)
    finally:
        await client.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="A2A Agent Demo - Todo App")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Fast mode (skip waits)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show status only"
    )
    
    args = parser.parse_args()
    
    try:
        if args.status:
            asyncio.run(quick_status_check())
        else:
            asyncio.run(run_demo(fast_mode=args.fast))
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Demo cancelled[/yellow]")
    except Exception as e:
        console.print(f"\n\n[bold red]❌ Demo failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
