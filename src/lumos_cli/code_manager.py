"""
Code Management System for Lumos CLI
Handles code generation, editing, testing, refactoring, and analysis
"""

import os
import subprocess
import ast
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from .client import LLMRouter
from .safety import SafeFileEditor
from .file_discovery import SmartFileDiscovery
from .debug_logger import debug_logger

console = Console()

@dataclass
class CodeAnalysis:
    """Results of code analysis"""
    complexity: int
    lines_of_code: int
    functions: int
    classes: int
    imports: int
    issues: List[str]
    suggestions: List[str]

@dataclass
class TestResult:
    """Results of test execution"""
    passed: int
    failed: int
    skipped: int
    errors: List[str]
    coverage: Optional[float] = None

class CodeManager:
    """Comprehensive code management system"""
    
    def __init__(self, backend: str = "auto", model: str = "devstral"):
        self.router = LLMRouter(backend, model)
        self.editor = SafeFileEditor()
        self.file_discovery = SmartFileDiscovery(".", console)
        
    def generate_code(self, specification: str, file_path: str = None, language: str = "python") -> Dict[str, Any]:
        """Generate new code from specifications"""
        debug_logger.log_function_call("CodeManager.generate_code", {
            "specification": specification,
            "file_path": file_path,
            "language": language
        })
        
        console.print(f"[cyan]🔧 Generating {language} code...[/cyan]")
        
        # Create generation prompt
        prompt = f"""Generate {language} code based on the following specification:

SPECIFICATION:
{specification}

REQUIREMENTS:
1. Write clean, production-ready code
2. Follow best practices for {language}
3. Include proper error handling
4. Add appropriate comments and docstrings
5. Use modern language features where applicable
6. Return ONLY the code, no explanations

LANGUAGE GUIDELINES:
{self._get_language_guidelines(language)}

Return the complete code file content:"""

        messages = [{"role": "user", "content": prompt}]
        code = self.router.chat(messages)
        
        # Determine file path if not provided
        if not file_path:
            file_path = self._suggest_file_path(specification, language)
        
        # Save the generated code
        success = self.editor.safe_write(file_path, code, preview=True)
        
        result = {
            "file_path": file_path,
            "code": code,
            "success": success,
            "language": language
        }
        
        debug_logger.log_function_return("CodeManager.generate_code", result)
        return result
    
    def edit_code(self, instruction: str, file_path: str = None) -> Dict[str, Any]:
        """Edit existing code (enhanced version of /edit)"""
        debug_logger.log_function_call("CodeManager.edit_code", {
            "instruction": instruction,
            "file_path": file_path
        })
        
        # Use existing edit functionality but with enhancements
        if not file_path:
            console.print(f"[cyan]🔍 Smart File Discovery:[/cyan] Looking for files to: {instruction}")
            suggested_files = self.file_discovery.suggest_files_for_instruction(instruction)
            
            if not suggested_files:
                console.print("[red]❌ No relevant files found for your instruction.[/red]")
                return {"success": False, "error": "No files found"}
            
            file_path = suggested_files[0]
            console.print(f"[green]✓[/green] Selected: {file_path}")
        
        # Read current file
        try:
            with open(file_path, 'r') as f:
                current_content = f.read()
        except FileNotFoundError:
            console.print(f"[red]❌ File not found: {file_path}[/red]")
            return {"success": False, "error": "File not found"}
        
        # Enhanced edit prompt
        system_prompt = f"""You are an expert code editor. Modify the following {self._get_file_language(file_path)} file according to the user's instruction.

CRITICAL RULES:
1. Return ONLY the complete file content as it should be written
2. Do NOT include markdown code blocks (```python, ```, etc.)
3. Do NOT include explanations or comments about the changes
4. Keep changes minimal and focused on the specific instruction
5. Maintain existing code style and patterns
6. Preserve all existing functionality unless explicitly asked to change it
7. Add proper error handling if requested
8. Follow the language's best practices

CURRENT FILE CONTENT:
{current_content}

INSTRUCTION: {instruction}

Return the complete updated file content:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": instruction}
        ]
        
        new_content = self.router.chat(messages)
        
        # Save with preview
        success = self.editor.safe_write(file_path, new_content, preview=True)
        
        result = {
            "file_path": file_path,
            "success": success,
            "changes": self._get_diff_summary(current_content, new_content)
        }
        
        debug_logger.log_function_return("CodeManager.edit_code", result)
        return result
    
    def generate_tests(self, file_path: str, test_type: str = "unit") -> Dict[str, Any]:
        """Generate tests for existing code"""
        debug_logger.log_function_call("CodeManager.generate_tests", {
            "file_path": file_path,
            "test_type": test_type
        })
        
        console.print(f"[cyan]🧪 Generating {test_type} tests for {file_path}...[/cyan]")
        
        # Read the source file
        try:
            with open(file_path, 'r') as f:
                source_code = f.read()
        except FileNotFoundError:
            console.print(f"[red]❌ File not found: {file_path}[/red]")
            return {"success": False, "error": "File not found"}
        
        # Generate test file path
        test_file_path = self._get_test_file_path(file_path)
        
        # Create test generation prompt
        prompt = f"""Generate comprehensive {test_type} tests for the following {self._get_file_language(file_path)} code:

SOURCE CODE:
{source_code}

REQUIREMENTS:
1. Write comprehensive test cases covering all functions and methods
2. Include edge cases and error conditions
3. Use appropriate testing framework for {self._get_file_language(file_path)}
4. Follow testing best practices
5. Include setup and teardown if needed
6. Add descriptive test names and docstrings
7. Mock external dependencies appropriately

TESTING FRAMEWORK GUIDELINES:
{self._get_testing_framework_guidelines(self._get_file_language(file_path))}

Return the complete test file content:"""

        messages = [{"role": "user", "content": prompt}]
        test_code = self.router.chat(messages)
        
        # Save test file
        success = self.editor.safe_write(test_file_path, test_code, preview=True)
        
        result = {
            "test_file_path": test_file_path,
            "test_code": test_code,
            "success": success,
            "test_type": test_type
        }
        
        debug_logger.log_function_return("CodeManager.generate_tests", result)
        return result
    
    def run_tests(self, test_path: str = None, coverage: bool = True) -> TestResult:
        """Run tests and return results"""
        debug_logger.log_function_call("CodeManager.run_tests", {
            "test_path": test_path,
            "coverage": coverage
        })
        
        console.print(f"[cyan]🧪 Running tests...[/cyan]")
        
        # Find test files if not specified
        if not test_path:
            test_files = self._find_test_files()
            if not test_files:
                console.print("[red]❌ No test files found[/red]")
                return TestResult(0, 0, 0, ["No test files found"])
        else:
            test_files = [test_path]
        
        # Run tests based on language
        language = self._get_file_language(test_files[0])
        result = self._execute_tests(test_files, language, coverage)
        
        debug_logger.log_function_return("CodeManager.run_tests", result)
        return result
    
    def analyze_code(self, file_path: str) -> CodeAnalysis:
        """Analyze code quality and complexity"""
        debug_logger.log_function_call("CodeManager.analyze_code", {
            "file_path": file_path
        })
        
        console.print(f"[cyan]📊 Analyzing code: {file_path}[/cyan]")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            console.print(f"[red]❌ File not found: {file_path}[/red]")
            return CodeAnalysis(0, 0, 0, 0, 0, ["File not found"], [])
        
        # Basic analysis
        lines = len(content.splitlines())
        functions = len(re.findall(r'def\s+\w+', content))
        classes = len(re.findall(r'class\s+\w+', content))
        imports = len(re.findall(r'^import\s+|^from\s+', content, re.MULTILINE))
        
        # Complexity analysis (simplified)
        complexity = self._calculate_complexity(content)
        
        # Find issues
        issues = self._find_code_issues(content, file_path)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(content, file_path)
        
        result = CodeAnalysis(
            complexity=complexity,
            lines_of_code=lines,
            functions=functions,
            classes=classes,
            imports=imports,
            issues=issues,
            suggestions=suggestions
        )
        
        debug_logger.log_function_return("CodeManager.analyze_code", result)
        return result
    
    def refactor_code(self, file_path: str, refactor_type: str = "general") -> Dict[str, Any]:
        """Refactor code for better quality"""
        debug_logger.log_function_call("CodeManager.refactor_code", {
            "file_path": file_path,
            "refactor_type": refactor_type
        })
        
        console.print(f"[cyan]🔧 Refactoring code: {file_path}[/cyan]")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            console.print(f"[red]❌ File not found: {file_path}[/red]")
            return {"success": False, "error": "File not found"}
        
        # Create refactoring prompt
        prompt = f"""Refactor the following {self._get_file_language(file_path)} code for better quality:

CURRENT CODE:
{content}

REFACTORING TYPE: {refactor_type}

REQUIREMENTS:
1. Improve code readability and maintainability
2. Follow SOLID principles
3. Reduce complexity where possible
4. Improve naming conventions
5. Add proper error handling
6. Optimize performance where appropriate
7. Maintain existing functionality
8. Follow language best practices

Return the refactored code:"""

        messages = [{"role": "user", "content": prompt}]
        refactored_code = self.router.chat(messages)
        
        # Save with preview
        success = self.editor.safe_write(file_path, refactored_code, preview=True)
        
        result = {
            "file_path": file_path,
            "success": success,
            "refactor_type": refactor_type,
            "changes": self._get_diff_summary(content, refactored_code)
        }
        
        debug_logger.log_function_return("CodeManager.refactor_code", result)
        return result
    
    def generate_docs(self, file_path: str, doc_type: str = "api") -> Dict[str, Any]:
        """Generate documentation for code"""
        debug_logger.log_function_call("CodeManager.generate_docs", {
            "file_path": file_path,
            "doc_type": doc_type
        })
        
        console.print(f"[cyan]📚 Generating {doc_type} documentation...[/cyan]")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            console.print(f"[red]❌ File not found: {file_path}[/red]")
            return {"success": False, "error": "File not found"}
        
        # Create documentation prompt
        prompt = f"""Generate {doc_type} documentation for the following {self._get_file_language(file_path)} code:

SOURCE CODE:
{content}

DOCUMENTATION TYPE: {doc_type}

REQUIREMENTS:
1. Create comprehensive documentation
2. Include function/method descriptions
3. Document parameters and return values
4. Add usage examples
5. Include error handling documentation
6. Follow documentation standards for {self._get_file_language(file_path)}
7. Make it clear and easy to understand

Return the documentation:"""

        messages = [{"role": "user", "content": prompt}]
        documentation = self.router.chat(messages)
        
        # Save documentation
        doc_file_path = self._get_doc_file_path(file_path, doc_type)
        success = self.editor.safe_write(doc_file_path, documentation, preview=True)
        
        result = {
            "doc_file_path": doc_file_path,
            "documentation": documentation,
            "success": success,
            "doc_type": doc_type
        }
        
        debug_logger.log_function_return("CodeManager.generate_docs", result)
        return result
    
    def format_code(self, file_path: str) -> Dict[str, Any]:
        """Format and lint code"""
        debug_logger.log_function_call("CodeManager.format_code", {
            "file_path": file_path
        })
        
        console.print(f"[cyan]🎨 Formatting code: {file_path}[/cyan]")
        
        language = self._get_file_language(file_path)
        formatter = self._get_formatter(language)
        
        if not formatter:
            console.print(f"[yellow]⚠️ No formatter available for {language}[/yellow]")
            return {"success": False, "error": f"No formatter for {language}"}
        
        # Run formatter
        try:
            result = subprocess.run(formatter + [file_path], capture_output=True, text=True)
            if result.returncode == 0:
                console.print(f"[green]✅ Code formatted successfully[/green]")
                return {"success": True, "output": result.stdout}
            else:
                console.print(f"[red]❌ Formatting failed: {result.stderr}[/red]")
                return {"success": False, "error": result.stderr}
        except FileNotFoundError:
            console.print(f"[red]❌ Formatter not found: {formatter[0]}[/red]")
            return {"success": False, "error": f"Formatter not found: {formatter[0]}"}
    
    def validate_code(self, file_path: str) -> Dict[str, Any]:
        """Validate code syntax and style"""
        debug_logger.log_function_call("CodeManager.validate_code", {
            "file_path": file_path
        })
        
        console.print(f"[cyan]✅ Validating code: {file_path}[/cyan]")
        
        language = self._get_file_language(file_path)
        linter = self._get_linter(language)
        
        if not linter:
            console.print(f"[yellow]⚠️ No linter available for {language}[/yellow]")
            return {"success": False, "error": f"No linter for {language}"}
        
        # Run linter
        try:
            result = subprocess.run(linter + [file_path], capture_output=True, text=True)
            if result.returncode == 0:
                console.print(f"[green]✅ Code validation passed[/green]")
                return {"success": True, "output": result.stdout}
            else:
                console.print(f"[yellow]⚠️ Validation warnings: {result.stderr}[/yellow]")
                return {"success": True, "warnings": result.stderr, "output": result.stdout}
        except FileNotFoundError:
            console.print(f"[red]❌ Linter not found: {linter[0]}[/red]")
            return {"success": False, "error": f"Linter not found: {linter[0]}"}
    
    # Helper methods
    def _get_language_guidelines(self, language: str) -> str:
        """Get language-specific coding guidelines"""
        guidelines = {
            "python": "Follow PEP8, use type hints, write docstrings, use f-strings",
            "javascript": "Use ES6+, async/await, const/let, arrow functions, JSDoc",
            "typescript": "Use strict types, interfaces, generics, JSDoc comments",
            "go": "Use gofmt, short names, error handling, interfaces",
            "java": "Use camelCase, proper OOP, Javadoc, modern Java features",
            "cpp": "Use modern C++, RAII, smart pointers, const correctness"
        }
        return guidelines.get(language, "Follow language best practices")
    
    def _get_testing_framework_guidelines(self, language: str) -> str:
        """Get testing framework guidelines"""
        frameworks = {
            "python": "Use pytest, unittest, or doctest. Mock external dependencies with unittest.mock",
            "javascript": "Use Jest, Mocha, or Jasmine. Mock with jest.fn() or sinon",
            "typescript": "Use Jest with TypeScript, or Vitest. Mock with jest.fn()",
            "go": "Use testing package, testify for assertions, mockery for mocks",
            "java": "Use JUnit 5, Mockito for mocks, AssertJ for assertions",
            "cpp": "Use Google Test, Catch2, or Boost.Test"
        }
        return frameworks.get(language, "Use appropriate testing framework")
    
    def _get_file_language(self, file_path: str) -> str:
        """Detect file language from extension"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.rs': 'rust'
        }
        return language_map.get(ext, 'python')
    
    def _suggest_file_path(self, specification: str, language: str) -> str:
        """Suggest file path based on specification"""
        # Simple heuristic - could be enhanced with LLM
        if "test" in specification.lower():
            return f"test_{language}.{self._get_extension(language)}"
        elif "main" in specification.lower():
            return f"main.{self._get_extension(language)}"
        else:
            return f"generated.{self._get_extension(language)}"
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'go': 'go',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'csharp': 'cs',
            'php': 'php',
            'ruby': 'rb',
            'rust': 'rs'
        }
        return extensions.get(language, 'py')
    
    def _get_test_file_path(self, file_path: str) -> str:
        """Generate test file path"""
        path = Path(file_path)
        return str(path.parent / f"test_{path.name}")
    
    def _get_doc_file_path(self, file_path: str, doc_type: str) -> str:
        """Generate documentation file path"""
        path = Path(file_path)
        if doc_type == "api":
            return str(path.parent / f"{path.stem}_api.md")
        else:
            return str(path.parent / f"{path.stem}_docs.md")
    
    def _find_test_files(self) -> List[str]:
        """Find test files in current directory"""
        test_files = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if (file.startswith("test_") or file.endswith("_test.py") or 
                    file.endswith(".test.js") or file.endswith(".spec.js")):
                    test_files.append(os.path.join(root, file))
        return test_files
    
    def _execute_tests(self, test_files: List[str], language: str, coverage: bool) -> TestResult:
        """Execute tests and return results"""
        if language == "python":
            return self._run_python_tests(test_files, coverage)
        elif language in ["javascript", "typescript"]:
            return self._run_js_tests(test_files, coverage)
        else:
            return TestResult(0, 0, 0, [f"No test runner for {language}"])
    
    def _run_python_tests(self, test_files: List[str], coverage: bool) -> TestResult:
        """Run Python tests with pytest"""
        cmd = ["python", "-m", "pytest"]
        if coverage:
            cmd.extend(["--cov", "--cov-report=term"])
        cmd.extend(test_files)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            # Parse pytest output (simplified)
            passed = result.stdout.count("PASSED")
            failed = result.stdout.count("FAILED")
            skipped = result.stdout.count("SKIPPED")
            
            return TestResult(passed, failed, skipped, [])
        except FileNotFoundError:
            return TestResult(0, 0, 0, ["pytest not found"])
    
    def _run_js_tests(self, test_files: List[str], coverage: bool) -> TestResult:
        """Run JavaScript/TypeScript tests"""
        # Try different test runners
        runners = ["npm test", "yarn test", "jest"]
        for runner in runners:
            try:
                result = subprocess.run(runner.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse output (simplified)
                    passed = result.stdout.count("✓") or result.stdout.count("PASS")
                    failed = result.stdout.count("✗") or result.stdout.count("FAIL")
                    return TestResult(passed, failed, 0, [])
            except FileNotFoundError:
                continue
        
        return TestResult(0, 0, 0, ["No test runner found"])
    
    def _calculate_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity (simplified)"""
        # Count decision points
        complexity = 1  # Base complexity
        complexity += len(re.findall(r'\bif\b|\bwhile\b|\bfor\b|\bexcept\b|\bcase\b', content))
        complexity += len(re.findall(r'\band\b|\bor\b', content))
        return complexity
    
    def _find_code_issues(self, content: str, file_path: str) -> List[str]:
        """Find potential code issues"""
        issues = []
        
        # Check for common issues
        if len(content.splitlines()) > 1000:
            issues.append("File is very long (>1000 lines)")
        
        if content.count('\n') > 0 and content.count('\n') / len(content.splitlines()) > 0.1:
            issues.append("High comment ratio")
        
        if re.search(r'print\s*\(', content):
            issues.append("Contains print statements (consider logging)")
        
        if re.search(r'# TODO|# FIXME|# HACK', content):
            issues.append("Contains TODO/FIXME/HACK comments")
        
        return issues
    
    def _generate_suggestions(self, content: str, file_path: str) -> List[str]:
        """Generate code improvement suggestions"""
        suggestions = []
        
        if not re.search(r'def\s+\w+.*->\s*\w+', content):
            suggestions.append("Consider adding type hints to functions")
        
        if not re.search(r'""".*"""', content, re.DOTALL):
            suggestions.append("Add docstrings to functions and classes")
        
        if re.search(r'except\s*:', content):
            suggestions.append("Use specific exception types instead of bare except")
        
        return suggestions
    
    def _get_diff_summary(self, old_content: str, new_content: str) -> str:
        """Get summary of changes between old and new content"""
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        added = len(new_lines) - len(old_lines)
        if added > 0:
            return f"Added {added} lines"
        elif added < 0:
            return f"Removed {abs(added)} lines"
        else:
            return "Modified existing lines"
    
    def _get_formatter(self, language: str) -> List[str]:
        """Get formatter command for language"""
        formatters = {
            "python": ["black"],
            "javascript": ["prettier", "--write"],
            "typescript": ["prettier", "--write"],
            "go": ["gofmt", "-w"],
            "java": ["google-java-format", "-i"],
            "cpp": ["clang-format", "-i"]
        }
        return formatters.get(language)
    
    def _get_linter(self, language: str) -> List[str]:
        """Get linter command for language"""
        linters = {
            "python": ["flake8"],
            "javascript": ["eslint"],
            "typescript": ["eslint"],
            "go": ["golint"],
            "java": ["checkstyle"],
            "cpp": ["cppcheck"]
        }
        return linters.get(language)
