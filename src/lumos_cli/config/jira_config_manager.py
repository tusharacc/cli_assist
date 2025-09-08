#!/usr/bin/env python3
"""
Jira configuration manager
"""

import json
import os
import requests
from typing import Dict, Optional
from rich.console import Console
from rich.prompt import Prompt
from ..utils.debug_logger import debug_logger
from ..utils.platform_utils import get_config_directory

console = Console()

class JiraConfigManager:
    """Manages Jira configuration"""
    
    def __init__(self):
        self.config_file = os.path.join(get_config_directory(), "jira_config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load Jira configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                debug_logger.warning(f"Failed to load Jira config: {e}")
        return {}
    
    def save_config(self, config: Dict):
        """Save Jira configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            os.chmod(self.config_file, 0o600)  # Secure permissions
            debug_logger.info("Jira configuration saved")
        except Exception as e:
            debug_logger.error(f"Failed to save Jira config: {e}")
    
    def load_config(self) -> Dict:
        """Load Jira configuration from file (public method)"""
        return self._load_config()
    
    def get_config(self) -> Dict:
        """Get current Jira configuration"""
        return self.config
    
    def is_configured(self) -> bool:
        """Check if Jira is configured"""
        return bool(self.config.get('base_url') and self.config.get('api_token'))
    
    def setup_interactive(self) -> Optional[Dict]:
        """Interactive Jira configuration setup"""
        console.print("🔧 Jira Configuration Setup", style="bold blue")
        console.print("=" * 40)
        
        console.print("📝 [dim]To get your Jira Personal Access Token:[/dim]")
        console.print("   1. Go to Jira → Profile → Personal Access Tokens")
        console.print("   2. Click 'Create API token'")
        console.print("   3. Give it a label and copy the generated token")
        console.print("   4. This will be used as a Bearer token for authentication")
        console.print()
        
        base_url = Prompt.ask("Jira Base URL", default="https://your-company.atlassian.net")
        username = Prompt.ask("Jira Username/Email")
        console.print("🔑 [dim]Your input will be hidden for security.[/dim]")
        api_token = Prompt.ask("Personal Access Token", password=True)
        
        config = {
            'base_url': base_url.rstrip('/'),
            'username': username,
            'api_token': api_token
        }
        
        # Test connection
        try:
            console.print("🔍 Testing Jira connection...")
            
            # Test the connection with a real API call
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {api_token}'
            }
            response = requests.get(f"{base_url}/rest/api/latest/myself", headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Check if response is actually JSON
                content_type = response.headers.get('content-type', '').lower()
                if 'application/json' not in content_type:
                    console.print(f"❌ Jira connection failed: Server returned HTML instead of JSON")
                    console.print(f"   Content-Type: {content_type}")
                    console.print(f"   Response preview: {response.text[:200]}...")
                    console.print("   This usually indicates API version incompatibility or authentication issues")
                    return None
                
                try:
                    # Try to parse JSON to ensure it's valid
                    data = response.json()
                    # Save the config only if connection is successful
                    self.save_config(config)
                    
                    console.print("✅ Jira configured successfully!")
                    console.print(f"   Base URL: {base_url}")
                    console.print(f"   Username: {username}")
                    
                    return config
                except ValueError as e:
                    console.print(f"❌ Jira connection failed: Invalid JSON response")
                    console.print(f"   Error: {e}")
                    console.print(f"   Response content: {response.text[:200]}...")
                    return None
            else:
                console.print(f"❌ Jira connection failed: HTTP {response.status_code}")
                console.print(f"   Response: {response.text[:200]}...")
                return None
                
        except requests.exceptions.RequestException as e:
            console.print(f"❌ Jira connection failed: {e}")
            return None
        except Exception as e:
            console.print(f"❌ Unexpected error: {e}")
            return None

def get_jira_config_manager() -> JiraConfigManager:
    """Get Jira configuration manager instance"""
    return JiraConfigManager()
