#!/usr/bin/env python3
"""Safe shell command execution with user confirmation"""

import subprocess
import sys
import os
from typing import Optional, List, Tuple
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

console = Console()

class ShellExecutor:
    """Handles safe execution of shell commands with user confirmation"""
    
    def __init__(self):
        self.dangerous_commands = {
            # Destructive commands
            'rm', 'del', 'rmdir', 'rd', 'format', 'fdisk', 'mkfs',
            # System modification
            'sudo', 'su', 'chmod', 'chown', 'passwd', 'useradd', 'userdel',
            # Network/security
            'wget', 'curl', 'ssh', 'scp', 'ftp', 'telnet',
            # Package management
            'apt', 'yum', 'brew', 'pip', 'npm', 'yarn',
            # System control
            'systemctl', 'service', 'reboot', 'shutdown', 'halt',
            # File system
            'mount', 'umount', 'fsck', 'dd'
        }
        
        self.very_dangerous_commands = {
            'rm -rf', 'del /s', 'format c:', 'dd if=', 'mkfs.',
            'rm -r', 'rm *', 'del *.*'
        }
    
    def is_dangerous_command(self, command: str) -> Tuple[bool, str]:
        """Check if a command is potentially dangerous"""
        cmd_lower = command.lower().strip()
        
        # Check for very dangerous command patterns
        for dangerous in self.very_dangerous_commands:
            if dangerous in cmd_lower:
                return True, f"Very dangerous: Contains '{dangerous}'"
        
        # Check first word (main command) 
        first_word = cmd_lower.split()[0] if cmd_lower.split() else ""
        if first_word in self.dangerous_commands:
            return True, f"Potentially dangerous: '{first_word}' command"
        
        # Check for dangerous flags/patterns
        dangerous_patterns = [
            '--force', '-f', '/f', '-rf', '/s', '| rm', '| del',
            '> /dev/', '2>&1', '&& rm', '&& del'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in cmd_lower:
                return True, f"Dangerous pattern: Contains '{pattern}'"
        
        return False, ""
    
    def show_command_preview(self, command: str, context: str = ""):
        """Show a preview of the command to be executed"""
        console.print()
        
        # Show context if provided
        if context:
            console.print(f"[bold blue]Context:[/bold blue] {context}")
        
        # Command preview panel
        preview_content = Syntax(command, "bash", theme="monokai", line_numbers=False)
        panel = Panel(
            preview_content,
            title="🔧 Command to Execute",
            border_style="blue",
            expand=False
        )
        console.print(panel)
        
        # Show working directory
        console.print(f"[dim]Working directory: {os.getcwd()}[/dim]")
        
        # Check for dangerous commands
        is_dangerous, danger_reason = self.is_dangerous_command(command)
        if is_dangerous:
            warning_panel = Panel(
                f"⚠️  [bold red]WARNING:[/bold red] {danger_reason}\n"
                f"This command may modify your system or files!",
                title="🚨 Safety Warning",
                border_style="red",
                expand=False
            )
            console.print(warning_panel)
    
    def get_user_confirmation(self, command: str, is_dangerous: bool = False) -> bool:
        """Get user confirmation before executing command"""
        if is_dangerous:
            console.print("\n[bold red]This command requires extra confirmation![/bold red]")
            
            # Double confirmation for dangerous commands
            confirm1 = Confirm.ask(
                "[bold red]Are you sure you want to run this potentially dangerous command?[/bold red]"
            )
            if not confirm1:
                return False
            
            # Ask user to type the command to confirm they understand it
            console.print(f"\n[yellow]To confirm, please type the command exactly as shown above:[/yellow]")
            user_input = Prompt.ask("Command")
            
            if user_input.strip() != command.strip():
                console.print("[red]Command confirmation failed. Execution cancelled.[/red]")
                return False
                
            return True
        else:
            return Confirm.ask(
                f"\n[bold]Execute this command?[/bold]",
                default=True
            )
    
    def execute_command(self, command: str, context: str = "") -> Tuple[bool, str, str]:
        """
        Execute a shell command with user confirmation
        
        Returns:
            Tuple[bool, str, str]: (success, stdout, stderr)
        """
        try:
            # Show command preview
            self.show_command_preview(command, context)
            
            # Check if dangerous
            is_dangerous, danger_reason = self.is_dangerous_command(command)
            
            # Get user confirmation
            if not self.get_user_confirmation(command, is_dangerous):
                console.print("[yellow]Command execution cancelled by user.[/yellow]")
                return False, "", "Cancelled by user"
            
            # Execute the command
            console.print(f"\n[green]Executing:[/green] {command}")
            console.print("=" * 50)
            
            # Use the appropriate shell based on OS
            shell = True
            if sys.platform.startswith('win'):
                # For Windows, we might want to use cmd
                pass
            
            # Execute with real-time output
            process = subprocess.Popen(
                command,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            stdout_lines = []
            stderr_lines = []
            
            # Read output in real-time
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                
                if stdout_line:
                    stdout_lines.append(stdout_line)
                    console.print(stdout_line.rstrip())
                
                if stderr_line:
                    stderr_lines.append(stderr_line)
                    console.print(f"[red]{stderr_line.rstrip()}[/red]")
                
                # Check if process is done
                if process.poll() is not None:
                    break
            
            # Get remaining output
            remaining_stdout, remaining_stderr = process.communicate()
            if remaining_stdout:
                stdout_lines.append(remaining_stdout)
                console.print(remaining_stdout)
            if remaining_stderr:
                stderr_lines.append(remaining_stderr)
                console.print(f"[red]{remaining_stderr}[/red]")
            
            # Combine outputs
            stdout = ''.join(stdout_lines)
            stderr = ''.join(stderr_lines)
            
            console.print("=" * 50)
            
            # Show execution result
            if process.returncode == 0:
                console.print("[green]✅ Command executed successfully![/green]")
                return True, stdout, stderr
            else:
                console.print(f"[red]❌ Command failed with exit code {process.returncode}[/red]")
                return False, stdout, stderr
                
        except FileNotFoundError:
            error_msg = f"Command not found: {command.split()[0]}"
            console.print(f"[red]❌ {error_msg}[/red]")
            return False, "", error_msg
            
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            return False, "", error_msg
    
    def suggest_safe_alternatives(self, dangerous_command: str) -> List[str]:
        """Suggest safer alternatives for dangerous commands"""
        suggestions = []
        
        cmd_lower = dangerous_command.lower()
        
        if 'rm -rf' in cmd_lower or 'rm -r' in cmd_lower:
            suggestions.extend([
                "Use 'ls' first to see what will be deleted",
                "Consider using a trash/recycle bin instead",
                "Use 'rm' without -rf to delete files individually"
            ])
        
        if 'sudo' in cmd_lower:
            suggestions.extend([
                "Make sure you understand what the command does",
                "Consider running without sudo first if possible",
                "Check if you really need administrator privileges"
            ])
        
        if any(pkg in cmd_lower for pkg in ['apt', 'yum', 'brew', 'pip', 'npm']):
            suggestions.extend([
                "Consider using a virtual environment",
                "Review package documentation first",
                "Use 'list' or 'search' commands first to explore"
            ])
        
        return suggestions


# Global executor instance
shell_executor = ShellExecutor()


def execute_shell_command(command: str, context: str = "") -> Tuple[bool, str, str]:
    """
    Execute a shell command with safety checks and user confirmation
    
    Args:
        command: The shell command to execute
        context: Optional context about why this command is being run
        
    Returns:
        Tuple[bool, str, str]: (success, stdout, stderr)
    """
    return shell_executor.execute_command(command, context)