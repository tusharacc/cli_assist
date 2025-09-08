#!/usr/bin/env python3
"""
Lumos CLI Comprehensive Test Runner

This script provides different testing modes:
1. Full test suite - tests everything
2. Feature-specific tests - test individual components
3. Integration tests - test service integrations
4. Quick smoke tests - basic functionality check

Usage:
    python test_runner.py --all                    # Run all tests
    python test_runner.py --feature github         # Test GitHub integration
    python test_runner.py --feature jenkins        # Test Jenkins integration
    python test_runner.py --smoke                  # Quick smoke test
    python test_runner.py --interactive            # Test interactive mode
    python test_runner.py --list                   # List available test categories
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

console = Console()

class TestRunner:
    """Comprehensive test runner for Lumos CLI"""
    
    def __init__(self):
        self.test_categories = {
            "core": {
                "description": "Core functionality (router, embeddings, safety, history)",
                "tests": ["tests/unit/core/"],
                "critical": True
            },
            "clients": {
                "description": "External service clients (GitHub, Jenkins, Jira, Neo4j, AppDynamics)",
                "tests": ["tests/unit/clients/"],
                "critical": True
            },
            "interactive": {
                "description": "Interactive mode and intent detection",
                "tests": ["tests/unit/interactive/"],
                "critical": True
            },
            "github": {
                "description": "GitHub integration and API functionality",
                "tests": ["tests/functional/test_github_parsing.py", "tests/functional/test_commit_parsing_fix.py", "tests/functional/test_hybrid_github_parsing.py"],
                "critical": False
            },
            "jenkins": {
                "description": "Jenkins integration and build monitoring",
                "tests": ["tests/functional/test_jenkins_*.py"],
                "critical": False
            },
            "jira": {
                "description": "Jira integration and ticket management",
                "tests": ["tests/functional/test_jira_*.py"],
                "critical": False
            },
            "neo4j": {
                "description": "Neo4j graph database integration",
                "tests": ["tests/functional/test_neo4j_*.py"],
                "critical": False
            },
            "appdynamics": {
                "description": "AppDynamics monitoring integration",
                "tests": ["tests/functional/test_appdynamics_*.py"],
                "critical": False
            },
            "shell": {
                "description": "Shell execution and command handling",
                "tests": ["tests/functional/test_shell_*.py"],
                "critical": True
            },
            "config": {
                "description": "Configuration management and validation",
                "tests": ["tests/functional/test_*config*.py", "tests/functional/test_*env*.py"],
                "critical": True
            },
            "integration": {
                "description": "End-to-end integration tests",
                "tests": ["tests/integration/"],
                "critical": False
            }
        }
        
        self.test_results = {}
        self.start_time = None
        
    def run_command(self, command: List[str], timeout: int = 300) -> tuple:
        """Run a command and return (success, output, error)"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path(__file__).parent.parent
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)
    
    def run_pytest(self, test_paths: List[str], verbose: bool = True) -> tuple:
        """Run pytest on specific test paths"""
        cmd = ["python", "-m", "pytest"]
        if verbose:
            cmd.append("-v")
        cmd.extend(test_paths)
        
        return self.run_command(cmd, timeout=600)
    
    def test_imports(self) -> bool:
        """Test that all modules can be imported"""
        console.print("\n🔍 Testing module imports...")
        
        import_tests = [
            ("Core modules", "from src.lumos_cli.core import LLMRouter, TaskType, EmbeddingDB, SafeFileEditor, HistoryManager"),
            ("Client modules", "from src.lumos_cli.clients import GitHubClient, JenkinsClient, JiraClient, Neo4jClient, AppDynamicsClient"),
            ("Interactive mode", "from src.lumos_cli.interactive import interactive_mode, detect_intent"),
            ("Main CLI", "from src.lumos_cli.cli_refactored_v2 import main"),
            ("Utils", "from src.lumos_cli.utils import debug_logger, get_platform_info"),
            ("Config", "from src.lumos_cli.config import GitHubConfigManager, JenkinsConfigManager")
        ]
        
        all_passed = True
        for name, import_stmt in import_tests:
            try:
                exec(import_stmt)
                console.print(f"  ✅ {name}")
            except Exception as e:
                console.print(f"  ❌ {name}: {e}")
                all_passed = False
        
        return all_passed
    
    def test_cli_basic(self) -> bool:
        """Test basic CLI functionality"""
        console.print("\n🚀 Testing basic CLI functionality...")
        
        # Test help command
        success, output, error = self.run_command(["python", "-m", "src.lumos_cli.cli_refactored_v2", "--help"])
        if not success:
            console.print(f"  ❌ CLI help command failed: {error}")
            return False
        
        console.print("  ✅ CLI help command works")
        
        # Test version or basic info
        success, output, error = self.run_command(["python", "-c", "from src.lumos_cli.cli_refactored_v2 import main; print('CLI imports successfully')"])
        if not success:
            console.print(f"  ❌ CLI import failed: {error}")
            return False
        
        console.print("  ✅ CLI imports successfully")
        return True
    
    def test_interactive_mode(self) -> bool:
        """Test interactive mode startup"""
        console.print("\n💬 Testing interactive mode...")
        
        # Test interactive mode startup (with timeout)
        success, output, error = self.run_command(
            ["timeout", "10", "python", "-c", "from src.lumos_cli.interactive import interactive_mode; print('Interactive mode ready')"],
            timeout=15
        )
        
        if success or "Interactive mode ready" in output:
            console.print("  ✅ Interactive mode starts successfully")
            return True
        else:
            console.print(f"  ❌ Interactive mode failed: {error}")
            return False
    
    def run_smoke_test(self) -> bool:
        """Run quick smoke test"""
        console.print("\n🔥 Running smoke test...")
        
        tests = [
            ("Module imports", self.test_imports),
            ("CLI basic", self.test_cli_basic),
            ("Interactive mode", self.test_interactive_mode)
        ]
        
        all_passed = True
        for name, test_func in tests:
            if not test_func():
                all_passed = False
        
        return all_passed
    
    def run_feature_test(self, feature: str) -> bool:
        """Run tests for a specific feature"""
        if feature not in self.test_categories:
            console.print(f"❌ Unknown feature: {feature}")
            console.print(f"Available features: {', '.join(self.test_categories.keys())}")
            return False
        
        category = self.test_categories[feature]
        console.print(f"\n🧪 Testing {feature} feature...")
        console.print(f"Description: {category['description']}")
        
        # Run the tests
        success, output, error = self.run_pytest(category["tests"])
        
        if success:
            console.print(f"  ✅ {feature} tests passed")
            self.test_results[feature] = "PASSED"
        else:
            console.print(f"  ❌ {feature} tests failed")
            console.print(f"Error: {error}")
            self.test_results[feature] = "FAILED"
        
        return success
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        console.print("\n🚀 Running comprehensive test suite...")
        
        all_passed = True
        critical_failed = []
        
        # Run critical tests first
        for feature, category in self.test_categories.items():
            if category["critical"]:
                if not self.run_feature_test(feature):
                    all_passed = False
                    critical_failed.append(feature)
        
        # If critical tests failed, stop here
        if critical_failed:
            console.print(f"\n❌ Critical tests failed: {', '.join(critical_failed)}")
            console.print("Skipping non-critical tests due to critical failures.")
            return False
        
        # Run non-critical tests
        for feature, category in self.test_categories.items():
            if not category["critical"]:
                self.run_feature_test(feature)
        
        return all_passed
    
    def list_categories(self):
        """List all available test categories"""
        table = Table(title="Available Test Categories")
        table.add_column("Feature", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Critical", style="green" if True else "red")
        
        for feature, category in self.test_categories.items():
            critical_text = "Yes" if category["critical"] else "No"
            table.add_row(feature, category["description"], critical_text)
        
        console.print(table)
    
    def show_results(self):
        """Show test results summary"""
        if not self.test_results:
            return
        
        console.print("\n📊 Test Results Summary:")
        
        table = Table()
        table.add_column("Feature", style="cyan")
        table.add_column("Status", style="green")
        
        for feature, status in self.test_results.items():
            status_style = "green" if status == "PASSED" else "red"
            table.add_row(feature, f"[{status_style}]{status}[/{status_style}]")
        
        console.print(table)
    
    def run_interactive_test(self):
        """Interactive test selection"""
        console.print("\n🎯 Interactive Test Selection")
        
        while True:
            console.print("\nSelect test mode:")
            console.print("1. Run all tests")
            console.print("2. Run smoke test only")
            console.print("3. Test specific feature")
            console.print("4. List available features")
            console.print("5. Exit")
            
            choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])
            
            if choice == "1":
                self.run_all_tests()
                break
            elif choice == "2":
                self.run_smoke_test()
                break
            elif choice == "3":
                self.list_categories()
                feature = Prompt.ask("Enter feature name")
                self.run_feature_test(feature)
                break
            elif choice == "4":
                self.list_categories()
            elif choice == "5":
                console.print("Goodbye!")
                break
    
    def run(self, args):
        """Main run method"""
        self.start_time = time.time()
        
        console.print(Panel.fit(
            "🌟 Lumos CLI Test Runner",
            style="bold blue"
        ))
        
        if args.list:
            self.list_categories()
            return
        
        if args.smoke:
            success = self.run_smoke_test()
        elif args.all:
            success = self.run_all_tests()
        elif args.feature:
            success = self.run_feature_test(args.feature)
        elif args.interactive:
            self.run_interactive_test()
            return
        else:
            console.print("No test mode specified. Use --help for options.")
            return
        
        # Show results
        if self.test_results:
            self.show_results()
        
        # Show timing
        elapsed = time.time() - self.start_time
        console.print(f"\n⏱️  Total time: {elapsed:.2f} seconds")
        
        if not args.interactive:
            sys.exit(0 if success else 1)

def main():
    parser = argparse.ArgumentParser(description="Lumos CLI Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--smoke", action="store_true", help="Run smoke test only")
    parser.add_argument("--feature", type=str, help="Test specific feature")
    parser.add_argument("--interactive", action="store_true", help="Interactive test selection")
    parser.add_argument("--list", action="store_true", help="List available test categories")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    runner.run(args)

if __name__ == "__main__":
    main()
