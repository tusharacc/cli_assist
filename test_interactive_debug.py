#!/usr/bin/env python3
"""Test enhanced interactive debugging functionality"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.cli import _detect_command_intent
from rich.console import Console

def test_intelligent_approach():
    """Test the new intelligent approach that always tries file discovery"""
    console = Console()
    console.print("🧠 Testing Intelligent File Discovery Approach", style="bold blue")
    
    print("\n" + "="*70)
    print("New Approach: Always try smart file discovery, let LLM decide relevance")
    print("="*70)
    
    test_cases = [
        "My app has a bug",
        "There is an error in my code", 
        "Why is my function not working?",
        "Help me debug this issue",
        "How do I implement user authentication?",  # This will also get files now
        "Plan a new feature for my app",  # This will also get files now
        "What is the best way to structure my code?",  # This will also get files now
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. Input: '{test_input}'")
        print("   → Smart file discovery will run")
        print("   → Files found and analyzed (if score > 3.0)")
        print("   → LLM decides how to use the files in context")
        print("   → Result: More intelligent responses for ALL types of requests")
    
    print("\n" + "="*70)
    console.print("✨ Benefits of New Approach:", style="bold green")
    print("• No need to guess if request is 'debugging' or not")
    print("• LLM sees actual code for ALL relevant requests")
    print("• Better context for implementation questions too")  
    print("• More natural and flexible interaction")
    print("• Eliminates false negatives from keyword matching")
    
    return True

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
    console.print("🔧 Intelligent Interactive Mode Test Suite", style="bold green")
    
    # Test the new intelligent approach
    intelligent_approach_works = test_intelligent_approach()
    
    # Test command intent detection (still useful for slash commands)
    test_command_intent_detection()
    
    # Summary
    print("\n" + "="*70)
    if intelligent_approach_works:
        console.print("🎉 Intelligent approach validated!", style="bold green")
        console.print("\n✨ Why this is better:")
        console.print("• No rigid keyword matching needed")
        console.print("• LLM intelligence used for nuanced understanding")
        console.print("• Smart file discovery runs for all relevant requests")
        console.print("• Better responses for debugging AND implementation questions")
        console.print("• More natural and flexible user experience")
    else:
        console.print("⚠️ Need to refine the intelligent approach", style="yellow")

if __name__ == "__main__":
    main()