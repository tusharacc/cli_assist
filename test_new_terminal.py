#!/usr/bin/env python3
"""Test behavior when opening new terminal without .env file"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.config import load_env_file, get_config
from lumos_cli.logger import LumosLogger
from lumos_cli.ui import create_header
from rich.console import Console

def test_new_terminal():
    """Test new terminal behavior"""
    console = Console()
    create_header(console, "New Terminal Test")
    
    # Initialize logger
    logger = LumosLogger()
    
    # Test scenario: No .env file in current directory
    console.print("🧪 Testing scenario: No .env file in current directory")
    
    # Try to load .env file that doesn't exist
    load_env_file(".env.nonexistent", debug=True)
    
    # Get configuration
    config = get_config()
    console.print(f"📊 Configuration loaded: {len(config)} settings")
    
    # Show what we have
    if config:
        console.print("✅ Global configuration found:")
        for key, value in config.items():
            if "key" in key.lower():
                console.print(f"  {key}: {'***' if value else 'Not set'}")
            else:
                console.print(f"  {key}: {value}")
    else:
        console.print("❌ No configuration found")
    
    # Show log entries
    console.print("\n📝 Recent log entries:")
    logger.info("New terminal test completed")
    
    return True

if __name__ == "__main__":
    test_new_terminal()