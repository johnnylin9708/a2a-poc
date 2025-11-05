"""
Enhanced logging utilities with rich formatting
"""

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box
from typing import List, Dict, Any
import logging

console = Console()


def setup_logger(name: str = "a2a_agent", level: str = "INFO") -> logging.Logger:
    """设置日志"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def log_success(message: str, details: str = ""):
    """成功日志"""
    console.print(f"✅ {message}", style="bold green")
    if details:
        console.print(f"   {details}", style="dim")


def log_error(message: str, error: Exception = None):
    """错误日志"""
    console.print(f"❌ {message}", style="bold red")
    if error:
        console.print(f"   Error: {str(error)}", style="dim red")


def log_info(message: str, details: str = ""):
    """信息日志"""
    console.print(f"ℹ️  {message}", style="bold blue")
    if details:
        console.print(f"   {details}", style="dim")


def log_warning(message: str):
    """警告日志"""
    console.print(f"⚠️  {message}", style="bold yellow")


def log_section(title: str):
    """节标题"""
    console.print()
    console.rule(f"[bold cyan]{title}[/bold cyan]")
    console.print()


def log_agent_search_results(agents: List[Dict]):
    """显示 Agent 搜索结果"""
    if not agents:
        console.print("   [dim]未找到符合条件的 Agent[/dim]")
        return
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Rank", style="dim", width=6)
    table.add_column("Name", style="cyan")
    table.add_column("Token ID", justify="center")
    table.add_column("Reputation", justify="center")
    table.add_column("Tasks", justify="center")
    table.add_column("Success Rate", justify="center")
    
    for idx, agent in enumerate(agents, 1):
        reputation = agent.get("reputation_score", 0) / 100
        total_tasks = agent.get("total_tasks", 0)
        completed = agent.get("completed_tasks", 0)
        success_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
        
        table.add_row(
            f"#{idx}",
            agent.get("name", "Unknown"),
            str(agent.get("token_id", "N/A")),
            f"{reputation:.1f} ⭐",
            str(total_tasks),
            f"{success_rate:.0f}%"
        )
    
    console.print(table)


def log_task_delegation(task_data: Dict):
    """显示任务委派详情"""
    console.print(Panel.fit(
        f"""[bold]Task Details[/bold]

Title: {task_data.get('title', 'N/A')}
Type: {task_data.get('task_type', 'general')}
Priority: {task_data.get('priority', 3)}/5
Deadline: {task_data.get('deadline', 'Not set')}

[dim]Description:[/dim]
{task_data.get('description', 'No description')}
""",
        border_style="green"
    ))


def log_progress(message: str):
    """显示进度"""
    console.print(f"⏳ {message}", style="bold yellow")


def log_completion(message: str, stats: Dict = None):
    """显示完成信息"""
    console.print()
    console.print(Panel.fit(
        f"""[bold green]✨ {message}[/bold green]

{_format_stats(stats) if stats else ''}
""",
        border_style="green",
        title="[bold]Demo Complete[/bold]"
    ))


def _format_stats(stats: Dict) -> str:
    """格式化统计信息"""
    lines = []
    for key, value in stats.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def log_agent_card(agent: Dict):
    """显示 Agent 卡片"""
    capabilities = ", ".join(agent.get("capabilities", []))
    reputation = agent.get("reputation_score", 0) / 100
    
    console.print(Panel(
        f"""[bold cyan]{agent.get('name', 'Unknown Agent')}[/bold cyan]
[dim]Token ID: {agent.get('token_id', 'N/A')}[/dim]

{agent.get('description', 'No description')}

[bold]Capabilities:[/bold] {capabilities}
[bold]Reputation:[/bold] {reputation:.1f} ⭐ ({agent.get('feedback_count', 0)} reviews)
[bold]Tasks:[/bold] {agent.get('total_tasks', 0)} total, {agent.get('completed_tasks', 0)} completed
""",
        border_style="cyan",
        expand=False
    ))


def create_progress_bar(description: str = "Processing..."):
    """创建进度条"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    )

