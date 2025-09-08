"""Advanced error handling and debugging system for Lumos CLI"""

import subprocess
import os
import re
import sys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
import traceback

@dataclass
class ErrorAnalysis:
    """Structured error analysis result"""
    error_type: str
    error_message: str
    file_path: Optional[str]
    line_number: Optional[int]
    suggested_fixes: List[str]
    relevant_files: List[str]
    confidence: float
    context: Dict[str, Any]

class RuntimeErrorHandler:
    """Handles runtime errors intelligently"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        
        # Common error patterns and their solutions
        self.error_patterns = {
            'ModuleNotFoundError': {
                'pattern': r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]",
                'handler': self._handle_missing_module,
                'category': 'dependency'
            },
            'FileNotFoundError': {
                'pattern': r"FileNotFoundError.*['\"]([^'\"]+)['\"]",
                'handler': self._handle_file_not_found,
                'category': 'file_system'
            },
            'ConnectionError': {
                'pattern': r"(Connection.*Error|Failed to connect)",
                'handler': self._handle_connection_error,
                'category': 'network'
            },
            'DatabaseError': {
                'pattern': r"(sqlite3\.OperationalError|DatabaseError|no such table)",
                'handler': self._handle_database_error,
                'category': 'database'
            },
            'EnvironmentError': {
                'pattern': r"(KeyError.*['\"]([^'\"]+)['\"]|environment variable)",
                'handler': self._handle_env_error,
                'category': 'configuration'
            },
            'ImportError': {
                'pattern': r"ImportError.*cannot import",
                'handler': self._handle_import_error,
                'category': 'dependency'
            },
            'SyntaxError': {
                'pattern': r"SyntaxError.*line (\d+)",
                'handler': self._handle_syntax_error,
                'category': 'code'
            },
            'AttributeError': {
                'pattern': r"AttributeError.*'([^']+)' object.*'([^']+)'",
                'handler': self._handle_attribute_error,
                'category': 'code'
            },
            'TypeError': {
                'pattern': r"TypeError.*",
                'handler': self._handle_type_error,
                'category': 'code'
            },
            'ZeroDivisionError': {
                'pattern': r"ZeroDivisionError",
                'handler': self._handle_zero_division,
                'category': 'logic'
            }
        }

    def run_and_debug(self, command: List[str], working_dir: str = ".") -> ErrorAnalysis:
        """Run a command and analyze any errors that occur"""
        try:
            # Run the command
            result = subprocess.run(
                command,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.console.print("[green]✅ Application started successfully![/green]")
                self.console.print(f"[dim]Output: {result.stdout[:200]}...[/dim]")
                return None
            
            # Analyze the error
            error_output = result.stderr or result.stdout
            return self.analyze_error(error_output, working_dir)
            
        except subprocess.TimeoutExpired:
            return ErrorAnalysis(
                error_type="Timeout",
                error_message="Application failed to start within 30 seconds",
                file_path=None,
                line_number=None,
                suggested_fixes=["Check for infinite loops or blocking operations", 
                               "Review startup dependencies", 
                               "Add startup logging to identify bottlenecks"],
                relevant_files=[],
                confidence=0.8,
                context={'timeout': 30}
            )
        except Exception as e:
            return ErrorAnalysis(
                error_type="SystemError",
                error_message=str(e),
                file_path=None,
                line_number=None,
                suggested_fixes=["Check system permissions", "Verify command exists"],
                relevant_files=[],
                confidence=0.5,
                context={'exception': str(e)}
            )

    def analyze_error(self, error_text: str, working_dir: str = ".") -> ErrorAnalysis:
        """Analyze error text and provide structured feedback"""
        
        # Extract traceback information
        file_path, line_number = self._extract_file_location(error_text)
        
        # Match against known error patterns
        for error_type, config in self.error_patterns.items():
            match = re.search(config['pattern'], error_text, re.IGNORECASE | re.MULTILINE)
            if match:
                return config['handler'](error_text, match, file_path, line_number, working_dir)
        
        # Fallback generic analysis
        return ErrorAnalysis(
            error_type="UnknownError",
            error_message=error_text.split('\n')[-1] if error_text else "Unknown error",
            file_path=file_path,
            line_number=line_number,
            suggested_fixes=["Review the full error traceback", 
                           "Check recent code changes", 
                           "Verify all dependencies are installed"],
            relevant_files=[file_path] if file_path else [],
            confidence=0.3,
            context={'raw_error': error_text}
        )

    def _extract_file_location(self, error_text: str) -> Tuple[Optional[str], Optional[int]]:
        """Extract file path and line number from traceback"""
        # Look for traceback patterns
        file_pattern = r'File "([^"]+)", line (\d+)'
        matches = re.findall(file_pattern, error_text)
        
        if matches:
            # Get the last (most relevant) file and line
            file_path, line_str = matches[-1]
            return file_path, int(line_str)
        
        return None, None

    # Error-specific handlers
    def _handle_missing_module(self, error_text: str, match, file_path: str, line_number: int, working_dir: str) -> ErrorAnalysis:
        module_name = match.group(1)
        
        # Check if it's a common module with known installation
        install_commands = {
            'flask': 'pip install flask',
            'requests': 'pip install requests',
            'numpy': 'pip install numpy',
            'pandas': 'pip install pandas',
            'PIL': 'pip install Pillow',
            'cv2': 'pip install opencv-python',
            'sklearn': 'pip install scikit-learn'
        }
        
        fixes = [f"Install the missing module: {install_commands.get(module_name, f'pip install {module_name}')}"]
        
        # Check for requirements.txt
        if os.path.exists(os.path.join(working_dir, 'requirements.txt')):
            fixes.append("Run: pip install -r requirements.txt")
        
        # Check for virtual environment
        if not os.environ.get('VIRTUAL_ENV'):
            fixes.append("Consider using a virtual environment: python -m venv venv && source venv/bin/activate")
        
        return ErrorAnalysis(
            error_type="ModuleNotFoundError",
            error_message=f"Module '{module_name}' is not installed",
            file_path=file_path,
            line_number=line_number,
            suggested_fixes=fixes,
            relevant_files=[file_path] if file_path else [],
            confidence=0.9,
            context={'module': module_name}
        )

    def _handle_file_not_found(self, error_text: str, match, file_path: str, line_number: int, working_dir: str) -> ErrorAnalysis:
        missing_file = match.group(1)
        
        fixes = [
            f"Create the missing file: {missing_file}",
            "Check if the file path is correct",
            "Verify current working directory"
        ]
        
        # Look for similar files
        directory = os.path.dirname(missing_file) or working_dir
        if os.path.exists(directory):
            similar_files = [f for f in os.listdir(directory) 
                           if f.lower().startswith(os.path.basename(missing_file)[:3].lower())]
            if similar_files:
                fixes.append(f"Similar files found: {', '.join(similar_files[:3])}")
        
        return ErrorAnalysis(
            error_type="FileNotFoundError",
            error_message=f"File '{missing_file}' not found",
            file_path=file_path,
            line_number=line_number,
            suggested_fixes=fixes,
            relevant_files=[file_path] if file_path else [],
            confidence=0.8,
            context={'missing_file': missing_file}
        )

    def _handle_database_error(self, error_text: str, match, file_path: str, line_number: int, working_dir: str) -> ErrorAnalysis:
        fixes = [
            "Initialize the database schema",
            "Check database connection parameters",
            "Verify database file permissions",
            "Run database migrations if applicable"
        ]
        
        # Look for database files or migration scripts
        db_files = []
        for root, dirs, files in os.walk(working_dir):
            for file in files:
                if file.endswith(('.db', '.sqlite', '.sqlite3')) or 'migration' in file.lower():
                    db_files.append(os.path.join(root, file))
        
        return ErrorAnalysis(
            error_type="DatabaseError",
            error_message="Database operation failed",
            file_path=file_path,
            line_number=line_number,
            suggested_fixes=fixes,
            relevant_files=db_files[:5],
            confidence=0.7,
            context={'database_files': db_files}
        )

    def _handle_env_error(self, error_text: str, match, file_path: str, line_number: int, working_dir: str) -> ErrorAnalysis:
        # Try to extract environment variable name
        env_var_pattern = r"KeyError.*['\"]([^'\"]+)['\"]"
        env_match = re.search(env_var_pattern, error_text)
        env_var = env_match.group(1) if env_match else "UNKNOWN"
        
        fixes = [
            f"Set the environment variable: export {env_var}=your_value",
            f"Add {env_var} to your .env file",
            "Check environment configuration documentation"
        ]
        
        # Look for .env files or config files
        config_files = []
        for file in ['.env', '.env.example', 'config.py', 'settings.py']:
            if os.path.exists(os.path.join(working_dir, file)):
                config_files.append(file)
        
        return ErrorAnalysis(
            error_type="EnvironmentError",
            error_message=f"Environment variable '{env_var}' is not set",
            file_path=file_path,
            line_number=line_number,
            suggested_fixes=fixes,
            relevant_files=config_files,
            confidence=0.8,
            context={'env_var': env_var, 'config_files': config_files}
        )

    def _handle_connection_error(self, error_text: str, match, file_path: str, line_number: int, working_dir: str) -> ErrorAnalysis:
        fixes = [
            "Check internet connection",
            "Verify service endpoint is running",
            "Check firewall/proxy settings",
            "Verify API credentials"
        ]
        
        return ErrorAnalysis(
            error_type="ConnectionError",
            error_message="Network connection failed",
            file_path=file_path,
            line_number=line_number,
            suggested_fixes=fixes,
            relevant_files=[file_path] if file_path else [],
            confidence=0.7,
            context={'network_error': True}
        )

    def _handle_import_error(self, error_text: str, match, file_path: str, line_number: int, working_dir: str) -> ErrorAnalysis:
        return self._handle_missing_module(error_text, match, file_path, line_number, working_dir)

    def _handle_syntax_error(self, error_text: str, match, file_path: str, line_number: int, working_dir: str) -> ErrorAnalysis:
        fixes = [
            "Check syntax around the indicated line",
            "Look for missing parentheses, brackets, or quotes",
            "Verify indentation is correct",
            "Check for typos in keywords"
        ]
        
        return ErrorAnalysis(
            error_type="SyntaxError",
            error_message="Python syntax error",
            file_path=file_path,
            line_number=line_number,
            suggested_fixes=fixes,
            relevant_files=[file_path] if file_path else [],
            confidence=0.9,
            context={'syntax_error': True}
        )

    def _handle_attribute_error(self, error_text: str, match, file_path: str, line_number: int, working_dir: str) -> ErrorAnalysis:
        object_type = match.group(1) if match.groups() else "object"
        attribute = match.group(2) if len(match.groups()) > 1 else "attribute"
        
        fixes = [
            f"Check if '{attribute}' method/property exists on {object_type}",
            f"Verify {object_type} object is properly initialized",
            "Check for typos in method/property names",
            "Review API documentation for correct usage"
        ]
        
        return ErrorAnalysis(
            error_type="AttributeError",
            error_message=f"'{object_type}' object has no attribute '{attribute}'",
            file_path=file_path,
            line_number=line_number,
            suggested_fixes=fixes,
            relevant_files=[file_path] if file_path else [],
            confidence=0.8,
            context={'object_type': object_type, 'attribute': attribute}
        )

    def _handle_type_error(self, error_text: str, match, file_path: str, line_number: int, working_dir: str) -> ErrorAnalysis:
        fixes = [
            "Check data types being passed to functions",
            "Verify function arguments match expected types",
            "Add type checking or validation",
            "Review function documentation"
        ]
        
        return ErrorAnalysis(
            error_type="TypeError",
            error_message="Type mismatch error",
            file_path=file_path,
            line_number=line_number,
            suggested_fixes=fixes,
            relevant_files=[file_path] if file_path else [],
            confidence=0.7,
            context={'type_error': True}
        )

    def _handle_zero_division(self, error_text: str, match, file_path: str, line_number: int, working_dir: str) -> ErrorAnalysis:
        fixes = [
            "Add validation to prevent division by zero",
            "Check input values before calculation",
            "Add conditional logic to handle zero cases",
            "Review mathematical logic"
        ]
        
        return ErrorAnalysis(
            error_type="ZeroDivisionError",
            error_message="Division by zero",
            file_path=file_path,
            line_number=line_number,
            suggested_fixes=fixes,
            relevant_files=[file_path] if file_path else [],
            confidence=0.9,
            context={'division_error': True}
        )

    def display_error_analysis(self, analysis: ErrorAnalysis):
        """Display error analysis with beautiful UI"""
        if not analysis:
            return
            
        # Import UI components
        try:
            from .ui import create_error_panel
            create_error_panel(self.console, analysis.error_type, analysis.error_message, 
                             analysis.suggested_fixes, analysis.confidence)
        except ImportError:
            # Fallback to original display if UI not available
            self._display_error_fallback(analysis)
    
    def _display_error_fallback(self, analysis: ErrorAnalysis):
        """Fallback error display without UI components"""
        # Main error panel
        self.console.print(f"\n[red]🚨 Runtime Error Detected[/red]")
        
        error_panel = Panel(
            f"[red]{analysis.error_type}[/red]: {analysis.error_message}",
            title="Error Details",
            border_style="red"
        )
        self.console.print(error_panel)
        
        # Location information
        if analysis.file_path:
            location = f"{analysis.file_path}"
            if analysis.line_number:
                location += f":{analysis.line_number}"
            self.console.print(f"[dim]📍 Location: {location}[/dim]")
        
        # Suggested fixes
        if analysis.suggested_fixes:
            self.console.print(f"\n[bold yellow]💡 Suggested Fixes:[/bold yellow]")
            for i, fix in enumerate(analysis.suggested_fixes, 1):
                self.console.print(f"  {i}. {fix}")
        
        # Relevant files
        if analysis.relevant_files:
            self.console.print(f"\n[dim]📁 Relevant Files:[/dim]")
            for file in analysis.relevant_files[:5]:
                self.console.print(f"  • {file}")
        
        # Confidence indicator
        confidence_color = "green" if analysis.confidence > 0.8 else "yellow" if analysis.confidence > 0.5 else "red"
        self.console.print(f"\n[{confidence_color}]🎯 Confidence: {analysis.confidence:.0%}[/{confidence_color}]")

def smart_start_app(app_command: List[str], working_dir: str = ".") -> bool:
    """Smart application startup with error handling"""
    console = Console()
    error_handler = RuntimeErrorHandler(console)
    
    console.print(f"[cyan]🚀 Starting application: {' '.join(app_command)}[/cyan]")
    
    analysis = error_handler.run_and_debug(app_command, working_dir)
    
    if analysis:
        error_handler.display_error_analysis(analysis)
        
        # Ask if user wants automated fix
        from rich.prompt import Confirm
        if analysis.confidence > 0.7 and Confirm.ask("\n🤖 Apply automated fix?", default=False):
            return _apply_automated_fix(analysis, working_dir)
        else:
            console.print("\n[yellow]💬 Tip: Use 'lumos-cli debug <file> <issue>' for more specific help[/yellow]")
        
        return False
    
    return True

def _apply_automated_fix(analysis: ErrorAnalysis, working_dir: str) -> bool:
    """Apply automated fixes when possible"""
    console = Console()
    
    if analysis.error_type == "ModuleNotFoundError":
        module = analysis.context.get('module')
        if module:
            console.print(f"[cyan]Installing {module}...[/cyan]")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', module], 
                             check=True, cwd=working_dir)
                console.print(f"[green]✅ Successfully installed {module}[/green]")
                return True
            except subprocess.CalledProcessError:
                console.print(f"[red]❌ Failed to install {module}[/red]")
    
    elif analysis.error_type == "EnvironmentError":
        env_var = analysis.context.get('env_var')
        if env_var:
            console.print(f"[yellow]Please set environment variable {env_var}[/yellow]")
    
    return False