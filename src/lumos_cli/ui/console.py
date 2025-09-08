"""
Console utilities for Lumos CLI
"""

import os
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
        def get_service_status():
            """Get actual service availability status based on configuration"""
            # First try to load environment variables from .env file
            try:
                from ..config import load_env_file
                load_env_file('.env', debug=False)
            except:
                pass  # Continue without .env file loading
            
            status_map = {}
            
            # Check LLM Models
            # Ollama - check if installed and running
            from ..utils.platform_utils import check_ollama_installed
            status_map['ollama'] = '🟢' if check_ollama_installed() else '🔴'
            
            # OpenAI - check for API key
            openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
            status_map['openai'] = '🟢' if openai_key else '🔴'
            
            # Enterprise LLM - check actual configuration
            try:
                from ..config import config
                enterprise_configured = config.is_enterprise_configured() if hasattr(config, 'is_enterprise_configured') else False
            except:
                # Fallback: check environment variables directly
                required_vars = [
                    'ENTERPRISE_TOKEN_URL', 'ENTERPRISE_CHAT_URL', 'ENTERPRISE_APP_ID',
                    'ENTERPRISE_APP_KEY', 'ENTERPRISE_APP_RESOURCE'
                ]
                enterprise_configured = all(os.getenv(var) for var in required_vars)
            
            status_map['enterprise'] = '🟢' if enterprise_configured else '🔴'
            
            # Check Services (simplified for now, can be enhanced)
            status_map['github'] = '🟢' if os.getenv("GITHUB_TOKEN") else '🟡'
            status_map['jenkins'] = '🟢' if os.getenv("JENKINS_URL") and os.getenv("JENKINS_TOKEN") else '🔴'
            status_map['jira'] = '🟢' if os.getenv("JIRA_URL") and os.getenv("JIRA_TOKEN") else '🔴'
            status_map['neo4j'] = '🟢' if os.getenv("NEO4J_URI") and os.getenv("NEO4J_USER") else '🔴'
            status_map['appdynamics'] = '🟢' if os.getenv("APPDYNAMICS_CONTROLLER_URL") else '🔴'
            
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