"""
Enterprise LLM integration commands for Lumos CLI
"""

import os
import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

def enterprise_llm_config():
    """View Enterprise LLM integration configuration status"""
    console.print("[bold cyan]🔍 Enterprise LLM Configuration Status[/bold cyan]")
    
    # Check if config file exists and load it
    from ..config.enterprise_llm_config import EnterpriseLLMConfigManager
    config_manager = EnterpriseLLMConfigManager()
    config = config_manager.load_config()
    
    if config and config.token_url and config.chat_url and config.app_id:
        console.print(f"[green]✅ Enterprise LLM is configured[/green]")
        console.print(f"[dim]Token URL: {config.token_url}[/dim]")
        console.print(f"[dim]Chat URL: {config.chat_url}[/dim]")
        console.print(f"[dim]APP_ID: {config.app_id}[/dim]")
        console.print(f"[dim]APP_KEY: {config.app_key[:8]}...{config.app_key[-4:] if len(config.app_key) > 8 else config.app_key}[/dim]")
        if config.app_resource:
            console.print(f"[dim]APP_RESOURCE: {config.app_resource}[/dim]")
        
        # Test connection if possible
        try:
            from ..enterprise_llm_replica import EnterpriseLLMReplica
            enterprise_llm = EnterpriseLLMReplica()
            if hasattr(enterprise_llm, 'test_connection') and enterprise_llm.test_connection():
                console.print("[green]✅ Enterprise LLM connection successful[/green]")
            else:
                console.print("[yellow]⚠️  Enterprise LLM connection test unavailable or failed[/yellow]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Enterprise LLM connection test error: {str(e)[:100]}...[/yellow]")
    else:
        console.print("[yellow]⚠️  Enterprise LLM not configured[/yellow]")
        console.print("\n[bold]To set up Enterprise LLM integration interactively:[/bold]")
        console.print("   [cyan]lumos-cli enterprise-llm config[/cyan]")
        console.print("\n[bold]Required OAuth2 configuration:[/bold]")
        console.print("1. Token URL - OAuth2 token endpoint")
        console.print("2. Chat URL - LLM chat API endpoint") 
        console.print("3. APP_ID - Client ID from your enterprise")
        console.print("4. APP_KEY - Client Secret from your enterprise")
        console.print("5. APP_RESOURCE - Optional resource identifier")
        console.print("\n[bold]Manual environment setup (alternative):[/bold]")
        console.print("   [dim]export ENTERPRISE_TOKEN_URL=https://your-auth.com/oauth/token[/dim]")
        console.print("   [dim]export ENTERPRISE_CHAT_URL=https://your-llm.com/chat[/dim]")
        console.print("   [dim]export ENTERPRISE_APP_ID=your_app_id[/dim]")
        console.print("   [dim]export ENTERPRISE_APP_KEY=your_app_key[/dim]")