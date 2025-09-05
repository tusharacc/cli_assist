"""Safety and preview system for file operations"""

import os
import shutil
import difflib
import tempfile
from datetime import datetime
from typing import Optional, Tuple
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()

class SafeFileEditor:
    """Safe file editing with preview and backup capabilities"""
    
    def __init__(self, backup_dir: str = ".llm_backups"):
        self.backup_dir = backup_dir
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, file_path: str) -> str:
        """Create a timestamped backup of the file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_name = f"{filename}.{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def show_diff(self, original_content: str, new_content: str, file_path: str = "file"):
        """Display a colored diff between original and new content"""
        diff_lines = list(difflib.unified_diff(
            original_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=""
        ))
        
        if not diff_lines:
            console.print("[dim]No changes detected[/dim]")
            return False
        
        # Convert diff to string and display with syntax highlighting
        diff_text = "".join(diff_lines)
        
        console.print(Panel(
            Syntax(diff_text, "diff", theme="monokai", line_numbers=False),
            title="[bold blue]Proposed Changes[/bold blue]",
            border_style="blue"
        ))
        
        return True
    
    def validate_content(self, content: str, file_path: str) -> Tuple[bool, list]:
        """Basic validation of generated content"""
        warnings = []
        
        # Check for common issues
        if not content.strip():
            warnings.append("Generated content is empty")
        
        # Check for potential encoding issues
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            warnings.append("Content contains non-UTF-8 characters")
        
        # Check file extension for syntax validation
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.py':
            warnings.extend(self._validate_python(content))
        elif ext in ['.js', '.ts']:
            warnings.extend(self._validate_javascript(content))
        
        return len(warnings) == 0, warnings
    
    def _validate_python(self, content: str) -> list:
        """Basic Python syntax validation"""
        warnings = []
        try:
            compile(content, '<string>', 'exec')
        except SyntaxError as e:
            warnings.append(f"Python syntax error: {e}")
        return warnings
    
    def _validate_javascript(self, content: str) -> list:
        """Basic JavaScript validation (simple checks)"""
        warnings = []
        
        # Count braces
        if content.count('{') != content.count('}'):
            warnings.append("Mismatched curly braces")
        
        if content.count('(') != content.count(')'):
            warnings.append("Mismatched parentheses")
        
        return warnings
    
    def preview_and_confirm(self, file_path: str, new_content: str, 
                          auto_confirm: bool = False) -> bool:
        """Show preview and get user confirmation"""
        
        # Read original content
        try:
            with open(file_path, 'r') as f:
                original_content = f.read()
        except FileNotFoundError:
            original_content = ""
            console.print(f"[yellow]Creating new file: {file_path}[/yellow]")
        
        # Show diff
        has_changes = self.show_diff(original_content, new_content, file_path)
        
        if not has_changes:
            console.print("[dim]No changes to apply[/dim]")
            return False
        
        # Validate content
        is_valid, warnings = self.validate_content(new_content, file_path)
        
        if warnings:
            console.print("\n[yellow]⚠️  Validation Warnings:[/yellow]")
            for warning in warnings:
                console.print(f"  • {warning}")
        
        if auto_confirm:
            console.print("[dim]Auto-confirming changes...[/dim]")
            return True
        
        # Get user confirmation
        console.print()
        return Confirm.ask(
            f"Apply changes to {file_path}?",
            default=True if is_valid else False
        )
    
    def safe_write(self, file_path: str, content: str, 
                   preview: bool = True, auto_confirm: bool = False) -> bool:
        """Safely write content to file with preview and backup"""
        
        # Create backup if file exists
        backup_path = None
        if os.path.exists(file_path):
            backup_path = self.create_backup(file_path)
            console.print(f"[dim]Backup created: {backup_path}[/dim]")
        
        # Preview and confirm if requested
        if preview:
            if not self.preview_and_confirm(file_path, content, auto_confirm):
                console.print("[yellow]Changes cancelled[/yellow]")
                return False
        
        try:
            # Write the file
            with open(file_path, 'w') as f:
                f.write(content)
            
            console.print(f"[green]✅ Successfully updated {file_path}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error writing file: {e}[/red]")
            
            # Restore from backup if available
            if backup_path and os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, file_path)
                    console.print(f"[yellow]Restored from backup[/yellow]")
                except Exception as restore_error:
                    console.print(f"[red]Failed to restore from backup: {restore_error}[/red]")
            
            return False
    
    def list_backups(self, file_path: Optional[str] = None) -> list:
        """List available backups"""
        if not os.path.exists(self.backup_dir):
            return []
        
        backups = []
        filename_filter = os.path.basename(file_path) if file_path else None
        
        for backup_file in os.listdir(self.backup_dir):
            if backup_file.endswith('.bak'):
                if filename_filter and not backup_file.startswith(filename_filter):
                    continue
                
                backup_path = os.path.join(self.backup_dir, backup_file)
                mtime = os.path.getmtime(backup_path)
                backups.append({
                    'file': backup_file,
                    'path': backup_path,
                    'mtime': mtime,
                    'timestamp': datetime.fromtimestamp(mtime)
                })
        
        return sorted(backups, key=lambda x: x['mtime'], reverse=True)
    
    def restore_backup(self, backup_path: str, target_path: str) -> bool:
        """Restore a file from backup"""
        try:
            shutil.copy2(backup_path, target_path)
            console.print(f"[green]✅ Restored {target_path} from backup[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Error restoring backup: {e}[/red]")
            return False