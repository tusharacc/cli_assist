#!/usr/bin/env python3
"""
Lumos CLI Test Script

Simple command-line interface for testing Lumos CLI functionality.

Usage:
    python test_lumos.py                    # Run quick smoke test
    python test_lumos.py --all              # Run all tests
    python test_lumos.py --feature github   # Test specific feature
    python test_lumos.py --quick            # Quick functionality test
    python test_lumos.py --list             # List available tests
"""

import sys
import os
import argparse
from pathlib import Path

# Add tests to path
sys.path.insert(0, str(Path(__file__).parent / "tests"))

def run_quick_test():
    """Run quick functionality test"""
    print("🚀 Running quick functionality test...")
    from quick_test import main as quick_main
    return quick_main()

def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("🧪 Running comprehensive test suite...")
    from test_runner import TestRunner
    runner = TestRunner()
    return runner.run_all_tests()

def run_feature_test(feature):
    """Run specific feature test"""
    print(f"🎯 Testing {feature} feature...")
    from test_runner import TestRunner
    runner = TestRunner()
    return runner.run_feature_test(feature)

def list_tests():
    """List available tests"""
    from test_runner import TestRunner
    runner = TestRunner()
    runner.list_categories()

def main():
    parser = argparse.ArgumentParser(description="Lumos CLI Test Script")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--feature", type=str, help="Test specific feature")
    parser.add_argument("--quick", action="store_true", help="Run quick test")
    parser.add_argument("--list", action="store_true", help="List available tests")
    
    args = parser.parse_args()
    
    if args.list:
        list_tests()
        return
    
    if args.quick:
        success = run_quick_test()
    elif args.all:
        success = run_comprehensive_test()
    elif args.feature:
        success = run_feature_test(args.feature)
    else:
        # Default to quick test
        success = run_quick_test()
    
    if success:
        print("\n✅ Tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
