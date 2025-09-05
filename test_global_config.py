#!/usr/bin/env python3
"""Test global configuration system"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.platform_utils import get_config_directory, get_logs_directory
from lumos_cli.config import get_config, save_global_config
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
    
    # Test saving/loading config
    test_config = {
        "rest_api_url": "https://api.openai.com/v1/chat/completions",
        "rest_api_key": "test-key",
        "backend": "auto"
    }
    
    console.print("💾 Testing config save/load...")
    save_global_config(test_config)
    loaded_config = get_config()
    
    # Show config table
    table = Table(title="Configuration Test Results")
    table.add_column("Setting", style="cyan")
    table.add_column("Expected", style="green")
    table.add_column("Actual", style="yellow")
    table.add_column("Status", style="bold")
    
    for key, expected in test_config.items():
        actual = loaded_config.get(key)
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        table.add_row(key, str(expected), str(actual), status)
    
    console.print(table)
    return True

if __name__ == "__main__":
    test_global_config()