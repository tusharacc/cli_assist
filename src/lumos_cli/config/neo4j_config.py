"""
Neo4j configuration management for Lumos CLI
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()

class Neo4jConfig:
    """Neo4j configuration data class"""
    
    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "uri": self.uri,
            "username": self.username,
            "password": self.password,
            "database": self.database
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Neo4jConfig':
        """Create config from dictionary"""
        return cls(
            uri=data.get("uri", ""),
            username=data.get("username", ""),
            password=data.get("password", ""),
            database=data.get("database", "neo4j")
        )

class Neo4jConfigManager:
    """Manages Neo4j configuration storage and retrieval"""
    
    def __init__(self, config_file: str = None):
        if config_file:
            self.config_file = Path(config_file)
        else:
            # Use default location
            config_dir = Path.home() / ".lumos"
            config_dir.mkdir(exist_ok=True)
            self.config_file = config_dir / "neo4j_config.json"
    
    def load_config(self) -> Optional[Neo4jConfig]:
        """Load Neo4j configuration from file"""
        try:
            if not self.config_file.exists():
                return None
            
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return Neo4jConfig.from_dict(data)
        except Exception as e:
            console.print(f"[red]Error loading Neo4j config: {e}[/red]")
            return None
    
    def save_config(self, config: Neo4jConfig) -> bool:
        """Save Neo4j configuration to file"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            
            # Set secure permissions
            os.chmod(self.config_file, 0o600)
            return True
        except Exception as e:
            console.print(f"[red]Error saving Neo4j config: {e}[/red]")
            return False
    
    def setup_interactive(self) -> bool:
        """Interactive setup for Neo4j configuration"""
        console.print("\n[bold blue]🔗 Neo4j Configuration Setup[/bold blue]")
        console.print("=" * 50)
        
        # Get current config if exists
        current_config = self.load_config()
        
        if current_config:
            console.print(f"[yellow]Current configuration found:[/yellow]")
            console.print(f"  URI: {current_config.uri}")
            console.print(f"  Username: {current_config.username}")
            console.print(f"  Database: {current_config.database}")
            
            if not Confirm.ask("\nDo you want to update the configuration?"):
                return True
        
        # Get configuration details
        console.print("\n[cyan]Please provide your Neo4j connection details:[/cyan]")
        
        uri = Prompt.ask(
            "Neo4j URI", 
            default=current_config.uri if current_config else "bolt://localhost:7687"
        )
        
        username = Prompt.ask(
            "Username", 
            default=current_config.username if current_config else "neo4j"
        )
        
        password = Prompt.ask(
            "Password", 
            password=True,
            default=current_config.password if current_config else ""
        )
        
        database = Prompt.ask(
            "Database name", 
            default=current_config.database if current_config else "neo4j"
        )
        
        # Create config object
        config = Neo4jConfig(uri, username, password, database)
        
        # Test connection
        console.print("\n[cyan]Testing connection...[/cyan]")
        from ..clients.neo4j_client import Neo4jClient
        
        client = Neo4jClient(uri, username, password)
        if client.test_connection():
            console.print("[green]✅ Connection successful![/green]")
            
            # Save configuration
            if self.save_config(config):
                console.print("[green]✅ Configuration saved successfully![/green]")
                console.print(f"\n[cyan]Configuration saved to: {self.config_file}[/cyan]")
                return True
            else:
                console.print("[red]❌ Failed to save configuration[/red]")
                return False
        else:
            console.print("[red]❌ Connection failed. Please check your credentials.[/red]")
            return False
    
    def is_configured(self) -> bool:
        """Check if Neo4j is configured"""
        config = self.load_config()
        if not config:
            return False
        
        # Test connection
        from ..clients.neo4j_client import Neo4jClient
        client = Neo4jClient(config.uri, config.username, config.password)
        return client.test_connection()
