#!/usr/bin/env python3
"""Run all Lumos CLI tests and show configuration status"""

import sys
from pathlib import Path
import subprocess
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from test_utils import print_configuration_status, get_configuration_status
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_test_file(test_file):
    """Run a single test file and return results"""
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=60)
        return {
            'file': test_file,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'file': test_file,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Test timed out after 60 seconds',
            'success': False
        }
    except Exception as e:
        return {
            'file': test_file,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }

def main():
    """Run all tests and show results"""
    console.print(Panel.fit("🧪 Lumos CLI Test Suite", style="bold blue"))
    
    # Show configuration status first
    console.print("\n📊 Configuration Status:")
    config_status = get_configuration_status()
    print_configuration_status()
    
    # Find all test files
    test_files = []
    for file in Path('.').glob('test_*.py'):
        if file.name != 'test_utils.py':  # Skip our utility file
            test_files.append(str(file))
    
    test_files.sort()
    
    console.print(f"\n🔍 Found {len(test_files)} test files to run")
    console.print("="*60)
    
    # Run tests
    results = []
    for test_file in test_files:
        console.print(f"\n▶️  Running {test_file}...")
        result = run_test_file(test_file)
        results.append(result)
        
        if result['success']:
            console.print(f"✅ {test_file} - PASSED")
        else:
            console.print(f"❌ {test_file} - FAILED (exit code: {result['returncode']})")
            if result['stderr']:
                console.print(f"   Error: {result['stderr'][:200]}...")
    
    # Summary
    console.print("\n" + "="*60)
    console.print("📈 Test Summary", style="bold")
    
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    console.print(f"✅ Passed: {passed}")
    console.print(f"❌ Failed: {failed}")
    console.print(f"📊 Total: {len(results)}")
    
    # Show failed tests
    if failed > 0:
        console.print("\n❌ Failed Tests:")
        for result in results:
            if not result['success']:
                console.print(f"   • {result['file']} (exit code: {result['returncode']})")
    
    # Show configuration recommendations
    console.print("\n💡 Configuration Recommendations:")
    if not config_status['github']:
        console.print("   • Run 'lumos-cli github config' to configure GitHub")
    if not config_status['jenkins']:
        console.print("   • Run 'lumos-cli jenkins config' to configure Jenkins")
    if not config_status['jira']:
        console.print("   • Run 'lumos-cli jira config' to configure Jira")
    if not config_status['enterprise_llm']:
        console.print("   • Run 'lumos-cli enterprise-llm config' to configure Enterprise LLM")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
