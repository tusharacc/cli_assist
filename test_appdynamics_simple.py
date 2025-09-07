#!/usr/bin/env python3
"""
Simple AppDynamics connection test
Quick test for OAuth2 authentication and SSL verification
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.appdynamics_client import AppDynamicsClient

def test_connection(base_url: str, client_id: str, client_secret: str):
    """Simple connection test"""
    print(f"🔧 Testing AppDynamics connection...")
    print(f"   URL: {base_url}")
    print(f"   Client ID: {client_id}")
    print(f"   SSL Verification: Disabled")
    
    # Create client
    client = AppDynamicsClient(base_url, client_id, client_secret)
    
    # Test connection
    if client.test_connection():
        print("✅ Connection successful!")
        
        # Get applications
        applications = client.get_applications()
        print(f"✅ Found {len(applications)} applications")
        
        # Show first few applications
        for i, app in enumerate(applications[:5]):
            print(f"   {i+1}. {app.get('name', 'Unknown')} (ID: {app.get('id', 'N/A')})")
        
        if len(applications) > 5:
            print(f"   ... and {len(applications) - 5} more")
        
        return True
    else:
        print("❌ Connection failed!")
        return False

if __name__ == "__main__":
    # Update these with your actual credentials
    BASE_URL = "https://chubbinaholdingsinc-prod.saas.appdynamics.com"
    CLIENT_ID = "sci_mp_read"
    CLIENT_SECRET = "your_client_secret_here"
    
    print("🚀 AppDynamics Simple Connection Test")
    print("=" * 50)
    
    if CLIENT_SECRET == "your_client_secret_here":
        print("⚠️ Please update CLIENT_SECRET in this file with your actual secret")
        print("   Or set environment variables:")
        print("   export APPDYNAMICS_BASE_URL='your_url'")
        print("   export APPDYNAMICS_CLIENT_ID='your_client_id'")
        print("   export APPDYNAMICS_CLIENT_SECRET='your_client_secret'")
    else:
        test_connection(BASE_URL, CLIENT_ID, CLIENT_SECRET)
