"""
GitHub configuration manager for interactive setup
"""

import os
import json
from typing import Optional
from dataclasses import dataclass
from rich.console import Console
from rich.prompt import Prompt

console = Console()

@dataclass
class GitHubConfig:
    """GitHub configuration settings"""
    token: str
    base_url: str = "https://api.github.com"
    username: str = ""

class GitHubConfigManager:
    """Manages GitHub configuration settings"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.expanduser("~/.lumos_github_config.json")
    
    def load_config(self) -> Optional[GitHubConfig]:
        """Load GitHub configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return GitHubConfig(**data)
            return None
        except Exception as e:
            console.print(f"[red]Error loading config: {e}[/red]")
            return None
    
    def save_config(self, config: GitHubConfig) -> bool:
        """Save GitHub configuration to file"""
        try:
            data = {
                'token': config.token,
                'base_url': config.base_url,
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
    
    def setup_interactive(self) -> Optional[GitHubConfig]:
        """Interactive GitHub configuration setup"""
        console.print("🔧 GitHub Configuration Setup", style="bold blue")
        console.print("=" * 40)
        
        console.print("📝 [dim]To get your GitHub token:[/dim]")
        console.print("   1. Go to GitHub → Settings → Developer settings")
        console.print("   2. Click 'Personal access tokens' → 'Tokens (classic)'")
        console.print("   3. Click 'Generate new token (classic)'")
        console.print("   4. Select 'repo' scope for repository access")
        console.print("   5. Copy the generated token")
        console.print()
        
        base_url = Prompt.ask("GitHub API Base URL", default="https://api.github.com")
        username = Prompt.ask("GitHub Username/Email")
        console.print("🔑 [dim]Your input will be hidden for security.[/dim]")
        token = Prompt.ask("Personal Access Token", password=True)
        
        config = GitHubConfig(
            token=token,
            base_url=base_url.rstrip('/'),
            username=username
        )
        
        # Test connection
        from ..clients.github_client import GitHubClient
        client = GitHubClient(token=token, base_url=base_url)
        success = client.test_connection()
        
        if success:
            console.print("✅ GitHub connection successful!")
            if self.save_config(config):
                console.print("✅ Configuration saved successfully")
                return config
            else:
                console.print("❌ Failed to save configuration")
        else:
            console.print("❌ GitHub connection failed. Please check your credentials.")
            
        return None

# Global instance
_github_config_manager = GitHubConfigManager()

def get_github_config() -> Optional[GitHubConfig]:
    """Get configured GitHub settings"""
    return _github_config_manager.load_config()
