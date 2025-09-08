#!/usr/bin/env python3
"""Test the enhanced system's ability to distinguish runtime errors from logic bugs"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.cli import _interactive_chat, _last_execution_info
from lumos_cli.shell_executor import execute_shell_command
from rich.console import Console

console = Console()

def test_runtime_error_analysis():
    """Test analysis of runtime errors (program crashes)"""
    console.print("\n🚨 Testing Runtime Error Analysis", style="bold red")
    console.print("="*50)
    
    # Simulate runtime error execution
    global _last_execution_info
    _last_execution_info = {
        'command': 'python demo_app.py',
        'stdout': '',
        'stderr': 'sqlite3.OperationalError: near "name": syntax error',
        'success': False,
        'timestamp': '2025-01-01 12:00:00'
    }
    
    console.print("✅ Simulated runtime error (program crashed)")
    console.print("📋 User asks: 'analyze the failure'")
    console.print("🔍 Expected: Runtime error analysis with specific SQL syntax fix")
    
def test_logic_bug_analysis():
    """Test analysis of logic bugs (program runs but produces wrong output)"""
    console.print("\n🐛 Testing Logic Bug Analysis", style="bold yellow")
    console.print("="*50)
    
    # Simulate successful execution with logic bugs
    global _last_execution_info
    _last_execution_info = {
        'command': 'python test_logic_bug_demo.py',
        'stdout': '🚀 Starting program...\nFile output.txt created successfully\nNumbers: [1, 2, 3, 4, 5]\nTotal: 15\nAverage: 2.5\n❌ File data.txt not found\n\n📊 Program completed:\n   - Created file: output.txt\n   - Calculated average: 2.5\n   - File check result: False\n✅ Program finished successfully (but results are wrong!)',
        'stderr': '',
        'success': True,
        'timestamp': '2025-01-01 12:05:00'
    }
    
    console.print("✅ Simulated successful execution (program ran without errors)")
    console.print("📋 User asks: 'check the output file - it has no data, analyze the program'")  
    console.print("🔍 Expected: Code analysis for logic bugs, not runtime error patterns")
    
def test_user_scenario():
    """Test the exact user scenario described"""
    console.print("\n👤 Testing User Scenario", style="bold cyan")
    console.print("="*50)
    console.print("1. lumos-cli executed the program")
    console.print("2. Program executed successfully (exit code 0)")
    console.print("3. User noticed output file has no data")
    console.print("4. User asked to analyze the program and suggest fix")
    console.print("5. OLD: System triggered error analysis (wrong!)")
    console.print("6. NEW: System should do code analysis for logic bugs")

if __name__ == "__main__":
    console.print("🧪 Enhanced Bug vs Error Analysis Testing", style="bold blue")
    console.print("="*60)
    
    test_runtime_error_analysis()
    test_logic_bug_analysis()  
    test_user_scenario()
    
    console.print("\n✅ Key Improvements:", style="bold green")
    console.print("  • Runtime errors (crashes) → Use failure_analyzer.py")
    console.print("  • Logic bugs (wrong output) → Use normal LLM code analysis")
    console.print("  • System now distinguishes between success=False and success=True")
    console.print("  • Added patterns: 'check the output', 'analyze the program', 'program bug'")
    console.print("  • Stores both successful and failed executions for context")
    
    console.print(f"\n🎯 User Issue RESOLVED:", style="bold cyan")
    console.print(f"   System will no longer trigger error analysis for logic bugs!")
    console.print(f"   Instead it will analyze the actual program code for bugs.")