"""Beautiful UI components for Lumos CLI"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich import box
from typing import Optional

def create_header(console: Console, title: str = "Lumos CLI", subtitle: str = None, show_status: bool = True) -> None:
    """Create a beautiful header panel for Lumos CLI"""
    
    # Main title with gradient effect
    title_text = Text()
    title_text.append("🌟 ", style="bold yellow")
    title_text.append("Lumos", style="bold bright_blue")
    title_text.append(" CLI", style="bold bright_cyan")
    
    if subtitle:
        title_text.append(f"\n{subtitle}", style="dim italic")
    
    # Status indicators if requested
    status_content = ""
    if show_status:
        from .config import config
        from .logger import log_debug
        
        # Check backend availability with logging
        log_debug("UI Header: Checking backend availability")
        backends = config.get_available_backends()
        log_debug(f"UI Header: Available backends: {backends}")
        
        ollama_status = "🟢" if "ollama" in backends else "🔴"
        rest_status = "🟢" if "rest" in backends else "🔴"
        
        log_debug(f"UI Header: Ollama status: {ollama_status}")
        log_debug(f"UI Header: REST status: {rest_status}")
        
        # If REST shows red, log detailed config check
        if rest_status == "🔴":
            log_debug("UI Header: REST API showing as red, checking detailed config...")
            is_configured = config.is_rest_api_configured(debug=True)
            log_debug(f"UI Header: REST API configured result: {is_configured}")
        
        # Create status table
        status_table = Table(show_header=False, show_lines=False, padding=(0, 1), box=None)
        status_table.add_column(style="dim")
        status_table.add_column()
        
        status_table.add_row("🤖", f"Ollama {ollama_status}")
        status_table.add_row("🌐", f"REST API {rest_status}")
        status_table.add_row("📁", f"Repository-aware")
        status_table.add_row("🛡️", f"Safety enabled")
    
    # Create the main header panel
    if show_status:
        # Two-column layout: title + status
        header_content = Columns([
            Align.center(title_text),
            Align.right(status_table)
        ], padding=(0, 2))
    else:
        header_content = Align.center(title_text)
    
    header_panel = Panel(
        header_content,
        style="bright_blue",
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    
    console.print(header_panel)

def create_welcome_panel(console: Console, project_info: dict = None) -> None:
    """Create a welcome panel with project information"""
    
    # Project information
    if project_info:
        project_text = Text()
        project_text.append("📂 ", style="bold")
        project_text.append(f"Project: ", style="bold")
        project_text.append(f"{project_info.get('name', 'Unknown')}", style="bright_green")
        
        if project_info.get('type'):
            project_text.append(f" ({project_info['type']})", style="dim")
        
        if project_info.get('languages'):
            project_text.append(f"\n💻 Languages: ", style="bold")
            project_text.append(", ".join(project_info['languages']), style="bright_yellow")
        
        if project_info.get('frameworks'):
            project_text.append(f"\n🛠️  Frameworks: ", style="bold")
            project_text.append(", ".join(project_info['frameworks']), style="bright_magenta")
    else:
        project_text = Text("🔍 Analyzing repository...", style="dim italic")
    
    welcome_panel = Panel(
        project_text,
        title="[bold bright_cyan]Repository Context[/bold bright_cyan]",
        style="bright_green",
        border_style="green",
        box=box.ROUNDED,
        padding=(0, 1)
    )
    
    console.print(welcome_panel)

def create_command_help_panel(console: Console) -> None:
    """Create a helpful commands panel"""
    
    # Commands table
    commands_table = Table(show_header=False, show_lines=False, padding=(0, 1), box=None)
    commands_table.add_column(style="bright_cyan bold", width=20)
    commands_table.add_column(style="dim")
    
    commands_table.add_row("💬 Chat naturally", "\"add error handling\"")
    commands_table.add_row("✏️  Edit files", "/edit <instruction>")
    commands_table.add_row("📋 Plan features", "/plan <goal>")
    commands_table.add_row("🔍 Review code", "/review <file>")
    commands_table.add_row("🚀 Start apps", "/start [command]")
    commands_table.add_row("🔧 Fix errors", "/fix [error]")
    commands_table.add_row("❓ Get help", "/help")
    commands_table.add_row("🚪 Exit", "exit or Ctrl+C")
    
    help_panel = Panel(
        commands_table,
        title="[bold bright_yellow]💡 Quick Commands[/bold bright_yellow]",
        style="bright_yellow",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(0, 1)
    )
    
    console.print(help_panel)

def create_status_panel(console: Console, status_type: str = "success", message: str = "", details: dict = None) -> None:
    """Create a status panel (success, error, warning, info)"""
    
    styles = {
        "success": {
            "emoji": "✅",
            "color": "bright_green",
            "border": "green",
            "title": "Success"
        },
        "error": {
            "emoji": "❌", 
            "color": "bright_red",
            "border": "red",
            "title": "Error"
        },
        "warning": {
            "emoji": "⚠️",
            "color": "bright_yellow", 
            "border": "yellow",
            "title": "Warning"
        },
        "info": {
            "emoji": "ℹ️",
            "color": "bright_blue",
            "border": "blue", 
            "title": "Info"
        }
    }
    
    style_config = styles.get(status_type, styles["info"])
    
    # Create content
    content = Text()
    content.append(f"{style_config['emoji']} ", style="bold")
    content.append(message, style=f"bold {style_config['color']}")
    
    if details:
        for key, value in details.items():
            content.append(f"\n• {key}: ", style="dim")
            content.append(str(value), style="bright_white")
    
    status_panel = Panel(
        content,
        title=f"[bold {style_config['color']}]{style_config['title']}[/bold {style_config['color']}]",
        style=style_config['color'],
        border_style=style_config['border'],
        box=box.ROUNDED,
        padding=(0, 1)
    )
    
    console.print(status_panel)

def create_progress_panel(console: Console, task: str, progress: float = 0.0, details: str = "") -> None:
    """Create a progress panel with progress bar"""
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    
    # Create progress content
    content = Text()
    content.append("🔄 ", style="bold bright_blue")
    content.append(f"Task: ", style="bold")
    content.append(task, style="bright_cyan")
    
    if details:
        content.append(f"\n{details}", style="dim")
    
    # Add progress bar if progress > 0
    if progress > 0:
        bar_width = 40
        filled = int(progress * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        content.append(f"\n{bar} {progress:.1%}", style="bright_green")
    
    progress_panel = Panel(
        content,
        title="[bold bright_blue]⚡ Processing[/bold bright_blue]",
        style="bright_blue",
        border_style="blue",
        box=box.ROUNDED,
        padding=(0, 1)
    )
    
    console.print(progress_panel)

def create_feature_showcase_panel(console: Console) -> None:
    """Create a panel showcasing Lumos features"""
    
    features_table = Table(show_header=False, show_lines=False, padding=(0, 1), box=None)
    features_table.add_column(style="bold", width=3)
    features_table.add_column(style="bright_cyan", width=25)
    features_table.add_column(style="dim")
    
    features_table.add_row("🧠", "Smart File Discovery", "Find files with natural language")
    features_table.add_row("🔍", "Repository Analysis", "Understands your entire codebase")
    features_table.add_row("🛡️", "Safety First", "Previews, backups & rollbacks")
    features_table.add_row("🚨", "Error Handling", "Intelligent debugging assistance")
    features_table.add_row("💾", "Persistent Memory", "Remembers conversation context")
    features_table.add_row("🎯", "Multi-Language", "Python, JS, Java, Go & more")
    
    showcase_panel = Panel(
        features_table,
        title="[bold bright_magenta]✨ Lumos Features[/bold bright_magenta]",
        style="bright_magenta",
        border_style="magenta", 
        box=box.ROUNDED,
        padding=(0, 1)
    )
    
    console.print(showcase_panel)

def create_error_panel(console: Console, error_type: str, error_message: str, 
                      fixes: list = None, confidence: float = 0.0) -> None:
    """Create a detailed error analysis panel"""
    
    # Error content
    content = Text()
    content.append("🚨 ", style="bold bright_red")
    content.append(f"{error_type}: ", style="bold bright_red")
    content.append(error_message, style="bright_white")
    
    # Confidence indicator
    if confidence > 0:
        confidence_color = "bright_green" if confidence > 0.8 else "bright_yellow" if confidence > 0.5 else "bright_red"
        content.append(f"\n🎯 Confidence: ", style="bold")
        content.append(f"{confidence:.0%}", style=f"bold {confidence_color}")
    
    # Suggested fixes
    if fixes:
        content.append(f"\n\n💡 Suggested Fixes:", style="bold bright_yellow")
        for i, fix in enumerate(fixes[:5], 1):
            content.append(f"\n  {i}. {fix}", style="bright_white")
    
    error_panel = Panel(
        content,
        title="[bold bright_red]🔥 Error Analysis[/bold bright_red]",
        style="bright_red",
        border_style="red",
        box=box.HEAVY,
        padding=(1, 2)
    )
    
    console.print(error_panel)

def create_config_panel(console: Console, config_data: dict) -> None:
    """Create a configuration display panel"""
    
    # Create configuration table
    config_table = Table(show_header=True, header_style="bold bright_cyan", box=box.SIMPLE)
    config_table.add_column("Component", style="bold")
    config_table.add_column("Status", justify="center", width=12)
    config_table.add_column("Details", style="dim")
    
    # Add configuration rows
    for component, info in config_data.items():
        status = info.get('status', 'unknown')
        details = info.get('details', '')
        
        # Status emoji and color
        if status == 'available' or status == 'configured':
            status_display = "[bright_green]✅ Ready[/bright_green]"
        elif status == 'partial':
            status_display = "[bright_yellow]⚠️ Partial[/bright_yellow]"
        else:
            status_display = "[bright_red]❌ Missing[/bright_red]"
        
        config_table.add_row(component, status_display, details)
    
    config_panel = Panel(
        config_table,
        title="[bold bright_blue]⚙️ Configuration Status[/bold bright_blue]",
        style="bright_blue",
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    
    console.print(config_panel)

def print_separator(console: Console, style: str = "dim") -> None:
    """Print a separator line"""
    console.print("─" * console.width, style=style)

def print_brand_footer(console: Console) -> None:
    """Print Lumos branding footer"""
    footer_text = Text()
    footer_text.append("✨ Powered by ", style="dim")
    footer_text.append("Lumos CLI", style="bold bright_blue")
    footer_text.append(" - Illuminate your code with AI", style="dim italic")
    
    console.print(Align.center(footer_text))