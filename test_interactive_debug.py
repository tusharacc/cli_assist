#!/usr/bin/env python3
"""Test enhanced interactive debugging functionality"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.cli import _is_debugging_request, _detect_command_intent
from rich.console import Console

def test_debugging_detection():
    """Test if debugging requests are properly detected"""
    console = Console()
    console.print("🧪 Testing Debugging Request Detection", style="bold blue")
    
    # Test cases for debugging detection
    test_cases = [
        # Should be detected as debugging requests
        ("My app has a bug", True),
        ("There is an error in my code", True),
        ("Why is my function not working?", True),
        ("Help me debug this issue", True),
        ("My login.py file is broken", True),
        ("I'm having trouble with authentication", True),
        ("The server crashes when I start it", True),
        ("What's wrong with my API?", True),
        ("Fix this database connection issue", True),
        ("Cannot connect to the database", True),
        
        # Should NOT be detected as debugging requests  
        ("How do I implement user authentication?", False),
        ("Plan a new feature for my app", False),
        ("What is the best way to structure my code?", False),
        ("Hello, how are you?", False),
    ]
    
    print("\n" + "="*70)
    print("Testing _is_debugging_request function:")
    print("="*70)
    
    passed = 0
    total = len(test_cases)
    
    for test_input, expected in test_cases:
        result = _is_debugging_request(test_input)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} | {test_input:<50} | Expected: {expected:<5} | Got: {result}")
        if result == expected:
            passed += 1
    
    print("="*70)
    print(f"Results: {passed}/{total} tests passed")
    
    return passed == total

def test_command_intent_detection():
    """Test command intent detection for debugging"""
    console = Console()
    
    test_cases = [
        "Fix my login bug",
        "There is an error in my app", 
        "Why doesn't my code work?",
        "Help me debug this issue",
        "My function is broken",
    ]
    
    print("\n" + "="*70)
    print("Testing _detect_command_intent function:")
    print("="*70)
    
    for test_input in test_cases:
        intent = _detect_command_intent(test_input)
        print(f"Input: {test_input}")
        print(f"Intent: {intent}")
        print("-" * 50)

def main():
    """Run all debugging detection tests"""
    console = Console()
    console.print("🔧 Enhanced Interactive Debugging Test Suite", style="bold green")
    
    # Test 1: Debugging detection
    debug_detection_passed = test_debugging_detection()
    
    # Test 2: Command intent detection
    test_command_intent_detection()
    
    # Summary
    print("\n" + "="*70)
    if debug_detection_passed:
        console.print("🎉 All debugging detection tests passed!", style="bold green")
        console.print("\n✨ Enhanced features:")
        console.print("• Lumos CLI will now automatically detect bug descriptions")
        console.print("• Smart file discovery will find relevant files")
        console.print("• Files will be read and analyzed automatically")
        console.print("• You'll get solutions based on actual code")
    else:
        console.print("⚠️ Some tests failed - debugging detection needs improvement", style="yellow")

if __name__ == "__main__":
    main()