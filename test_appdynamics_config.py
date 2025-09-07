#!/usr/bin/env python3
"""
AppDynamics configuration test
Test configuration saving and loading
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.appdynamics_config import AppDynamicsConfig, AppDynamicsConfigManager
from lumos_cli.appdynamics_client import AppDynamicsClient

def test_config_creation():
    """Test creating and saving configuration"""
    print("🔧 Testing AppDynamics configuration creation...")
    
    # Create configuration
    config = AppDynamicsConfig(
        base_url="https://chubbinaholdingsinc-prod.saas.appdynamics.com",
        client_id="sci_mp_read",
        client_secret="your_client_secret_here",
        instance_name="Production",
        projects=["SCI Markpet Place PROD Azure", "SCI Market Place PROD"]
    )
    
    print(f"   Instance: {config.instance_name}")
    print(f"   URL: {config.base_url}")
    print(f"   Client ID: {config.client_id}")
    print(f"   Projects: {config.projects}")
    
    # Save configuration
    config_manager = AppDynamicsConfigManager()
    if config_manager.save_config(config):
        print("✅ Configuration saved successfully!")
        return True
    else:
        print("❌ Failed to save configuration")
        return False

def test_config_loading():
    """Test loading configuration"""
    print("\n🔧 Testing AppDynamics configuration loading...")
    
    config_manager = AppDynamicsConfigManager()
    config = config_manager.load_config()
    
    if config:
        print("✅ Configuration loaded successfully!")
        print(f"   Instance: {config.instance_name}")
        print(f"   URL: {config.base_url}")
        print(f"   Client ID: {config.client_id}")
        print(f"   Projects: {config.projects}")
        return config
    else:
        print("❌ No configuration found")
        return None

def test_config_validation():
    """Test configuration validation"""
    print("\n🔧 Testing AppDynamics configuration validation...")
    
    config_manager = AppDynamicsConfigManager()
    
    if config_manager.is_configured():
        print("✅ Configuration is valid and complete")
        return True
    else:
        print("❌ Configuration is incomplete or invalid")
        return False

def test_client_with_config():
    """Test client creation with loaded configuration"""
    print("\n🔧 Testing AppDynamics client with configuration...")
    
    config = test_config_loading()
    if not config:
        return False
    
    # Create client with configuration
    client = AppDynamicsClient(
        config.base_url,
        config.client_id,
        config.client_secret
    )
    
    print(f"   Client created with URL: {client.base_url}")
    print(f"   Client ID: {client.client_id}")
    print(f"   SSL Verification: {'Disabled' if not client.session.verify else 'Enabled'}")
    
    # Test connection (only if secret is not placeholder)
    if config.client_secret != "your_client_secret_here":
        print("   Testing connection...")
        if client.test_connection():
            print("✅ Connection test successful!")
            return True
        else:
            print("❌ Connection test failed!")
            return False
    else:
        print("⚠️ Skipping connection test (placeholder secret)")
        return True

def main():
    """Main test function"""
    print("🚀 AppDynamics Configuration Test Suite")
    print("=" * 50)
    
    # Test 1: Create configuration
    test_config_creation()
    
    # Test 2: Load configuration
    test_config_loading()
    
    # Test 3: Validate configuration
    test_config_validation()
    
    # Test 4: Create client with configuration
    test_client_with_config()
    
    print("\n" + "=" * 50)
    print("✅ Configuration test suite completed!")
    print("\nTo test with real credentials:")
    print("1. Update the CLIENT_SECRET in this file")
    print("2. Or run: lumos-cli appdynamics config")
    print("3. Then run this test again")

if __name__ == "__main__":
    main()
