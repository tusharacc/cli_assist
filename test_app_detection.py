#!/usr/bin/env python3
"""Test current application execution detection capabilities"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.cli import _auto_detect_start_command
from lumos_cli.persona_manager import PersonaManager
from rich.console import Console

def test_current_detection():
    """Test what the current system can detect"""
    console = Console()
    console.print("🔍 Testing Current Application Execution Detection", style="bold blue")
    console.print("=" * 60)
    
    # Get project context
    persona_manager = PersonaManager()
    context = persona_manager.get_project_context(".")
    
    console.print(f"\n📋 Detected Project Context:")
    console.print(f"   Languages: {context.primary_languages}")
    console.print(f"   Frameworks: {context.frameworks}")
    console.print(f"   Dependencies: {len(context.dependencies)} detected")
    console.print(f"   Confidence: {context.confidence_score:.1%}")
    
    # Test auto-detect start command
    detected_command = _auto_detect_start_command(context)
    
    console.print(f"\n🚀 Auto-detected Start Command:")
    if detected_command:
        console.print(f"   ✅ {detected_command}")
    else:
        console.print(f"   ❌ No start command detected")
    
    # Test specific scenarios
    console.print(f"\n🧪 Testing Specific Scenarios:")
    
    import os
    existing_files = []
    test_files = [
        'app.py', 'main.py', 'server.py', 'manage.py',
        'app.js', 'server.js', 'index.js', 'package.json',
        'requirements.txt', 'setup.py', 'Dockerfile',
        'demo_app.py'  # We know this exists
    ]
    
    for file in test_files:
        if os.path.exists(file):
            existing_files.append(file)
    
    console.print(f"   📁 Found executable files: {existing_files}")
    
    return context, detected_command, existing_files

def test_framework_specific_detection():
    """Test framework-specific execution patterns"""
    console = Console()
    console.print("\n🏗️ Framework-Specific Execution Patterns", style="bold yellow")
    console.print("=" * 50)
    
    # Simulate different project types
    framework_patterns = {
        'Python Flask': {
            'files': ['app.py'],
            'content_patterns': ['Flask', 'app.run()'],
            'expected_command': 'python app.py'
        },
        'Python Django': {
            'files': ['manage.py'],
            'content_patterns': ['django'],
            'expected_command': 'python manage.py runserver'
        },
        'Node.js Express': {
            'files': ['package.json', 'server.js'],
            'package_scripts': {'start': 'node server.js'},
            'expected_command': 'npm start'
        },
        'Python FastAPI': {
            'files': ['main.py'],
            'content_patterns': ['FastAPI', 'uvicorn'],
            'expected_command': 'uvicorn main:app --reload'
        },
        'React': {
            'files': ['package.json'],
            'package_scripts': {'start': 'react-scripts start'},
            'expected_command': 'npm start'
        }
    }
    
    for framework, pattern in framework_patterns.items():
        console.print(f"\n📦 {framework}:")
        console.print(f"   Files: {pattern['files']}")
        if 'expected_command' in pattern:
            console.print(f"   Expected: {pattern['expected_command']}")

def suggest_enhancements():
    """Suggest enhancements to the current system"""
    console = Console()
    console.print("\n💡 Suggested Enhancements", style="bold green")
    console.print("=" * 40)
    
    enhancements = [
        "🔍 **Smarter Python Detection**",
        "   • Detect main entry point from __name__ == '__main__'",
        "   • Check for if __name__ == '__main__': patterns", 
        "   • Scan for main() function definitions",
        "   • Detect FastAPI/Uvicorn patterns: uvicorn main:app",
        "",
        "📦 **Enhanced Package.json Support**",
        "   • Priority: dev > start > serve > build",
        "   • Detect custom scripts beyond common ones",
        "   • Framework-specific patterns (React, Vue, Angular)",
        "",
        "🏗️ **Extended Framework Detection**",
        "   • Go: detect main.go, go run/build patterns",
        "   • Rust: detect main.rs, cargo run patterns", 
        "   • Java: detect Main class, mvn/gradle patterns",
        "   • Docker: detect Dockerfile, docker run patterns",
        "",
        "🧠 **Context-Aware Intelligence**",
        "   • Ask user for confirmation of detected command",
        "   • Learn from user corrections and preferences",
        "   • Provide multiple options when ambiguous",
        "   • Remember project-specific execution preferences",
        "",
        "🔧 **Enhanced Error Handling**",
        "   • Detect missing dependencies and suggest installation",
        "   • Provide setup instructions for detected frameworks",
        "   • Smart error recovery with alternative commands"
    ]
    
    for enhancement in enhancements:
        if enhancement.startswith("   "):
            console.print(enhancement, style="dim")
        elif enhancement == "":
            console.print()
        else:
            console.print(enhancement)

if __name__ == "__main__":
    console = Console()
    
    # Test current capabilities
    context, command, files = test_current_detection()
    
    # Test framework patterns
    test_framework_specific_detection()
    
    # Suggest improvements
    suggest_enhancements()
    
    # Summary
    console.print("\n" + "="*60)
    console.print("📊 Current Capability Assessment", style="bold cyan")
    console.print("="*60)
    
    if command:
        console.print(f"✅ Successfully detected: {command}")
    else:
        console.print("❌ Could not auto-detect execution command")
    
    console.print(f"📁 Project has {len(files)} executable files")
    console.print(f"🎯 Detection confidence: {context.confidence_score:.1%}")
    
    console.print("\n🚀 Recommendation:")
    if context.confidence_score > 0.7:
        console.print("   Current detection is good but can be enhanced")
    else:
        console.print("   Detection needs significant improvement")
        
    console.print("   Focus on: Python entry point detection, package.json script priorities")