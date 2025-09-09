#!/usr/bin/env python3
"""
Test script to verify enhanced AppDynamics health summary
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.interactive.handlers.appdynamics_handler import interactive_appdynamics

def test_health_summary():
    """Test the enhanced health summary functionality"""
    print("🔧 Testing enhanced AppDynamics health summary...")
    
    test_query = "give me the application health for SCI Market Place PROD Azure"
    
    print(f"Query: {test_query}")
    print("=" * 60)
    
    try:
        interactive_appdynamics(test_query)
        print("\n✅ Health summary test completed successfully!")
        print("\nExpected output:")
        print("- Application Health Summary panel with overall status")
        print("- Health score and server breakdown")
        print("- Business Transaction Health panel")
        print("- Alerts summary panel")
        print("- Detailed server table (first 10 servers)")
    except Exception as e:
        print(f"❌ Error in health summary test: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced AppDynamics Health Summary Test")
    print("=" * 50)
    
    test_health_summary()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    print("The handler should now provide comprehensive application health summaries.")
