"""
Console utilities for Lumos CLI
"""

import os
import platform
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.align import Align
from rich import box
from typing import Optional

# Global console instance
console = Console()

def clear_console():
    """Clear the console screen in a cross-platform way"""
    try:
        # Use Rich's built-in clear method first
        console.clear()
    except Exception:
        # Fallback to system-specific clear commands
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

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
            """Get actual service availability status based on global configuration"""
            import json
            from ..utils.platform_utils import get_config_directory
            
            # First try to load environment variables from .env file
            try:
                from ..config import load_env_file
                load_env_file('.env', debug=False)
            except:
                pass  # Continue without .env file loading
            
            status_map = {}
            config_dir = get_config_directory()  # Standardized: ~/.lumos/.config/
            
            # Check LLM Models
            # Ollama - check if installed and running
            from ..utils.platform_utils import check_ollama_installed
            status_map['ollama'] = '🟢' if check_ollama_installed() else '🔴'
            
            # OpenAI - check for API key (environment variables)
            openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
            status_map['openai'] = '🟢' if openai_key else '🔴'
            
            # Enterprise LLM - check config file
            enterprise_config_file = config_dir / "enterprise_llm_config.json"
            enterprise_configured = False
            if enterprise_config_file.exists():
                try:
                    with open(enterprise_config_file, 'r') as f:
                        config_data = json.load(f)
                        # Check if all required fields are present and non-empty
                        required_fields = ['token_url', 'chat_url', 'app_id', 'app_key', 'app_resource']
                        enterprise_configured = all(config_data.get(field, '').strip() for field in required_fields)
                except:
                    pass
            status_map['enterprise'] = '🟢' if enterprise_configured else '🔴'
            
            # Check Services using standardized config files
            # GitHub - check config file
            github_config_file = config_dir / "github_config.json"
            github_configured = False
            if github_config_file.exists():
                try:
                    with open(github_config_file, 'r') as f:
                        config_data = json.load(f)
                        github_configured = bool(config_data.get('token', '').strip())
                except:
                    pass
            # Fallback to environment variable
            if not github_configured:
                github_configured = bool(os.getenv("GITHUB_TOKEN"))
            status_map['github'] = '🟢' if github_configured else '🟡'
            
            # Jenkins - check config file  
            jenkins_config_file = config_dir / "jenkins_config.json"
            jenkins_configured = False
            if jenkins_config_file.exists():
                try:
                    with open(jenkins_config_file, 'r') as f:
                        config_data = json.load(f)
                        jenkins_configured = bool(config_data.get('url', '').strip() and config_data.get('token', '').strip())
                except:
                    pass
            status_map['jenkins'] = '🟢' if jenkins_configured else '🔴'
            
            # Jira - check config file
            jira_config_file = config_dir / "jira_config.json"
            jira_configured = False
            if jira_config_file.exists():
                try:
                    with open(jira_config_file, 'r') as f:
                        config_data = json.load(f)
                        jira_configured = bool(config_data.get('url', '').strip() and config_data.get('token', '').strip())
                except:
                    pass
            status_map['jira'] = '🟢' if jira_configured else '🔴'
            
            # Neo4j - check config file
            neo4j_config_file = config_dir / "neo4j_config.json"
            neo4j_configured = False
            if neo4j_config_file.exists():
                try:
                    with open(neo4j_config_file, 'r') as f:
                        config_data = json.load(f)
                        neo4j_configured = bool(config_data.get('uri', '').strip() and config_data.get('username', '').strip())
                except:
                    pass
            status_map['neo4j'] = '🟢' if neo4j_configured else '🔴'
            
            # AppDynamics - check config file
            appdynamics_config_file = config_dir / "appdynamics_config.json"
            appdynamics_configured = False
            if appdynamics_config_file.exists():
                try:
                    with open(appdynamics_config_file, 'r') as f:
                        config_data = json.load(f)
                        appdynamics_configured = bool(config_data.get('base_url', '').strip())
                except:
                    pass
            status_map['appdynamics'] = '🟢' if appdynamics_configured else '🔴'
            
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