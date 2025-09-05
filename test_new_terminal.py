#!/usr/bin/env python3
"""Test behavior when opening new terminal without .env file"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.config import load_env_file, config
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
    backends = config.get_available_backends()
    console.print(f"📊 Available backends: {backends}")
    
    # Show current settings
    console.print("✅ Configuration status:")
    console.print(f"  Ollama: {'Available' if config.is_ollama_available() else 'Not available'}")
    console.print(f"  REST API: {'Configured' if config.is_rest_api_configured() else 'Not configured'}")
    console.print(f"  API URL: {config.get('llm.rest_api_url', 'Not set')}")
    console.print(f"  API Key: {'Set' if config.get('llm.rest_api_key') else 'Not set'}")
    
    # Show log entries
    console.print("\n📝 Recent log entries:")
    logger.info("New terminal test completed")
    
    return True

if __name__ == "__main__":
    test_new_terminal()