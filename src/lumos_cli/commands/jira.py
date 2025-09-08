"""
JIRA integration commands for Lumos CLI
"""

import os
import typer
from rich.console import Console
from rich.panel import Panel
from ..clients.jira_client import JiraClient

console = Console()

def jira_config():
    """View JIRA integration configuration status"""
    console.print("[bold cyan]🔍 JIRA Configuration Status[/bold cyan]")
    
    # Check if config file exists and load it
    from ..config.jira_config_manager import JiraConfigManager
    config_manager = JiraConfigManager()
    config = config_manager.get_config()
    
    if config and config.get('base_url') and config.get('api_token'):
        console.print(f"[green]✅ JIRA is configured[/green]")
        console.print(f"[dim]Base URL: {config.get('base_url')}[/dim]")
        console.print(f"[dim]Username: {config.get('username')}[/dim]")
        console.print(f"[dim]Token: {config.get('api_token', '')[:8]}...{config.get('api_token', '')[-4:]}[/dim]")
        
        # Test connection
        try:
            jira = JiraClient()
            if jira.test_connection():
                console.print("[green]✅ JIRA connection successful[/green]")
            else:
                console.print("[red]❌ JIRA connection failed[/red]")
        except Exception as e:
            console.print(f"[red]❌ JIRA connection error: {e}[/red]")
    else:
        console.print("[yellow]⚠️  JIRA not configured[/yellow]")
        console.print("\n[bold]To set up JIRA integration interactively:[/bold]")
        console.print("   [cyan]lumos-cli jira config[/cyan]")
        console.print("\n[bold]Or set manually:[/bold]")
        console.print("1. Go to JIRA → Profile → Personal Access Tokens")
        console.print("2. Create an API token")
        console.print("3. Save configuration using the interactive setup")