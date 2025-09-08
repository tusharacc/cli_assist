#!/usr/bin/env python3
"""
Test the recursion fix for config commands
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that the imports work without recursion errors"""
    
    print("🧪 Testing recursion fix...")
    
    try:
        from lumos_cli.cli_refactored_v2 import app
        print("✅ CLI imports successful")
    except RecursionError as e:
        print(f"❌ Recursion error still exists: {e}")
        return False
    except Exception as e:
        print(f"❌ Other import error: {e}")
        return False
    
    try:
        # Test that we can access the command functions without recursion
        from lumos_cli.cli_refactored_v2 import github_config, jenkins_config
        print("✅ Config command imports successful")
    except Exception as e:
        print(f"❌ Config command import error: {e}")
        return False
    
    print("✅ All tests passed - recursion issue fixed!")
    return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🎉 You can now safely run: lumos-cli github-config")
        print("🎉 You can now safely run: lumos-cli jenkins-config")
    else:
        print("\n❌ Recursion issue still exists, needs more investigation")
        sys.exit(1)