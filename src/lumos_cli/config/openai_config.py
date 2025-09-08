"""
OpenAI/GPT configuration management for Lumos CLI
"""

import os
import json
import requests
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass
from rich.console import Console
from rich.prompt import Prompt, Confirm
from ..utils.debug_logger import get_debug_logger

console = Console()
debug_logger = get_debug_logger()

@dataclass
class OpenAIConfig:
    """OpenAI configuration data"""
    api_key: str
    api_url: str = "https://api.openai.com/v1/chat/completions"
    model: str = "gpt-3.5-turbo"
    organization_id: str = ""
    
class OpenAIConfigManager:
    """Manages OpenAI configuration"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_file = config_file or self._get_config_path()
        debug_logger.log_function_call("OpenAIConfigManager.__init__", kwargs={
            "config_file": str(self.config_file)
        })
    
    def _get_config_path(self) -> Path:
        """Get the configuration file path using standardized location"""
        from ..utils.platform_utils import get_config_directory
        config_dir = get_config_directory()
        return config_dir / 'openai_config.json'
    
    def load_config(self) -> Optional[OpenAIConfig]:
        """Load configuration from file"""
        debug_logger.log_function_call("OpenAIConfigManager.load_config")
        
        try:
            if not self.config_file.exists():
                debug_logger.info("OpenAI config file not found")
                debug_logger.log_function_return("OpenAIConfigManager.load_config", "Not found")
                return None
            
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            config = OpenAIConfig(
                api_key=data.get('api_key', ''),
                api_url=data.get('api_url', 'https://api.openai.com/v1/chat/completions'),
                model=data.get('model', 'gpt-3.5-turbo'),
                organization_id=data.get('organization_id', '')
            )
            
            debug_logger.info("OpenAI config loaded successfully")
            debug_logger.log_function_return("OpenAIConfigManager.load_config", "Success")
            return config
        except Exception as e:
            debug_logger.error(f"Failed to load OpenAI config: {e}")
            debug_logger.log_function_return("OpenAIConfigManager.load_config", "Failed")
            return None
    
    def save_config(self, config_data: OpenAIConfig) -> bool:
        """Save configuration to file"""
        debug_logger.log_function_call("OpenAIConfigManager.save_config")
        
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'api_key': config_data.api_key,
                'api_url': config_data.api_url,
                'model': config_data.model,
                'organization_id': config_data.organization_id
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Set secure permissions
            self.config_file.chmod(0o600)
            
            debug_logger.info("OpenAI config saved successfully")
            debug_logger.log_function_return("OpenAIConfigManager.save_config", "Success")
            return True
        except Exception as e:
            debug_logger.error(f"Failed to save OpenAI config: {e}")
            debug_logger.log_function_return("OpenAIConfigManager.save_config", "Failed")
            return False
    
    def is_configured(self) -> bool:
        """Check if OpenAI is configured"""
        config = self.load_config()
        if config and config.api_key:
            return True
        
        # Also check environment variables as fallback
        env_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
        return bool(env_key)
    
    def test_connection(self, config: OpenAIConfig = None) -> bool:
        """Test OpenAI API connection"""
        if not config:
            config = self.load_config()
            if not config:
                # Try environment variables
                api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
                api_url = os.getenv("LLM_API_URL") or "https://api.openai.com/v1/chat/completions"
                if not api_key:
                    return False
                config = OpenAIConfig(api_key=api_key, api_url=api_url)
        
        try:
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            if config.organization_id:
                headers["OpenAI-Organization"] = config.organization_id
            
            # Test with a simple completion request
            test_data = {
                "model": config.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
            
            response = requests.post(config.api_url, headers=headers, json=test_data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            debug_logger.error(f"OpenAI connection test failed: {e}")
            return False
    
    def setup_interactive(self) -> Optional[OpenAIConfig]:
        """Interactive setup for OpenAI configuration"""
        debug_logger.log_function_call("OpenAIConfigManager.setup_interactive")
        
        console.print("\n[bold blue]🤖 OpenAI/GPT Configuration Setup[/bold blue]")
        console.print("=" * 50)
        
        console.print("\n[yellow]This will configure OpenAI/GPT API access for Lumos CLI[/yellow]")
        console.print("[dim]You'll need an OpenAI API key from: https://platform.openai.com/api-keys[/dim]")
        
        # Check current config
        current_config = self.load_config()
        if current_config:
            console.print(f"\n[yellow]Current configuration found:[/yellow]")
            console.print(f"  API URL: {current_config.api_url}")
            console.print(f"  Model: {current_config.model}")
            console.print(f"  API Key: {current_config.api_key[:8]}...{current_config.api_key[-4:] if len(current_config.api_key) > 8 else current_config.api_key}")
            if current_config.organization_id:
                console.print(f"  Organization: {current_config.organization_id}")
            
            if not Confirm.ask("\nDo you want to update the configuration?"):
                return current_config
        
        if not Confirm.ask("\nDo you want to continue with OpenAI configuration?"):
            return None
        
        try:
            # Get API Key
            console.print("\n[bold]1. API Key[/bold]")
            console.print("[dim]Enter your OpenAI API key (starts with sk-)[/dim]")
            console.print("🔑 [dim]Your input will be hidden for security.[/dim]")
            api_key = Prompt.ask("OpenAI API Key", password=True, 
                               default=current_config.api_key if current_config else "")
            
            if not api_key:
                console.print("[red]❌ API Key is required[/red]")
                return None
            
            if not api_key.startswith("sk-"):
                console.print("[yellow]⚠️  Warning: OpenAI API keys usually start with 'sk-'[/yellow]")
            
            # Get API URL
            console.print("\n[bold]2. API URL[/bold]")
            console.print("[dim]OpenAI API endpoint URL[/dim]")
            api_url = Prompt.ask("API URL", 
                               default=current_config.api_url if current_config else "https://api.openai.com/v1/chat/completions")
            
            # Get Model
            console.print("\n[bold]3. Model[/bold]")
            console.print("[dim]OpenAI model to use (gpt-3.5-turbo, gpt-4, etc.)[/dim]")
            model = Prompt.ask("Model", 
                             default=current_config.model if current_config else "gpt-3.5-turbo")
            
            # Get Organization ID (optional)
            console.print("\n[bold]4. Organization ID (Optional)[/bold]")
            console.print("[dim]Leave empty if not using OpenAI organization[/dim]")
            organization_id = Prompt.ask("Organization ID", 
                                       default=current_config.organization_id if current_config else "")
            
            # Create config
            config = OpenAIConfig(
                api_key=api_key,
                api_url=api_url,
                model=model,
                organization_id=organization_id
            )
            
            # Test connection
            console.print(f"\n[bold]Testing OpenAI connection...[/bold]")
            if self.test_connection(config):
                console.print("[green]✅ Connection successful![/green]")
                
                # Save configuration
                if Confirm.ask("\nSave this configuration?"):
                    if self.save_config(config):
                        console.print("[green]✅ Configuration saved successfully![/green]")
                        console.print(f"\n[cyan]Configuration saved to: {self.config_file}[/cyan]")
                        console.print("\n[bold]Usage:[/bold]")
                        console.print("  • OpenAI is now available as an LLM backend")
                        console.print("  • Use 'lumos-cli openai-config' to check status")
                        console.print("  • Set LUMOS_BACKEND=openai to use OpenAI by default")
                        debug_logger.log_function_return("OpenAIConfigManager.setup_interactive", "Success")
                        return config
                    else:
                        console.print("[red]❌ Failed to save configuration[/red]")
                        debug_logger.log_function_return("OpenAIConfigManager.setup_interactive", "Save failed")
                        return None
                else:
                    console.print("[yellow]Configuration not saved[/yellow]")
                    debug_logger.log_function_return("OpenAIConfigManager.setup_interactive", "Not saved")
                    return None
            else:
                console.print("[red]❌ Connection failed. Please check your API key and settings.[/red]")
                console.print("\n[bold]Troubleshooting:[/bold]")
                console.print("  • Verify your API key is correct")
                console.print("  • Check your OpenAI account has credits")
                console.print("  • Ensure the API URL is correct")
                console.print("  • Check your internet connection")
                debug_logger.log_function_return("OpenAIConfigManager.setup_interactive", "Connection failed")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Configuration error: {e}[/red]")
            debug_logger.log_function_return("OpenAIConfigManager.setup_interactive", f"Error: {e}")
            return None