#!/usr/bin/env python3
"""
Test script to demonstrate debug logging for GitHub and Jenkins integrations
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lumos_cli.debug_logger import get_debug_logger
from lumos_cli.github_client import GitHubClient
from lumos_cli.jenkins_client import JenkinsClient

def test_github_debug_logging():
    """Test GitHub client with debug logging"""
    print("🔍 Testing GitHub Client Debug Logging")
    print("=" * 50)
    
    debug_logger = get_debug_logger()
    debug_logger.info("Starting GitHub client debug test")
    
    try:
        # Initialize GitHub client
        github = GitHubClient()
        
        # Test PR listing
        print("\n📋 Testing GitHub PR listing...")
        prs = github.list_pull_requests("microsoft", "vscode", state="open")
        print(f"Found {len(prs)} pull requests")
        
    except Exception as e:
        debug_logger.error(f"GitHub test failed: {e}")
        print(f"❌ GitHub test failed: {e}")

def test_jenkins_debug_logging():
    """Test Jenkins client with debug logging"""
    print("\n🔍 Testing Jenkins Client Debug Logging")
    print("=" * 50)
    
    debug_logger = get_debug_logger()
    debug_logger.info("Starting Jenkins client debug test")
    
    try:
        # Initialize Jenkins client (this will fail without proper config)
        jenkins = JenkinsClient()
        
        # Test connection
        print("\n📋 Testing Jenkins connection...")
        success = jenkins.test_connection()
        print(f"Jenkins connection: {'✅ Success' if success else '❌ Failed'}")
        
    except Exception as e:
        debug_logger.error(f"Jenkins test failed: {e}")
        print(f"❌ Jenkins test failed: {e}")

def show_log_locations():
    """Show where log files are located on different platforms"""
    print("\n📁 Log File Locations")
    print("=" * 50)
    
    # Use the same logic as the debug logger
    from src.lumos_cli.platform_utils import get_logs_directory
    
    log_dir = get_logs_directory()
    print(f"📂 Actual log directory: {log_dir}")
    
    if os.name == 'nt':  # Windows
        print(f"🪟 Windows: %LOCALAPPDATA%\\Lumos\\Logs\\")
        print(f"   Example: C:\\Users\\YourUsername\\AppData\\Local\\Lumos\\Logs\\")
    else:  # Unix-like (macOS, Linux)
        print(f"🐧 Unix/Linux/macOS: ~/Library/Logs/Lumos/ (macOS) or ~/.lumos/logs/ (Linux)")
        print(f"   Example: /Users/username/Library/Logs/Lumos/ (macOS)")
    
    print(f"\n📝 Log files are created daily:")
    print(f"   lumos-YYYY-MM-DD.log (main logs)")
    print(f"   lumos-debug-YYYY-MM-DD.log (debug logs with function traces)")
    
    print(f"\n📖 For complete debugging guide, see: COMPREHENSIVE_DEBUGGING_GUIDE.md")

if __name__ == "__main__":
    print("🚀 Lumos CLI Debug Logging Test")
    print("=" * 50)
    
    show_log_locations()
    
    # Test GitHub logging
    test_github_debug_logging()
    
    # Test Jenkins logging
    test_jenkins_debug_logging()
    
    print("\n✅ Debug logging test completed!")
    print("Check the log files for detailed function call traces.")
