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
        # Get actual service status (simplified for now, can be enhanced later)
        def get_service_status():
            """Get current service availability status"""
            status_map = {
                # LLM Models
                'ollama': '🟢',      # Assume available if configured
                'openai': '🟢',     # Assume available if API key exists
                'enterprise': '🟡', # Partial - requires config
                
                # Services  
                'github': '🟢',     # Usually available
                'jenkins': '🟡',    # Requires config
                'jira': '🟡',       # Requires config
                'neo4j': '🟡',      # Requires config
                'appdynamics': '🔴' # Requires extensive config
            }
            return status_map
        
        status = get_service_status()
        
        # LLM Models with consistent format: Icon + Name + Status
        llm_line = f"🧠 Ollama {status['ollama']}  🤖 OpenAI/GPT {status['openai']}  🏢 Enterprise LLM {status['enterprise']}"
        
        # Services with consistent format: Icon + Name + Status  
        services_line = f"🐙 GitHub {status['github']}  🔧 Jenkins {status['jenkins']}  🎫 Jira {status['jira']}  📊 Neo4j {status['neo4j']}  📈 AppDynamics {status['appdynamics']}"
        
        status_content = f"\n{llm_line}\n{services_line}"
    
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