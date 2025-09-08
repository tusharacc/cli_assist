"""
Code interactive mode handlers
"""

from rich.console import Console
from ...core.code_manager import CodeManager
from ...utils.debug_logger import debug_logger

console = Console()

def interactive_code(query: str):
    """Handle code operations in interactive mode"""
    try:
        # Parse the query to extract action and parameters
        words = query.split()
        if not words:
            console.print("[yellow]Usage: /code <action> [options][/yellow]")
            console.print("Available actions: generate, edit, test, analyze, refactor, docs, format, validate")
            return
        
        action = words[0].lower()
        remaining_query = " ".join(words[1:]) if len(words) > 1 else ""
        
        # Initialize code manager
        code_manager = CodeManager()
        
        if action == "generate":
            if not remaining_query:
                console.print("[yellow]Usage: /code generate <description> [language] [options][/yellow]")
                return
            
            # Extract language if specified
            language = "python"  # default
            if any(word in remaining_query.lower() for word in ["javascript", "js", "typescript", "ts", "java", "go", "rust", "c++", "cpp"]):
                for word in remaining_query.split():
                    if word.lower() in ["javascript", "js"]:
                        language = "javascript"
                    elif word.lower() in ["typescript", "ts"]:
                        language = "typescript"
                    elif word.lower() == "java":
                        language = "java"
                    elif word.lower() == "go":
                        language = "go"
                    elif word.lower() == "rust":
                        language = "rust"
                    elif word.lower() in ["c++", "cpp"]:
                        language = "cpp"
                    break
            
            console.print(f"[cyan]🔧 Generating {language} code: {remaining_query}[/cyan]")
            result = code_manager.generate_code(remaining_query, language=language)
            console.print(f"\n[bold]Generated Code:[/bold]")
            console.print(f"[green]{result}[/green]")
        
        elif action == "edit":
            if not remaining_query:
                console.print("[yellow]Usage: /code edit <file> <instruction>[/yellow]")
                return
            
            # Split file and instruction
            parts = remaining_query.split(" ", 1)
            if len(parts) < 2:
                console.print("[yellow]Usage: /code edit <file> <instruction>[/yellow]")
                return
            
            file_path = parts[0]
            instruction = parts[1]
            
            console.print(f"[cyan]✏️ Editing {file_path}: {instruction}[/cyan]")
            result = code_manager.edit_code(file_path, instruction)
            console.print(f"\n[bold]Edit Result:[/bold]")
            console.print(f"[green]{result}[/green]")
        
        elif action == "test":
            if not remaining_query:
                console.print("[yellow]Usage: /code test <file_or_directory>[/yellow]")
                return
            
            console.print(f"[cyan]🧪 Testing: {remaining_query}[/cyan]")
            result = code_manager.run_tests(remaining_query)
            console.print(f"\n[bold]Test Results:[/bold]")
            console.print(f"[green]{result}[/green]")
        
        elif action == "analyze":
            if not remaining_query:
                console.print("[yellow]Usage: /code analyze <file>[/yellow]")
                return
            
            console.print(f"[cyan]🔍 Analyzing: {remaining_query}[/cyan]")
            result = code_manager.analyze_code(remaining_query)
            console.print(f"\n[bold]Analysis Results:[/bold]")
            console.print(f"[green]{result}[/green]")
        
        elif action == "refactor":
            if not remaining_query:
                console.print("[yellow]Usage: /code refactor <file> <instruction>[/yellow]")
                return
            
            # Split file and instruction
            parts = remaining_query.split(" ", 1)
            if len(parts) < 2:
                console.print("[yellow]Usage: /code refactor <file> <instruction>[/yellow]")
                return
            
            file_path = parts[0]
            instruction = parts[1]
            
            console.print(f"[cyan]🔄 Refactoring {file_path}: {instruction}[/cyan]")
            result = code_manager.refactor_code(file_path, instruction)
            console.print(f"\n[bold]Refactoring Results:[/bold]")
            console.print(f"[green]{result}[/green]")
        
        elif action == "docs":
            if not remaining_query:
                console.print("[yellow]Usage: /code docs <file>[/yellow]")
                return
            
            console.print(f"[cyan]📚 Generating documentation: {remaining_query}[/cyan]")
            result = code_manager.generate_documentation(remaining_query)
            console.print(f"\n[bold]Documentation:[/bold]")
            console.print(f"[green]{result}[/green]")
        
        elif action == "format":
            if not remaining_query:
                console.print("[yellow]Usage: /code format <file>[/yellow]")
                return
            
            console.print(f"[cyan]🎨 Formatting: {remaining_query}[/cyan]")
            result = code_manager.format_code(remaining_query)
            console.print(f"\n[bold]Formatting Results:[/bold]")
            console.print(f"[green]{result}[/green]")
        
        elif action == "validate":
            if not remaining_query:
                console.print("[yellow]Usage: /code validate <file>[/yellow]")
                return
            
            console.print(f"[cyan]✅ Validating: {remaining_query}[/cyan]")
            result = code_manager.validate_code(remaining_query)
            console.print(f"\n[bold]Validation Results:[/bold]")
            console.print(f"[green]{result}[/green]")
        
        else:
            console.print(f"[red]Unknown action: {action}[/red]")
            console.print("Available actions: generate, edit, test, analyze, refactor, docs, format, validate")
    
    except Exception as e:
        console.print(f"[red]Code command error: {e}[/red]")
