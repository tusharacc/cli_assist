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
    
    if os.name == 'nt':  # Windows
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        log_dir = os.path.join(appdata, 'Lumos', 'Logs')
        print(f"🪟 Windows: {log_dir}")
        print(f"   Example: C:\\Users\\YourUsername\\AppData\\Roaming\\Lumos\\Logs\\")
    else:  # Unix-like (macOS, Linux)
        log_dir = os.path.join(os.path.expanduser('~'), '.lumos', 'logs')
        print(f"🐧 Unix/Linux/macOS: {log_dir}")
        print(f"   Example: /home/username/.lumos/logs/")
    
    print(f"\n📝 Log files are created with timestamps:")
    print(f"   lumos-debug-YYYYMMDD_HHMMSS.log")
    
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
