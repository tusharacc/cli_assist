#!/usr/bin/env python3
"""Test Lumos CLI in fresh terminal scenario"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.config import config
from src.lumos_cli.utils.platform_utils import get_config_directory
from src.lumos_cli.ui import create_header
from rich.console import Console

def test_fresh_terminal():
    """Test Lumos CLI behavior in fresh terminal (no .env file)"""
    console = Console()
    create_header(console, "Fresh Terminal Test")
    
    # Backup existing config if it exists
    config_dir = get_config_directory()
    config_file = config_dir / "config.json"
    backup_file = None
    
    if config_file.exists():
        backup_file = config_file.with_suffix(".backup")
        shutil.copy(config_file, backup_file)
        console.print(f"💾 Backed up existing config to {backup_file}")
    
    try:
        # Remove config to simulate fresh terminal
        if config_file.exists():
            config_file.unlink()
            console.print("🗑️ Removed existing config")
        
        # Clear environment variables
        env_vars = ["LLM_API_URL", "LLM_API_KEY", "LUMOS_BACKEND"]
        original_values = {}
        for var in env_vars:
            if var in os.environ:
                original_values[var] = os.environ[var]
                del os.environ[var]
        
        console.print("🧹 Cleared environment variables")
        
        # Test configuration loading  
        console.print(f"📊 Fresh config available backends: {config.get_available_backends()}")
        console.print(f"📊 Ollama available: {config.is_ollama_available()}")
        console.print(f"📊 REST configured: {config.is_rest_api_configured()}")
        
        # Restore environment
        for var, value in original_values.items():
            os.environ[var] = value
        
        console.print("✅ Test completed successfully")
        
    finally:
        # Restore backup if it exists
        if backup_file and backup_file.exists():
            shutil.copy(backup_file, config_file)
            backup_file.unlink()
            console.print(f"🔄 Restored config from backup")
    
    return True

if __name__ == "__main__":
    test_fresh_terminal()