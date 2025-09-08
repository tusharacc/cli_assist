#!/usr/bin/env python3
"""Debug command extraction to see exactly what's happening"""

import sys
from pathlib import Path
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console

def debug_command_extraction():
    """Debug the exact command extraction logic"""
    console = Console()
    console.print("🔧 Debugging Command Extraction Logic", style="bold yellow")
    
    # Simulate the exact logic from _detect_command_intent
    shell_patterns = [
        r'^(run|execute|shell)\s+(.+)',
        r'^(ls|dir|cd|pwd|mkdir|rmdir|cp|mv|rm|del)(\s+.*)?$',
        r'^(git|npm|pip|python|node|java|gcc|make|cmake|docker|kubectl)\s+.*',
        r'^(curl|wget|ssh|scp|rsync)\s+.*',
        r'^(ps|top|htop|kill|killall|chmod|chown|sudo)\s*.*',
        r'^(cat|grep|find|sort|wc|head|tail|less|more)\s+.*',
        r'^(echo|printf|which|whereis|whoami|date|uptime)\s*.*'
    ]
    
    test_cases = [
        "execute app.py",
        "execute the file app.py",
        "run script.py",
        "shell python main.py"
    ]
    
    for user_input in test_cases:
        console.print(f"\n📝 Testing: '{user_input}'")
        lower_input = user_input.lower()
        
        for i, pattern in enumerate(shell_patterns):
            match = re.search(pattern, lower_input)
            if match:
                console.print(f"   ✅ Matched pattern {i+1}: {pattern}")
                console.print(f"   Groups: {match.groups()}")
                
                # Extract command logic
                if pattern.startswith(r'^(run|execute|shell)'):
                    command = match.group(2) if len(match.groups()) >= 2 else user_input
                else:
                    command = user_input
                
                console.print(f"   Raw extracted command: '{command}'")
                
                # Apply our simplified fix
                command = command.strip()
                if '.py' in command and not command.startswith('python '):
                    console.print(f"   🔍 Attempting Python fix for: '{command}'")
                    # Extract Python filename from command using regex
                    py_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*\.py)', command)
                    console.print(f"   🔍 Regex search result: {py_match}")
                    if py_match:
                        py_filename = py_match.group(1)
                        command = f"python {py_filename}"
                        console.print(f"   ✅ Fixed: '{command}'")
                    else:
                        console.print(f"   ❌ No .py filename found in: '{command}'")
                else:
                    console.print(f"   → Final command: '{command}'")
                break
        else:
            console.print(f"   ❌ No pattern matched")

if __name__ == "__main__":
    debug_command_extraction()