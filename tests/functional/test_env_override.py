#!/usr/bin/env python3
"""Test environment variable override functionality"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.config import load_env_file
from lumos_cli.ui import create_header
from rich.console import Console

def test_env_override():
    """Test environment variable override functionality"""
    console = Console()
    create_header(console, "Environment Override Test")
    
    # Set initial environment variables
    os.environ["TEST_VAR"] = "original_value"
    console.print(f"🔄 Initial TEST_VAR: {os.environ.get('TEST_VAR')}")
    
    # Create temporary .env file
    env_content = "TEST_VAR=overridden_value\nNEW_VAR=new_value"
    with open(".env.test", "w") as f:
        f.write(env_content)
    
    console.print("📝 Created .env.test with:")
    console.print("  TEST_VAR=overridden_value")
    console.print("  NEW_VAR=new_value")
    
    # Test loading with force override
    load_env_file(".env.test", debug=True, force_override=True)
    
    # Check results
    console.print(f"\n✅ After override TEST_VAR: {os.environ.get('TEST_VAR')}")
    console.print(f"✅ New variable NEW_VAR: {os.environ.get('NEW_VAR')}")
    
    # Cleanup
    os.remove(".env.test")
    console.print("\n🧹 Cleaned up .env.test")
    
    return True

if __name__ == "__main__":
    test_env_override()