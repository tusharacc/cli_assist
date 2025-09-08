"""
Neo4j integration commands for Lumos CLI
"""

import os
import typer
from rich.console import Console
from rich.panel import Panel
from ..clients.neo4j_client import Neo4jClient

console = Console()

def neo4j_config():
    """View Neo4j integration configuration status"""
    console.print("[bold cyan]🔍 Neo4j Configuration Status[/bold cyan]")
    
    # Check if config file exists and load it
    from ..config.neo4j_config import Neo4jConfigManager
    config_manager = Neo4jConfigManager()
    config = config_manager.load_config()
    
    if config and config.uri and config.username:
        console.print(f"[green]✅ Neo4j is configured[/green]")
        console.print(f"[dim]URI: {config.uri}[/dim]")
        console.print(f"[dim]Username: {config.username}[/dim]")
        console.print(f"[dim]Database: {config.database}[/dim]")
        console.print(f"[dim]Password: {'*' * len(config.password)}[/dim]")
        
        # Test connection
        try:
            client = Neo4jClient(config.uri, config.username, config.password)
            if client.test_connection():
                console.print("[green]✅ Neo4j connection successful[/green]")
            else:
                console.print("[red]❌ Neo4j connection failed[/red]")
        except Exception as e:
            console.print(f"[red]❌ Neo4j connection error: {e}[/red]")
    else:
        console.print("[yellow]⚠️  Neo4j not configured[/yellow]")
        console.print("\n[bold]To set up Neo4j integration interactively:[/bold]")
        console.print("   [cyan]lumos-cli neo4j config[/cyan]")
        console.print("\n[bold]Or set manually using environment variables:[/bold]")
        console.print("1. Set connection details:")
        console.print("   [dim]export NEO4J_URI=bolt://localhost:7687[/dim]")
        console.print("   [dim]export NEO4J_USERNAME=neo4j[/dim]")
        console.print("   [dim]export NEO4J_PASSWORD=your_password[/dim]")
        console.print("2. Use the interactive setup for persistent configuration")