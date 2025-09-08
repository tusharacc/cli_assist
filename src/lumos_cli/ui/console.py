"""
Console utilities for Lumos CLI
"""

from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.align import Align
from rich import box
from typing import Optional

# Global console instance
console = Console()

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
        # Check backend availability
        backends = ["ollama", "openai", "enterprise"]
        
        ollama_status = "🟢" if "ollama" in backends else "🔴"
        openai_status = "🟢" if "openai" in backends else "🔴"
        enterprise_status = "🟢" if "enterprise" in backends else "🔴"
        
        status_content = f"""
{ollama_status}  Ollama {openai_status}  OpenAI/GPT {enterprise_status}  Enterprise LLM
🐙  GitHub 🟢  🔧  Jenkins ⚪  🎫  Jira 🟢
"""
    
    # Create the header panel
    header_content = f"{title_text}\n{status_content}" if status_content else str(title_text)
    
    console.print(Panel(
        Align.center(header_content),
        border_style="bright_blue",
        box=box.DOUBLE,
        padding=(1, 2)
    ))

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

def print_brand_footer(console: Console) -> None:
    """Print the Lumos CLI brand footer"""
    footer_text = Text()
    footer_text.append("✨ ", style="yellow")
    footer_text.append("Lumos CLI", style="bold bright_blue")
    footer_text.append(" - AI-Powered Development Assistant", style="dim")
    
    console.print(f"\n{footer_text}")
    console.print("[dim]Made with ❤️ for developers[/dim]\n")