#!/usr/bin/env python3
"""
Lumos CLI Quick Test Script

Quick functionality tests that can be run without external dependencies.
Tests core functionality, imports, and basic CLI operations.

Usage:
    python quick_test.py
"""

import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

console = Console()

def test_imports():
    """Test that all critical modules can be imported"""
    console.print("\n🔍 Testing module imports...")
    
    import_tests = [
        ("Core Router", "from src.lumos_cli.core.router import LLMRouter, TaskType"),
        ("Core Embeddings", "from src.lumos_cli.core.embeddings import EmbeddingDB"),
        ("Core Safety", "from src.lumos_cli.core.safety import SafeFileEditor"),
        ("Core History", "from src.lumos_cli.core.history import HistoryManager"),
        ("GitHub Client", "from src.lumos_cli.clients.github_client import GitHubClient"),
        ("Jenkins Client", "from src.lumos_cli.clients.jenkins_client import JenkinsClient"),
        ("Jira Client", "from src.lumos_cli.clients.jira_client import JiraClient"),
        ("Neo4j Client", "from src.lumos_cli.clients.neo4j_client import Neo4jClient"),
        ("AppDynamics Client", "from src.lumos_cli.clients.appdynamics_client import AppDynamicsClient"),
        ("Interactive Mode", "from src.lumos_cli.interactive import interactive_mode, detect_intent"),
        ("Main CLI", "from src.lumos_cli.cli_refactored_v2 import main"),
        ("Utils", "from src.lumos_cli.utils.debug_logger import debug_logger"),
        ("Config Managers", "from src.lumos_cli.config import GitHubConfigManager, JenkinsConfigManager"),
        ("UI Components", "from src.lumos_cli.ui import console, show_footer"),
    ]
    
    results = []
    for name, import_stmt in import_tests:
        try:
            exec(import_stmt)
            results.append((name, "✅ PASS", "green"))
        except Exception as e:
            results.append((name, f"❌ FAIL: {str(e)[:50]}...", "red"))
    
    # Display results
    table = Table(title="Import Test Results")
    table.add_column("Module", style="cyan")
    table.add_column("Status", style="white")
    
    for name, status, color in results:
        table.add_row(name, f"[{color}]{status}[/{color}]")
    
    console.print(table)
    
    # Return success if all passed
    return all("PASS" in status for _, status, _ in results)

def test_cli_help():
    """Test CLI help command"""
    console.print("\n🚀 Testing CLI help command...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-m", "src.lumos_cli.cli_refactored_v2", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0 and "Lumos CLI" in result.stdout:
            console.print("  ✅ CLI help command works")
            return True
        else:
            console.print(f"  ❌ CLI help command failed: {result.stderr}")
            return False
    except Exception as e:
        console.print(f"  ❌ CLI help command error: {e}")
        return False

def test_config_managers():
    """Test configuration managers"""
    console.print("\n⚙️ Testing configuration managers...")
    
    config_tests = [
        ("GitHub Config", "from src.lumos_cli.config.github_config_manager import GitHubConfigManager"),
        ("Jenkins Config", "from src.lumos_cli.config.jenkins_config_manager import JenkinsConfigManager"),
        ("Neo4j Config", "from src.lumos_cli.config.neo4j_config import Neo4jConfigManager"),
        ("AppDynamics Config", "from src.lumos_cli.config.appdynamics_config import AppDynamicsConfigManager"),
        ("Enterprise LLM Config", "from src.lumos_cli.config.enterprise_llm_config import EnterpriseLLMConfigManager"),
    ]
    
    results = []
    for name, import_stmt in config_tests:
        try:
            exec(import_stmt)
            results.append((name, "✅ PASS", "green"))
        except Exception as e:
            results.append((name, f"❌ FAIL: {str(e)[:50]}...", "red"))
    
    # Display results
    table = Table(title="Config Manager Test Results")
    table.add_column("Manager", style="cyan")
    table.add_column("Status", style="white")
    
    for name, status, color in results:
        table.add_row(name, f"[{color}]{status}[/{color}]")
    
    console.print(table)
    
    return all("PASS" in status for _, status, _ in results)

def test_interactive_components():
    """Test interactive mode components"""
    console.print("\n💬 Testing interactive components...")
    
    interactive_tests = [
        ("Intent Detection", "from src.lumos_cli.interactive.intent_detection import detect_intent"),
        ("Interactive Mode", "from src.lumos_cli.interactive.mode import interactive_mode"),
        ("GitHub Handler", "from src.lumos_cli.interactive.handlers.github_handler import interactive_github"),
        ("Jenkins Handler", "from src.lumos_cli.interactive.handlers.jenkins_handler import interactive_jenkins"),
        ("Jira Handler", "from src.lumos_cli.interactive.handlers.jira_handler import interactive_jira"),
        ("Code Handler", "from src.lumos_cli.interactive.handlers.code_handler import interactive_code"),
    ]
    
    results = []
    for name, import_stmt in interactive_tests:
        try:
            exec(import_stmt)
            results.append((name, "✅ PASS", "green"))
        except Exception as e:
            results.append((name, f"❌ FAIL: {str(e)[:50]}...", "red"))
    
    # Display results
    table = Table(title="Interactive Components Test Results")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    
    for name, status, color in results:
        table.add_row(name, f"[{color}]{status}[/{color}]")
    
    console.print(table)
    
    return all("PASS" in status for _, status, _ in results)

def test_utils():
    """Test utility functions"""
    console.print("\n🛠️ Testing utility functions...")
    
    util_tests = [
        ("Debug Logger", "from src.lumos_cli.utils.debug_logger import debug_logger, get_debug_logger"),
        ("Platform Utils", "from src.lumos_cli.utils.platform_utils import get_platform_info, get_logs_directory"),
        ("File Discovery", "from src.lumos_cli.utils.file_discovery import SmartFileDiscovery"),
        ("Error Handler", "from src.lumos_cli.utils.error_handler import RuntimeErrorHandler"),
        ("Failure Analyzer", "from src.lumos_cli.utils.failure_analyzer import IntelligentFailureAnalyzer"),
        ("Shell Executor", "from src.lumos_cli.utils.shell_executor import execute_shell_command"),
        ("GitHub Query Parser", "from src.lumos_cli.utils.github_query_parser import GitHubQueryParser"),
    ]
    
    results = []
    for name, import_stmt in util_tests:
        try:
            exec(import_stmt)
            results.append((name, "✅ PASS", "green"))
        except Exception as e:
            results.append((name, f"❌ FAIL: {str(e)[:50]}...", "red"))
    
    # Display results
    table = Table(title="Utility Functions Test Results")
    table.add_column("Utility", style="cyan")
    table.add_column("Status", style="white")
    
    for name, status, color in results:
        table.add_row(name, f"[{color}]{status}[/{color}]")
    
    console.print(table)
    
    return all("PASS" in status for _, status, _ in results)

def main():
    """Run all quick tests"""
    console.print(Panel.fit(
        "🌟 Lumos CLI Quick Test Suite",
        style="bold blue"
    ))
    
    tests = [
        ("Module Imports", test_imports),
        ("CLI Help Command", test_cli_help),
        ("Configuration Managers", test_config_managers),
        ("Interactive Components", test_interactive_components),
        ("Utility Functions", test_utils),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, "✅ PASSED" if success else "❌ FAILED", "green" if success else "red"))
        except Exception as e:
            results.append((name, f"❌ ERROR: {str(e)[:50]}...", "red"))
    
    # Final summary
    console.print("\n📊 Quick Test Summary:")
    
    table = Table(title="Test Results")
    table.add_column("Test Category", style="cyan")
    table.add_column("Result", style="white")
    
    for name, result, color in results:
        table.add_row(name, f"[{color}]{result}[/{color}]")
    
    console.print(table)
    
    # Overall result
    all_passed = all("PASSED" in result for _, result, _ in results)
    
    if all_passed:
        console.print("\n🎉 All quick tests passed! The refactored CLI is working correctly.")
    else:
        console.print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
