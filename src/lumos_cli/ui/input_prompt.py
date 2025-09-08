"""
Enhanced input prompt with intent shortcuts display
Similar to Claude CLI's "? for help" but showing available intents
"""

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich import box
from typing import Optional

console = Console()

def show_intent_shortcuts(compact: bool = True) -> None:
    """Display available intent shortcuts below the input prompt"""
    if compact:
        _show_compact_shortcuts()
    else:
        _show_detailed_shortcuts()

def _show_compact_shortcuts() -> None:
    """Show compact intent shortcuts (single line)"""
    shortcuts_text = Text()
    
    # Main intent shortcuts with colors
    intents = [
        ("/code", "cyan"),
        ("/github", "green"), 
        ("/jenkins", "blue"),
        ("/jira", "yellow"),
        ("/neo4j", "magenta"),
        ("/appdynamics", "red")
    ]
    
    shortcuts_text.append("Available: ")
    
    intent_parts = []
    for intent, color in intents:
        intent_parts.append(f"[{color}]{intent}[/{color}]")
    
    shortcuts_text.append(" | ".join(intent_parts))
    shortcuts_text.append(" | [dim]/help for details[/dim]")
    
    console.print(shortcuts_text)

def _show_detailed_shortcuts() -> None:
    """Show detailed intent shortcuts with descriptions"""
    console.print("\n[bold]Available Intents:[/bold]")
    
    intents = [
        ("/code", "Code operations (generate, edit, review, test)", "cyan"),
        ("/github", "Repository management (PRs, commits, clone)", "green"),
        ("/jenkins", "CI/CD operations (builds, jobs, status)", "blue"), 
        ("/jira", "Project management (tickets, issues)", "yellow"),
        ("/neo4j", "Graph database (dependencies, impact)", "magenta"),
        ("/appdynamics", "Monitoring (resources, alerts)", "red")
    ]
    
    for intent, description, color in intents:
        console.print(f"  [{color}]{intent:12}[/{color}] - {description}")
    
    console.print("  [dim]/help       - Show detailed help[/dim]")
    console.print("  [dim]/exit       - Exit Lumos CLI[/dim]\n")

def get_user_input_with_shortcuts(prompt: str = "🤖 You", show_shortcuts: bool = True) -> str:
    """
    Get user input with intent shortcuts displayed below
    
    Args:
        prompt: Input prompt text
        show_shortcuts: Whether to show intent shortcuts
    
    Returns:
        User input string
    """
    if show_shortcuts:
        _show_compact_shortcuts()
    
    try:
        user_input = input(f"{prompt}: ").strip()
        return user_input
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Use /exit to quit properly[/yellow]")
        return ""

def show_intent_hint() -> None:
    """Show a Claude CLI style hint line"""
    hint_text = Text()
    hint_text.append("/code /github /jenkins /jira /neo4j /appdynamics for intents", style="dim")
    console.print(hint_text)

def create_input_panel_with_shortcuts() -> None:
    """Create a visual input panel with shortcuts (alternative approach)"""
    content = Text()
    content.append("Enter your command or question:\n\n", style="bold white")
    
    # Add shortcuts
    shortcuts = [
        ("/code", "Code operations", "cyan"),
        ("/github", "GitHub", "green"),
        ("/jenkins", "Jenkins", "blue"),
        ("/jira", "Jira", "yellow"),
        ("/neo4j", "Neo4j", "magenta"),
        ("/appdynamics", "AppDynamics", "red")
    ]
    
    content.append("Quick shortcuts: ")
    shortcut_parts = []
    for shortcut, desc, color in shortcuts:
        shortcut_parts.append(f"[{color}]{shortcut}[/{color}]")
    
    content.append(" | ".join(shortcut_parts))
    content.append("\nType [dim]/help[/dim] for detailed information")
    
    panel = Panel(
        content,
        title="[bold bright_blue]Lumos CLI Input[/bold bright_blue]",
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    
    console.print(panel)

def display_claude_style_prompt() -> str:
    """
    Display a Claude CLI style input with shortcuts hint below
    This is the main function to replace the simple input() call
    """
    # Show the shortcuts hint first
    show_intent_hint()
    
    # Get input
    try:
        user_input = input("🤖 You: ").strip()
        return user_input
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Use /exit to quit properly[/yellow]")
        return ""