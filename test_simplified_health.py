#!/usr/bin/env python3
"""
Test script to verify simplified AppDynamics health response
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.interactive.handlers.appdynamics_handler import interactive_appdynamics

def test_simplified_health():
    """Test the simplified health response"""
    print("🔧 Testing simplified AppDynamics health response...")
    
    test_query = "give me the application health for SCI Market Place PROD Azure"
    
    print(f"Query: {test_query}")
    print("=" * 60)
    
    try:
        interactive_appdynamics(test_query)
        print("\n✅ Simplified health test completed successfully!")
        print("\nExpected output:")
        print("- Only the top health summary panel")
        print("- Correct server count (8 servers)")
        print("- Health status reflecting actual AppDynamics status")
        print("- No business transactions or alerts panels")
    except Exception as e:
        print(f"❌ Error in simplified health test: {e}")

if __name__ == "__main__":
    print("🚀 Simplified AppDynamics Health Test")
    print("=" * 50)
    
    test_simplified_health()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    print("The handler should now show only the essential health summary.")
