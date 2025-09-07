#!/usr/bin/env python3
"""
Test file for AppDynamics connection with OAuth2 authentication
Allows passing all configuration parameters directly for testing
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.appdynamics_client import AppDynamicsClient
from lumos_cli.appdynamics_config import AppDynamicsConfig, AppDynamicsConfigManager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def test_appdynamics_connection(
    base_url: str,
    client_id: str, 
    client_secret: str,
    instance_name: str = "Test",
    projects: list = None
):
    """
    Test AppDynamics connection with provided credentials
    
    Args:
        base_url: AppDynamics controller URL
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        instance_name: Instance name for identification
        projects: List of projects to monitor
    """
    if projects is None:
        projects = []
    
    console.print(Panel.fit(
        f"[bold blue]🔧 AppDynamics Connection Test[/bold blue]\n"
        f"Instance: {instance_name}\n"
        f"URL: {base_url}\n"
        f"Client ID: {client_id}\n"
        f"Projects: {', '.join(projects) if projects else 'None'}",
        title="Configuration"
    ))
    
    # Create AppDynamics client
    console.print("\n[bold]Creating AppDynamics client...[/bold]")
    client = AppDynamicsClient(base_url, client_id, client_secret)
    
    # Test connection
    console.print("[bold]Testing OAuth2 authentication...[/bold]")
    if client.test_connection():
        console.print("[green]✅ Connection successful![/green]")
        
        # Get applications
        console.print("\n[bold]Fetching applications...[/bold]")
        applications = client.get_applications()
        
        if applications:
            console.print(f"[green]✅ Found {len(applications)} applications[/green]")
            
            # Display applications in a table
            table = Table(title="Available Applications")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Description", style="dim")
            
            for app in applications[:10]:  # Show first 10
                table.add_row(
                    str(app.get('id', 'N/A')),
                    app.get('name', 'Unknown'),
                    app.get('description', 'No description')[:50] + "..." if len(app.get('description', '')) > 50 else app.get('description', 'No description')
                )
            
            if len(applications) > 10:
                table.add_row("...", f"... and {len(applications) - 10} more", "")
            
            console.print(table)
            
            # Test specific project if provided
            if projects:
                console.print(f"\n[bold]Testing specific projects: {', '.join(projects)}[/bold]")
                for project in projects:
                    app_id = client.get_application_id(project)
                    if app_id:
                        console.print(f"[green]✅ Found project '{project}' with ID: {app_id}[/green]")
                        
                        # Get servers for this project
                        servers = client.get_servers(app_id)
                        if servers:
                            console.print(f"  📊 Found {len(servers)} servers")
                        else:
                            console.print("  ⚠️ No servers found")
                    else:
                        console.print(f"[red]❌ Project '{project}' not found[/red]")
        else:
            console.print("[yellow]⚠️ No applications found[/yellow]")
        
        return True
    else:
        console.print("[red]❌ Connection failed![/red]")
        console.print("Please check:")
        console.print("  • Controller URL is correct")
        console.print("  • Client ID and Client Secret are valid")
        console.print("  • OAuth2 credentials have proper permissions")
        console.print("  • Network connectivity to AppDynamics")
        return False

def test_with_environment_variables():
    """Test using environment variables"""
    console.print(Panel.fit(
        "[bold blue]🔧 Testing with Environment Variables[/bold blue]\n"
        "Using APPDYNAMICS_BASE_URL, APPDYNAMICS_CLIENT_ID, APPDYNAMICS_CLIENT_SECRET",
        title="Environment Test"
    ))
    
    base_url = os.getenv('APPDYNAMICS_BASE_URL')
    client_id = os.getenv('APPDYNAMICS_CLIENT_ID')
    client_secret = os.getenv('APPDYNAMICS_CLIENT_SECRET')
    
    if not all([base_url, client_id, client_secret]):
        console.print("[red]❌ Missing environment variables[/red]")
        console.print("Please set:")
        console.print("  export APPDYNAMICS_BASE_URL='https://your-controller.saas.appdynamics.com'")
        console.print("  export APPDYNAMICS_CLIENT_ID='your_client_id'")
        console.print("  export APPDYNAMICS_CLIENT_SECRET='your_client_secret'")
        return False
    
    return test_appdynamics_connection(base_url, client_id, client_secret)

def test_with_config_file():
    """Test using saved configuration file"""
    console.print(Panel.fit(
        "[bold blue]🔧 Testing with Configuration File[/bold blue]\n"
        "Using saved AppDynamics configuration",
        title="Config File Test"
    ))
    
    config_manager = AppDynamicsConfigManager()
    config = config_manager.load_config()
    
    if not config:
        console.print("[red]❌ No configuration file found[/red]")
        console.print("Run 'lumos-cli appdynamics config' to create configuration")
        return False
    
    return test_appdynamics_connection(
        config.base_url,
        config.client_id,
        config.client_secret,
        config.instance_name,
        config.projects
    )

def main():
    """Main test function with example configurations"""
    console.print(Panel.fit(
        "[bold green]🚀 AppDynamics Connection Test Suite[/bold green]\n"
        "Test AppDynamics OAuth2 authentication and SSL verification",
        title="Test Suite"
    ))
    
    # Example 1: Direct configuration
    console.print("\n" + "="*60)
    console.print("[bold]Example 1: Direct Configuration[/bold]")
    console.print("="*60)
    
    # Replace these with your actual AppDynamics credentials
    test_config = {
        "base_url": "https://chubbinaholdingsinc-prod.saas.appdynamics.com",
        "client_id": "sci_mp_read",
        "client_secret": "your_client_secret_here",
        "instance_name": "Production",
        "projects": ["SCI Markpet Place PROD Azure", "SCI Market Place PROD"]
    }
    
    console.print("[yellow]⚠️ Update the credentials in this file before testing[/yellow]")
    console.print(f"Current config: {test_config['base_url']} with client_id: {test_config['client_id']}")
    
    # Uncomment the line below to test with your credentials
    # test_appdynamics_connection(**test_config)
    
    # Example 2: Environment variables
    console.print("\n" + "="*60)
    console.print("[bold]Example 2: Environment Variables[/bold]")
    console.print("="*60)
    test_with_environment_variables()
    
    # Example 3: Configuration file
    console.print("\n" + "="*60)
    console.print("[bold]Example 3: Configuration File[/bold]")
    console.print("="*60)
    test_with_config_file()
    
    console.print("\n" + "="*60)
    console.print("[bold green]✅ Test suite completed![/bold green]")
    console.print("="*60)

if __name__ == "__main__":
    main()
