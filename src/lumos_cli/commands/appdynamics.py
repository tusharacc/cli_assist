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

def appdynamics_set_default(application_name: str = None):
    """Set or view the default application for AppDynamics monitoring
    
    Examples:
        lumos-cli appdynamics set-default "SCI Market Place PROD Azure"
        lumos-cli appdynamics set-default  # Show current default
    """
    from ..config.appdynamics_config import AppDynamicsConfigManager
    config_manager = AppDynamicsConfigManager()
    
    if not config_manager.is_configured():
        console.print("[red]❌ AppDynamics not configured. Run 'lumos-cli appdynamics config' first.[/red]")
        return
    
    if application_name:
        # Set default application
        if config_manager.set_default_application(application_name):
            console.print(f"[green]✅ Default application set to: {application_name}[/green]")
        else:
            console.print("[red]❌ Failed to set default application[/red]")
    else:
        # Show current default
        default_app = config_manager.get_default_application()
        if default_app:
            console.print(f"[cyan]Current default application: {default_app}[/cyan]")
        else:
            console.print("[yellow]No default application set[/yellow]")
            console.print("\n[bold]To set a default application:[/bold]")
            console.print("   [cyan]lumos-cli appdynamics set-default \"Application Name\"[/cyan]")

def appdynamics_debug(application_name: str = None, server_id: int = None):
    """Debug AppDynamics metrics to see what's available
    
    Examples:
        lumos-cli appdynamics debug  # Debug default application
        lumos-cli appdynamics debug "SCI Market Place PROD Azure" 12345
    """
    from ..config.appdynamics_config import AppDynamicsConfigManager
    from ..clients.appdynamics_client import AppDynamicsClient
    
    config_manager = AppDynamicsConfigManager()
    
    if not config_manager.is_configured():
        console.print("[red]❌ AppDynamics not configured. Run 'lumos-cli appdynamics config' first.[/red]")
        return
    
    config = config_manager.load_config()
    client = AppDynamicsClient(config.base_url, config.client_id, config.client_secret)
    
    if not client.test_connection():
        console.print("[red]❌ Failed to connect to AppDynamics[/red]")
        return
    
    # Determine application
    if not application_name:
        application_name = config_manager.get_default_application()
        if not application_name:
            console.print("[yellow]No application specified and no default set. Available applications:[/yellow]")
            applications = client.get_applications()
            if applications:
                for i, app in enumerate(applications[:10]):
                    console.print(f"  {i+1}. {app.get('name', 'Unknown')}")
                return
            else:
                console.print("[red]No applications found[/red]")
                return
        else:
            console.print(f"[cyan]Using default application: {application_name}[/cyan]")
    
    # Get application ID
    app_id = client.get_application_id(application_name)
    if not app_id:
        console.print(f"[red]❌ Application '{application_name}' not found[/red]")
        return
    
    console.print(f"[green]✅ Found application ID: {app_id}[/green]")
    
    # Get servers
    servers = client.get_servers(app_id)
    if not servers:
        console.print("[red]❌ No servers found for this application[/red]")
        return
    
    # Use specified server or first available
    if server_id:
        target_server = next((s for s in servers if s.get('id') == server_id), None)
        if not target_server:
            console.print(f"[red]❌ Server ID {server_id} not found[/red]")
            return
    else:
        target_server = servers[0]
        server_id = target_server.get('id')
    
    console.print(f"[cyan]Debugging server: {target_server.get('name', 'Unknown')} (ID: {server_id})[/cyan]")
    
    # Run debug
    client.debug_metrics(app_id, server_id)