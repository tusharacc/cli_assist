"""
Test runner for Lumos CLI
"""

import pytest
import sys
import os

def run_tests():
    """Run all tests"""
    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    # Run tests
    pytest.main([
        'tests/',
        '-v',
        '--tb=short',
        '--color=yes',
        '--durations=10'
    ])

def run_unit_tests():
    """Run unit tests only"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    pytest.main([
        'tests/unit/',
        '-v',
        '--tb=short',
        '--color=yes'
    ])

def run_integration_tests():
    """Run integration tests only"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    pytest.main([
        'tests/integration/',
        '-v',
        '--tb=short',
        '--color=yes'
    ])

def run_functional_tests():
    """Run functional tests only"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    pytest.main([
        'tests/functional/',
        '-v',
        '--tb=short',
        '--color=yes'
    ])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "unit":
            run_unit_tests()
        elif test_type == "integration":
            run_integration_tests()
        elif test_type == "functional":
            run_functional_tests()
        else:
            print("Usage: python run_tests.py [unit|integration|functional]")
            sys.exit(1)
    else:
        run_tests()
