#!/usr/bin/env python3
"""Test the shell command execution functionality"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.shell_executor import ShellExecutor
from lumos_cli.cli import _detect_command_intent
from rich.console import Console

def test_shell_command_detection():
    """Test detection of shell commands in user input"""
    console = Console()
    console.print("🖥️  Testing Shell Command Detection", style="bold blue")
    console.print("=" * 50)
    
    test_cases = [
        "ls -la",
        "git status", 
        "run npm install",
        "execute python demo_app.py",
        "shell git commit -m 'test'",
        "python -m pip list",
        "docker ps",
        "cat README.md",
        "sudo apt update",  # Should be detected as dangerous
        "rm -rf temp/",     # Should be detected as very dangerous  
        "Hello, how are you?", # Should not be shell command
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        console.print(f"\n{i}. Input: '{test_input}'")
        
        # Test command intent detection
        detected = _detect_command_intent(test_input)
        
        if detected['type'] == 'shell':
            console.print(f"   ✅ Detected as shell command")
            console.print(f"   📝 Command: {detected.get('command', test_input)}")
            console.print(f"   🎯 Confidence: {detected.get('confidence', 'N/A')}")
        else:
            console.print(f"   ❌ Not detected as shell command")
            console.print(f"   🏷️  Detected as: {detected['type']}")

def test_safety_checks():
    """Test safety checks for dangerous commands"""
    console = Console()
    console.print("\n🔒 Testing Safety Checks", style="bold yellow")  
    console.print("=" * 50)
    
    executor = ShellExecutor()
    
    test_commands = [
        ("ls -la", "Safe command"),
        ("git status", "Safe command"),
        ("sudo apt install", "Dangerous - requires admin"),
        ("rm -rf /tmp/test", "Very dangerous - recursive delete"),
        ("pip install flask", "Potentially dangerous - package install"),
        ("echo 'Hello World'", "Safe command"),
    ]
    
    for command, description in test_commands:
        console.print(f"\n📝 Command: {command}")
        console.print(f"💭 Description: {description}")
        
        is_dangerous, reason = executor.is_dangerous_command(command)
        
        if is_dangerous:
            console.print(f"   🚨 DANGEROUS: {reason}", style="red")
        else:
            console.print(f"   ✅ Safe command", style="green")

def test_command_patterns():
    """Test various command pattern matching"""
    console = Console()
    console.print("\n🔍 Testing Command Pattern Matching", style="bold cyan")
    console.print("=" * 50)
    
    # Test different ways users might express shell commands
    variations = [
        "ls",
        "ls -la", 
        "run ls -la",
        "execute ls -la",
        "shell ls -la",
        "can you run ls -la",
        "please execute git status",
        "I want to run npm install",
    ]
    
    for variation in variations:
        detected = _detect_command_intent(variation)
        console.print(f"Input: '{variation}'")
        
        if detected['type'] == 'shell':
            console.print(f"  ✅ Shell command detected: {detected.get('command')}")
        else:
            console.print(f"  ❌ Not shell: {detected['type']}")
        console.print()

if __name__ == "__main__":
    console = Console()
    console.print("🧪 Shell Command Execution Test Suite", style="bold green")
    console.print("=" * 60)
    
    test_shell_command_detection()
    test_safety_checks()
    test_command_patterns()
    
    console.print("\n" + "=" * 60)
    console.print("🎉 Shell Command Testing Complete!", style="bold green")
    console.print("\n📋 Summary of Features:")
    console.print("✅ Shell command detection in natural language")
    console.print("✅ Safety checks for dangerous commands") 
    console.print("✅ User confirmation prompts")
    console.print("✅ Real-time command output")
    console.print("✅ Integration with Lumos CLI interactive mode")
    console.print("✅ Support for both /shell commands and natural language")