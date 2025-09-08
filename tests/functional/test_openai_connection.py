#!/usr/bin/env python3
"""Test OpenAI API connection with Lumos CLI configuration"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.lumos_cli.config import load_env_file, config
from src.lumos_cli.core.router import LLMRouter
from src.lumos_cli.ui import create_header
from rich.console import Console

def test_openai_connection():
    """Test OpenAI API connection"""
    console = Console()
    create_header(console, "OpenAI Connection Test")
    
    # Load environment
    load_env_file(debug=True)
    
    # Show configuration
    console.print(f"📊 REST API URL: {config.get('llm.rest_api_url', 'Not set')}")
    console.print(f"🔑 API Key: {'✅ Set' if config.get('llm.rest_api_key') else '❌ Not set'}")
    
    # Test connection
    try:
        router = LLMRouter(backend="rest")
        response = router.chat([{"role": "user", "content": "Say hello in one word"}])
        console.print(f"✅ Connection successful: {response}")
        return True
    except Exception as e:
        console.print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_openai_connection()