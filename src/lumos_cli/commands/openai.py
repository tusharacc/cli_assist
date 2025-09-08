"""
OpenAI/GPT integration commands for Lumos CLI
"""

import os
import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

def openai_config():
    """View OpenAI/GPT integration configuration status"""
    console.print("[bold cyan]🔍 OpenAI/GPT Configuration Status[/bold cyan]")
    
    # Check if config file exists and load it
    from ..config.openai_config import OpenAIConfigManager
    config_manager = OpenAIConfigManager()
    config = config_manager.load_config()
    
    # Also check environment variables
    env_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    env_url = os.getenv("LLM_API_URL")
    
    configured_via_file = config and config.api_key
    configured_via_env = bool(env_key)
    
    if configured_via_file or configured_via_env:
        console.print(f"[green]✅ OpenAI/GPT is configured[/green]")
        
        if configured_via_file:
            console.print(f"\n[bold]📁 File Configuration:[/bold]")
            console.print(f"[dim]API URL: {config.api_url}[/dim]")
            console.print(f"[dim]Model: {config.model}[/dim]")
            console.print(f"[dim]API Key: {config.api_key[:8]}...{config.api_key[-4:] if len(config.api_key) > 8 else config.api_key}[/dim]")
            if config.organization_id:
                console.print(f"[dim]Organization: {config.organization_id}[/dim]")
        
        if configured_via_env:
            console.print(f"\n[bold]🌍 Environment Variables:[/bold]")
            console.print(f"[dim]OPENAI_API_KEY: {env_key[:8]}...{env_key[-4:] if len(env_key) > 8 else env_key}[/dim]")
            if env_url:
                console.print(f"[dim]LLM_API_URL: {env_url}[/dim]")
        
        if configured_via_file and configured_via_env:
            console.print(f"\n[yellow]⚠️  Both file and environment configuration found.[/yellow]")
            console.print(f"[yellow]   File configuration takes precedence.[/yellow]")
        
        # Test connection
        console.print(f"\n[bold]🔗 Connection Test:[/bold]")
        try:
            if config_manager.test_connection(config):
                console.print("[green]✅ OpenAI API connection successful[/green]")
            else:
                console.print("[red]❌ OpenAI API connection failed[/red]")
                console.print("[yellow]   Check your API key and credits[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ OpenAI connection error: {str(e)[:100]}...[/red]")
    else:
        console.print("[yellow]⚠️  OpenAI/GPT not configured[/yellow]")
        console.print("\n[bold]To set up OpenAI/GPT integration interactively:[/bold]")
        console.print("   [cyan]lumos-cli openai config[/cyan]")
        console.print("\n[bold]Required for OpenAI API access:[/bold]")
        console.print("1. OpenAI API Key - Get from https://platform.openai.com/api-keys")
        console.print("2. API URL - Usually https://api.openai.com/v1/chat/completions")
        console.print("3. Model - e.g., gpt-3.5-turbo, gpt-4, gpt-4-turbo")
        console.print("4. Organization ID - Optional, for organization accounts")
        console.print("\n[bold]Quick environment setup (alternative):[/bold]")
        console.print("   [dim]export OPENAI_API_KEY=sk-your-key-here[/dim]")
        console.print("   [dim]export LLM_API_URL=https://api.openai.com/v1/chat/completions[/dim]")
        console.print("\n[bold]Usage after setup:[/bold]")
        console.print("   [dim]lumos-cli chat \"Hello\"  # Uses auto backend selection[/dim]")
        console.print("   [dim]LUMOS_BACKEND=openai lumos-cli chat \"Hello\"  # Force OpenAI[/dim]")