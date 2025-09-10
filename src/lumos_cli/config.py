"""Configuration management for Lumos CLI"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from .platform_utils import (
    get_config_directory, get_env_file_locations, 
    get_default_ollama_url, is_windows, create_directory_if_not_exists,
    check_ollama_installed
)

def load_env_file(env_path: str = ".env", debug: bool = False, force_override: bool = True):
    """Load environment variables from .env file with detailed logging"""
    env_file = Path(env_path)
    
    if debug:
        print(f"🔍 Looking for .env file at: {env_file.absolute()}")
    
    if not env_file.exists():
        # Try platform-appropriate common locations
        search_paths = [str(path) for path in get_env_file_locations()]
        if debug:
            print(f"🔍 .env not found, trying: {search_paths}")
        
        for path in search_paths:
            if Path(path).exists():
                env_file = Path(path)
                if debug:
                    print(f"✅ Found .env file at: {env_file.absolute()}")
                break
        else:
            if debug:
                print("❌ No .env file found in any location")
            return  # No .env file found
    
    try:
        loaded_vars = {}
        overridden_vars = {}
        
        with open(env_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")  # Remove quotes
                    
                    # Check if we're overriding an existing value
                    if key in os.environ and not force_override:
                        if debug:
                            print(f"⚠️  Skipping {key} (already in environment)")
                        continue
                    elif key in os.environ and force_override:
                        old_value = os.environ[key]
                        overridden_vars[key] = {'old': old_value, 'new': value}
                        if debug:
                            if 'key' in key.lower() or 'secret' in key.lower():
                                old_masked = f"{old_value[:8]}..." if len(old_value) > 8 else "***"
                                new_masked = f"{value[:8]}..." if len(value) > 8 else "***"
                                print(f"🔄 Overriding {key}: {old_masked} -> {new_masked}")
                            else:
                                print(f"🔄 Overriding {key}: {old_value} -> {value}")
                    
                    # Set the environment variable
                    os.environ[key] = value
                    loaded_vars[key] = value
        
        if debug:
            total_loaded = len(loaded_vars)
            total_overridden = len(overridden_vars)
            print(f"✅ Loaded {total_loaded} environment variables ({total_overridden} overridden):")
            for key, value in loaded_vars.items():
                if key not in overridden_vars:  # Only show new variables
                    if 'key' in key.lower() or 'secret' in key.lower():
                        masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
                        print(f"   {key}={masked_value}")
                    else:
                        print(f"   {key}={value}")
                        
    except Exception as e:
        if debug:
            print(f"❌ Error reading .env file: {e}")
        pass  # Ignore errors reading .env file

# Load .env file when module is imported, try multiple locations
import sys
import os.path

def _find_project_root():
    """Find project root by looking for .env file or git repo"""
    current = Path.cwd()
    
    # Go up the directory tree looking for .env or .git
    for parent in [current] + list(current.parents):
        if (parent / ".env").exists() or (parent / ".git").exists():
            return parent
    
    # Fallback to current directory
    return current

# Try to load from project root first, then platform-specific locations
project_root = _find_project_root()
env_locations = [str(project_root / ".env")] + [str(path) for path in get_env_file_locations()]

for env_path in env_locations:
    if Path(env_path).exists():
        load_env_file(env_path)
        break

class LumosConfig:
    """Centralized configuration management"""
    
    def __init__(self):
        # Use platform-appropriate config directory
        self.config_dir = get_config_directory()
        self.config_file = self.config_dir / "config.json"
        
        # Ensure config directory exists with proper error handling
        if not create_directory_if_not_exists(self.config_dir):
            # Fallback to home directory if config directory can't be created
            self.config_dir = Path.home() / ".lumos"
            self.config_file = self.config_dir / "config.json"
            create_directory_if_not_exists(self.config_dir)
        
        # Always try to load environment variables first
        self._ensure_env_loaded()
        self._config = self._load_config()
    
    def _ensure_env_loaded(self):
        """Ensure environment variables are loaded from .env file"""
        from .logger import log_debug
        
        log_debug("Config: Ensuring environment variables are loaded")
        
        # Find project root
        current = Path.cwd()
        project_root = current
        
        # Go up the directory tree looking for .env or .git
        for parent in [current] + list(current.parents):
            if (parent / ".env").exists() or (parent / ".git").exists():
                project_root = parent
                log_debug(f"Config: Found project root at: {project_root}")
                break
        
        # Try multiple platform-appropriate locations for .env file
        env_locations = [
            project_root / ".env",
            current / ".env"
        ] + get_env_file_locations()
        
        log_debug(f"Config: Searching for .env file in locations: {[str(p) for p in env_locations]}")
        
        # Clear cached LLM environment variables if no .env file found
        found_env_file = False
        for env_path in env_locations:
            if env_path.exists():
                log_debug(f"Config: Found .env file at: {env_path}")
                load_env_file(str(env_path), debug=True, force_override=True)
                found_env_file = True
                break
        
        if not found_env_file:
            log_debug("Config: No .env file found in any location")
            # Clear LLM-related environment variables when no .env file is found
            self._clear_llm_env_vars()
    
    def _clear_llm_env_vars(self):
        """Clear LLM-related environment variables when no .env file is found"""
        from .logger import log_debug
        
        llm_env_vars = ['LLM_API_URL', 'LLM_API_KEY', 'LUMOS_BACKEND', 'LLM_REST_MODEL']
        cleared_vars = []
        
        for var in llm_env_vars:
            if var in os.environ:
                old_value = os.environ[var]
                del os.environ[var]
                cleared_vars.append(var)
                if 'key' in var.lower():
                    log_debug(f"Config: Cleared {var} (was: {old_value[:8]}...)")
                else:
                    log_debug(f"Config: Cleared {var} (was: {old_value})")
        
        if cleared_vars:
            log_debug(f"Config: Cleared {len(cleared_vars)} cached environment variables: {cleared_vars}")
        else:
            log_debug("Config: No cached environment variables to clear")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment"""
        
        # Start with defaults
        config = {
            # LLM Settings - prioritize global config, then env vars, then defaults
            'llm': {
                # OpenAI/Standard REST API
                'rest_api_url': None,
                'rest_api_key': None,
                'rest_model': "gpt-3.5-turbo",
                
                # Enterprise LLM Settings
                'enterprise_token_url': None,
                'enterprise_chat_url': None, 
                'enterprise_app_id': None,
                'enterprise_app_key': None,
                'enterprise_app_resource': None,
                'enterprise_model': "enterprise-default",
                
                # Local Ollama
                'ollama_url': get_default_ollama_url(),
                'ollama_model': "devstral",
                
                # Backend selection: auto, openai, enterprise, ollama
                'default_backend': "auto"
            },
            
            # Embeddings
            'embeddings': {
                'db_path': os.getenv("LLM_EMBED_DB", ".lumos_embeddings.db"),
                'model': os.getenv("EMBED_MODEL", "nomic-embed-text"),
                'fallback_mode': True  # Use hash-based embeddings if Ollama unavailable
            },
            
            # Safety
            'safety': {
                'backup_dir': os.getenv("LUMOS_BACKUP_DIR", ".llm_backups"),
                'auto_backup': True,
                'preview_by_default': True
            },
            
            # Features
            'features': {
                'interactive_mode': True,
                'smart_file_discovery': True,
                'error_handling': True,
                'history_enabled': True
            }
        }
        
        # Load from global config file if exists (highest priority)
        if self.config_file.exists():
            try:
                import json
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self._merge_configs(config, file_config)
            except Exception:
                pass  # Use defaults if file is corrupted
        
        # Then overlay environment variables (medium priority)
        env_overrides = {
            'llm': {
                # OpenAI/Standard REST API
                'rest_api_url': os.getenv("LLM_API_URL"),
                'rest_api_key': os.getenv("LLM_API_KEY"), 
                'rest_model': os.getenv("LLM_REST_MODEL"),
                
                # Enterprise LLM Settings
                'enterprise_token_url': os.getenv("ENTERPRISE_TOKEN_URL"),
                'enterprise_chat_url': os.getenv("ENTERPRISE_CHAT_URL"),
                'enterprise_app_id': os.getenv("ENTERPRISE_APP_ID"),
                'enterprise_app_key': os.getenv("ENTERPRISE_APP_KEY"),
                'enterprise_app_resource': os.getenv("ENTERPRISE_APP_RESOURCE"),
                'enterprise_model': os.getenv("ENTERPRISE_MODEL"),
                
                # Local Ollama  
                'ollama_url': os.getenv("OLLAMA_URL"),
                'ollama_model': os.getenv("OLLAMA_MODEL"),
                
                # Backend selection
                'default_backend': os.getenv("LUMOS_BACKEND")
            }
        }
        
        # Only apply non-None environment variables
        for section, values in env_overrides.items():
            if section not in config:
                config[section] = {}
            for key, value in values.items():
                if value is not None:
                    config[section][key] = value
        
        return config
    
    def _merge_configs(self, base: Dict, update: Dict):
        """Recursively merge configuration dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'llm.rest_api_url')"""
        keys = key_path.split('.')
        current = self._config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def set(self, key_path: str, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            import json
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception:
            pass  # Fail silently
    
    def is_ollama_available(self) -> bool:
        """Check if Ollama is available"""
        # First check if Ollama is installed
        if not check_ollama_installed():
            return False
        
        # Then check if it's running
        try:
            import httpx
            url = self.get('llm.ollama_url', get_default_ollama_url())
            with httpx.Client(timeout=2.0) as client:
                response = client.get(f"{url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
    
    def is_rest_api_configured(self, debug: bool = False) -> bool:
        """Check if OpenAI API is properly configured"""
        url = self.get('llm.rest_api_url')
        key = self.get('llm.rest_api_key')
        
        # Also check OpenAI JSON config file
        if not (url and key):
            try:
                from .openai_config import OpenAIConfigManager
                manager = OpenAIConfigManager()
                openai_config = manager.load_config()
                if openai_config and openai_config.api_key and openai_config.api_url:
                    url = openai_config.api_url
                    key = openai_config.api_key
            except Exception:
                pass
        
        if debug:
            print(f"🔍 OpenAI API Configuration Check:")
            print(f"   URL: {url or 'Not set'}")
            print(f"   Key: {'sk-...' + key[-10:] if key and len(key) > 10 else 'Not set'}")
            print(f"   Configured: {bool(url and key)}")
        
        return bool(url and key)
    
    def is_enterprise_configured(self, debug: bool = False) -> bool:
        """Check if Enterprise LLM is properly configured"""
        required_fields = [
            'llm.enterprise_token_url',
            'llm.enterprise_chat_url', 
            'llm.enterprise_app_id',
            'llm.enterprise_app_key',
            'llm.enterprise_app_resource'
        ]
        
        config_values = {field: self.get(field) for field in required_fields}
        configured = all(config_values.values())
        
        if debug:
            print(f"🔍 Enterprise LLM Configuration Check:")
            for field, value in config_values.items():
                field_name = field.replace('llm.enterprise_', '').upper()
                if 'key' in field.lower():
                    display_value = f"{value[:8]}..." if value and len(value) > 8 else 'Not set'
                else:
                    display_value = value or 'Not set'
                print(f"   {field_name}: {display_value}")
            print(f"   Configured: {configured}")
        
        return configured
    
    def get_available_backends(self) -> list:
        """Get list of available backends"""
        from .logger import log_debug
        
        log_debug("Config: Checking available backends")
        backends = []
        
        ollama_available = self.is_ollama_available()
        log_debug(f"Config: Ollama available: {ollama_available}")
        if ollama_available:
            backends.append('ollama')
            
        # Check OpenAI API (REST endpoint)
        rest_configured = self.is_rest_api_configured()
        log_debug(f"Config: OpenAI API configured: {rest_configured}")
        if rest_configured:
            backends.append('openai')  # More specific name
        else:
            # Log detailed info when OpenAI is not configured
            url = self.get('llm.rest_api_url')
            key = self.get('llm.rest_api_key')
            log_debug(f"Config: OpenAI API details - URL: {url or 'None'}, Key: {'Present' if key else 'None'}")
        
        # Check Enterprise LLM
        enterprise_configured = self.is_enterprise_configured()
        log_debug(f"Config: Enterprise LLM configured: {enterprise_configured}")
        if enterprise_configured:
            backends.append('enterprise')
            
        log_debug(f"Config: Final available backends: {backends}")
        return backends

# Global config instance
config = LumosConfig()

def setup_wizard():
    """Interactive setup wizard for first-time users"""
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    
    console = Console()
    
    console.print(Panel(
        "[bold green]🌟 Welcome to Lumos CLI Setup[/bold green]\n\n"
        "Let's configure your AI assistant for the best experience!",
        title="Setup Wizard",
        border_style="green"
    ))
    
    # Check current status
    console.print("\n[cyan]🔍 Checking current configuration...[/cyan]")
    
    ollama_available = config.is_ollama_available()
    rest_configured = config.is_rest_api_configured()
    
    console.print(f"{'✅' if ollama_available else '❌'} Ollama (local): {'Available' if ollama_available else 'Not available'}")
    console.print(f"{'✅' if rest_configured else '❌'} OpenAI API: {'Configured' if rest_configured else 'Not configured'}")
    
    if not ollama_available and not rest_configured:
        console.print("\n[yellow]⚠️ No LLM backends are available![/yellow]")
        console.print("\n[bold]Options:[/bold]")
        console.print("1. Install Ollama: https://ollama.ai")
        console.print("2. Configure OpenAI API (or other compatible REST API)")
        
        if Confirm.ask("\nConfigure OpenAI API now?", default=True):
            api_url = Prompt.ask("API URL", default="https://api.openai.com/v1/chat/completions")
            console.print("🔑 [dim]Your input will be hidden for security.[/dim]")
            api_key = Prompt.ask("API Key", password=True)
            
            config.set('llm.rest_api_url', api_url)
            config.set('llm.rest_api_key', api_key)
            
            console.print("[green]✅ OpenAI API configured![/green]")
    
    # Setup complete
    console.print("\n[green]🎉 Setup complete! You can now use Lumos CLI.[/green]")
    console.print("[dim]Tip: Run 'lumos-cli' to start interactive mode[/dim]")

if __name__ == "__main__":
    setup_wizard()