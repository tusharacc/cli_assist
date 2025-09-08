"""
Panel creation functions for Lumos CLI UI
"""

from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich import box
from typing import Optional, List, Dict, Any

def create_command_help_panel(console, commands: List[Dict[str, str]]) -> Panel:
    """Create a help panel showing available commands"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Example", style="dim")
    
    for cmd in commands:
        table.add_row(cmd["command"], cmd["description"], cmd["example"])
    
    return Panel(
        table,
        title="[bold blue]Available Commands[/bold blue]",
        border_style="blue",
        box=box.ROUNDED
    )

def create_status_panel(console, status_data: Dict[str, Any]) -> Panel:
    """Create a status panel showing system status"""
    content = ""
    for service, status in status_data.items():
        status_icon = "🟢" if status else "🔴"
        content += f"{status_icon} {service}\n"
    
    return Panel(
        content.strip(),
        title="[bold green]System Status[/bold green]",
        border_style="green",
        box=box.ROUNDED
    )

def create_config_panel(console, config_data: Dict[str, Any]) -> Panel:
    """Create a configuration panel showing current settings"""
    content = ""
    for key, value in config_data.items():
        if isinstance(value, bool):
            value_str = "✅ Enabled" if value else "❌ Disabled"
        else:
            value_str = str(value)
        content += f"{key}: {value_str}\n"
    
    return Panel(
        content.strip(),
        title="[bold yellow]Configuration[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED
    )

def create_welcome_panel(console) -> Panel:
    """Create a welcome panel for new users"""
    welcome_text = Text()
    welcome_text.append("Welcome to ", style="white")
    welcome_text.append("Lumos CLI", style="bold bright_blue")
    welcome_text.append("! 🚀\n\n", style="white")
    welcome_text.append("Your AI-powered command line assistant is ready to help.\n", style="dim")
    welcome_text.append("Type ", style="white")
    welcome_text.append("/help", style="cyan bold")
    welcome_text.append(" to get started.", style="white")
    
    return Panel(
        Align.center(welcome_text),
        title="[bold green]🌟 Welcome[/bold green]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2)
    )
