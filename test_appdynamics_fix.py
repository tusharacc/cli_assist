#!/usr/bin/env python3
"""
Test script to verify AppDynamics configuration fix
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.config.appdynamics_config import AppDynamicsConfigManager
from lumos_cli.ui.console import get_service_status

def test_appdynamics_status():
    """Test AppDynamics status detection"""
    print("🔧 Testing AppDynamics status detection...")
    
    # Load configuration
    config_manager = AppDynamicsConfigManager()
    config = config_manager.load_config()
    
    if config:
        print(f"✅ Configuration loaded successfully")
        print(f"   Base URL: {config.base_url}")
        print(f"   Client ID: {config.client_id}")
        print(f"   Instance: {config.instance_name}")
        print(f"   Projects: {config.projects}")
        
        # Check if configured
        is_configured = config_manager.is_configured()
        print(f"   Is Configured: {is_configured}")
        
        # Check service status
        status_map = get_service_status()
        appdynamics_status = status_map.get('appdynamics', 'Unknown')
        print(f"   Status Indicator: {appdynamics_status}")
        
        if appdynamics_status == '🟢':
            print("✅ AppDynamics status is now GREEN!")
            return True
        else:
            print("❌ AppDynamics status is still RED")
            return False
    else:
        print("❌ No configuration found")
        return False

if __name__ == "__main__":
    print("🚀 AppDynamics Configuration Fix Test")
    print("=" * 50)
    
    success = test_appdynamics_status()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Fix successful! AppDynamics should now show green status.")
    else:
        print("❌ Fix may need additional investigation.")
