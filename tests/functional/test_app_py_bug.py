#!/usr/bin/env python3
"""Test to reproduce the app.py execution bug"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.cli import _detect_command_intent, _auto_detect_start_command
from lumos_cli.persona_manager import PersonaManager
from lumos_cli.app_detector import EnhancedAppDetector
from rich.console import Console

def test_app_py_command_detection():
    """Test how various app.py related commands are detected"""
    console = Console()
    console.print("🔍 Testing app.py Command Detection Bug", style="bold red")
    console.print("=" * 60)
    
    # Test cases that should result in python app.py
    test_cases = [
        "execute app.py",
        "run app.py", 
        "start app.py",
        "python app.py",
        "execute the file app.py",  # The problematic case
        "run the app.py file",
        "start the application app.py"
    ]
    
    for test_input in test_cases:
        console.print(f"\n📝 Input: '{test_input}'")
        
        # Test command intent detection
        detected = _detect_command_intent(test_input)
        console.print(f"   Intent Type: {detected['type']}")
        
        if detected['type'] == 'shell':
            console.print(f"   🖥️  Shell Command: {detected.get('command', 'N/A')}")
            if detected.get('command') == 'app.py':
                console.print(f"   🚨 BUG FOUND: Should be 'python app.py', not 'app.py'", style="bold red")
            elif detected.get('command') == 'python app.py':
                console.print(f"   ✅ Correct: 'python app.py'", style="green")
        elif detected['type'] == 'start':
            console.print(f"   🚀 Start Command: {detected.get('instruction', 'N/A')}")
        else:
            console.print(f"   💬 Other: {detected.get('instruction', 'N/A')}")

def test_enhanced_app_detector():
    """Test if enhanced app detector correctly handles app.py"""
    console = Console()
    console.print(f"\n🧠 Testing Enhanced App Detector", style="bold blue")
    console.print("-" * 50)
    
    detector = EnhancedAppDetector(".")
    app_context = detector.detect_execution_options()
    
    # Find app.py specific options
    app_py_options = [opt for opt in app_context.all_options if 'app.py' in opt.command]
    
    console.print(f"📊 Found {len(app_py_options)} options for app.py:")
    for option in app_py_options:
        console.print(f"   • {option.command} (confidence: {option.confidence:.1%})")
        if option.command == 'app.py':
            console.print(f"     🚨 BUG: Missing 'python' prefix!", style="bold red")
        elif option.command == 'python app.py':
            console.print(f"     ✅ Correct command format", style="green")

def test_start_command_detection():
    """Test what the start command auto-detection returns"""
    console = Console()
    console.print(f"\n🚀 Testing Start Command Auto-Detection", style="bold yellow")
    console.print("-" * 50)
    
    # Get project context
    persona_manager = PersonaManager()
    context = persona_manager.get_project_context(".")
    
    # Test auto-detect start command
    detected_command = _auto_detect_start_command(context)
    
    console.print(f"📋 Project Context:")
    console.print(f"   Languages: {context.primary_languages}")
    console.print(f"   Frameworks: {context.frameworks}")
    
    console.print(f"\n🎯 Auto-detected Start Command: {detected_command}")
    
    if detected_command and 'app.py' in detected_command:
        if detected_command == 'app.py':
            console.print(f"🚨 BUG CONFIRMED: Returns 'app.py' instead of 'python app.py'", style="bold red")
        elif detected_command == 'python app.py':
            console.print(f"✅ Working correctly: 'python app.py'", style="green")

if __name__ == "__main__":
    test_app_py_command_detection()
    test_enhanced_app_detector()
    test_start_command_detection()
    
    console = Console()
    console.print("\n" + "=" * 60)
    console.print("🔍 Bug Analysis Summary", style="bold cyan")
    console.print("=" * 60)
    console.print("1. Command intent detection for 'execute app.py' type phrases")
    console.print("2. Enhanced app detector Python file handling")  
    console.print("3. Auto-start command detection priority")
    console.print("\nIf bug found, the fix should ensure Python files always get 'python' prefix")