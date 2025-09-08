"""
AppDynamics integration commands for Lumos CLI
"""

import os
import typer
from rich.console import Console
from rich.panel import Panel
from ..clients.appdynamics_client import AppDynamicsClient

console = Console()

def appdynamics_config():
    """View AppDynamics integration configuration status"""
    console.print("[bold cyan]🔍 AppDynamics Configuration Status[/bold cyan]")
    
    # Check if config file exists and load it
    from ..config.appdynamics_config import AppDynamicsConfigManager
    config_manager = AppDynamicsConfigManager()
    config = config_manager.load_config()
    
    if config and config.base_url and config.client_id:
        console.print(f"[green]✅ AppDynamics is configured[/green]")
        console.print(f"[dim]Instance: {config.instance_name}[/dim]")
        console.print(f"[dim]Base URL: {config.base_url}[/dim]")
        console.print(f"[dim]Client ID: {config.client_id}[/dim]")
        console.print(f"[dim]Client Secret: {config.client_secret[:8]}...{config.client_secret[-4:]}[/dim]")
        if config.projects:
            console.print(f"[dim]Projects: {', '.join(config.projects)}[/dim]")
        else:
            console.print(f"[dim]Projects: None configured[/dim]")
        
        # Test connection
        try:
            client = AppDynamicsClient(config.base_url, config.client_id, config.client_secret)
            if client.test_connection():
                console.print("[green]✅ AppDynamics connection successful[/green]")
            else:
                console.print("[red]❌ AppDynamics connection failed[/red]")
        except Exception as e:
            console.print(f"[red]❌ AppDynamics connection error: {e}[/red]")
    else:
        console.print("[yellow]⚠️  AppDynamics not configured[/yellow]")
        console.print("\n[bold]To set up AppDynamics integration interactively:[/bold]")
        console.print("   [cyan]lumos-cli appdynamics config[/cyan]")
        console.print("\n[bold]Or set manually using environment variables:[/bold]")
        console.print("1. Set connection details:")
        console.print("   [dim]export APPDYNAMICS_BASE_URL=https://your-controller.saas.appdynamics.com[/dim]")
        console.print("   [dim]export APPDYNAMICS_CLIENT_ID=your_client_id[/dim]")
        console.print("   [dim]export APPDYNAMICS_CLIENT_SECRET=your_client_secret[/dim]")
        console.print("2. Use the interactive setup for persistent configuration")