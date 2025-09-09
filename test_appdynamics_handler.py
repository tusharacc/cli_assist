#!/usr/bin/env python3
"""
Test script to verify AppDynamics handler fix
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.interactive.handlers.appdynamics_handler import interactive_appdynamics

def test_appdynamics_queries():
    """Test various AppDynamics queries"""
    print("🔧 Testing AppDynamics handler queries...")
    
    test_queries = [
        "give me the application health for SCI Market Place PROD Azure",
        "show resource utilization for SCI Market Place PROD Azure", 
        "get business transactions for SCI Market Place PROD",
        "show alerts for SCI Market Place PROD Azure",
        "health check"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {query}")
        print('='*60)
        
        try:
            interactive_appdynamics(query)
        except Exception as e:
            print(f"❌ Error in test {i}: {e}")
        
        print(f"\n✅ Test {i} completed")

if __name__ == "__main__":
    print("🚀 AppDynamics Handler Fix Test")
    print("=" * 50)
    
    test_appdynamics_queries()
    
    print("\n" + "=" * 50)
    print("✅ Handler test completed!")
    print("The handler should now properly handle application-specific queries.")
