#!/usr/bin/env python3
"""Test Windows compatibility features"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.lumos_cli.utils.platform_utils import (
    is_windows, is_macos, is_linux,
    get_config_directory, get_logs_directory, get_cache_directory,
    check_ollama_installed, get_platform_info
)
from lumos_cli.ui import create_header
from rich.console import Console
from rich.table import Table

def test_windows_compatibility():
    """Test Windows compatibility features"""
    console = Console()
    create_header(console, "Windows Compatibility Test")
    
    # Platform detection
    platform_info = get_platform_info()
    
    table = Table(title="Platform Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("System", platform_info["system"])
    table.add_row("Platform", platform_info["platform"])
    table.add_row("Machine", platform_info["machine"])
    table.add_row("Python Version", platform_info["python_version"])
    table.add_row("Is Windows", str(is_windows()))
    table.add_row("Is macOS", str(is_macos()))
    table.add_row("Is Linux", str(is_linux()))
    
    console.print(table)
    
    # Directory paths
    console.print("\n📁 Platform-specific directories:")
    console.print(f"Config: {get_config_directory()}")
    console.print(f"Logs: {get_logs_directory()}")
    console.print(f"Cache: {get_cache_directory()}")
    
    # Ollama detection
    console.print("\n🦙 Ollama detection:")
    ollama_installed = check_ollama_installed()
    if ollama_installed:
        console.print("✅ Ollama is installed")
    else:
        console.print("❌ Ollama not found")
    
    return True

if __name__ == "__main__":
    test_windows_compatibility()