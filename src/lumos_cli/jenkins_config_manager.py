"""
Jenkins configuration manager for interactive setup
"""

import os
import json
from typing import Optional
from dataclasses import dataclass
from rich.console import Console
from rich.prompt import Prompt

console = Console()

@dataclass
class JenkinsConfig:
    """Jenkins configuration settings"""
    url: str
    token: str
    username: str = "api"

class JenkinsConfigManager:
    """Manages Jenkins configuration settings"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.expanduser("~/.lumos_jenkins_config.json")
    
    def load_config(self) -> Optional[JenkinsConfig]:
        """Load Jenkins configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return JenkinsConfig(**data)
            return None
        except Exception as e:
            console.print(f"[red]Error loading config: {e}[/red]")
            return None
    
    def save_config(self, config: JenkinsConfig) -> bool:
        """Save Jenkins configuration to file"""
        try:
            data = {
                'url': config.url,
                'token': config.token,
                'username': config.username
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Set secure permissions
            os.chmod(self.config_file, 0o600)
            return True
            
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
            return False
    
    def setup_interactive(self) -> Optional[JenkinsConfig]:
        """Interactive Jenkins configuration setup"""
        console.print("🔧 Jenkins Configuration Setup", style="bold blue")
        console.print("=" * 40)
        
        console.print("📝 [dim]To get your Jenkins API token:[/dim]")
        console.print("   1. Go to Jenkins → User → Configure")
        console.print("   2. Click 'Add new Token' in the API Token section")
        console.print("   3. Give it a name and click 'Generate'")
        console.print("   4. Copy the token (you won't see it again)")
        console.print()
        
        url = Prompt.ask("Jenkins Base URL (e.g., https://jenkins.company.com)")
        username = Prompt.ask("Jenkins Username", default="api")
        console.print("🔑 [dim]Your input will be hidden for security.[/dim]")
        token = Prompt.ask("API Token", password=True)
        
        config = JenkinsConfig(
            url=url.rstrip('/'),
            token=token,
            username=username
        )
        
        # Test connection
        from .jenkins_client import JenkinsClient
        client = JenkinsClient(base_url=url, token=token, username=username)
        success = client.test_connection()
        
        if success:
            console.print("✅ Jenkins connection successful!")
            if self.save_config(config):
                console.print("✅ Configuration saved successfully")
                return config
            else:
                console.print("❌ Failed to save configuration")
        else:
            console.print("❌ Jenkins connection failed. Please check your credentials.")
            
        return None

# Global instance
_jenkins_config_manager = JenkinsConfigManager()

def get_jenkins_config() -> Optional[JenkinsConfig]:
    """Get configured Jenkins settings"""
    return _jenkins_config_manager.load_config()
