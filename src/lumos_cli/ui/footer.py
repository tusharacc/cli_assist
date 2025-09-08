"""
Simple Footer system for Lumos CLI
Shows available intents and commands in a dynamic footer
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def show_footer(compact: bool = False):
    """Show the footer with available intents"""
    if compact:
        _show_compact_footer()
    else:
        _show_full_footer()

def _show_compact_footer():
    """Show a compact footer with just the main commands"""
    footer_text = Text()
    
    # Add main command categories
    categories = [
        "[cyan]/code[/cyan]",
        "[green]/github[/green]",
        "[blue]/jenkins[/blue]",
        "[yellow]/jira[/yellow]",
        "[magenta]/neo4j[/magenta]",
        "[red]/appdynamics[/red]",
        "[white]/start[/white]",
        "[white]/sessions[/white]"
    ]
    
    footer_text.append("Available: ")
    footer_text.append(" | ".join(categories))
    footer_text.append(" | Type /help for details")
    
    # Create a simple footer panel
    footer_panel = Panel(
        footer_text,
        title="[bold]Lumos CLI[/bold]",
        border_style="dim",
        padding=(0, 1)
    )
    
    console.print(footer_panel)

def _show_full_footer():
    """Show a full footer with detailed information"""
    console.print("\n[bold]Available Intents & Commands[/bold]")
    console.print("=" * 60)
    
    intents = [
        ("Code Operations", "/code", "Comprehensive code management", "generate, edit, plan, review, fix, test, analyze, refactor, docs, format, validate", "cyan"),
        ("GitHub", "/github", "Repository management", "PRs, commits, cloning, repos", "green"),
        ("Jenkins", "/jenkins", "CI/CD operations", "builds, jobs, status, console", "blue"),
        ("Jira", "/jira", "Project management", "tickets, issues, comments, sprints", "yellow"),
        ("Neo4j", "/neo4j", "Graph database", "dependencies, impact, analysis, queries", "magenta"),
        ("AppDynamics", "/appdynamics", "SRE monitoring", "resources, alerts, transactions, health", "red"),
        ("System", "/start, /sessions, /help", "System operations", "start, sessions, help", "white")
    ]
    
    for category, commands, description, actions, color in intents:
        console.print(f"\n[{color}]{category}[/{color}]:")
        console.print(f"  Commands: {commands}")
        console.print(f"  Description: {description}")
        console.print(f"  Actions: {actions}")

def show_status_footer(status_info: dict = None):
    """Show a status footer with integration status"""
    if not status_info:
        status_info = {
            "Ollama": "🟢",
            "OpenAI": "🟢", 
            "Enterprise LLM": "🟡",
            "GitHub": "🟢",
            "Jenkins": "🟢",
            "Jira": "🟢",
            "Neo4j": "🟡",
            "AppDynamics": "🔴"
        }
    
    # Create status text
    status_text = Text()
    status_text.append("Status: ")
    
    status_items = []
    for service, status in status_info.items():
        status_items.append(f"{service} {status}")
    
    status_text.append(" | ".join(status_items))
    
    # Create footer panel
    footer_panel = Panel(
        status_text,
        title="[bold]Lumos CLI Status[/bold]",
        border_style="dim",
        padding=(0, 1)
    )
    
    console.print(footer_panel)

def show_intent_help(intent_name: str = None):
    """Show intent help"""
    if intent_name:
        console.print(f"\n[bold]{intent_name.upper()} Intent Help[/bold]")
        console.print("Use /help for detailed information about all intents.")
    else:
        _show_full_footer()

def show_quick_reference():
    """Show quick reference"""
    console.print("\n[bold]Quick Reference Card[/bold]")
    console.print("=" * 40)
    
    console.print("\n[bold cyan]Code Operations:[/bold cyan]")
    console.print("  /code - Comprehensive code management")
    console.print("  Actions: generate, edit, plan, review, fix, test, analyze, refactor, docs, format, validate")
    
    console.print("\n[bold green]Services:[/bold green]")
    console.print("  /github - Repository management")
    console.print("  /jenkins - CI/CD operations")
    console.print("  /jira - Project management")
    
    console.print("\n[bold magenta]Data & Monitoring:[/bold magenta]")
    console.print("  /neo4j - Graph database")
    console.print("  /appdynamics - SRE monitoring")
