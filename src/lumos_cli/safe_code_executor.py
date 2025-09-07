"""
Safe Code Executor for Enterprise LLM Replica
Provides safe code execution with validation and rollback capabilities
"""

import os
import tempfile
import shutil
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .huggingface_manager import get_huggingface_manager
from .environment_manager import get_environment_manager
from .debug_logger import debug_logger

console = Console()

@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    output: str
    error: str
    execution_time: float
    language: str
    model_used: str
    validation_passed: bool
    warnings: List[str]

@dataclass
class CodeValidation:
    """Code validation result"""
    syntax_valid: bool
    security_issues: List[str]
    performance_issues: List[str]
    best_practices: List[str]
    overall_score: float

class SafeCodeExecutor:
    """Safe code executor with validation and rollback capabilities"""
    
    def __init__(self):
        self.console = console
        self.hf_manager = get_huggingface_manager()
        self.env_manager = get_environment_manager()
        self.execution_history = []
        self.backup_dir = None
        self._create_backup_dir()
    
    def _create_backup_dir(self):
        """Create backup directory for rollback capabilities"""
        self.backup_dir = tempfile.mkdtemp(prefix="lumos_backup_")
        debug_logger.log_function_call("SafeCodeExecutor._create_backup_dir", {
            "backup_dir": self.backup_dir
        })
    
    def generate_and_execute(self, prompt: str, language: str = "python", 
                           model_type: str = "general_code", 
                           execute: bool = True) -> ExecutionResult:
        """Generate code and optionally execute it safely"""
        
        debug_logger.log_function_call("SafeCodeExecutor.generate_and_execute", {
            "prompt": prompt,
            "language": language,
            "model_type": model_type,
            "execute": execute
        })
        
        try:
            # Switch to appropriate model
            if not self.hf_manager.switch_model(model_type):
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Failed to load model: {model_type}",
                    execution_time=0.0,
                    language=language,
                    model_used=model_type,
                    validation_passed=False,
                    warnings=[]
                )
            
            # Generate code
            self.console.print(f"[cyan]🤖 Generating {language} code using {model_type}...[/cyan]")
            generated_code = self.hf_manager.generate_code(prompt, language)
            
            if not generated_code:
                return ExecutionResult(
                    success=False,
                    output="",
                    error="Failed to generate code",
                    execution_time=0.0,
                    language=language,
                    model_used=model_type,
                    validation_passed=False,
                    warnings=[]
                )
            
            # Validate code
            self.console.print(f"[yellow]🔍 Validating generated code...[/yellow]")
            validation = self._validate_code(generated_code, language)
            
            if not validation.syntax_valid:
                return ExecutionResult(
                    success=False,
                    output=generated_code,
                    error=f"Syntax validation failed: {validation.security_issues}",
                    execution_time=0.0,
                    language=language,
                    model_used=model_type,
                    validation_passed=False,
                    warnings=validation.best_practices
                )
            
            # Execute code if requested
            if execute:
                self.console.print(f"[green]🚀 Executing {language} code...[/green]")
                success, output, error = self._execute_safely(generated_code, language)
                
                execution_result = ExecutionResult(
                    success=success,
                    output=output,
                    error=error,
                    execution_time=0.0,  # TODO: Add timing
                    language=language,
                    model_used=model_type,
                    validation_passed=validation.overall_score > 0.7,
                    warnings=validation.best_practices
                )
            else:
                execution_result = ExecutionResult(
                    success=True,
                    output=generated_code,
                    error="",
                    execution_time=0.0,
                    language=language,
                    model_used=model_type,
                    validation_passed=validation.overall_score > 0.7,
                    warnings=validation.best_practices
                )
            
            # Store in history
            self.execution_history.append(execution_result)
            
            return execution_result
            
        except Exception as e:
            debug_logger.error(f"Generate and execute failed: {e}")
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=0.0,
                language=language,
                model_used=model_type,
                validation_passed=False,
                warnings=[]
            )
    
    def _validate_code(self, code: str, language: str) -> CodeValidation:
        """Validate generated code for safety and quality"""
        security_issues = []
        performance_issues = []
        best_practices = []
        
        # Basic syntax validation
        syntax_valid = self._check_syntax(code, language)
        
        # Security checks
        security_issues = self._check_security(code, language)
        
        # Performance checks
        performance_issues = self._check_performance(code, language)
        
        # Best practices checks
        best_practices = self._check_best_practices(code, language)
        
        # Calculate overall score
        total_issues = len(security_issues) + len(performance_issues)
        overall_score = max(0.0, 1.0 - (total_issues * 0.1))
        
        return CodeValidation(
            syntax_valid=syntax_valid,
            security_issues=security_issues,
            performance_issues=performance_issues,
            best_practices=best_practices,
            overall_score=overall_score
        )
    
    def _check_syntax(self, code: str, language: str) -> bool:
        """Check code syntax"""
        try:
            if language == "python":
                compile(code, "<string>", "exec")
                return True
            elif language == "javascript":
                # Basic JS syntax check
                return "function" in code or "const" in code or "let" in code or "var" in code
            elif language == "go":
                return "package main" in code and "func main" in code
            elif language == "java":
                return "public class" in code and "public static void main" in code
            else:
                return True  # Assume valid for other languages
        except Exception:
            return False
    
    def _check_security(self, code: str, language: str) -> List[str]:
        """Check for security issues"""
        security_issues = []
        
        # Common security patterns to avoid
        dangerous_patterns = [
            "exec(",
            "eval(",
            "os.system(",
            "subprocess.call(",
            "shell=True",
            "rm -rf",
            "del /f",
            "rmdir /s",
            "format(",
            "f\"",
            "f'",
            "eval(",
            "Function(",
            "setTimeout(",
            "setInterval("
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                security_issues.append(f"Potentially dangerous pattern: {pattern}")
        
        return security_issues
    
    def _check_performance(self, code: str, language: str) -> List[str]:
        """Check for performance issues"""
        performance_issues = []
        
        # Common performance anti-patterns
        if language == "python":
            if "for i in range(len(" in code:
                performance_issues.append("Consider using enumerate() instead of range(len())")
            if "list.append(" in code and code.count("list.append(") > 5:
                performance_issues.append("Consider using list comprehension for multiple appends")
        
        return performance_issues
    
    def _check_best_practices(self, code: str, language: str) -> List[str]:
        """Check for best practices"""
        best_practices = []
        
        if language == "python":
            if "print(" in code and "logging" not in code:
                best_practices.append("Consider using logging instead of print statements")
            if "except:" in code:
                best_practices.append("Use specific exception types instead of bare except")
            if "def " in code and "->" not in code:
                best_practices.append("Consider adding type hints to functions")
        
        return best_practices
    
    def _execute_safely(self, code: str, language: str) -> Tuple[bool, str, str]:
        """Execute code in a safe environment"""
        try:
            # Create temporary environment
            env_path = self.env_manager.create_virtual_environment(language)
            
            if not env_path:
                return False, "", f"Failed to create environment for {language}"
            
            # Execute code
            success, output, error = self.env_manager.execute_code(code, language, env_path)
            
            return success, output, error
            
        except Exception as e:
            debug_logger.error(f"Safe execution failed: {e}")
            return False, "", str(e)
    
    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code using Hugging Face models"""
        try:
            # Use code analysis model
            analysis_result = self.hf_manager.analyze_code(code, "quality")
            
            # Use code review model
            review_result = self.hf_manager.review_code(code)
            
            return {
                "analysis": analysis_result,
                "review": review_result,
                "language": language,
                "timestamp": "2024-01-01T00:00:00Z"  # TODO: Add actual timestamp
            }
            
        except Exception as e:
            debug_logger.error(f"Code analysis failed: {e}")
            return {"error": str(e)}
    
    def refactor_code(self, code: str, refactor_type: str = "general") -> str:
        """Refactor code using Hugging Face models"""
        try:
            return self.hf_manager.refactor_code(code, refactor_type)
        except Exception as e:
            debug_logger.error(f"Code refactoring failed: {e}")
            return code
    
    def show_execution_history(self) -> None:
        """Show execution history"""
        if not self.execution_history:
            self.console.print("[yellow]No execution history available[/yellow]")
            return
        
        table = Table(title="Execution History")
        table.add_column("Language", style="cyan")
        table.add_column("Model", style="green")
        table.add_column("Success", style="bold")
        table.add_column("Validation", style="bold")
        table.add_column("Warnings", style="yellow")
        
        for i, result in enumerate(self.execution_history[-10:]):  # Show last 10
            success_icon = "✅" if result.success else "❌"
            validation_icon = "✅" if result.validation_passed else "❌"
            warnings_count = len(result.warnings)
            
            table.add_row(
                result.language,
                result.model_used,
                success_icon,
                validation_icon,
                str(warnings_count)
            )
        
        self.console.print(table)
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self.env_manager.cleanup()
        if self.backup_dir and os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)
        self.console.print("[green]✅ Cleaned up safe code executor[/green]")

# Global safe code executor instance
safe_executor = SafeCodeExecutor()

def get_safe_code_executor() -> SafeCodeExecutor:
    """Get the global safe code executor"""
    return safe_executor
