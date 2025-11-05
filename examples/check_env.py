#!/usr/bin/env python3
"""
环境检查脚本
快速验证所有必要的服务和依赖是否就绪
"""

import sys
import asyncio
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


async def check_service(name: str, url: str, method: str = "GET", json_data: dict = None) -> bool:
    """检查服务是否可用"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            if method == "GET":
                response = await client.get(url)
            else:
                response = await client.post(url, json=json_data)
            return response.status_code in [200, 201]
    except Exception:
        return False


async def check_environment():
    """检查所有环境"""
    
    console.print(Panel.fit(
        "[bold cyan]A2A Platform Environment Check[/bold cyan]\n\n"
        "验证所有必要服务是否运行中...",
        border_style="cyan"
    ))
    console.print()
    
    # 定义检查项
    checks = [
        {
            "name": "Backend API",
            "url": "http://localhost:8000/health",
            "required": True,
            "tip": "运行: pnpm dev"
        },
        {
            "name": "Blockchain (Hardhat)",
            "url": "http://localhost:8545",
            "method": "POST",
            "json_data": {
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 1
            },
            "required": True,
            "tip": "运行: cd apps/contracts && pnpm hardhat node"
        },
        {
            "name": "Frontend",
            "url": "http://localhost:5173",
            "required": False,
            "tip": "运行: cd apps/frontend && pnpm dev"
        },
        {
            "name": "MongoDB",
            "url": "http://localhost:27017",
            "required": True,
            "tip": "运行: brew services start mongodb-community"
        }
    ]
    
    # 执行检查
    results = []
    for check in checks:
        name = check["name"]
        with console.status(f"[yellow]检查 {name}...[/yellow]"):
            status = await check_service(
                name,
                check["url"],
                check.get("method", "GET"),
                check.get("json_data")
            )
            results.append({
                **check,
                "status": status
            })
    
    # 显示结果
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("服务", style="cyan", width=25)
    table.add_column("状态", width=10)
    table.add_column("URL", style="dim")
    table.add_column("必需", width=8)
    
    all_required_ok = True
    
    for result in results:
        status_icon = "✅" if result["status"] else "❌"
        status_text = "运行中" if result["status"] else "未运行"
        required = "是" if result["required"] else "否"
        
        if result["required"] and not result["status"]:
            all_required_ok = False
            status_text = f"[red]{status_text}[/red]"
        
        table.add_row(
            result["name"],
            f"{status_icon} {status_text}",
            result["url"],
            required
        )
    
    console.print(table)
    console.print()
    
    # 检查 Python 依赖
    console.print("[bold]Python 依赖检查:[/bold]")
    
    required_packages = [
        "httpx",
        "rich",
        "web3",
        "eth_account",
        "tenacity"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            console.print(f"  ✅ {package}")
        except ImportError:
            console.print(f"  ❌ {package}")
            missing_packages.append(package)
    
    console.print()
    
    # 显示建议
    if not all_required_ok:
        console.print(Panel(
            "[bold red]❌ 环境未就绪[/bold red]\n\n"
            "以下必需服务未运行:\n" +
            "\n".join([
                f"  • {r['name']}: {r['tip']}"
                for r in results
                if r['required'] and not r['status']
            ]),
            border_style="red",
            title="错误"
        ))
        return False
    
    if missing_packages:
        console.print(Panel(
            "[bold yellow]⚠️  依赖缺失[/bold yellow]\n\n"
            "请运行以下命令安装依赖:\n\n"
            f"  pip install {' '.join(missing_packages)}",
            border_style="yellow",
            title="警告"
        ))
        return False
    
    # 检查是否有演示数据
    console.print("[bold]演示数据检查:[/bold]")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/api/v1/agents?limit=5")
            if response.status_code == 200:
                data = response.json()
                agent_count = len(data.get("agents", []))
                
                if agent_count >= 2:
                    console.print(f"  ✅ 找到 {agent_count} 个 Agent")
                else:
                    console.print(f"  ⚠️  只有 {agent_count} 个 Agent")
                    console.print("  💡 运行以下命令创建演示数据:")
                    console.print("     [cyan]python scenarios/setup_demo_data.py[/cyan]")
                    console.print()
    except Exception:
        console.print("  ❌ 无法检查 Agent 数据")
    
    console.print()
    
    # 成功
    console.print(Panel.fit(
        "[bold green]✅ 环境就绪！[/bold green]\n\n"
        "所有必需服务正常运行，可以开始演示了！\n\n"
        "运行演示:\n"
        "  [cyan]python scenarios/demo_todo_app.py[/cyan]\n\n"
        "或使用快速启动脚本:\n"
        "  [cyan]./run_demo.sh[/cyan]",
        border_style="green",
        title="成功"
    ))
    
    return True


def main():
    """主函数"""
    try:
        result = asyncio.run(check_environment())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]检查已取消[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]检查失败: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

