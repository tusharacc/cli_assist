"""
Interactive mode for Lumos CLI
"""

import os
import re
from rich.console import Console
from ..core import LLMRouter, EmbeddingDB, HistoryManager
from ..core.persona_manager import PersonaManager
from ..ui import console, show_footer, display_claude_style_prompt
from .intent_detection import detect_intent
from .handlers import (
    interactive_github, interactive_jenkins, interactive_jira,
    interactive_neo4j, interactive_appdynamics, interactive_code
)

def interactive_mode():
    """Enhanced interactive mode with command detection"""
    # Initialize components
    router = LLMRouter()
    db = EmbeddingDB()
    history = HistoryManager()
    persona = PersonaManager()
    
    # Get current repository context
    current_repo = os.path.basename(os.getcwd())
    context = {"repository": current_repo}
    
    # Get current session
    current_session = history.get_or_create_session()
    
    # Get repository stats
    repo_stats = history.get_repository_stats(current_repo)
    
    # Show header
    from ..ui import create_header
    create_header(console, "Lumos CLI", "Interactive AI Assistant")
    
    # Session info
    console.print(f"[dim]💾 Session: {current_session} | 📚 {repo_stats['message_count']} messages across {repo_stats['session_count']} sessions[/dim]\n")
    
    while True:
        try:
            user_input = display_claude_style_prompt()
            
            if not user_input:
                continue
                
            # Handle exit commands
            if user_input.lower() in ['exit', 'quit', 'bye', '/exit']:
                console.print("\n[green]👋 Thanks for using Lumos! Happy coding![/green]")
                break
                
            # Handle special slash commands
            if user_input.startswith('/'):
                if user_input.startswith('/help'):
                    _show_interactive_help()
                    show_footer(compact=True)
                    continue
                elif user_input.startswith('/edit'):
                    instruction = user_input[5:].strip()
                    if instruction:
                        _interactive_edit(instruction)
                    else:
                        console.print("[yellow]Usage: /edit <instruction> [file]  or  /edit <file> <instruction>[/yellow]")
                    show_footer(compact=True)
                    continue
                elif user_input.startswith('/plan'):
                    goal = user_input[5:].strip()
                    if goal:
                        _interactive_plan(goal)
                    else:
                        console.print("[yellow]Usage: /plan <goal>[/yellow]")
                    show_footer(compact=True)
                    continue
                elif user_input.startswith('/review'):
                    file_path = user_input[7:].strip()
                    if file_path:
                        _interactive_review(file_path)
                    else:
                        console.print("[yellow]Usage: /review <file>[/yellow]")
                    show_footer(compact=True)
                    continue
                elif user_input.startswith('/sessions'):
                    _show_sessions(history)
                    show_footer(compact=True)
                    continue
                elif user_input.startswith('/footer'):
                    query = user_input[7:].strip()
                    if query == "compact":
                        show_footer(compact=True)
                    elif query == "full":
                        show_footer(compact=False)
                    elif query == "status":
                        from ..ui import show_status_footer
                        show_status_footer()
                    elif query == "help":
                        from ..ui import show_quick_reference
                        show_quick_reference()
                    else:
                        show_footer(compact=True)
                    continue
                elif user_input.startswith('/shell'):
                    command = user_input[6:].strip()
                    if command:
                        _interactive_shell(command)
                    else:
                        console.print("[yellow]Usage: /shell <command>[/yellow]")
                    show_footer(compact=True)
                    continue
                # Handle explicit intent prefixes
                elif user_input.startswith('/github'):
                    query = user_input[7:].strip()
                    if query:
                        interactive_github(query)
                    else:
                        console.print("[yellow]Usage: /github <query>[/yellow]")
                    show_footer(compact=True)
                    continue
                elif user_input.startswith('/jenkins'):
                    query = user_input[8:].strip()
                    if query:
                        interactive_jenkins(query)
                    else:
                        console.print("[yellow]Usage: /jenkins <query>[/yellow]")
                    show_footer(compact=True)
                    continue
                elif user_input.startswith('/jira'):
                    query = user_input[5:].strip()
                    if query:
                        interactive_jira(query)
                    else:
                        console.print("[yellow]Usage: /jira <query>[/yellow]")
                    show_footer(compact=True)
                    continue
                elif user_input.startswith('/neo4j'):
                    query = user_input[6:].strip()
                    if query:
                        interactive_neo4j(query)
                    else:
                        console.print("[yellow]Usage: /neo4j <query>[/yellow]")
                    show_footer(compact=True)
                    continue
                elif user_input.startswith('/appdynamics'):
                    query = user_input[12:].strip()
                    if query:
                        interactive_appdynamics(query)
                    else:
                        console.print("[yellow]Usage: /appdynamics <query>[/yellow]")
                    show_footer(compact=True)
                    continue
                elif user_input.startswith('/code'):
                    query = user_input[5:].strip()
                    if query:
                        interactive_code(query)
                    else:
                        console.print("[yellow]Usage: /code <action> [options][/yellow]")
                        _show_code_help()
                    show_footer(compact=True)
                    continue
                else:
                    console.print(f"[red]Unknown command: {user_input}[/red]")
                    show_footer(compact=True)
                    continue
            
            # Smart command detection in natural language
            detected_command = detect_intent(user_input)
            
            # Check if we should suggest explicit intent for better performance
            if detected_command.get('confidence', 0) < 0.7:
                console.print("[dim]💡 Tip: Use explicit commands for faster results: /github, /jenkins, /jira, /code[/dim]")
            
            # Route to appropriate handler
            if detected_command['type'] == 'github':
                interactive_github(detected_command.get('query', user_input))
            elif detected_command['type'] == 'jenkins':
                interactive_jenkins(detected_command.get('query', user_input))
            elif detected_command['type'] == 'jira':
                interactive_jira(detected_command.get('query', user_input))
            elif detected_command['type'] == 'neo4j':
                interactive_neo4j(detected_command.get('query', user_input))
            elif detected_command['type'] == 'appdynamics':
                interactive_appdynamics(detected_command.get('query', user_input))
            elif detected_command['type'] == 'code':
                interactive_code(detected_command.get('query', user_input))
            elif detected_command['type'] == 'edit':
                _show_legacy_intent_warning('edit')
                interactive_code(f"edit {detected_command.get('instruction', detected_command.get('query', ''))}")
            elif detected_command['type'] == 'plan':
                _show_legacy_intent_warning('plan')
                interactive_code(f"plan {detected_command.get('instruction', detected_command.get('query', ''))}")
            elif detected_command['type'] == 'review':
                _show_legacy_intent_warning('review')
                interactive_code(f"review {detected_command.get('file', detected_command.get('query', ''))}")
            elif detected_command['type'] == 'start':
                _interactive_start(detected_command['instruction'])
            elif detected_command['type'] == 'fix':
                _show_legacy_intent_warning('fix')
                interactive_code(f"fix {detected_command.get('instruction', detected_command.get('query', ''))}")
            elif detected_command['type'] == 'shell':
                _interactive_shell(detected_command['command'])
            else:
                # Default to chat mode
                _interactive_chat(user_input, router, db, history, persona, context)
            
            # Show compact footer after each interaction
            if user_input.lower() not in ['/footer', '/help', '/sessions']:
                show_footer(compact=True)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' or '/exit' to quit[/yellow]")
        except EOFError:
            console.print("\n[green]👋 Goodbye![/green]")
            break

def _show_interactive_help():
    """Show interactive mode help"""
    console.print("\n[bold blue]🌟 Lumos CLI Interactive Mode[/bold blue]")
    console.print("\n[bold]Available Commands:[/bold]")
    console.print("  [cyan]/help[/cyan]           - Show this help")
    console.print("  [cyan]/edit[/cyan]           - Edit code")
    console.print("  [cyan]/plan[/cyan]           - Create implementation plan")
    console.print("  [cyan]/review[/cyan]         - Review code quality")
    console.print("  [cyan]/sessions[/cyan]       - Manage chat sessions")
    console.print("  [cyan]/footer[/cyan]         - Show footer options")
    console.print("  [cyan]/shell[/cyan]          - Execute shell commands")
    console.print("\n[bold]Service Commands:[/bold]")
    console.print("  [green]/github[/green]       - GitHub operations")
    console.print("  [blue]/jenkins[/blue]        - Jenkins operations")
    console.print("  [yellow]/jira[/yellow]        - Jira operations")
    console.print("  [magenta]/neo4j[/magenta]     - Neo4j operations")
    console.print("  [red]/appdynamics[/red]      - AppDynamics operations")
    console.print("  [cyan]/code[/cyan]           - Code operations")
    console.print("\n[bold]Natural Language:[/bold]")
    console.print("  Just type naturally! Examples:")
    console.print("  • 'add error handling to api.py'")
    console.print("  • 'get latest PRs from scimarketplace/externaldata'")
    console.print("  • 'show me failed builds in jenkins'")
    console.print("  • 'analyze dependencies of UserService'")
    console.print("\n[bold]Exit:[/bold] [dim]exit, quit, bye, or Ctrl+C[/dim]")

def _show_legacy_intent_warning(intent: str):
    """Show warning for legacy intents"""
    console.print(f"[yellow]⚠️ '{intent}' is deprecated. Use '/code {intent}' instead.[/yellow]")

def _show_code_help():
    """Show code command help"""
    console.print("\n[bold blue]Code Command Help[/bold blue]")
    console.print("\n[bold]Available Actions:[/bold]")
    console.print("  [cyan]generate[/cyan]  - Generate new code")
    console.print("  [cyan]edit[/cyan]      - Edit existing code")
    console.print("  [cyan]test[/cyan]      - Run tests")
    console.print("  [cyan]analyze[/cyan]   - Analyze code quality")
    console.print("  [cyan]refactor[/cyan]  - Refactor code")
    console.print("  [cyan]docs[/cyan]      - Generate documentation")
    console.print("  [cyan]format[/cyan]    - Format code")
    console.print("  [cyan]validate[/cyan]  - Validate code")
    console.print("\n[bold]Examples:[/bold]")
    console.print("  /code generate 'create a REST API endpoint'")
    console.print("  /code edit api.py 'add error handling'")
    console.print("  /code test tests/")
    console.print("  /code analyze src/main.py")

def _show_sessions(history):
    """Show session management"""
    console.print("\n[bold blue]Session Management[/bold blue]")
    sessions = history.get_sessions()
    if sessions:
        for session in sessions[-5:]:  # Show last 5
            console.print(f"  {session['id']} - {session['title']}")
    else:
        console.print("  No sessions found")

def _interactive_edit(instruction: str, file_path: str = None):
    """Handle edit command in interactive mode"""
    try:
        from ..commands.edit import edit
        edit(instruction, file_path)
    except Exception as e:
        console.print(f"[red]Edit error: {e}[/red]")

def _interactive_plan(goal: str):
    """Handle plan command in interactive mode"""  
    try:
        from ..commands.plan import plan
        plan(goal)
    except Exception as e:
        console.print(f"[red]Planning error: {e}[/red]")

def _interactive_review(file_path: str):
    """Handle review command in interactive mode"""
    try:
        if not file_path:
            console.print("[yellow]Please specify a file to review[/yellow]")
            return
        from ..commands.review import review
        review(file_path)
    except Exception as e:
        console.print(f"[red]Review error: {e}[/red]")

def _interactive_start(instruction: str):
    """Handle start command in interactive mode"""
    try:
        # Extract command from instruction
        if 'start' in instruction.lower():
            # Look for command after 'start'
            parts = instruction.split(' ', 1)
            if len(parts) > 1:
                command = parts[1]
                console.print(f"[cyan]🚀 Starting: {command}[/cyan]")
                from ..commands.start import start
                start(command)
            else:
                console.print("[yellow]Please specify what to start[/yellow]")
        else:
            console.print("[yellow]Please specify what to start[/yellow]")
    except Exception as e:
        console.print(f"[red]Start error: {e}[/red]")

def _interactive_shell(command: str):
    """Handle shell command in interactive mode"""
    try:
        from ..shell_executor import execute_shell_command
        
        # Add context about interactive mode
        context = {
            "mode": "interactive",
            "command": command,
            "timestamp": "now"
        }
        
        console.print(f"[cyan]🔧 Executing: {command}[/cyan]")
        result = execute_shell_command(command, context)
        
        if result['success']:
            console.print(f"[green]✅ Command completed successfully[/green]")
            if result['output']:
                console.print(f"\n[bold]Output:[/bold]")
                console.print(result['output'])
        else:
            console.print(f"[red]❌ Command failed[/red]")
            if result['error']:
                console.print(f"\n[bold]Error:[/bold]")
                console.print(result['error'])
                
    except Exception as e:
        console.print(f"[red]Shell error: {e}[/red]")

def _interactive_chat(user_input: str, router, db, history, persona, context):
    """Handle general chat in interactive mode with intelligent file discovery"""
    try:
        # Check if user is asking for program analysis (errors, bugs, or output issues)
        global _last_execution_info
        analysis_patterns = [
            'analyze the failure', 'analyze this failure', 'what went wrong',
            'why did it fail', 'explain the error', 'debug the error',
            'what caused the failure', 'help with the error',
            # Bug analysis patterns
            'check the output', 'analyze the program', 'why no data', 
            'output is wrong', 'not working correctly', 'program bug',
            'suggest fix', 'fix the bug', 'debug the program'
        ]
        
        user_lower = user_input.lower()
        if any(pattern in user_lower for pattern in analysis_patterns) and _last_execution_info:
            
            if not _last_execution_info['success']:
                # Runtime error - program crashed
                console.print("[dim]🔍 Analyzing recent runtime failure...[/dim]")
                
                try:
                    from ..utils.failure_analyzer import analyze_command_failure, failure_analyzer
                    
                    # Get detailed analysis
                    analysis = analyze_command_failure(
                        _last_execution_info['command'],
                        _last_execution_info['stdout'], 
                        _last_execution_info['stderr'],
                        1  # Assume exit code 1 for failures
                    )
                    
                    # Display comprehensive analysis
                    failure_analyzer.display_analysis(analysis)
                    
                    # Add to history
                    analysis_summary = f"Analyzed runtime failure of '{_last_execution_info['command']}': {analysis.likely_cause}"
                    history.add_message("user", user_input, command="failure_analysis")
                    history.add_message("assistant", analysis_summary, command="failure_analysis")
                    
                    console.print(f"\n[dim]💡 This analysis was based on the recent runtime error[/dim]")
                    show_footer(compact=True)
                    return
                    
                except Exception as e:
                    console.print(f"[red]Failed to analyze: {e}[/red]")
                    # Fall through to normal processing
            
            else:
                # Logic bug - program ran successfully but output is wrong
                console.print("[dim]🐛 Analyzing program logic and output...[/dim]")
                console.print(f"[dim]📋 Last successful execution: {_last_execution_info['command']}[/dim]")
                
                # This is a logic bug, not a runtime error - use normal LLM analysis
                # Fall through to normal processing to let LLM analyze the code
        
        elif any(pattern in user_lower for pattern in analysis_patterns) and not _last_execution_info:
            console.print("[yellow]No recent program execution to analyze.[/yellow]")
            console.print("[dim]Run a program first, then ask me to analyze it.[/dim]")
            show_footer(compact=True)
            return
        
        # Always try smart file discovery first - let the LLM decide if it needs the files
        console.print("[dim]🔍 Analyzing your request and searching for relevant files...[/dim]")
        
        # Use smart file discovery to find relevant files
        from ..utils.file_discovery import SmartFileDiscovery
        discovery = SmartFileDiscovery(".", console)
        
        # Get suggested files based on the user's description
        suggested_files = discovery.discover_files(user_input)
        
        if suggested_files and suggested_files[0].score > 3.0:  # Only use if reasonably relevant
            console.print(f"[dim]📂 Found {len(suggested_files)} potentially relevant files[/dim]")
            
            # Read the most relevant files automatically
            file_contents = {}
            for file_candidate in suggested_files[:3]:  # Top 3 files
                try:
                    with open(file_candidate.path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_contents[file_candidate.path] = content
                        console.print(f"[dim]📖 Analyzed: {file_candidate.path} (score: {file_candidate.score:.1f})[/dim]")
                except Exception as e:
                    console.print(f"[dim]⚠️ Could not read {file_candidate.path}: {e}[/dim]")
            
            # Build comprehensive context with file contents
            if file_contents:
                file_context = ""
                for file_path, content in file_contents.items():
                    file_context += f"\n\n=== {file_path} ===\n{content}"
                
                user_content = f"""{user_input}\n\nRELEVANT FILES FOUND AND ANALYZED:\n{file_context}\n\nPlease analyze the above in context of my request. If this is a bug/issue, provide a solution. If this is a general question, use the code as reference for your answer."""
            else:
                # Fallback to embedding search
                ctx = db.search(user_input, top_k=3)
                snippets = "\n\n".join(c for _,c,_ in ctx)
                user_content = f"""{user_input}\n        
RELATED CODE (from embeddings):\n{snippets}"""
        else:
            console.print("[dim]📂 No specific files identified, using general code search...[/dim]")
            # Fallback to embedding search
            ctx = db.search(user_input, top_k=3)
            snippets = "\n\n".join(c for _,c,_ in ctx)
            user_content = f"""{user_input}\n        
RELATED CODE:\n{snippets}"""
        
        # Add to history
        history.add_message("user", user_content, command="interactive")
        
        # Get conversation context and enhance with persona
        conversation_history = history.get_recent_context(max_tokens=4000)
        enhanced_messages = persona.get_enhanced_messages(conversation_history, context, "chat")
        
        # Get response
        resp = router.chat(enhanced_messages)
        
        # Add response to history
        history.add_message("assistant", resp, command="interactive")
        
        console.print(f"\n[bold green]🤖 Lumos:[/bold green] {resp}\n")
        show_footer(compact=True)
        
    except Exception as e:
        console.print(f"[red]Chat error: {e}[/red]")
        show_footer(compact=True)

# Global variable for last execution info
_last_execution_info = None
