"""
Configuration Manager for Enterprise LLM Replica
Handles OAuth2 configuration and setup
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from ..utils.debug_logger import debug_logger

console = Console()

@dataclass
class EnterpriseLLMConfigData:
    """Configuration data for Enterprise LLM"""
    token_url: str = ""
    chat_url: str = ""
    app_id: str = ""
    app_key: str = ""
    app_resource: str = ""

class EnterpriseLLMConfigManager:
    """Manages Enterprise LLM configuration"""
    
    def __init__(self):
        self.console = console
        self.config_file = os.path.expanduser("~/.lumos/enterprise_llm_config.json")
        self.config_data = EnterpriseLLMConfigData()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.config_data.token_url = data.get("token_url", "")
                    self.config_data.chat_url = data.get("chat_url", "")
                    self.config_data.app_id = data.get("app_id", "")
                    self.config_data.app_key = data.get("app_key", "")
                    self.config_data.app_resource = data.get("app_resource", "")
                
                debug_logger.log_function_call("EnterpriseLLMConfigManager._load_config", {
                    "config_file": self.config_file,
                    "has_token_url": bool(self.config_data.token_url),
                    "has_chat_url": bool(self.config_data.chat_url),
                    "has_app_id": bool(self.config_data.app_id)
                })
        except Exception as e:
            debug_logger.error(f"Failed to load Enterprise LLM config: {e}")
    
    def save_config(self, config_data: EnterpriseLLMConfigData):
        """Save configuration to file"""
        try:
            # Create config directory if it doesn't exist
            config_dir = os.path.dirname(self.config_file)
            os.makedirs(config_dir, exist_ok=True)
            
            # Save configuration
            config_dict = {
                "token_url": config_data.token_url,
                "chat_url": config_data.chat_url,
                "app_id": config_data.app_id,
                "app_key": config_data.app_key,
                "app_resource": config_data.app_resource
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            # Update local config
            self.config_data = config_data
            
            # Set file permissions to 600 (owner read/write only)
            os.chmod(self.config_file, 0o600)
            
            debug_logger.log_function_call("EnterpriseLLMConfigManager.save_config", {
                "config_file": self.config_file,
                "token_url": config_data.token_url,
                "chat_url": config_data.chat_url,
                "app_id": config_data.app_id
            })
            
            return True
            
        except Exception as e:
            debug_logger.error(f"Failed to save Enterprise LLM config: {e}")
            return False
    
    def load_config(self) -> EnterpriseLLMConfigData:
        """Load configuration"""
        return self.config_data
    
    def is_configured(self) -> bool:
        """Check if Enterprise LLM is configured"""
        return bool(
            self.config_data.token_url and 
            self.config_data.chat_url and 
            self.config_data.app_id and 
            self.config_data.app_key
        )
    
    def setup_interactive(self) -> bool:
        """Interactive setup for Enterprise LLM configuration"""
        self.console.print("\n[bold cyan]🏢 Enterprise LLM Replica Configuration[/bold cyan]")
        self.console.print("=" * 60)
        
        self.console.print("\n[yellow]This will configure the Enterprise LLM Replica to use OAuth2 authentication[/yellow]")
        self.console.print("[dim]You'll need the following information from your enterprise:[/dim]")
        self.console.print("  • Token URL (OAuth2 token endpoint)")
        self.console.print("  • Chat URL (LLM chat API endpoint)")
        self.console.print("  • APP_ID (Client ID)")
        self.console.print("  • APP_KEY (Client Secret)")
        self.console.print("  • APP_RESOURCE (Optional resource identifier)")
        
        if not Confirm.ask("\nDo you want to continue with the configuration?"):
            return False
        
        try:
            # Get Token URL
            self.console.print("\n[bold]1. Token URL[/bold]")
            self.console.print("[dim]Enter the OAuth2 token endpoint URL[/dim]")
            token_url = Prompt.ask("Token URL", default=self.config_data.token_url)
            
            if not token_url:
                self.console.print("[red]❌ Token URL is required[/red]")
                return False
            
            # Get Chat URL
            self.console.print("\n[bold]2. Chat URL[/bold]")
            self.console.print("[dim]Enter the LLM chat API endpoint URL[/dim]")
            chat_url = Prompt.ask("Chat URL", default=self.config_data.chat_url)
            
            if not chat_url:
                self.console.print("[red]❌ Chat URL is required[/red]")
                return False
            
            # Get APP_ID
            self.console.print("\n[bold]3. APP_ID[/bold]")
            self.console.print("[dim]Enter the Client ID (APP_ID)[/dim]")
            app_id = Prompt.ask("APP_ID", default=self.config_data.app_id)
            
            if not app_id:
                self.console.print("[red]❌ APP_ID is required[/red]")
                return False
            
            # Get APP_KEY
            self.console.print("\n[bold]4. APP_KEY[/bold]")
            self.console.print("[dim]Enter the Client Secret (APP_KEY)[/dim]")
            app_key = Prompt.ask("APP_KEY", password=True, default=self.config_data.app_key)
            
            if not app_key:
                self.console.print("[red]❌ APP_KEY is required[/red]")
                return False
            
            # Get APP_RESOURCE (optional)
            self.console.print("\n[bold]5. APP_RESOURCE (Optional)[/bold]")
            self.console.print("[dim]Enter the resource identifier (optional)[/dim]")
            app_resource = Prompt.ask("APP_RESOURCE", default=self.config_data.app_resource)
            
            # Create configuration
            config_data = EnterpriseLLMConfigData(
                token_url=token_url,
                chat_url=chat_url,
                app_id=app_id,
                app_key=app_key,
                app_resource=app_resource
            )
            
            # Save configuration
            if self.save_config(config_data):
                self.console.print("\n[green]✅ Enterprise LLM Replica configured successfully![/green]")
                self.console.print(f"[dim]Configuration saved to: {self.config_file}[/dim]")
                
                # Test connection
                if Confirm.ask("\nDo you want to test the connection?"):
                    self._test_connection()
                
                return True
            else:
                self.console.print("[red]❌ Failed to save configuration[/red]")
                return False
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Configuration cancelled by user[/yellow]")
            return False
        except Exception as e:
            self.console.print(f"[red]❌ Configuration failed: {str(e)}[/red]")
            debug_logger.error(f"Interactive setup failed: {e}")
            return False
    
    def _test_connection(self):
        """Test the Enterprise LLM connection"""
        try:
            from ..enterprise_llm_replica import get_enterprise_llm_replica
            
            self.console.print("\n[cyan]🧪 Testing Enterprise LLM connection...[/cyan]")
            
            enterprise_llm = get_enterprise_llm_replica()
            
            if enterprise_llm.test_connection():
                self.console.print("[green]✅ Enterprise LLM connection successful![/green]")
            else:
                self.console.print("[red]❌ Enterprise LLM connection failed[/red]")
                self.console.print("[yellow]Please check your configuration and try again[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Connection test failed: {str(e)}[/red]")
            debug_logger.error(f"Connection test failed: {e}")
    
    def show_config(self):
        """Show current configuration"""
        self.console.print("\n[bold cyan]🏢 Enterprise LLM Replica Configuration[/bold cyan]")
        self.console.print("=" * 60)
        
        if self.is_configured():
            self.console.print(f"[green]✅ Status: Configured[/green]")
            self.console.print(f"[dim]Token URL: {self.config_data.token_url}[/dim]")
            self.console.print(f"[dim]Chat URL: {self.config_data.chat_url}[/dim]")
            self.console.print(f"[dim]APP_ID: {self.config_data.app_id}[/dim]")
            self.console.print(f"[dim]APP_RESOURCE: {self.config_data.app_resource or 'Not set'}[/dim]")
        else:
            self.console.print("[yellow]⚠️  Status: Not configured[/yellow]")
            self.console.print("[dim]Run 'lumos-cli enterprise-llm config' to configure[/dim]")
    
    def clear_config(self):
        """Clear configuration"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
                self.config_data = EnterpriseLLMConfigData()
                self.console.print("[green]✅ Enterprise LLM configuration cleared[/green]")
            else:
                self.console.print("[yellow]⚠️  No configuration to clear[/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to clear configuration: {str(e)}[/red]")
            debug_logger.error(f"Failed to clear config: {e}")

# Global configuration manager instance
config_manager = EnterpriseLLMConfigManager()

def get_enterprise_llm_config_manager() -> EnterpriseLLMConfigManager:
    """Get the global Enterprise LLM configuration manager"""
    return config_manager
