#!/usr/bin/env python3
"""Intelligent failure analysis for command execution results"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console

@dataclass
class FailureAnalysis:
    """Contains detailed analysis of a command failure"""
    error_type: str
    error_message: str
    likely_cause: str
    suggested_fixes: List[str]
    code_location: Optional[str] = None
    confidence: float = 0.0

class IntelligentFailureAnalyzer:
    """Analyzes command execution failures and provides intelligent insights"""
    
    def __init__(self):
        self.console = Console()
        
        # Common error patterns and their analysis
        self.error_patterns = {
            'python': {
                'SyntaxError': {
                    'patterns': [r'SyntaxError: (.+)', r'invalid syntax'],
                    'likely_cause': 'Python syntax error in the code',
                    'fixes': [
                        'Check for missing commas, parentheses, or colons',
                        'Verify proper indentation',
                        'Look for unclosed quotes or brackets'
                    ]
                },
                'ModuleNotFoundError': {
                    'patterns': [r'ModuleNotFoundError: No module named \'(.+)\''],
                    'likely_cause': 'Missing Python module/package',
                    'fixes': [
                        'Install the missing module: pip install {module}',
                        'Check if module name is spelled correctly',
                        'Ensure virtual environment is activated if used'
                    ]
                },
                'ImportError': {
                    'patterns': [r'ImportError: (.+)'],
                    'likely_cause': 'Import statement issue',
                    'fixes': [
                        'Check if the module exists in the current environment',
                        'Verify the import path is correct',
                        'Install missing dependencies'
                    ]
                },
                'NameError': {
                    'patterns': [r'NameError: name \'(.+)\' is not defined'],
                    'likely_cause': 'Using undefined variable or function',
                    'fixes': [
                        'Check for typos in variable/function names',
                        'Ensure variables are defined before use',
                        'Import required modules/functions'
                    ]
                },
                'sqlite3.OperationalError': {
                    'patterns': [r'sqlite3\.OperationalError: (.+)'],
                    'likely_cause': 'Database operation error',
                    'fixes': [
                        'Check SQL syntax for errors',
                        'Verify database file permissions',
                        'Ensure database connection is established',
                        'Check for missing columns or tables'
                    ]
                },
                'FileNotFoundError': {
                    'patterns': [r'FileNotFoundError: \[Errno 2\] No such file or directory: \'(.+)\''],
                    'likely_cause': 'Trying to access non-existent file',
                    'fixes': [
                        'Verify the file path is correct',
                        'Check if the file exists in the expected location',
                        'Create the missing file if needed'
                    ]
                }
            },
            'javascript': {
                'ReferenceError': {
                    'patterns': [r'ReferenceError: (.+) is not defined'],
                    'likely_cause': 'Using undefined variable or function',
                    'fixes': [
                        'Declare the variable before use',
                        'Check for typos in variable names',
                        'Import required modules/functions'
                    ]
                },
                'SyntaxError': {
                    'patterns': [r'SyntaxError: (.+)'],
                    'likely_cause': 'JavaScript syntax error',
                    'fixes': [
                        'Check for missing semicolons or brackets',
                        'Verify proper function syntax',
                        'Look for unclosed strings or comments'
                    ]
                }
            },
            'system': {
                'command not found': {
                    'patterns': [r'(.+): command not found', r'\'(.+)\' is not recognized'],
                    'likely_cause': 'Command or program not installed',
                    'fixes': [
                        'Install the required program',
                        'Check if the command is in your PATH',
                        'Verify the command spelling'
                    ]
                },
                'permission denied': {
                    'patterns': [r'Permission denied', r'Access is denied'],
                    'likely_cause': 'Insufficient permissions to execute',
                    'fixes': [
                        'Run with elevated permissions (sudo/admin)',
                        'Check file permissions',
                        'Ensure you have access to the directory'
                    ]
                }
            }
        }
    
    def analyze_failure(self, command: str, stdout: str, stderr: str, exit_code: int) -> FailureAnalysis:
        """
        Analyze command failure and provide intelligent insights
        
        Args:
            command: The command that was executed
            stdout: Standard output from the command
            stderr: Standard error from the command  
            exit_code: Exit code from the command
            
        Returns:
            FailureAnalysis: Detailed analysis of the failure
        """
        # Combine all error output
        error_output = f"{stderr}\n{stdout}".strip()
        
        # Detect language/tool based on command
        language = self._detect_language(command)
        
        # Find matching error pattern
        analysis = self._match_error_patterns(error_output, language)
        
        if not analysis:
            # Generic analysis if no specific pattern matched
            analysis = self._generic_analysis(command, error_output, exit_code)
        
        # Extract code location if available
        code_location = self._extract_code_location(error_output)
        if code_location:
            analysis.code_location = code_location
        
        # Customize fixes based on the specific command
        analysis.suggested_fixes = self._customize_fixes(analysis.suggested_fixes, command, error_output)
        
        return analysis
    
    def _detect_language(self, command: str) -> str:
        """Detect the programming language/tool from command"""
        command_lower = command.lower()
        
        if command_lower.startswith('python') or '.py' in command:
            return 'python'
        elif command_lower.startswith('node') or '.js' in command:
            return 'javascript'
        elif command_lower.startswith(('npm', 'yarn')):
            return 'javascript'
        elif command_lower.startswith('java'):
            return 'java'
        else:
            return 'system'
    
    def _match_error_patterns(self, error_output: str, language: str) -> Optional[FailureAnalysis]:
        """Match error output against known patterns"""
        if language not in self.error_patterns:
            return None
        
        patterns = self.error_patterns[language]
        
        for error_type, pattern_info in patterns.items():
            for pattern in pattern_info['patterns']:
                match = re.search(pattern, error_output, re.IGNORECASE | re.MULTILINE)
                if match:
                    return FailureAnalysis(
                        error_type=error_type,
                        error_message=match.group(0) if match else error_type,
                        likely_cause=pattern_info['likely_cause'],
                        suggested_fixes=pattern_info['fixes'].copy(),
                        confidence=0.9
                    )
        
        return None
    
    def _generic_analysis(self, command: str, error_output: str, exit_code: int) -> FailureAnalysis:
        """Provide generic analysis when no specific pattern matches"""
        return FailureAnalysis(
            error_type=f"Command failure (exit code {exit_code})",
            error_message=error_output[:200] + "..." if len(error_output) > 200 else error_output,
            likely_cause="Command execution failed",
            suggested_fixes=[
                "Check the command syntax and arguments",
                "Verify all required files and dependencies exist",
                "Review the error output for specific issues",
                "Try running the command with verbose output for more details"
            ],
            confidence=0.5
        )
    
    def _extract_code_location(self, error_output: str) -> Optional[str]:
        """Extract file location and line number from error output"""
        # Python traceback format
        python_location = re.search(r'File "(.+)", line (\d+)', error_output)
        if python_location:
            return f"{python_location.group(1)}:{python_location.group(2)}"
        
        # JavaScript error format
        js_location = re.search(r'at (.+):(\d+):(\d+)', error_output)
        if js_location:
            return f"{js_location.group(1)}:{js_location.group(2)}"
        
        return None
    
    def _customize_fixes(self, fixes: List[str], command: str, error_output: str) -> List[str]:
        """Customize generic fixes based on specific command and error"""
        customized_fixes = []
        
        for fix in fixes:
            # Replace {module} placeholder with actual module name
            if '{module}' in fix:
                module_match = re.search(r'No module named \'(.+?)\'', error_output)
                if module_match:
                    fix = fix.replace('{module}', module_match.group(1))
            
            customized_fixes.append(fix)
        
        # Add command-specific suggestions
        if 'python' in command.lower() and '.py' in command:
            if 'sqlite3' in error_output.lower():
                customized_fixes.append("Use lumos-cli to analyze the database setup in your Python file")
            elif 'import' in error_output.lower():
                customized_fixes.append("Check your virtual environment and installed packages")
        
        return customized_fixes
    
    def display_analysis(self, analysis: FailureAnalysis):
        """Display the failure analysis in a user-friendly format"""
        self.console.print("\n🔍 Intelligent Failure Analysis", style="bold red")
        self.console.print("=" * 50)
        
        # Error type and message
        self.console.print(f"🚨 Error Type: [bold]{analysis.error_type}[/bold]")
        self.console.print(f"📝 Message: {analysis.error_message}")
        
        # Code location if available
        if analysis.code_location:
            self.console.print(f"📍 Location: [bold cyan]{analysis.code_location}[/bold cyan]")
        
        # Likely cause
        self.console.print(f"\n💡 Likely Cause:")
        self.console.print(f"   {analysis.likely_cause}")
        
        # Suggested fixes
        self.console.print(f"\n🔧 Suggested Fixes:")
        for i, fix in enumerate(analysis.suggested_fixes, 1):
            self.console.print(f"   {i}. {fix}")
        
        # Confidence
        confidence_color = "green" if analysis.confidence >= 0.8 else "yellow" if analysis.confidence >= 0.6 else "red"
        self.console.print(f"\n🎯 Confidence: [{confidence_color}]{analysis.confidence:.1%}[/{confidence_color}]")

# Global analyzer instance
failure_analyzer = IntelligentFailureAnalyzer()

def analyze_command_failure(command: str, stdout: str, stderr: str, exit_code: int) -> FailureAnalysis:
    """
    Analyze a command failure and provide intelligent insights
    
    Args:
        command: The command that was executed
        stdout: Standard output from the command
        stderr: Standard error from the command
        exit_code: Exit code from the command
        
    Returns:
        FailureAnalysis: Detailed analysis of the failure
    """
    return failure_analyzer.analyze_failure(command, stdout, stderr, exit_code)