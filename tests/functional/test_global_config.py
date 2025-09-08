#!/usr/bin/env python3
"""Test global configuration system"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.platform_utils import get_config_directory, get_logs_directory
from lumos_cli.config import config
from lumos_cli.ui import create_header
from rich.console import Console
from rich.table import Table

def test_global_config():
    """Test global configuration system"""
    console = Console()
    create_header(console, "Global Config Test")
    
    # Show platform directories
    config_dir = get_config_directory()
    logs_dir = get_logs_directory()
    
    console.print(f"📁 Config Directory: {config_dir}")
    console.print(f"📁 Logs Directory: {logs_dir}")
    
    # Test config access
    test_settings = {
        "llm.rest_api_url": "https://api.openai.com/v1/chat/completions",
        "llm.rest_api_key": "test-key",
        "llm.default_backend": "auto"
    }
    
    console.print("💾 Testing config access...")
    
    # Show config table
    table = Table(title="Configuration Test Results")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_column("Status", style="bold")
    
    for setting in test_settings.keys():
        actual = config.get(setting)
        status = "✅ CONFIGURED" if actual else "❌ NOT SET"
        value = str(actual) if actual else "Not set"
        if 'key' in setting.lower():
            value = f"{value[:8]}..." if len(value) > 8 else "***"
        table.add_row(setting, value, status)
    
    console.print(table)
    return True

if __name__ == "__main__":
    test_global_config()