"""
AppDynamics configuration management
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass
from rich.console import Console
from rich.prompt import Prompt, Confirm
from .debug_logger import get_debug_logger
from .appdynamics_client import AppDynamicsClient

console = Console()
debug_logger = get_debug_logger()

@dataclass
class AppDynamicsConfig:
    """AppDynamics configuration data"""
    base_url: str
    username: str
    password: str
    instance_name: str
    projects: list  # List of project names to monitor

class AppDynamicsConfigManager:
    """Manages AppDynamics configuration"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_file = config_file or self._get_config_path()
        debug_logger.log_function_call("AppDynamicsConfigManager.__init__", kwargs={
            "config_file": str(self.config_file)
        })
    
    def _get_config_path(self) -> Path:
        """Get the configuration file path"""
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / 'lumos' / 'appdynamics'
        else:  # macOS/Linux
            config_dir = Path.home() / '.config' / 'lumos' / 'appdynamics'
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'config.json'
    
    def load_config(self) -> Optional[AppDynamicsConfig]:
        """Load configuration from file"""
        debug_logger.log_function_call("AppDynamicsConfigManager.load_config")
        
        try:
            if not self.config_file.exists():
                debug_logger.info("AppDynamics config file not found")
                debug_logger.log_function_return("AppDynamicsConfigManager.load_config", "Not found")
                return None
            
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            config = AppDynamicsConfig(
                base_url=data.get('base_url', ''),
                username=data.get('username', ''),
                password=data.get('password', ''),
                instance_name=data.get('instance_name', ''),
                projects=data.get('projects', [])
            )
            
            debug_logger.info("AppDynamics config loaded successfully")
            debug_logger.log_function_return("AppDynamicsConfigManager.load_config", "Success")
            return config
        except Exception as e:
            debug_logger.error(f"Failed to load AppDynamics config: {e}")
            debug_logger.log_function_return("AppDynamicsConfigManager.load_config", "Failed")
            return None
    
    def save_config(self, config_data: AppDynamicsConfig) -> bool:
        """Save configuration to file"""
        debug_logger.log_function_call("AppDynamicsConfigManager.save_config")
        
        try:
            data = {
                'base_url': config_data.base_url,
                'username': config_data.username,
                'password': config_data.password,
                'instance_name': config_data.instance_name,
                'projects': config_data.projects
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Set secure permissions
            self.config_file.chmod(0o600)
            
            debug_logger.info("AppDynamics config saved successfully")
            debug_logger.log_function_return("AppDynamicsConfigManager.save_config", "Success")
            return True
        except Exception as e:
            debug_logger.error(f"Failed to save AppDynamics config: {e}")
            debug_logger.log_function_return("AppDynamicsConfigManager.save_config", "Failed")
            return False
    
    def is_configured(self) -> bool:
        """Check if AppDynamics is configured"""
        config = self.load_config()
        return config is not None and bool(config.base_url and config.username and config.password)
    
    def setup_interactive(self) -> Optional[AppDynamicsConfig]:
        """Interactive setup for AppDynamics configuration"""
        debug_logger.log_function_call("AppDynamicsConfigManager.setup_interactive")
        
        console.print("\n[bold blue]🔧 AppDynamics Configuration Setup[/bold blue]")
        console.print("=" * 50)
        
        # Get instance information
        console.print("\n[bold]Instance Configuration:[/bold]")
        instance_name = Prompt.ask("Instance name (e.g., 'Production', 'Staging')", default="Production")
        
        base_url = Prompt.ask("AppDynamics Controller URL", default="https://your-controller.saas.appdynamics.com")
        if not base_url.startswith(('http://', 'https://')):
            base_url = f"https://{base_url}"
        
        username = Prompt.ask("Username")
        password = Prompt.ask("Password", password=True)
        
        # Get projects to monitor
        console.print("\n[bold]Projects to Monitor:[/bold]")
        console.print("Enter the names of projects you want to monitor (comma-separated)")
        projects_input = Prompt.ask("Project names", default="")
        projects = [p.strip() for p in projects_input.split(',') if p.strip()]
        
        if not projects:
            console.print("[yellow]No projects specified. You can add them later.[/yellow]")
            projects = []
        
        # Create config
        config = AppDynamicsConfig(
            base_url=base_url,
            username=username,
            password=password,
            instance_name=instance_name,
            projects=projects
        )
        
        # Test connection
        console.print(f"\n[bold]Testing connection to {instance_name}...[/bold]")
        client = AppDynamicsClient(config.base_url, config.username, config.password)
        
        if client.test_connection():
            console.print("[green]✅ Connection successful![/green]")
            
            # Show available applications
            applications = client.get_applications()
            if applications:
                console.print(f"\n[bold]Available Applications ({len(applications)}):[/bold]")
                for app in applications[:10]:  # Show first 10
                    console.print(f"  • {app.get('name', 'Unknown')}")
                if len(applications) > 10:
                    console.print(f"  ... and {len(applications) - 10} more")
            
            # Save configuration
            if Confirm.ask("\nSave this configuration?"):
                if self.save_config(config):
                    console.print("[green]✅ Configuration saved successfully![/green]")
                    debug_logger.log_function_return("AppDynamicsConfigManager.setup_interactive", "Success")
                    return config
                else:
                    console.print("[red]❌ Failed to save configuration[/red]")
                    debug_logger.log_function_return("AppDynamicsConfigManager.setup_interactive", "Save failed")
                    return None
            else:
                console.print("[yellow]Configuration not saved[/yellow]")
                debug_logger.log_function_return("AppDynamicsConfigManager.setup_interactive", "Not saved")
                return None
        else:
            console.print("[red]❌ Connection failed. Please check your credentials and URL.[/red]")
            debug_logger.log_function_return("AppDynamicsConfigManager.setup_interactive", "Connection failed")
            return None
