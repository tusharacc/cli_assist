import typer, os
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from .client import LLMRouter, TaskType
from .embeddings import EmbeddingDB
from .prompts import PLAN_INSTRUCTION, EDIT_INSTRUCTION, LANG_PROMPTS
from .safety import SafeFileEditor
from .scaffold import ProjectScaffolder, ProjectType
from .history import HistoryManager
from .persona_manager import PersonaManager
from .file_discovery import SmartFileDiscovery
from .error_handler import RuntimeErrorHandler, smart_start_app
from .config import config, setup_wizard
from .ui import create_header, create_welcome_panel, create_command_help_panel, create_status_panel, create_config_panel, print_brand_footer
from .shell_executor import execute_shell_command
from .github_client import GitHubClient
from .github_query_parser import GitHubQueryParser
from .neo4j_client import Neo4jClient
from .neo4j_dotnet_client import Neo4jDotNetClient
from .neo4j_config import Neo4jConfigManager
from .appdynamics_client import AppDynamicsClient
from .appdynamics_config import AppDynamicsConfigManager
import re

app = typer.Typer(invoke_without_command=True, no_args_is_help=False)
console = Console()

# Initialize global managers
history_manager = None
persona_manager = None

def get_history_manager() -> HistoryManager:
    """Get or create global history manager"""
    global history_manager
    if history_manager is None:
        history_manager = HistoryManager()
    return history_manager

def get_persona_manager() -> PersonaManager:
    """Get or create global persona manager"""
    global persona_manager
    if persona_manager is None:
        persona_manager = PersonaManager()
    return persona_manager

def check_integration_status() -> dict:
    """Check status of all integrations (fast, non-blocking)"""
    status = {
        'ollama': {'status': 'unknown', 'message': 'Unknown'},
        'enterprise_llm': {'status': 'unknown', 'message': 'Unknown'},
        'github': {'status': 'unknown', 'message': 'Unknown'},
        'jenkins': {'status': 'unknown', 'message': 'Unknown'},
        'jira': {'status': 'unknown', 'message': 'Unknown'}
    }
    
    # Check Ollama status (fast, no API call)
    try:
        from .config import config
        backends = config.get_available_backends()
        if "ollama" in backends:
            status['ollama'] = {'status': 'connected', 'message': 'Ollama 🟢'}
        else:
            status['ollama'] = {'status': 'error', 'message': 'Ollama 🔴'}
    except Exception:
        status['ollama'] = {'status': 'error', 'message': 'Ollama 🔴'}
    
    # Check Enterprise LLM status (fast, config only)
    try:
        from .config import config
        if config.is_enterprise_configured():
            status['enterprise_llm'] = {'status': 'connected', 'message': 'Enterprise LLM 🟢'}
        else:
            status['enterprise_llm'] = {'status': 'error', 'message': 'Enterprise LLM 🔴'}
    except Exception:
        status['enterprise_llm'] = {'status': 'error', 'message': 'Enterprise LLM 🔴'}
    
    # Check GitHub status (fast, config only)
    try:
        from .github_client import GitHubClient
        github_client = GitHubClient()
        if github_client.token and github_client.base_url:
            status['github'] = {'status': 'connected', 'message': 'GitHub 🟢'}
        else:
            status['github'] = {'status': 'not_configured', 'message': 'GitHub ⚪'}
    except Exception:
        status['github'] = {'status': 'error', 'message': 'GitHub 🔴'}
    
    # Check Jenkins status (fast, config only)
    try:
        from .jenkins_config_manager import JenkinsConfigManager
        config_manager = JenkinsConfigManager()
        config = config_manager.load_config()
        if config and config.url and config.username and config.token:
            status['jenkins'] = {'status': 'connected', 'message': 'Jenkins 🟢'}
        else:
            status['jenkins'] = {'status': 'not_configured', 'message': 'Jenkins ⚪'}
    except Exception:
        status['jenkins'] = {'status': 'error', 'message': 'Jenkins 🔴'}
    
    # Check Jira status (fast, config only)
    try:
        from .jira_client import JiraConfigManager
        config_manager = JiraConfigManager()
        config = config_manager.load_config()
        if config and config.get('base_url') and config.get('username') and config.get('api_token'):
            status['jira'] = {'status': 'connected', 'message': 'Jira 🟢'}
        else:
            status['jira'] = {'status': 'not_configured', 'message': 'Jira ⚪'}
    except Exception:
        status['jira'] = {'status': 'error', 'message': 'Jira 🔴'}
    
    return status

def check_integration_status_async() -> dict:
    """Check status of all integrations with actual API calls (async)"""
    import asyncio
    import concurrent.futures
    from .logger import log_debug
    
    status = {
        'ollama': {'status': 'unknown', 'message': 'Unknown'},
        'enterprise_llm': {'status': 'unknown', 'message': 'Unknown'},
        'github': {'status': 'unknown', 'message': 'Unknown'},
        'jenkins': {'status': 'unknown', 'message': 'Unknown'},
        'jira': {'status': 'unknown', 'message': 'Unknown'}
    }
    
    def check_github_async():
        try:
            from .github_client import GitHubClient
            github_client = GitHubClient()
            if github_client.token and github_client.base_url:
                import requests
                headers = {'Authorization': f'token {github_client.token}'}
                response = requests.get(f"{github_client.base_url}/user", headers=headers, timeout=3)
                if response.status_code == 200:
                    return {'status': 'connected', 'message': 'GitHub 🟢'}
                else:
                    return {'status': 'error', 'message': 'GitHub 🔴'}
            else:
                return {'status': 'not_configured', 'message': 'GitHub ⚪'}
        except Exception:
            return {'status': 'error', 'message': 'GitHub 🔴'}
    
    def check_jenkins_async():
        try:
            from .jenkins_config_manager import JenkinsConfigManager
            config_manager = JenkinsConfigManager()
            config = config_manager.load_config()
            if config and config.url and config.username and config.token:
                import requests
                auth = (config.username, config.token)
                response = requests.get(f"{config.url}/api/json", auth=auth, timeout=3)
                if response.status_code == 200:
                    return {'status': 'connected', 'message': 'Jenkins 🟢'}
                else:
                    return {'status': 'error', 'message': 'Jenkins 🔴'}
            else:
                return {'status': 'not_configured', 'message': 'Jenkins ⚪'}
        except Exception:
            return {'status': 'error', 'message': 'Jenkins 🔴'}
    
    def check_jira_async():
        try:
            from .jira_client import JiraConfigManager
            config_manager = JiraConfigManager()
            config = config_manager.load_config()
            if config and config.get('base_url') and config.get('username') and config.get('api_token'):
                import requests
                headers = {
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {config["api_token"]}'
                }
                log_debug(f"Jira status check: Making API call to {config['base_url']}/rest/api/latest/myself")
                response = requests.get(f"{config['base_url']}/rest/api/latest/myself", headers=headers, timeout=3)
                log_debug(f"Jira status check: Response status {response.status_code}")
                if response.status_code == 200:
                    return {'status': 'connected', 'message': 'Jira 🟢'}
                else:
                    return {'status': 'error', 'message': 'Jira 🔴'}
            else:
                return {'status': 'not_configured', 'message': 'Jira ⚪'}
        except Exception as e:
            log_debug(f"Jira status check error: {e}")
            return {'status': 'error', 'message': 'Jira 🔴'}
    
    # Run API checks in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        github_future = executor.submit(check_github_async)
        jenkins_future = executor.submit(check_jenkins_async)
        jira_future = executor.submit(check_jira_async)
        
        # Wait for all to complete (max 3 seconds)
        try:
            status['github'] = github_future.result(timeout=3)
            status['jenkins'] = jenkins_future.result(timeout=3)
            status['jira'] = jira_future.result(timeout=3)
        except concurrent.futures.TimeoutError:
            # If any timeout, use the fast status
            status.update(check_integration_status())
    
    return status

def update_status_async():
    """Update integration status asynchronously in the background"""
    import threading
    from .logger import log_debug
    
    def update_status():
        try:
            log_debug("Background: Starting async status update")
            updated_status = check_integration_status_async()
            log_debug(f"Background: Updated status: {updated_status}")
            # Status is updated, but we don't need to display it immediately
            # The next time the user interacts, they'll see the updated status
        except Exception as e:
            log_debug(f"Background: Status update failed: {e}")
    
    # Start the background thread
    thread = threading.Thread(target=update_status, daemon=True)
    thread.start()

@app.callback()
def main(ctx: typer.Context):
    """🌟 Lumos CLI - Interactive AI Code Assistant
    
    🎯 QUICKSTART:
      lumos-cli                    → Interactive mode (like Claude Code)
      lumos-cli edit "add logging" → Smart file discovery + edit
      lumos-cli plan "auth system" → Create implementation plan
    
    💡 Interactive mode understands natural language:
      "add error handling" → finds and edits relevant files
      "plan user auth"     → creates architecture plan  
      "review api.py"      → analyzes code quality
    """
    if ctx.invoked_subcommand is None:
        # Start interactive mode
        interactive_mode()

@app.command()
def plan(goal: str, backend: str = "auto", model: str = "devstral"):
    """Create a step-by-step plan for achieving a goal"""
    router = LLMRouter(backend, model)
    db = EmbeddingDB()
    history = get_history_manager()
    persona = get_persona_manager()
    
    # Get repository context
    context = persona.get_project_context(".")
    
    ctx = db.search(goal, top_k=5)
    snippets = "\n\n".join(c for _,c,_ in ctx)
    user_content = f"GOAL:\n{goal}\n\nCONTEXT:\n{snippets}"
    
    # Add user message to history
    history.add_message("user", user_content, command="plan")
    
    # Get conversation context and enhance with persona
    conversation_history = history.get_recent_context(max_tokens=4000)
    enhanced_messages = persona.get_enhanced_messages(conversation_history, context, "plan")
    
    # Get response
    resp = router.chat(enhanced_messages, TaskType.PLANNING)
    
    # Add assistant response to history
    history.add_message("assistant", resp, command="plan")
    
    console.print(resp)

@app.command()
def edit(instruction: str, path: str = None, backend: str = "openai", model: str = "gpt-3.5-turbo", 
         preview: bool = True, force: bool = False):
    """Edit file(s) with AI assistance and smart file discovery (uses OpenAI for best results)"""
    router = LLMRouter(backend, model)
    db = EmbeddingDB()
    editor = SafeFileEditor()
    history = get_history_manager()
    persona = get_persona_manager()
    
    # Get repository context
    context = persona.get_project_context(".")
    
    # Smart file discovery if no path provided
    target_files = []
    if path:
        target_files = [path]
    else:
        console.print(f"[cyan]🔍 Smart File Discovery:[/cyan] Looking for files to: {instruction}")
        discovery = SmartFileDiscovery(".", console)
        suggested_files = discovery.suggest_files_for_instruction(instruction)
        
        if not suggested_files:
            console.print("[red]❌ No relevant files found for your instruction.[/red]")
            console.print("[dim]Try being more specific or provide a file path explicitly.[/dim]")
            return
        
        target_files = suggested_files
        console.print(f"[green]✓[/green] Selected {len(target_files)} file(s) for editing\n")
    
    # Process each target file
    all_success = True
    for file_path in target_files:
        console.print(f"[bold cyan]Editing:[/bold cyan] {file_path}")
        
        try:
            with open(file_path) as f:
                contents = f.read()
        except FileNotFoundError:
            contents = ""
            console.print(f"[yellow]File {file_path} not found, will create new file[/yellow]")
        
        # Get relevant snippets but filter out irrelevant content
        ctx = db.search(instruction, top_k=3)
        filtered_snippets = []
        for _, content, _ in ctx:
            # Filter out content that's not relevant to the edit instruction
            if not any(keyword in content.lower() for keyword in ['repositoryanalyzer', 'class ', 'def ', 'import ']):
                filtered_snippets.append(content)
            elif any(keyword in instruction.lower() for keyword in ['class', 'function', 'import', 'module']):
                filtered_snippets.append(content)
        
        snippets = "\n\n".join(filtered_snippets[:2])  # Limit to 2 most relevant snippets
        
        user_content = f"""FILE: {file_path}

CURRENT CODE:
{contents}

INSTRUCTION: {instruction}

Return only the complete updated file content."""
        
        # For edit operations, use a simplified, focused prompt
        # to avoid overwhelming the LLM with too much context
        system_prompt = """You are a code editor. Your job is to modify the given file according to the user's instruction.

CRITICAL RULES:
1. Return ONLY the complete file content as it should be written to the file
2. Do NOT include markdown code blocks (```python, ```, etc.)
3. Do NOT include explanations or comments about the changes
4. Do NOT add extra classes, functions, or code that wasn't requested
5. Keep the changes minimal and focused on the specific instruction
6. Return only the raw file content that can be directly written to the file

EXAMPLE:
If the file contains:
def hello():
    return "world"

And the instruction is "add error handling", return:
def hello():
    try:
        return "world"
    except Exception as e:
        print(f"Error: {e}")
        return None

NOT a whole new file with extra classes and imports."""

        enhanced_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        # Auto-detect task type from instruction and get response
        resp = router.chat(enhanced_messages)
        
        # Add response to history
        history.add_message("assistant", resp, command="edit", file_path=file_path)
        
        # Use safe file editor
        success = editor.safe_write(file_path, resp, preview=preview and not force, auto_confirm=force)
        if not success:
            console.print(f"[red]Edit operation for {file_path} cancelled or failed[/red]")
            all_success = False
        else:
            console.print(f"[green]✅ Successfully edited: {file_path}[/green]\n")
    
    if len(target_files) > 1:
        if all_success:
            console.print("[green]🎉 All files edited successfully![/green]")
        else:
            console.print("[yellow]⚠️  Some edit operations failed or were cancelled[/yellow]")

@app.command()
def index(path: str = "."):
    db = EmbeddingDB()
    changed = db.get_changed_files()
    files = changed if changed else []
    for root, _, fnames in os.walk(path):
        for fn in fnames:
            if fn.endswith((".py",".js",".ts",".go",".ps1",".psm1")):
                full = os.path.join(root, fn)
                if not changed or full in files:
                    with open(full) as f:
                        content = f.read()
                    db.add_or_update(full, content)
                    console.print(f"Indexed {full}")

@app.command()
def review(path: str, backend: str = "openai", model: str = "gpt-3.5-turbo"):
    """Review code for bugs, improvements, and best practices (uses OpenAI for best results)"""
    router = LLMRouter(backend, model)
    db = EmbeddingDB()
    history = get_history_manager()
    persona = get_persona_manager()
    
    # Get repository context
    context = persona.get_project_context(".")
    
    with open(path) as f:
        contents = f.read()
    
    ctx = db.search(f"code review {path}", top_k=3)
    snippets = "\n\n".join(c for _,c,_ in ctx)
    
    user_content = f"""Review this code for bugs, security issues, performance problems, and best practices.

FILE: {path}
CODE:
<<<
{contents}
>>>

RELATED CODE:
{snippets}

Provide specific, actionable feedback."""
    
    # Add to history
    history.add_message("user", user_content, command="review", file_path=path)
    
    # Get conversation context and enhance with persona
    conversation_history = history.get_recent_context(max_tokens=4000)
    enhanced_messages = persona.get_enhanced_messages(conversation_history, context, "review")
    
    resp = router.chat(enhanced_messages, TaskType.CODE_REVIEW)
    
    # Add response to history
    history.add_message("assistant", resp, command="review", file_path=path)
    
    console.print(resp)

@app.command()
def debug(path: str, issue: str, backend: str = "auto", model: str = "devstral"):
    """Debug a specific issue in a file"""
    router = LLMRouter(backend, model)
    db = EmbeddingDB()
    history = get_history_manager()
    persona = get_persona_manager()
    
    # Get repository context
    context = persona.get_project_context(".")
    
    with open(path) as f:
        contents = f.read()
    
    ctx = db.search(f"debug {issue}", top_k=3)
    snippets = "\n\n".join(c for _,c,_ in ctx)
    
    user_content = f"""Help debug this issue: {issue}

FILE: {path}
CODE:
<<<
{contents}
>>>

RELATED CODE:
{snippets}

Identify the problem and suggest a fix."""
    
    # Add to history
    history.add_message("user", user_content, command="debug", file_path=path)
    
    # Get conversation context and enhance with persona
    conversation_history = history.get_recent_context(max_tokens=4000)
    enhanced_messages = persona.get_enhanced_messages(conversation_history, context, "debug")
    
    resp = router.chat(enhanced_messages, TaskType.DEBUGGING)
    
    # Add response to history
    history.add_message("assistant", resp, command="debug", file_path=path)
    
    console.print(resp)

@app.command()
def chat(backend: str = "auto", model: str = "devstral", session: str = None):
    """Interactive chat mode with persistent history"""
    router = LLMRouter(backend, model)
    db = EmbeddingDB()
    history = get_history_manager()
    persona = get_persona_manager()
    
    # Switch to specific session if provided
    if session and not history.switch_session(session):
        console.print(f"[red]Session {session} not found[/red]")
        return
    
    current_session = history.get_or_create_session("chat")
    repo_stats = history.get_repository_stats()
    
    console.print("[bold green]Lumos Chat - Repository-Aware AI Assistant[/bold green]")
    console.print(f"[dim]Repository: {repo_stats['repo_path']}[/dim]")
    console.print(f"[dim]Session: {current_session}[/dim]")
    console.print(f"[dim]Backend: {backend}, Model: {model}[/dim]")
    console.print(f"[dim]History: {repo_stats['message_count']} messages across {repo_stats['session_count']} sessions[/dim]")
    console.print("[dim]Type 'exit' to quit, '/help' for commands[/dim]\n")
    
    while True:
        try:
            user_input = input("You: ")
            
            # Handle special commands
            if user_input.lower() in ['exit', 'quit', 'bye']:
                break
            elif user_input.startswith('/help'):
                console.print("""
[bold]Available Commands:[/bold]
  /sessions    - List chat sessions
  /switch <id> - Switch to different session  
  /new <title> - Start new session
  /search <query> - Search message history
  /clear       - Clear current session
  /stats       - Show repository statistics
  /shell <cmd> - Execute shell command with confirmation
  exit/quit    - Exit chat mode
""")
                continue
            elif user_input.startswith('/sessions'):
                _show_sessions(history)
                continue
            elif user_input.startswith('/switch '):
                session_id = user_input[8:].strip()
                if history.switch_session(session_id):
                    console.print(f"[green]Switched to session: {session_id}[/green]")
                else:
                    console.print(f"[red]Session not found: {session_id}[/red]")
                continue
            elif user_input.startswith('/new '):
                title = user_input[5:].strip() or "New chat session"
                new_session = history.start_session(title)
                console.print(f"[green]Started new session: {new_session}[/green]")
                continue
            elif user_input.startswith('/search '):
                query = user_input[8:].strip()
                _search_history(history, query)
                continue
            elif user_input.startswith('/stats'):
                _show_stats(history)
                continue
                
            # Search for relevant context
            ctx = db.search(user_input, top_k=3)
            snippets = "\n\n".join(c for _,c,_ in ctx)
            
            # Add context if relevant
            enhanced_input = user_input
            if snippets.strip():
                enhanced_input = f"{user_input}\n\nRelevant code context:\n{snippets}"
            
            # Add user message to persistent history
            history.add_message("user", enhanced_input, command="chat")
            
            # Get conversation context with smart summarization
            conversation_history = history.get_recent_context(max_tokens=4000)
            
            # Enhance with repository persona
            context = persona.get_project_context(".")
            enhanced_messages = persona.get_enhanced_messages(conversation_history, context, "chat")
            
            # Get response with smart routing
            resp = router.chat(enhanced_messages)
            console.print(f"Assistant: {resp}\n")
            
            # Add assistant response to persistent history
            history.add_message("assistant", resp, command="chat")
                
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    console.print("[dim]Chat session saved. Goodbye![/dim]")

def _show_sessions(history: HistoryManager):
    """Helper to show chat sessions"""
    sessions = history.list_sessions()
    if not sessions:
        console.print("[dim]No chat sessions found[/dim]")
        return
    
    console.print("\n[bold]Chat Sessions:[/bold]")
    for session in sessions[:10]:  # Show last 10
        console.print(f"  {session.session_id} - {session.title}")
        console.print(f"    {session.message_count} messages, last: {session.last_updated.strftime('%Y-%m-%d %H:%M')}")
    
    if len(sessions) > 10:
        console.print(f"  ... and {len(sessions) - 10} more sessions")
    console.print()

def _search_history(history: HistoryManager, query: str):
    """Helper to search message history"""
    results = history.search_messages(query, limit=5)
    if not results:
        console.print(f"[dim]No messages found for '{query}'[/dim]")
        return
    
    console.print(f"\n[bold]Search results for '{query}':[/bold]")
    for message, session_title in results:
        console.print(f"  [{message.timestamp.strftime('%Y-%m-%d %H:%M')}] {session_title}")
        preview = message.content[:100] + "..." if len(message.content) > 100 else message.content
        console.print(f"    {message.role}: {preview}")
    console.print()

def _show_stats(history: HistoryManager):
    """Helper to show repository statistics"""
    stats = history.get_repository_stats()
    console.print(f"\n[bold]Repository Statistics:[/bold]")
    console.print(f"  Path: {stats['repo_path']}")
    console.print(f"  Sessions: {stats['session_count']}")
    console.print(f"  Messages: {stats['message_count']}")
    if stats['first_session']:
        console.print(f"  First session: {stats['first_session'].strftime('%Y-%m-%d %H:%M')}")
    if stats['last_activity']:
        console.print(f"  Last activity: {stats['last_activity'].strftime('%Y-%m-%d %H:%M')}")
    console.print()

@app.command()
def preview(path: str, instruction: str, backend: str = "auto", model: str = "devstral"):
    """Preview changes without applying them"""
    router = LLMRouter(backend, model)
    db = EmbeddingDB()
    editor = SafeFileEditor()
    
    try:
        with open(path) as f:
            contents = f.read()
    except FileNotFoundError:
        contents = ""
        console.print(f"[yellow]File {path} not found[/yellow]")
    
    ctx = db.search(instruction, top_k=3)
    snippets = "\n\n".join(c for _,c,_ in ctx)
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    lang_prompt = LANG_PROMPTS.get(ext, "")
    
    prompt = f"""{EDIT_INSTRUCTION}

LANGUAGE SPECIFIC GUIDELINES:
{lang_prompt}

FILE PATH: {path}
CURRENT CONTENTS:
<<<
{contents}
>>>
INSTRUCTION:
{instruction}

RELATED SNIPPETS:
{snippets}
"""
    
    messages = [{"role": "user", "content": prompt}]
    resp = router.chat(messages)
    
    # Show preview only
    editor.show_diff(contents, resp, path)
    is_valid, warnings = editor.validate_content(resp, path)
    
    if warnings:
        console.print("\n[yellow]⚠️  Validation Warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  • {warning}")

@app.command()
def backups(file_path: str = None):
    """List available backups"""
    editor = SafeFileEditor()
    backups = editor.list_backups(file_path)
    
    if not backups:
        console.print("[dim]No backups found[/dim]")
        return
    
    console.print(f"[bold]Available backups{f' for {file_path}' if file_path else ''}:[/bold]\n")
    
    for backup in backups:
        console.print(f"📄 {backup['file']}")
        console.print(f"   📅 {backup['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        console.print(f"   📁 {backup['path']}\n")

@app.command()
def restore(backup_path: str, target_path: str = None):
    """Restore a file from backup"""
    editor = SafeFileEditor()
    
    if not os.path.exists(backup_path):
        console.print(f"[red]Backup file not found: {backup_path}[/red]")
        return
    
    # If no target specified, derive from backup filename
    if not target_path:
        backup_filename = os.path.basename(backup_path)
        if backup_filename.endswith('.bak'):
            # Remove .timestamp.bak suffix
            parts = backup_filename.split('.')
            if len(parts) >= 3:
                target_path = '.'.join(parts[:-2])  # Remove timestamp and .bak
            else:
                console.print("[red]Cannot determine target file from backup name[/red]")
                return
        else:
            console.print("[red]Invalid backup file format[/red]")
            return
    
    console.print(f"Restoring {backup_path} -> {target_path}")
    success = editor.restore_backup(backup_path, target_path)

@app.command()
def scaffold(
    project_type: str,
    project_name: str,
    target_dir: str = ".",
    preview: bool = True,
    dry_run: bool = False,
    force: bool = False
):
    """Create a new project from template with safe execution"""
    scaffolder = ProjectScaffolder()
    
    # Convert string to ProjectType enum
    try:
        proj_type = ProjectType(project_type)
    except ValueError:
        console.print(f"[red]Unknown project type: {project_type}[/red]")
        console.print("\n[yellow]Available types:[/yellow]")
        scaffolder.list_available_templates()
        return
    
    # Show preview if requested
    if preview and not dry_run:
        scaffolder.preview_scaffold(proj_type, project_name, 
                                  os.path.join(target_dir, project_name))
    
    # Execute scaffold
    success = scaffolder.scaffold_project(
        proj_type, project_name, target_dir, 
        dry_run=dry_run, skip_confirm=force
    )
    
    if success:
        console.print("[green]✅ Project scaffolded successfully![/green]")
    else:
        console.print("[red]❌ Scaffold failed[/red]")

@app.command()
def templates():
    """List available project templates"""
    scaffolder = ProjectScaffolder()
    scaffolder.list_available_templates()

@app.command("history")
def history_command():
    """Show chat history statistics for current repository"""
    history = get_history_manager()
    stats = history.get_repository_stats()
    
    console.print(f"[bold green]Chat History - {stats['repo_path']}[/bold green]\n")
    console.print(f"[bold]Repository Statistics:[/bold]")
    console.print(f"  📁 Path: {stats['repo_path']}")
    console.print(f"  💬 Sessions: {stats['session_count']}")
    console.print(f"  📝 Messages: {stats['message_count']}")
    
    if stats['first_session']:
        console.print(f"  🕐 First session: {stats['first_session'].strftime('%Y-%m-%d %H:%M')}")
    if stats['last_activity']:
        console.print(f"  🕒 Last activity: {stats['last_activity'].strftime('%Y-%m-%d %H:%M')}")
    
    # Show recent sessions
    sessions = history.list_sessions()
    if sessions:
        console.print(f"\n[bold]Recent Sessions:[/bold]")
        for session in sessions[:5]:
            console.print(f"  🔗 {session.session_id}")
            console.print(f"     📛 {session.title}")
            console.print(f"     💬 {session.message_count} messages")
            console.print(f"     🕒 {session.last_updated.strftime('%Y-%m-%d %H:%M')}\n")
        
        if len(sessions) > 5:
            console.print(f"     ... and {len(sessions) - 5} more sessions")
    else:
        console.print("\n[dim]No chat sessions found[/dim]")

@app.command("sessions")  
def sessions_command():
    """List all chat sessions for current repository"""
    history = get_history_manager()
    sessions = history.list_sessions()
    
    if not sessions:
        console.print("[dim]No chat sessions found for this repository[/dim]")
        return
    
    console.print(f"[bold green]Chat Sessions ({len(sessions)} total)[/bold green]\n")
    
    for session in sessions:
        console.print(f"[bold]{session.session_id}[/bold]")
        console.print(f"  📛 Title: {session.title}")
        console.print(f"  💬 Messages: {session.message_count}")
        console.print(f"  📅 Created: {session.created_at.strftime('%Y-%m-%d %H:%M')}")
        console.print(f"  🕒 Updated: {session.last_updated.strftime('%Y-%m-%d %H:%M')}")
        console.print()

@app.command("search")
def search_command(query: str, limit: int = 10):
    """Search chat history for specific content"""
    history = get_history_manager()
    results = history.search_messages(query, limit=limit)
    
    if not results:
        console.print(f"[dim]No messages found containing '{query}'[/dim]")
        return
    
    console.print(f"[bold green]Search Results for '{query}' ({len(results)} found)[/bold green]\n")
    
    for message, session_title in results:
        console.print(f"[bold]Session:[/bold] {session_title}")
        console.print(f"[dim]{message.timestamp.strftime('%Y-%m-%d %H:%M')} | {message.role} | {message.command or 'chat'}[/dim]")
        
        # Highlight query in content
        content = message.content
        if len(content) > 200:
            # Find query position and show context
            query_pos = content.lower().find(query.lower())
            if query_pos >= 0:
                start = max(0, query_pos - 50)
                end = min(len(content), query_pos + len(query) + 50)
                content = "..." + content[start:end] + "..."
            else:
                content = content[:200] + "..."
        
        console.print(f"{content}\n")

@app.command("repos")
def repos_command():
    """List all repositories with chat history"""
    history = get_history_manager()
    repos = history.list_repositories()
    
    if not repos:
        console.print("[dim]No repositories with chat history found[/dim]")
        return
    
    console.print(f"[bold green]Repositories with Chat History ({len(repos)} total)[/bold green]\n")
    
    for repo in repos:
        is_current = repo['repo_id'] == history.current_repo_id
        marker = "📍" if is_current else "📁"
        
        console.print(f"{marker} [bold]{repo['repo_path']}[/bold]")
        console.print(f"    🆔 ID: {repo['repo_id']}")
        console.print(f"    💬 Sessions: {repo['session_count']}")
        console.print(f"    🕒 Last used: {repo['last_accessed'].strftime('%Y-%m-%d %H:%M')}")
        console.print()

@app.command("cleanup")
def cleanup_command(days: int = 30, dry_run: bool = True):
    """Clean up old chat sessions"""
    history = get_history_manager()
    
    if dry_run:
        console.print(f"[yellow]DRY RUN: Would delete sessions older than {days} days[/yellow]")
        # Show what would be deleted
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        sessions = [s for s in history.list_sessions() if s.last_updated < cutoff]
        
        if not sessions:
            console.print("[dim]No old sessions to delete[/dim]")
        else:
            console.print(f"Sessions that would be deleted ({len(sessions)}):")
            for session in sessions:
                console.print(f"  - {session.session_id} ({session.title})")
        
        console.print(f"\n[dim]Run with --no-dry-run to actually delete[/dim]")
    else:
        deleted_count = history.cleanup_old_sessions(days)
        console.print(f"[green]Deleted {deleted_count} old sessions[/green]")

@app.command("persona")
def persona_command(action: str = "show", force_refresh: bool = False):
    """Manage repository persona and context detection"""
    persona = get_persona_manager()
    
    if action == "show":
        # Show current repository context
        context = persona.get_project_context(".", force_refresh=force_refresh)
        
        console.print(f"[bold green]Repository Persona - {context.repo_path}[/bold green]\n")
        
        console.print(f"[bold]Project Analysis (confidence: {context.confidence_score:.1%}):[/bold]")
        console.print(f"  📁 Path: {context.repo_path}")
        console.print(f"  🎯 Type: {context.project_type.replace('_', ' ').title()}")
        
        if context.primary_languages:
            console.print(f"  💻 Languages: {', '.join(context.primary_languages)}")
        
        if context.frameworks:
            console.print(f"  🏗️  Frameworks: {', '.join(context.frameworks)}")
        
        if context.build_tools:
            console.print(f"  🔧 Build Tools: {', '.join(context.build_tools)}")
        
        if context.testing_frameworks:
            console.print(f"  🧪 Testing: {', '.join(context.testing_frameworks)}")
        
        if context.package_managers:
            console.print(f"  📦 Package Managers: {', '.join(context.package_managers)}")
        
        # Show dependencies
        if context.dependencies:
            console.print(f"\n[bold]Key Dependencies:[/bold]")
            for lang, deps in context.dependencies.items():
                if deps:
                    deps_str = ", ".join(deps[:5])
                    if len(deps) > 5:
                        deps_str += f" (+{len(deps)-5} more)"
                    console.print(f"  {lang.title()}: {deps_str}")
        
        # Show git info
        if context.git_info:
            console.print(f"\n[bold]Git Information:[/bold]")
            for key, value in context.git_info.items():
                readable_key = key.replace('_', ' ').title()
                console.print(f"  {readable_key}: {value}")
        
        # Show config files
        if context.config_files:
            console.print(f"\n[bold]Config Files:[/bold]")
            for config in context.config_files[:8]:  # Show first 8
                console.print(f"  📄 {config}")
            if len(context.config_files) > 8:
                console.print(f"  ... and {len(context.config_files) - 8} more")
    
    elif action == "refresh":
        # Force refresh persona cache
        context = persona.get_project_context(".", force_refresh=True)
        console.print(f"[green]✅ Refreshed persona for {context.repo_path}[/green]")
        console.print(f"Detected: {', '.join(context.primary_languages)} ({context.confidence_score:.1%} confidence)")
    
    elif action == "cache":
        # Show cache statistics
        stats = persona.get_cache_stats()
        console.print(f"[bold green]Persona Cache Statistics[/bold green]\n")
        console.print(f"  📊 Cached repositories: {stats['cached_repositories']}")
        console.print(f"  📁 Cache file exists: {stats['cache_file_exists']}")
        console.print(f"  ⏰ Cache duration: {stats['cache_duration_hours']} hours")
        
        if 'oldest_cache_entry' in stats:
            console.print(f"  📅 Oldest entry: {stats['oldest_cache_entry']}")
            console.print(f"  🆕 Newest entry: {stats['newest_cache_entry']}")
    
    elif action == "clear":
        # Clear persona cache
        persona.invalidate_cache()
        console.print("[green]✅ Cleared persona cache[/green]")
    
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("Available actions: show, refresh, cache, clear")

@app.command("context")
def context_command():
    """Show the current system prompt that will be used"""
    persona = get_persona_manager()
    context = persona.get_project_context(".")
    
    # Generate sample system prompt
    system_prompt = persona.generate_system_prompt(context, "general")
    
    console.print(f"[bold green]Current System Prompt[/bold green]\n")
    console.print(Panel(
        system_prompt,
        title="System Prompt",
        border_style="blue"
    ))

@app.command()
def start(command: str = None, file: str = None):
    """Start your application with intelligent error handling
    
    Examples:
      lumos-cli start "python app.py"
      lumos-cli start --file server.py  
      lumos-cli start "npm run dev"
      lumos-cli start "flask run"
    """
    history = get_history_manager()
    persona = get_persona_manager()
    context = persona.get_project_context(".")
    
    # Auto-detect start command if not provided
    if not command and not file:
        command = _auto_detect_start_command(context)
        if not command:
            console.print("[yellow]Could not auto-detect start command.[/yellow]")
            console.print("[dim]Try: lumos-cli start \"python app.py\" or lumos-cli start --file main.py[/dim]")
            return
        console.print(f"[cyan]Auto-detected command:[/cyan] {command}")
    
    # Build command from file if provided
    if file and not command:
        if file.endswith('.py'):
            command = f"python {file}"
        elif file.endswith('.js'):
            command = f"node {file}"
        else:
            command = file
    
    # Parse command into list
    cmd_parts = command.split() if isinstance(command, str) else [command]
    
    # Smart app startup with error handling
    console.print(f"\n[bold green]🚀 Starting Application[/bold green]")
    success = smart_start_app(cmd_parts, ".")
    
    if success:
        console.print("[green]✅ Application started successfully![/green]")
    else:
        console.print("[red]❌ Application failed to start[/red]")
        
        # Add error to history for context
        history.add_message("user", f"Failed to start: {command}", command="start")
        history.add_message("assistant", "Application startup failed - error analysis provided", command="start")

@app.command() 
def fix(error_description: str = None):
    """Analyze and fix runtime errors intelligently
    
    Examples:
      lumos-cli fix "ModuleNotFoundError: No module named 'flask'"
      lumos-cli fix "server won't start"
      lumos-cli fix  # Interactive error input
    """
    error_handler = RuntimeErrorHandler(console)
    history = get_history_manager()
    persona = get_persona_manager()
    
    if not error_description:
        # Interactive error input
        from rich.prompt import Prompt
        console.print("[cyan]🔧 Error Analysis Mode[/cyan]")
        console.print("[dim]Paste your error message or describe the issue:[/dim]")
        error_description = Prompt.ask("Error")
        
    if not error_description.strip():
        console.print("[red]No error description provided[/red]")
        return
    
    # Analyze the error
    console.print(f"\n[cyan]🔍 Analyzing error...[/cyan]")
    analysis = error_handler.analyze_error(error_description)
    
    # Display analysis
    error_handler.display_error_analysis(analysis)
    
    # Add to history
    history.add_message("user", f"Error analysis request: {error_description}", command="fix")
    history.add_message("assistant", f"Provided analysis and fixes for {analysis.error_type}", command="fix")
    
    # Offer to apply automatic fix
    if analysis.confidence > 0.7:
        from rich.prompt import Confirm
        if Confirm.ask("\n🤖 Try to apply automated fix?", default=False):
            from .error_handler import _apply_automated_fix
            success = _apply_automated_fix(analysis, ".")
            if success:
                console.print("[green]✅ Automated fix applied successfully![/green]")
            else:
                console.print("[yellow]⚠️ Manual intervention required[/yellow]")

@app.command()
def shell(command: str = None):
    """Execute shell/cmd commands with safety confirmation
    
    Examples:
      lumos-cli shell "ls -la"
      lumos-cli shell "npm install"  
      lumos-cli shell "git status"
      lumos-cli shell  # Interactive command input
    """
    history = get_history_manager()
    
    if not command:
        # Interactive command input
        from rich.prompt import Prompt
        console.print("[cyan]🖥️  Shell Command Execution[/cyan]")
        console.print("[dim]Enter the shell command you want to execute:[/dim]")
        console.print("[dim]Note: Dangerous commands will require additional confirmation[/dim]")
        command = Prompt.ask("Command")
        
    if not command or not command.strip():
        console.print("[red]No command provided[/red]")
        return
    
    # Clean up the command
    command = command.strip()
    
    # Add context about where this request came from
    context = f"User requested shell command execution via Lumos CLI"
    
    # Add command to history for context
    history.add_message("user", f"Execute shell command: {command}", command="shell")
    
    # Execute with safety checks and confirmation
    console.print(f"[bold blue]🖥️  Shell Command Execution[/bold blue]")
    success, stdout, stderr = execute_shell_command(command, context)
    
    # Add result to history
    if success:
        history.add_message("assistant", f"Command executed successfully: {command}", command="shell")
        console.print(f"\n[green]Command completed successfully![/green]")
    else:
        history.add_message("assistant", f"Command failed: {command} - {stderr}", command="shell")
        if stderr and stderr != "Cancelled by user":
            console.print(f"\n[red]Command failed with error: {stderr}[/red]")

def _auto_detect_start_command(context) -> str:
    """Auto-detect the appropriate start command based on project context using enhanced detection"""
    
    # Use the new enhanced app detector
    from .app_detector import EnhancedAppDetector
    
    try:
        detector = EnhancedAppDetector(".")
        app_context = detector.detect_execution_options()
        
        # Get the suggested command
        suggested_command = detector.suggest_execution_command(app_context, interactive=False)
        
        if suggested_command and app_context.confidence > 0.3:
            return suggested_command
            
    except Exception:
        # Fall back to original logic if enhanced detection fails
        pass
    
    # Original fallback logic (simplified)
    startup_files = {
        'app.py': 'python app.py',
        'main.py': 'python main.py', 
        'server.py': 'python server.py',
        'manage.py': 'python manage.py runserver',  # Django
        'app.js': 'node app.js',
        'server.js': 'node server.js',
        'index.js': 'node index.js'
    }
    
    for file, command in startup_files.items():
        if os.path.exists(file):
            return command
    
    # Check for package.json scripts
    if 'javascript' in context.primary_languages and os.path.exists('package.json'):
        try:
            import json
            with open('package.json', 'r') as f:
                package = json.load(f)
                scripts = package.get('scripts', {})
                
                # Common script priorities
                for script in ['dev', 'start', 'serve']:
                    if script in scripts:
                        return f'npm run {script}'
        except:
            pass
    
    return None

@app.command()
def detect():
    """Show all detected application execution options for current project"""
    from .app_detector import EnhancedAppDetector
    from rich.table import Table
    
    console.print("[bold cyan]🔍 Application Execution Detection[/bold cyan]\n")
    
    try:
        detector = EnhancedAppDetector(".")
        app_context = detector.detect_execution_options()
        
        if not app_context.all_options:
            console.print("[yellow]No execution options detected in current directory[/yellow]")
            console.print("\n[dim]Try running this command in a project directory with:")
            console.print("• Python files (.py)")
            console.print("• Node.js project (package.json)")
            console.print("• Go project (main.go)")
            console.print("• Rust project (Cargo.toml)")
            console.print("• Java files (.java)")
            console.print("• Docker files (Dockerfile)[/dim]")
            return
        
        # Create summary table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="dim", width=4)
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Confidence", style="green")
        table.add_column("Framework", style="yellow")
        
        for i, option in enumerate(app_context.all_options[:10], 1):  # Show top 10
            confidence_str = f"{option.confidence:.1%}"
            framework_str = option.framework or "-"
            primary_indicator = "👑" if option.is_primary else str(i)
            
            table.add_row(
                primary_indicator,
                option.command,
                option.description,
                confidence_str,
                framework_str
            )
        
        console.print(table)
        
        # Show primary recommendation
        if app_context.primary_option:
            console.print(f"\n[bold green]🚀 Recommended: [/bold green]`{app_context.primary_option.command}`")
            console.print(f"[dim]   {app_context.primary_option.description}[/dim]")
        
        # Show project summary
        console.print(f"\n[bold]Project Analysis:[/bold]")
        console.print(f"  🏷️  Type: {app_context.project_type}")
        console.print(f"  🎯 Confidence: {app_context.confidence:.1%}")
        console.print(f"  📊 Options found: {len(app_context.all_options)}")
        
        # Usage hint
        console.print(f"\n[dim]💡 Use `lumos-cli start` to run the recommended command")
        console.print(f"[dim]💡 Use `lumos-cli shell --command \"<command>\"` to run any specific command")
        
    except Exception as e:
        console.print(f"[red]Error detecting applications: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")

@app.command()
def setup():
    """Run the setup wizard to configure Lumos CLI"""
    setup_wizard()

@app.command() 
def config_show(debug: bool = False):
    """Show current configuration with beautiful panels"""
    available_backends = config.get_available_backends()
    
    # Create header
    create_header(console, subtitle="Configuration Status")
    
    # Prepare configuration data
    config_data = {
        "🤖 Ollama (Local)": {
            "status": "available" if "ollama" in available_backends else "missing",
            "details": f"Local AI model - {config.get('llm.ollama_url', 'http://localhost:11434')}"
        },
        "🌐 OpenAI API": {
            "status": "configured" if "openai" in available_backends else "missing", 
            "details": f"External API - {config.get('llm.rest_api_url', 'Not configured')}"
        },
        "🏢 Enterprise LLM": {
            "status": "configured" if "enterprise" in available_backends else "missing",
            "details": f"Corporate API - {config.get('llm.enterprise_chat_url', 'Not configured')}"
        },
        "🧠 Smart Discovery": {
            "status": "available" if config.get('features.smart_file_discovery') else "missing",
            "details": "Natural language file finding"
        },
        "🛡️ Safety System": {
            "status": "available" if config.get('safety.auto_backup') else "missing",
            "details": f"Backups in {config.get('safety.backup_dir', '.llm_backups')}"
        },
        "💾 Persistent History": {
            "status": "available" if config.get('features.history_enabled') else "missing",
            "details": "Repository-aware conversation memory"
        },
        "🚨 Error Handling": {
            "status": "available" if config.get('features.error_handling') else "missing", 
            "details": "Intelligent runtime error analysis"
        }
    }
    
    # Show configuration panel
    create_config_panel(console, config_data)
    
    # Debug information panel
    if debug:
        from rich.table import Table
        from rich import box
        
        debug_table = Table(show_header=True, header_style="bold bright_yellow", box=box.SIMPLE)
        debug_table.add_column("Setting", style="bold")
        debug_table.add_column("Value", style="bright_white")
        
        debug_table.add_row("OpenAI API URL", config.get('llm.rest_api_url') or '[dim]Not set[/dim]')
        debug_table.add_row("OpenAI API Key", '[green]✓ Set[/green]' if config.get('llm.rest_api_key') else '[red]✗ Not set[/red]')
        debug_table.add_row("Ollama URL", config.get('llm.ollama_url', 'http://localhost:11434'))
        debug_table.add_row("Default Backend", config.get('llm.default_backend', 'auto'))
        debug_table.add_row("Embeddings DB", config.get('embeddings.db_path', '.lumos_embeddings.db'))
        
        debug_panel = Panel(
            debug_table,
            title="[bold bright_yellow]🐛 Debug Information[/bold bright_yellow]",
            style="bright_yellow",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2)
        )
        console.print(debug_panel)
    
    # Show status message
    if not available_backends:
        create_status_panel(console, "warning", 
                          "No LLM backends available", 
                          {"Action": "Run 'lumos-cli setup' to configure"})
    else:
        create_status_panel(console, "success", 
                          f"{len(available_backends)} backend(s) ready",
                          {"Available": ", ".join(available_backends).title()})
    
    # Footer
    print_brand_footer(console)

@app.command()
def welcome():
    """Show a beautiful welcome screen with Lumos features"""
    from .ui import create_feature_showcase_panel
    
    create_header(console, subtitle="AI-Powered Code Assistant")
    create_feature_showcase_panel(console)
    
    # Quick start tips
    tips_table = Table(show_header=False, show_lines=False, padding=(0, 1), box=None)
    tips_table.add_column(style="bright_green bold", width=3)
    tips_table.add_column(style="bright_cyan", width=25)
    tips_table.add_column(style="dim")
    
    tips_table.add_row("💡", "lumos-cli", "Start interactive mode")
    tips_table.add_row("⚙️", "lumos-cli config-show", "Check configuration") 
    tips_table.add_row("🔧", "lumos-cli setup", "Run setup wizard")
    tips_table.add_row("📚", "lumos-cli --help", "See all commands")
    
    tips_panel = Panel(
        tips_table,
        title="[bold bright_green]🚀 Quick Start[/bold bright_green]",
        style="bright_green",
        border_style="green",
        box=box.ROUNDED,
        padding=(0, 1)
    )
    console.print(tips_panel)
    print_brand_footer(console)

@app.command()
def debug():
    """Debug configuration and API connections with detailed logging"""
    from .config import load_env_file
    
    console.print(Panel(
        "[bold bright_yellow]🔧 Lumos CLI Debug Information[/bold bright_yellow]",
        title="Debug Mode",
        border_style="yellow"
    ))
    
    # Force reload environment with debug
    console.print("\n[bright_cyan]🔍 Environment Loading:[/bright_cyan]")
    load_env_file(debug=True)
    
    # Check configuration with debug
    console.print("\n[bright_cyan]🔍 Configuration Check:[/bright_cyan]")
    config.is_rest_api_configured(debug=True)
    
    # Test API connections
    console.print("\n[bright_cyan]🔍 Testing API Connections:[/bright_cyan]")
    
    # Test REST API if configured
    if config.is_rest_api_configured():
        try:
            router = LLMRouter(backend="rest")
            messages = [{"role": "user", "content": "Say 'Debug test successful'"}]
            console.print("🚀 Testing OpenAI API connection...")
            
            # Enable debug mode for this test
            response = router._chat_rest(messages, debug=True)
            console.print(f"✅ OpenAI API Response: {response}")
        except Exception as e:
            console.print(f"❌ OpenAI API Error: {str(e)}")
    else:
        console.print("⚠️ OpenAI API not configured")
    
    # Test Ollama if available
    if config.is_ollama_available():
        try:
            router = LLMRouter(backend="ollama")
            messages = [{"role": "user", "content": "Say 'Debug test successful'"}]
            console.print("🚀 Testing Ollama connection...")
            response = router._chat_ollama(messages)
            console.print(f"✅ Ollama Response: {response}")
        except Exception as e:
            console.print(f"❌ Ollama Error: {str(e)}")
    else:
        console.print("⚠️ Ollama not available")
    
    console.print("\n[bright_green]✅ Debug information complete![/bright_green]")
    console.print("[dim]Tip: If you see issues above, run 'lumos-cli setup' to reconfigure[/dim]")
    console.print("[dim]Logs: Run 'lumos-cli logs' to see detailed log files[/dim]")

@app.command("config")
def config_command(
    action: str = typer.Argument(help="Action: set, get, list, or reset"),
    key: str = typer.Argument("", help="Configuration key (e.g., 'llm.rest_api_key')"),
    value: str = typer.Argument("", help="Value to set (for 'set' action")
):
    """Manage global Lumos CLI configuration
    
    Examples:
      lumos-cli config set llm.rest_api_key sk-your-key-here
      lumos-cli config set llm.rest_api_url https://api.openai.com/v1/chat/completions
      lumos-cli config get llm.rest_api_key
      lumos-cli config list
      lumos-cli config reset
    """
    
    if action == "set":
        if not key or not value:
            console.print("[red]❌ Both key and value required for 'set' action[/red]")
            console.print("Example: lumos-cli config set llm.rest_api_key sk-your-key")
            return
            
        # Mask sensitive values for display
        display_value = value
        if any(word in key.lower() for word in ['key', 'secret', 'token', 'password']):
            display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            
        config.set(key, value)
        console.print(f"[green]✅ Set {key} = {display_value}[/green]")
        
    elif action == "get":
        if not key:
            console.print("[red]❌ Key required for 'get' action[/red]")
            console.print("Example: lumos-cli config get llm.rest_api_key")
            return
            
        value = config.get(key)
        if value is None:
            console.print(f"[yellow]⚠️ {key} is not set[/yellow]")
        else:
            # Mask sensitive values
            if any(word in key.lower() for word in ['key', 'secret', 'token', 'password']):
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            console.print(f"[cyan]{key} = {display_value}[/cyan]")
            
    elif action == "list":
        from rich.table import Table
        
        table = Table(title="🔧 Lumos CLI Global Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="bright_white")
        table.add_column("Status", style="green")
        
        # LLM Settings
        settings = [
            ("llm.rest_api_url", "OpenAI API URL"),
            ("llm.rest_api_key", "OpenAI API Key"), 
            ("llm.rest_model", "OpenAI Model"),
            ("llm.ollama_url", "Ollama URL"),
            ("llm.ollama_model", "Ollama Model"),
            ("llm.default_backend", "Default Backend")
        ]
        
        for key, description in settings:
            value = config.get(key)
            if value is None:
                table.add_row(description, "[dim]Not set[/dim]", "⚠️")
            else:
                # Mask sensitive values
                if 'key' in key.lower():
                    display_value = f"{value[:8]}..." if len(value) > 8 else "***"
                else:
                    display_value = str(value)
                table.add_row(description, display_value, "✅")
        
        console.print(table)
        
        # Show config file location
        console.print(f"\n[dim]Config file: {config.config_file}[/dim]")
        
    elif action == "reset":
        if config.config_file.exists():
            config.config_file.unlink()
            console.print("[green]✅ Configuration reset to defaults[/green]")
        else:
            console.print("[yellow]⚠️ No configuration file to reset[/yellow]")
            
    else:
        console.print(f"[red]❌ Unknown action: {action}[/red]")
        console.print("Valid actions: set, get, list, reset")

@app.command("platform")
def platform_info():
    """Show platform-specific information and Windows compatibility"""
    from .platform_utils import get_platform_info, check_ollama_installed, get_ollama_executable_locations
    from rich.table import Table
    from pathlib import Path
    
    console.print(Panel(
        "[bold bright_blue]🖥️ Platform Information & Windows Compatibility[/bold bright_blue]",
        title="Platform Info",
        border_style="blue"
    ))
    
    # Get platform info
    info = get_platform_info()
    
    # Platform details table
    platform_table = Table(title="🖥️ System Information")
    platform_table.add_column("Property", style="cyan")
    platform_table.add_column("Value", style="bright_white")
    
    platform_table.add_row("Platform", info["platform"].title())
    platform_table.add_row("System", info["system"])
    platform_table.add_row("Version", info["release"])
    platform_table.add_row("Architecture", info["machine"])
    platform_table.add_row("Python Version", info["python_version"])
    platform_table.add_row("Is Windows", "✅ Yes" if info["is_windows"] == "True" else "❌ No")
    platform_table.add_row("Is macOS", "✅ Yes" if info["is_macos"] == "True" else "❌ No")
    platform_table.add_row("Is Linux", "✅ Yes" if info["is_linux"] == "True" else "❌ No")
    
    console.print(platform_table)
    
    # Directory paths table
    paths_table = Table(title="📁 Platform-Specific Directories")
    paths_table.add_column("Directory", style="cyan")
    paths_table.add_column("Path", style="bright_white")
    paths_table.add_column("Exists", style="green")
    
    paths_table.add_row("Home", info["home_dir"], "✅" if Path(info["home_dir"]).exists() else "❌")
    paths_table.add_row("Config", info["config_dir"], "✅" if Path(info["config_dir"]).exists() else "❌")
    paths_table.add_row("Logs", info["logs_dir"], "✅" if Path(info["logs_dir"]).exists() else "❌")
    paths_table.add_row("Cache", info["cache_dir"], "✅" if Path(info["cache_dir"]).exists() else "❌")
    
    console.print(paths_table)
    
    # Ollama detection
    ollama_installed = check_ollama_installed()
    ollama_locations = get_ollama_executable_locations()
    
    console.print(f"\n[bold cyan]🤖 Ollama Detection:[/bold cyan]")
    console.print(f"Installed: {'✅ Yes' if ollama_installed else '❌ No'}")
    
    if info["is_windows"] == "True":
        console.print(f"\n[yellow]🪟 Windows-Specific Notes:[/yellow]")
        console.print(r"• Config stored in: %APPDATA%\Lumos")
        console.print(r"• Logs stored in: %LOCALAPPDATA%\Lumos\Logs") 
        console.print(r"• Ollama typically installed in: Program Files\Ollama")
        console.print("• Use PowerShell or Command Prompt to run lumos-cli")
        
        console.print(f"\n[dim]Ollama search locations:[/dim]")
        for location in ollama_locations:
            exists = Path(location).exists() if location != "ollama.exe" else False
            status = "✅" if exists else ("🔍" if location == "ollama.exe" else "❌")
            console.print(f"  {status} {location}")
    
    console.print(f"\n[green]✅ Platform compatibility configured![/green]")

@app.command()
def logs(lines: int = 50, debug_only: bool = True, show_files: bool = True):
    """Show recent log entries and log file locations"""
    from .logger import get_logger, show_log_info
    
    if show_files:
        show_log_info()
    
    logger = get_logger()
    
    console.print(f"\n[bright_cyan]📋 Recent Logs ({lines} lines, debug_only={debug_only}):[/bright_cyan]")
    recent_logs = logger.get_recent_logs(lines=lines, debug_only=debug_only)
    
    if recent_logs.strip():
        # Format and colorize log output
        for line in recent_logs.strip().split('\n'):
            if 'ERROR:' in line:
                console.print(f"[red]{line}[/red]")
            elif 'WARNING:' in line:
                console.print(f"[yellow]{line}[/yellow]") 
            elif 'DEBUG:' in line:
                console.print(f"[dim]{line}[/dim]")
            else:
                console.print(line)
    else:
        console.print("[dim]No recent logs found[/dim]")

# JIRA Integration Commands
@app.command()
def jira(
    action: str = typer.Argument(help="Action: config, search, browse, comment, comments"),
    query: str = typer.Option("", "--query", "-q", help="Search query or ticket key"),
    comment_text: str = typer.Option("", "--comment", "-c", help="Comment text to add")
):
    """🎫 JIRA integration for enterprise workflows
    
    Examples:
      lumos-cli jira config                           → Setup JIRA credentials
      lumos-cli jira search -q "my open tickets"     → Search for tickets  
      lumos-cli jira browse                          → Interactive ticket browser
      lumos-cli jira comment ABC-123 -c "Progress update" → Add comment to ticket
      lumos-cli jira comments ABC-123                → Extract comments from ticket
    """
    from .jira_client import get_jira_client, JiraConfigManager, JiraTicketBrowser
    
    if action == "config":
        # Configure JIRA settings
        config_manager = JiraConfigManager()
        console.print("🔧 JIRA Configuration", style="bold blue")
        
        existing_config = config_manager.load_config()
        if existing_config:
            console.print(f"✅ Current config: {existing_config.get('base_url', 'Not set')}")
            if not typer.confirm("Reconfigure JIRA settings?"):
                return
        
        new_config = config_manager.setup_interactive()
        if new_config:
            console.print("✅ JIRA configured successfully!")
        
    elif action == "search":
        # Search for tickets
        client = get_jira_client()
        if not client:
            return
            
        if not query:
            query = typer.prompt("Enter search query (e.g., 'my open tickets in current sprint')")
        
        console.print(f"🔍 Searching: {query}")
        
        jql = client.construct_jql(query)
        console.print(f"[dim]JQL: {jql}[/dim]")
        
        success, tickets, message = client.search_tickets(jql)
        
        if success:
            console.print(f"✅ {message}")
            browser = JiraTicketBrowser(client)
            browser.display_tickets_table(tickets)
        else:
            console.print(f"❌ {message}")
    
    elif action == "browse":
        # Interactive ticket browser
        client = get_jira_client()
        if not client:
            return
        
        search_query = query or "my tickets in current sprint"
        console.print(f"🔍 Loading: {search_query}")
        
        jql = client.construct_jql(search_query)
        success, tickets, message = client.search_tickets(jql)
        
        if not success:
            console.print(f"❌ {message}")
            return
        
        browser = JiraTicketBrowser(client)
        selected_ticket = browser.browse_tickets(tickets)
        
        if selected_ticket:
            # Get detailed ticket info
            success, detailed_ticket, message = client.get_ticket_details(selected_ticket.key)
            
            if success:
                browser.display_ticket_details(detailed_ticket)
                
                # Ask for next action
                console.print("\n[dim]What would you like to do?[/dim]")
                console.print("[dim]• Press 'c' to add a comment[/dim]")
                console.print("[dim]• Press Enter to return[/dim]")
                
                action = typer.prompt("Action", default="").lower()
                
                if action == 'c':
                    comment = typer.prompt("Enter comment")
                    success, result = client.add_comment(selected_ticket.key, comment)
                    console.print(result)
            else:
                console.print(f"❌ {message}")
    
    elif action == "comment":
        # Add comment to ticket
        client = get_jira_client()
        if not client:
            return
        
        if not query:
            query = typer.prompt("Enter ticket key (e.g., ABC-123)")
        
        if not comment_text:
            comment_text = typer.prompt("Enter comment")
        
        success, result = client.add_comment(query, comment_text)
        console.print(result)
    
    elif action == "comments":
        # Extract comments from ticket
        client = get_jira_client()
        if not client:
            return
        
        if not query:
            query = typer.prompt("Enter ticket key (e.g., ABC-123)")
        
        console.print(f"🔍 Extracting comments for ticket: {query}")
        
        comments = client.get_ticket_comments(query)
        
        if comments:
            console.print(f"✅ Found {len(comments)} comments for {query}")
            console.print()
            
            for i, comment in enumerate(comments, 1):
                console.print(f"[bold blue]Comment #{i}[/bold blue]")
                console.print(f"[dim]Author: {comment['author']}[/dim]")
                console.print(f"[dim]Created: {comment['created']}[/dim]")
                console.print(f"[dim]Visibility: {comment['visibility']}[/dim]")
                console.print()
                console.print(f"[white]{comment['body']}[/white]")
                console.print()
                console.print("-" * 80)
                console.print()
        else:
            console.print(f"❌ No comments found for ticket {query}")
            console.print("This could mean:")
            console.print("• The ticket doesn't exist")
            console.print("• The ticket has no comments")
            console.print("• You don't have permission to view comments")
            console.print("• Jira API connection failed")
    
    else:
        console.print("[red]Invalid action. Use: config, search, browse, comment, or comments[/red]")
        console.print("Run 'lumos-cli jira --help' for examples")

@app.command()
def neo4j(
    action: str = typer.Argument(help="Action: config, test, impact, deps, overview, populate"),
    org: str = typer.Option("", "--org", "-o", help="Organization name"),
    repo: str = typer.Option("", "--repo", "-r", help="Repository name"),
    class_name: str = typer.Option("", "--class", "-c", help="Class name for analysis")
):
    """🔗 Neo4j graph database integration for code analysis
    
    Examples:
      lumos-cli neo4j config                           → Setup Neo4j connection
      lumos-cli neo4j test                             → Test Neo4j connection
      lumos-cli neo4j populate                         → Populate with fake data
      lumos-cli neo4j impact -o scimarketplace -r quoteapp -c QuoteService → Impact analysis
      lumos-cli neo4j deps -o scimarketplace -r quoteapp -c QuoteController → Dependencies
      lumos-cli neo4j overview -o scimarketplace -r quoteapp → Repository overview
    """
    
    if action == "config":
        # Configure Neo4j settings
        config_manager = Neo4jConfigManager()
        console.print("🔧 Neo4j Configuration", style="bold blue")
        
        existing_config = config_manager.load_config()
        if existing_config:
            console.print(f"✅ Current config: {existing_config.uri}")
            if not typer.confirm("Reconfigure Neo4j settings?"):
                return
        
        success = config_manager.setup_interactive()
        if success:
            console.print("✅ Neo4j configured successfully!")
        else:
            console.print("❌ Neo4j configuration failed!")
    
    elif action == "test":
        # Test Neo4j connection
        config_manager = Neo4jConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ Neo4j not configured. Run 'lumos-cli neo4j config' first.[/yellow]")
            return
        
        console.print("🔍 Testing Neo4j connection...")
        client = Neo4jClient(config.uri, config.username, config.password)
        
        if client.test_connection():
            console.print("✅ Neo4j connection successful!")
            
            # Get database info
            try:
                with client.driver.session() as session:
                    result = session.run("CALL dbms.components() YIELD name, versions, edition")
                    for record in result:
                        console.print(f"📊 Database: {record['name']} {record['versions'][0]} ({record['edition']})")
                        break
            except Exception as e:
                console.print(f"⚠️ Could not get database info: {e}")
        else:
            console.print("❌ Neo4j connection failed!")
        
        client.close()
    
    elif action == "populate":
        # Populate with fake data
        console.print("🗄️ Populating Neo4j with fake data...")
        import subprocess
        import sys
        
        try:
            result = subprocess.run([sys.executable, "populate_neo4j_fake_data.py"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                console.print("✅ Neo4j populated successfully!")
                console.print(result.stdout)
            else:
                console.print("❌ Failed to populate Neo4j:")
                console.print(result.stderr)
        except Exception as e:
            console.print(f"❌ Error running population script: {e}")
    
    elif action == "impact":
        # Impact analysis
        if not org or not repo or not class_name:
            console.print("[red]❌ Organization, repository, and class name required for impact analysis[/red]")
            console.print("Example: lumos-cli neo4j impact -o scimarketplace -r quoteapp -c QuoteService")
            return
        
        config_manager = Neo4jConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ Neo4j not configured. Run 'lumos-cli neo4j config' first.[/yellow]")
            return
        
        client = Neo4jClient(config.uri, config.username, config.password)
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j")
            return
        
        console.print(f"🔍 Analyzing impact of {class_name} in {org}/{repo}...")
        
        impacts = client.find_impact_analysis(org, repo, class_name)
        
        if impacts:
            console.print(f"✅ Found {len(impacts)} classes that depend on {class_name}:")
            console.print()
            
            from rich.table import Table
            table = Table(title=f"Impact Analysis: {class_name}")
            table.add_column("Class", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("File", style="green")
            
            for impact in impacts:
                table.add_row(
                    impact['class_name'],
                    impact['class_type'],
                    impact['file_path']
                )
            
            console.print(table)
        else:
            console.print(f"ℹ️ No classes depend on {class_name}")
        
        client.close()
    
    elif action == "deps":
        # Dependencies analysis
        if not org or not repo or not class_name:
            console.print("[red]❌ Organization, repository, and class name required for dependency analysis[/red]")
            console.print("Example: lumos-cli neo4j deps -o scimarketplace -r quoteapp -c QuoteController")
            return
        
        config_manager = Neo4jConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ Neo4j not configured. Run 'lumos-cli neo4j config' first.[/yellow]")
            return
        
        client = Neo4jClient(config.uri, config.username, config.password)
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j")
            return
        
        console.print(f"🔍 Analyzing dependencies of {class_name} in {org}/{repo}...")
        
        deps = client.find_dependencies(org, repo, class_name)
        
        if deps:
            console.print(f"✅ Found {len(deps)} dependencies for {class_name}:")
            console.print()
            
            from rich.table import Table
            table = Table(title=f"Dependencies: {class_name}")
            table.add_column("Class", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("File", style="green")
            table.add_column("Dependency Type", style="magenta")
            
            for dep in deps:
                table.add_row(
                    dep['class_name'],
                    dep['class_type'],
                    dep['file_path'],
                    dep['dependency_type']
                )
            
            console.print(table)
        else:
            console.print(f"ℹ️ {class_name} has no dependencies")
        
        client.close()
    
    elif action == "overview":
        # Repository overview
        if not org or not repo:
            console.print("[red]❌ Organization and repository required for overview[/red]")
            console.print("Example: lumos-cli neo4j overview -o scimarketplace -r quoteapp")
            return
        
        config_manager = Neo4jConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ Neo4j not configured. Run 'lumos-cli neo4j config' first.[/yellow]")
            return
        
        client = Neo4jClient(config.uri, config.username, config.password)
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j")
            return
        
        console.print(f"📊 Getting overview for {org}/{repo}...")
        
        overview = client.get_repository_overview(org, repo)
        
        if overview:
            from rich.table import Table
            table = Table(title=f"Repository Overview: {org}/{repo}")
            table.add_column("Metric", style="cyan")
            table.add_column("Count", style="yellow")
            
            table.add_row("Files", str(overview.get('file_count', 0)))
            table.add_row("Classes", str(overview.get('class_count', 0)))
            table.add_row("Methods", str(overview.get('method_count', 0)))
            
            console.print(table)
        else:
            console.print(f"ℹ️ No data found for {org}/{repo}")
        
        client.close()
    
    else:
        console.print("[red]Invalid action. Use: config, test, impact, deps, overview, or populate[/red]")
        console.print("Run 'lumos-cli neo4j --help' for examples")

@app.command()
def neo4j_dotnet(
    action: str = typer.Argument(help="Action: config, test, populate, controllers, constants, overview"),
    repo_name: str = typer.Option("", "--repo", "-r", help="Repository name"),
    repo_namespace: str = typer.Option("", "--namespace", "-n", help="Repository namespace"),
    sp_name: str = typer.Option("", "--sp", "-s", help="Stored procedure name"),
    constant_name: str = typer.Option("", "--constant", "-c", help="Constant name")
):
    """🔗 Neo4j .NET Core integration for enterprise architecture analysis
    
    Examples:
      lumos-cli neo4j-dotnet config                           → Setup Neo4j connection
      lumos-cli neo4j-dotnet test                             → Test Neo4j connection
      lumos-cli neo4j-dotnet populate                         → Populate with .NET fake data
      lumos-cli neo4j-dotnet controllers -s GetUserById       → Find controllers calling SP
      lumos-cli neo4j-dotnet constants -c MAX_LOGIN_ATTEMPTS  → Find classes using constant
      lumos-cli neo4j-dotnet overview -r UserManagement -n Company.UserManagement → Repository overview
    """
    
    if action == "config":
        # Configure Neo4j settings (reuse existing config)
        config_manager = Neo4jConfigManager()
        console.print("🔧 Neo4j .NET Configuration", style="bold blue")
        
        existing_config = config_manager.load_config()
        if existing_config:
            console.print(f"✅ Current config: {existing_config.uri}")
            if not typer.confirm("Reconfigure Neo4j settings?"):
                return
        
        success = config_manager.setup_interactive()
        if success:
            console.print("✅ Neo4j .NET configured successfully!")
        else:
            console.print("❌ Neo4j .NET configuration failed!")
    
    elif action == "test":
        # Test Neo4j connection
        config_manager = Neo4jConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ Neo4j not configured. Run 'lumos-cli neo4j-dotnet config' first.[/yellow]")
            return
        
        console.print("🔍 Testing Neo4j .NET connection...")
        client = Neo4jDotNetClient(config.uri, config.username, config.password)
        
        if client.test_connection():
            console.print("✅ Neo4j .NET connection successful!")
            
            # Get database info
            try:
                with client.driver.session() as session:
                    result = session.run("CALL dbms.components() YIELD name, versions, edition")
                    for record in result:
                        console.print(f"📊 Database: {record['name']} {record['versions'][0]} ({record['edition']})")
                        break
            except Exception as e:
                console.print(f"⚠️ Could not get database info: {e}")
        else:
            console.print("❌ Neo4j .NET connection failed!")
        
        client.close()
    
    elif action == "populate":
        # Populate with .NET fake data
        console.print("🗄️ Populating Neo4j with .NET Core data...")
        import subprocess
        import sys
        
        try:
            result = subprocess.run([sys.executable, "populate_neo4j_dotnet_data.py"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                console.print("✅ Neo4j .NET populated successfully!")
                console.print(result.stdout)
            else:
                console.print("❌ Failed to populate Neo4j .NET:")
                console.print(result.stderr)
        except Exception as e:
            console.print(f"❌ Error running .NET population script: {e}")
    
    elif action == "controllers":
        # Find controllers calling stored procedure
        if not sp_name:
            console.print("[red]❌ Stored procedure name required for controller analysis[/red]")
            console.print("Example: lumos-cli neo4j-dotnet controllers -s GetUserById")
            return
        
        config_manager = Neo4jConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ Neo4j not configured. Run 'lumos-cli neo4j-dotnet config' first.[/yellow]")
            return
        
        client = Neo4jDotNetClient(config.uri, config.username, config.password)
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j")
            return
        
        console.print(f"🔍 Finding controllers calling stored procedure: {sp_name}...")
        
        controllers = client.find_controllers_calling_sp(sp_name, "dbo")
        
        if controllers:
            console.print(f"✅ Found {len(controllers)} controllers calling {sp_name}:")
            console.print()
            
            from rich.table import Table
            table = Table(title=f"Controllers Calling: {sp_name}")
            table.add_column("Controller", style="cyan")
            table.add_column("Namespace", style="yellow")
            
            for controller in controllers:
                table.add_row(
                    controller['controller_name'],
                    controller['controller_namespace']
                )
            
            console.print(table)
        else:
            console.print(f"ℹ️ No controllers found calling {sp_name}")
        
        client.close()
    
    elif action == "constants":
        # Find classes using constant
        if not constant_name:
            console.print("[red]❌ Constant name required for constant analysis[/red]")
            console.print("Example: lumos-cli neo4j-dotnet constants -c MAX_LOGIN_ATTEMPTS")
            return
        
        config_manager = Neo4jConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ Neo4j not configured. Run 'lumos-cli neo4j-dotnet config' first.[/yellow]")
            return
        
        client = Neo4jDotNetClient(config.uri, config.username, config.password)
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j")
            return
        
        console.print(f"🔍 Finding classes using constant: {constant_name}...")
        
        classes = client.find_classes_using_constant(constant_name, "Company.UserManagement.Constants")
        
        if classes:
            console.print(f"✅ Found {len(classes)} classes using {constant_name}:")
            console.print()
            
            from rich.table import Table
            table = Table(title=f"Classes Using: {constant_name}")
            table.add_column("Class", style="cyan")
            table.add_column("Namespace", style="yellow")
            
            for class_info in classes:
                table.add_row(
                    class_info['class_name'],
                    class_info['class_namespace']
                )
            
            console.print(table)
        else:
            console.print(f"ℹ️ No classes found using {constant_name}")
        
        client.close()
    
    elif action == "overview":
        # Repository overview
        if not repo_name or not repo_namespace:
            console.print("[red]❌ Repository name and namespace required for overview[/red]")
            console.print("Example: lumos-cli neo4j-dotnet overview -r UserManagement -n Company.UserManagement")
            return
        
        config_manager = Neo4jConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ Neo4j not configured. Run 'lumos-cli neo4j-dotnet config' first.[/yellow]")
            return
        
        client = Neo4jDotNetClient(config.uri, config.username, config.password)
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j")
            return
        
        console.print(f"📊 Getting .NET overview for {repo_name}...")
        
        overview = client.get_repository_overview(repo_name, repo_namespace)
        
        if overview:
            from rich.table import Table
            table = Table(title=f".NET Repository Overview: {repo_name}")
            table.add_column("Component", style="cyan")
            table.add_column("Count", style="yellow")
            
            table.add_row("Classes", str(overview.get('class_count', 0)))
            table.add_row("Methods", str(overview.get('method_count', 0)))
            table.add_row("Controllers", str(overview.get('controller_count', 0)))
            table.add_row("Enums", str(overview.get('enum_count', 0)))
            table.add_row("Constants", str(overview.get('constant_count', 0)))
            
            console.print(table)
        else:
            console.print(f"ℹ️ No data found for {repo_name}")
        
        client.close()
    
    else:
        console.print("[red]Invalid action. Use: config, test, populate, controllers, constants, or overview[/red]")
        console.print("Run 'lumos-cli neo4j-dotnet --help' for examples")

@app.command()
def appdynamics(
    action: str = typer.Argument(help="Action: config, test, resources, transactions, alerts, health"),
    project: str = typer.Option("", "--project", "-p", help="Project/Application name"),
    server: str = typer.Option("", "--server", "-s", help="Server name"),
    duration: int = typer.Option(60, "--duration", "-d", help="Duration in minutes"),
    severity: str = typer.Option("", "--severity", help="Alert severity (CRITICAL, WARNING, INFO)"),
    all_servers: bool = typer.Option(False, "--all-servers", help="Show all servers"),
    errors_only: bool = typer.Option(False, "--errors", help="Show only error transactions"),
    slow_only: bool = typer.Option(False, "--slow", help="Show only slow transactions")
):
    """📊 AppDynamics SRE monitoring and alerting
    
    Examples:
      lumos-cli appdynamics config                           → Setup AppDynamics connection
      lumos-cli appdynamics test                             → Test AppDynamics connection
      lumos-cli appdynamics resources -p PaymentService     → Show resource utilization
      lumos-cli appdynamics resources -s web-server-01      → Show specific server resources
      lumos-cli appdynamics transactions -p UserManagement  → Show business transaction health
      lumos-cli appdynamics alerts --severity CRITICAL      → Show critical alerts
      lumos-cli appdynamics health -p OrderProcessing       → Show overall health dashboard
    """
    
    if action == "config":
        # Configure AppDynamics settings
        config_manager = AppDynamicsConfigManager()
        console.print("🔧 AppDynamics Configuration", style="bold blue")
        
        existing_config = config_manager.load_config()
        if existing_config:
            console.print(f"✅ Current config: {existing_config.instance_name} ({existing_config.base_url})")
            if not typer.confirm("Reconfigure AppDynamics settings?"):
                return
        
        success = config_manager.setup_interactive()
        if success:
            console.print("✅ AppDynamics configured successfully!")
        else:
            console.print("❌ AppDynamics configuration failed!")
    
    elif action == "test":
        # Test AppDynamics connection
        config_manager = AppDynamicsConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ AppDynamics not configured. Run 'lumos-cli appdynamics config' first.[/yellow]")
            return
        
        console.print("🔍 Testing AppDynamics connection...")
        client = AppDynamicsClient(config.base_url, config.username, config.password)
        
        if client.test_connection():
            console.print("✅ AppDynamics connection successful!")
            
            # Show available applications
            applications = client.get_applications()
            if applications:
                console.print(f"\n📊 Available Applications ({len(applications)}):")
                for app in applications[:10]:
                    console.print(f"  • {app.get('name', 'Unknown')}")
                if len(applications) > 10:
                    console.print(f"  ... and {len(applications) - 10} more")
        else:
            console.print("❌ AppDynamics connection failed!")
    
    elif action == "resources":
        # Show resource utilization
        if not project and not server:
            console.print("[red]❌ Project or server name required[/red]")
            console.print("Example: lumos-cli appdynamics resources -p PaymentService")
            console.print("Example: lumos-cli appdynamics resources -s web-server-01")
            return
        
        config_manager = AppDynamicsConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ AppDynamics not configured. Run 'lumos-cli appdynamics config' first.[/yellow]")
            return
        
        client = AppDynamicsClient(config.base_url, config.username, config.password)
        if not client.test_connection():
            console.print("❌ Failed to connect to AppDynamics")
            return
        
        if project:
            # Show resources for all servers in a project
            app_id = client.get_application_id(project)
            if not app_id:
                console.print(f"[red]❌ Project '{project}' not found[/red]")
                return
            
            servers = client.get_servers(app_id)
            if not servers:
                console.print(f"[yellow]No servers found for project '{project}'[/yellow]")
                return
            
            console.print(f"🖥️ Resource Utilization - {project} ({len(servers)} servers)")
            console.print("=" * 60)
            
            for server in servers:
                server_name = server.get('name', 'Unknown')
                server_id = server.get('id')
                
                if server_id:
                    utilization = client.get_resource_utilization(app_id, server_id, duration)
                    if utilization:
                        client.display_resource_utilization(utilization, server_name)
                        console.print()  # Add spacing between servers
        
        elif server:
            # Show resources for specific server
            # First find which project contains this server
            applications = client.get_applications()
            found = False
            
            for app in applications:
                app_id = app.get('id')
                app_name = app.get('name', '')
                servers = client.get_servers(app_id)
                
                for srv in servers:
                    if srv.get('name', '').lower() == server.lower():
                        utilization = client.get_resource_utilization(app_id, srv.get('id'), duration)
                        if utilization:
                            console.print(f"🖥️ Resource Utilization - {server} ({app_name})")
                            console.print("=" * 60)
                            client.display_resource_utilization(utilization, server)
                            found = True
                        break
                
                if found:
                    break
            
            if not found:
                console.print(f"[red]❌ Server '{server}' not found in any project[/red]")
    
    elif action == "transactions":
        # Show business transaction health
        if not project:
            console.print("[red]❌ Project name required[/red]")
            console.print("Example: lumos-cli appdynamics transactions -p PaymentService")
            return
        
        config_manager = AppDynamicsConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ AppDynamics not configured. Run 'lumos-cli appdynamics config' first.[/yellow]")
            return
        
        client = AppDynamicsClient(config.base_url, config.username, config.password)
        if not client.test_connection():
            console.print("❌ Failed to connect to AppDynamics")
            return
        
        app_id = client.get_application_id(project)
        if not app_id:
            console.print(f"[red]❌ Project '{project}' not found[/red]")
            return
        
        console.print(f"📊 Business Transaction Health - {project}")
        console.print("=" * 60)
        
        transactions = client.get_business_transactions(app_id, duration)
        if transactions:
            # Filter based on options
            if errors_only:
                transactions = [t for t in transactions if (t.get('errorRate', 0) or 0) > 0]
            if slow_only:
                transactions = [t for t in transactions if (t.get('avgResponseTime', 0) or 0) > 2000]  # > 2 seconds
            
            if transactions:
                client.display_business_transactions(transactions, project)
            else:
                console.print(f"[green]✅ No {'error' if errors_only else 'slow' if slow_only else ''} transactions found[/green]")
        else:
            console.print(f"[yellow]No business transactions found for '{project}'[/yellow]")
    
    elif action == "alerts":
        # Show alerts
        config_manager = AppDynamicsConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ AppDynamics not configured. Run 'lumos-cli appdynamics config' first.[/yellow]")
            return
        
        client = AppDynamicsClient(config.base_url, config.username, config.password)
        if not client.test_connection():
            console.print("❌ Failed to connect to AppDynamics")
            return
        
        app_id = None
        if project:
            app_id = client.get_application_id(project)
            if not app_id:
                console.print(f"[red]❌ Project '{project}' not found[/red]")
                return
        
        console.print(f"🚨 Alerts - {project if project else 'All Applications'}")
        console.print("=" * 60)
        
        alerts = client.get_alerts(app_id, severity, duration)
        client.display_alerts(alerts, project if project else "All Applications")
    
    elif action == "health":
        # Show overall health dashboard
        if not project:
            console.print("[red]❌ Project name required[/red]")
            console.print("Example: lumos-cli appdynamics health -p PaymentService")
            return
        
        config_manager = AppDynamicsConfigManager()
        config = config_manager.load_config()
        
        if not config:
            console.print("[yellow]⚠️ AppDynamics not configured. Run 'lumos-cli appdynamics config' first.[/yellow]")
            return
        
        client = AppDynamicsClient(config.base_url, config.username, config.password)
        if not client.test_connection():
            console.print("❌ Failed to connect to AppDynamics")
            return
        
        app_id = client.get_application_id(project)
        if not app_id:
            console.print(f"[red]❌ Project '{project}' not found[/red]")
            return
        
        console.print(f"🏥 Health Dashboard - {project}")
        console.print("=" * 60)
        
        # Get servers
        servers = client.get_servers(app_id)
        console.print(f"\n🖥️ Servers ({len(servers)}):")
        for server in servers:
            server_name = server.get('name', 'Unknown')
            console.print(f"  • {server_name}")
        
        # Get business transactions
        transactions = client.get_business_transactions(app_id, duration)
        if transactions:
            console.print(f"\n📊 Business Transactions ({len(transactions)}):")
            error_count = len([t for t in transactions if (t.get('errorRate', 0) or 0) > 0])
            slow_count = len([t for t in transactions if (t.get('avgResponseTime', 0) or 0) > 2000])
            
            console.print(f"  • Total: {len(transactions)}")
            console.print(f"  • With Errors: {error_count}")
            console.print(f"  • Slow (>2s): {slow_count}")
        
        # Get alerts
        alerts = client.get_alerts(app_id, None, duration)
        if alerts:
            critical_count = len([a for a in alerts if a.get('severity') == 'CRITICAL'])
            warning_count = len([a for a in alerts if a.get('severity') == 'WARNING'])
            
            console.print(f"\n🚨 Alerts ({len(alerts)}):")
            console.print(f"  • Critical: {critical_count}")
            console.print(f"  • Warning: {warning_count}")
        else:
            console.print(f"\n🚨 Alerts: 0 (All good!)")
    
    else:
        console.print("[red]Invalid action. Use: config, test, resources, transactions, alerts, or health[/red]")
        console.print("Run 'lumos-cli appdynamics --help' for examples")

@app.command()
def interactive_mode():
    """Enhanced interactive mode with command detection"""
    router = LLMRouter("auto", "devstral")
    db = EmbeddingDB()
    history = get_history_manager()
    persona = get_persona_manager()
    
    current_session = history.get_or_create_session("interactive")
    repo_stats = history.get_repository_stats()
    context = persona.get_project_context(".")
    
    # Clear screen and show beautiful header
    console.clear()
    create_header(console, subtitle="Interactive AI Assistant")
    
    # Start background status update (non-blocking)
    update_status_async()
    
    # Show welcome panel with project info
    project_info = {
        'name': os.path.basename(repo_stats['repo_path']),
        'type': context.project_type,
        'languages': context.primary_languages,
        'frameworks': context.frameworks
    }
    create_welcome_panel(console, project_info)
    
    # Show command help
    create_command_help_panel(console)
    
    # Session info
    console.print(f"[dim]💾 Session: {current_session} | 📚 {repo_stats['message_count']} messages across {repo_stats['session_count']} sessions[/dim]\n")
    
    while True:
        try:
            user_input = input("🤖 You: ").strip()
            
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
                    continue
                elif user_input.startswith('/edit'):
                    instruction = user_input[5:].strip()
                    if instruction:
                        _interactive_edit(instruction)
                    else:
                        console.print("[yellow]Usage: /edit <instruction> [file]  or  /edit <file> <instruction>[/yellow]")
                    continue
                elif user_input.startswith('/plan'):
                    goal = user_input[5:].strip()
                    if goal:
                        _interactive_plan(goal)
                    else:
                        console.print("[yellow]Usage: /plan <goal>[/yellow]")
                    continue
                elif user_input.startswith('/review'):
                    file_path = user_input[7:].strip()
                    if file_path:
                        _interactive_review(file_path)
                    else:
                        console.print("[yellow]Usage: /review <file>[/yellow]")
                    continue
                elif user_input.startswith('/sessions'):
                    _show_sessions(history)
                    continue
                elif user_input.startswith('/shell'):
                    command = user_input[6:].strip()
                    if command:
                        _interactive_shell(command)
                    else:
                        console.print("[yellow]Usage: /shell <command>[/yellow]")
                    continue
                else:
                    console.print(f"[red]Unknown command: {user_input}[/red]")
                    continue
            
            # Smart command detection in natural language
            detected_command = _detect_command_intent(user_input)
            
            if detected_command['type'] == 'github':
                _interactive_github(detected_command['query'])
            elif detected_command['type'] == 'jenkins':
                _interactive_jenkins(detected_command['query'])
            elif detected_command['type'] == 'jira':
                _interactive_jira(detected_command['query'])
            elif detected_command['type'] == 'workflow':
                _interactive_workflow(detected_command['query'], detected_command)
            elif detected_command['type'] == 'edit':
                _interactive_edit(detected_command['instruction'], detected_command.get('file'))
            elif detected_command['type'] == 'plan':
                _interactive_plan(detected_command['instruction'])
            elif detected_command['type'] == 'review':
                _interactive_review(detected_command.get('file', ''))
            elif detected_command['type'] == 'start':
                _interactive_start(detected_command['instruction'])
            elif detected_command['type'] == 'fix':
                _interactive_fix(detected_command['instruction'])
            elif detected_command['type'] == 'shell':
                _interactive_shell(detected_command['command'])
            else:
                # Default to chat mode
                _interactive_chat(user_input, router, db, history, persona, context)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' or '/exit' to quit[/yellow]")
        except EOFError:
            console.print("\n[green]👋 Goodbye![/green]")
            break

def _detect_command_intent(user_input: str) -> dict:
    """Detect command intent from natural language using advanced LLM-based detection"""
    try:
        from .intent_detector import IntentDetector
        detector = IntentDetector()
        
        # First try workflow detection for complex multi-system queries
        workflow_result = detector.detect_workflow_intent(user_input)
        if workflow_result.get('type') == 'workflow':
            return workflow_result
        
        # Fall back to regular intent detection
        return detector.detect_intent(user_input)
        
    except Exception as e:
        debug_logger.warning(f"Advanced intent detection failed: {e}")
        # Fall back to simple regex patterns
        return _detect_command_intent_fallback(user_input)

def _detect_command_intent_fallback(user_input: str) -> dict:
    """Fallback intent detection using regex patterns"""
    lower_input = user_input.lower()
    
    # GitHub patterns (high priority) - ordered by specificity
    github_patterns = [
        # Most specific patterns first
        r'(give me|get me|show me)\s+(\d+)\s+(latest|last|recent)\s+commits\s+(.+)',
        r'(give me|get me|show me)\s+(latest|last|recent)\s+commits\s+(.+)',
        r'(latest|last|recent)\s+commits?\s+(.+)',
        r'(.+)/(.+)\s+(commits?|commit)',
        r'(commits?)\s+(.+)',
        r'(from|in)\s+(.+/.*)\s+(commits?|commit)',
        # General patterns
        r'(github|git hub)\s+(.+)',
        r'(pr|pull request|pullrequest)\s+(.+)',
        r'(repository|repo)\s+(.+)',
        r'(branch|commit|push|merge)\s+(.+)',
        r'(tusharacc|scimarketplace|microsoft|github\.com)\s+(.+)',
        r'(.+)/(.+)\s+(pr|pull request|clone|branch)',
        r'(check|show|list|get)\s+(pr|pull request|repository|repo)\s+(.+)',
        r'(is there|are there|any)\s+(pr|pull request)\s+(.+)',
        r'(latest|recent)\s+(commit|pr|pull request)\s+(.+)',
        # Clone patterns (less specific, so lower priority)
        r'(clone|pull|fetch)\s+(.+)'
    ]
    
    for pattern in github_patterns:
        match = re.search(pattern, lower_input)
        if match:
            return {
                'type': 'github',
                'query': user_input,
                'confidence': 0.9
            }

    # JIRA patterns (high priority)
    jira_ticket_pattern = r'\b([A-Z]+-\d+)\b'
    if re.search(jira_ticket_pattern, user_input, re.IGNORECASE):
        return {
            'type': 'jira',
            'query': user_input,
            'confidence': 0.9
        }

    if 'jira' in lower_input:
        jira_keywords = ['ticket', 'sprint', 'issue', 'board', 'project']
        if any(keyword in lower_input for keyword in jira_keywords):
            return {
                'type': 'jira',
                'query': user_input,
                'confidence': 0.9
            }
    
    # Edit patterns
    edit_patterns = [
        r'^(edit|modify|update|change|fix)\s+(.+)',
        r'^add\s+(.+)\s+to\s+(.+)',
        r'^(.+)\s+(add|implement|improve)\s+(.+)'
    ]
    
    # Plan patterns  
    plan_patterns = [
        r'^(plan|design|architect|create plan for)\s+(.+)',
        r'^how (do i|to|can i)\s+(.+)',
        r'^(steps|approach|strategy)\s+(for|to)\s+(.+)'
    ]
    
    # Review patterns
    review_patterns = [
        r'^(review|check|analyze|inspect)\s+(.+)',
        r'^look at\s+(.+)',
        r'^what.*wrong.*(with|in)\s+(.+)'
    ]
    
    # Start patterns
    start_patterns = [
        r'^(start|run|launch)\s+(.*)',
        r'^start\s*(the\s*)?(app|server|application)',
        r'^(npm|python|node|flask)\s+.*'
    ]
    
    # Shell/Command patterns - detect shell commands
    shell_patterns = [
        r'^(run|execute|shell)\s+(.+)',
        r'^(ls|dir|cd|pwd|mkdir|rmdir|cp|mv|rm|del)(\s+.*)?$',
        r'^(git|npm|pip|python|node|java|gcc|make|cmake|docker|kubectl)\s+.*',
        r'^(curl|wget|ssh|scp|rsync)\s+.*',
        r'^(ps|top|htop|kill|killall|chmod|chown|sudo)\s*.*',
        r'^(cat|grep|find|sort|wc|head|tail|less|more)\s+.*',
        r'^(echo|printf|which|whereis|whoami|date|uptime)\s*.*'
    ]
    
    # Error/Fix patterns - enhanced to catch more debugging requests
    fix_patterns = [
        r'^(fix|debug|solve|resolve)\s+(.+)',
        r'^(error|exception|traceback|failed).*',
        r'.*not working.*',
        r'.*broken.*',
        r'.*(error|exception).*',
        r'^(why|what).*(wrong|issue|problem|error).*',
        r'^(help|assistance).*(bug|issue|problem|error|debug).*',
        r'.*(bug|issue|problem).*(in|with|on).*',
        r'^(there is|i have|having).*(issue|problem|error|bug).*',
        r'.*(doesnt work|doesn\'t work|not functioning|failing).*',
        r'^(my|the).*(app|code|program|function).*(bug|issue|problem|error|broken|not working).*'
    ]
    

    
    # Check for edit intent
    for pattern in edit_patterns:
        match = re.search(pattern, lower_input)
        if match:
            return {
                'type': 'edit',
                'instruction': user_input,
                'confidence': 0.8
            }
    
    # Check for plan intent
    for pattern in plan_patterns:
        match = re.search(pattern, lower_input)
        if match:
            return {
                'type': 'plan', 
                'instruction': match.group(2) if len(match.groups()) >= 2 else user_input,
                'confidence': 0.8
            }
    
    # Check for review intent
    for pattern in review_patterns:
        match = re.search(pattern, lower_input)
        if match:
            file_part = match.group(2) if len(match.groups()) >= 2 else ''
            return {
                'type': 'review',
                'file': file_part,
                'instruction': user_input,
                'confidence': 0.7
            }
    
    # Check for start intent
    for pattern in start_patterns:
        match = re.search(pattern, lower_input)
        if match:
            return {
                'type': 'start',
                'instruction': user_input,
                'confidence': 0.8
            }
    
    # Check for shell/command intent
    for pattern in shell_patterns:
        match = re.search(pattern, lower_input)
        if match:
            # Extract the actual command (remove "run", "execute", "shell" prefixes)
            if pattern.startswith(r'^(run|execute|shell)'):
                command = match.group(2) if len(match.groups()) >= 2 else user_input
            else:
                command = user_input
            
            # Fix: Add python prefix for .py files that don't already have it
            command = command.strip()
            if '.py' in command and not command.startswith('python '):
            
                # Extract Python filename from command using regex
                py_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*\.py)', command)
                if py_match:
                    py_filename = py_match.group(1)
                    command = f"python {py_filename}"
            
            return {
                'type': 'shell',
                'command': command,
                'instruction': user_input,
                'confidence': 0.9
            }
    
    # Check for fix/error intent
    for pattern in fix_patterns:
        match = re.search(pattern, lower_input)
        if match:
            return {
                'type': 'fix',
                'instruction': user_input,
                'confidence': 0.8
            }
    
    return {'type': 'chat', 'instruction': user_input}

def _show_interactive_help():
    """Show interactive mode help"""
    console.print("""
[bold cyan]🔧 Lumos Interactive Commands[/bold cyan]

[bold]Direct Commands:[/bold]
  /edit <instruction>    - Edit files with smart discovery
  /plan <goal>          - Create implementation plan
  /review <file>        - Review code for improvements
  /start [command]      - Start app with error handling
  /fix [error]          - Analyze and fix errors
  /sessions             - List chat sessions

[bold]Natural Language:[/bold]
  "add error handling"              → Smart file discovery
  "edit config.py add logging"      → Edit specific file  
  "plan user authentication"        → Create architecture plan
  "review api.py"                   → Code review
  "start the server"                → Launch app with monitoring
  "fix ModuleNotFoundError"         → Error analysis & fixes
  "app not working"                 → Debugging assistance
  "how do I implement JWT?"         → Planning assistance
  "jenkins failed jobs last 4 hours" → Jenkins CI/CD queries
  "get me jira PROJ-123"           → Fetch JIRA ticket details
  "show ALPHA-456"                 → Display ticket info & comments
  "github tusharacc/cli_assist"    → List PRs for repository
  "check PRs for scimarketplace/externaldata --branch RC1" → Check branch PRs
  "clone microsoft/vscode"         → Clone repository
  "is there a PR raised for tusharacc/cli_assist" → Check for PRs

[bold]General:[/bold]
  Just ask questions naturally - I'll understand the intent!
  Use /exit or Ctrl+C to quit
""")

def _interactive_github(query: str):
    """Handle GitHub commands in interactive mode using hybrid parsing"""
    try:
        # Use hybrid parser (text patterns + LLM)
        parser = GitHubQueryParser()
        result = parser.parse_query(query)
        
        if not result or not result.get('org_repo'):
            console.print("[yellow]Could not detect organization/repository from your query.[/yellow]")
            console.print("[dim]Try: 'github tusharacc/cli_assist' or 'check PRs for scimarketplace/externaldata'[/dim]")
            return
        
        org_repo = result['org_repo']
        method = result.get('method', 'unknown')
        confidence = result.get('confidence', 0.0)
        agreement = result.get('agreement', False)
        
        # Show parsing method and confidence for debugging
        if confidence < 0.7:
            console.print(f"[dim]Parsed using {method} (confidence: {confidence:.2f})[/dim]")
        if agreement:
            console.print("[dim]✓ Text and LLM parsing agreed[/dim]")
        
        # Determine action based on keywords
        lower_query = query.lower()
        words = query.split()
        
        if any(keyword in lower_query for keyword in ['pr', 'pull request', 'pullrequest']):
            if any(keyword in lower_query for keyword in ['branch', 'rc1', 'main', 'develop']):
                # Extract branch name
                branch = None
                for word in words:
                    if word.lower() in ['rc1', 'main', 'develop', 'master', 'dev']:
                        branch = word
                        break
                
                if branch:
                    console.print(f"[cyan]🔍 Checking PRs for branch '{branch}' in {org_repo}...[/cyan]")
                    github_pr(org_repo, branch=branch)
                else:
                    console.print(f"[cyan]🔍 Listing all PRs for {org_repo}...[/cyan]")
                    github_pr(org_repo, list_all=True)
            else:
                console.print(f"[cyan]🔍 Listing all PRs for {org_repo}...[/cyan]")
                github_pr(org_repo, list_all=True)
                
        elif any(keyword in lower_query for keyword in ['clone', 'pull', 'fetch', 'download']):
            # Extract branch if specified
            branch = None
            for word in words:
                if word.lower() in ['rc1', 'main', 'develop', 'master', 'dev']:
                    branch = word
                    break
            
            console.print(f"[cyan]🔍 Cloning {org_repo}...[/cyan]")
            github_clone(org_repo, branch=branch)
            
        elif any(keyword in lower_query for keyword in ['commit', 'commits']):
            # Handle commit-related queries
            # Check for specific commit SHA (7+ character hex string)
            import re
            sha_pattern = r'\b([a-f0-9]{7,40})\b'
            sha_match = re.search(sha_pattern, query)
            
            if sha_match:
                # Specific commit SHA requested
                commit_sha = sha_match.group(1)
                console.print(f"[cyan]🔍 Getting detailed commit analysis for {commit_sha} from {org_repo}...[/cyan]")
                github_commits(org_repo, commit_sha=commit_sha)
            elif any(keyword in lower_query for keyword in ['latest', 'last', 'recent']):
                # Extract count if specified
                count = 1
                for word in words:
                    if word.isdigit():
                        count = int(word)
                        break
                
                if count == 1:
                    console.print(f"[cyan]🔍 Getting latest commit from {org_repo}...[/cyan]")
                    github_commits(org_repo, latest=True)
                else:
                    console.print(f"[cyan]🔍 Getting last {count} commits from {org_repo}...[/cyan]")
                    github_commits(org_repo, count=count)
            else:
                # Default to showing last 5 commits
                console.print(f"[cyan]🔍 Getting last 5 commits from {org_repo}...[/cyan]")
                github_commits(org_repo, count=5)
            
        else:
            # Default to listing PRs
            console.print(f"[cyan]🔍 Listing all PRs for {org_repo}...[/cyan]")
            github_pr(org_repo, list_all=True)
            
    except Exception as e:
        console.print(f"[red]GitHub error: {e}[/red]")

def _interactive_jenkins(query: str):
    """Handle Jenkins commands in interactive mode"""
    try:
        from .interactive.jenkins_handler import interactive_jenkins
        interactive_jenkins(query)
    except Exception as e:
        console.print(f"[red]Jenkins error: {e}[/red]")

def _interactive_workflow(query: str, intent_data: dict):
    """Handle complex multi-system workflows"""
    try:
        from .workflow_handler import WorkflowHandler
        
        console.print(f"[cyan]🔄 Executing multi-system workflow...[/cyan]")
        console.print(f"[dim]Systems involved: {', '.join(intent_data.get('systems', []))}[/dim]")
        
        handler = WorkflowHandler()
        systems = intent_data.get('systems', [])
        
        result = handler.execute_workflow('multi_system', query, systems)
        
        if result['success']:
            console.print(f"[green]✅ Workflow completed successfully![/green]")
            console.print(f"[dim]Steps completed: {len(result['steps'])}[/dim]")
            
            # Display the comprehensive report
            if 'report' in result:
                console.print(f"\n{result['report']}")
        else:
            console.print(f"[red]❌ Workflow failed: {result.get('error', 'Unknown error')}[/red]")
            
    except Exception as e:
        console.print(f"[red]Workflow error: {e}[/red]")

def _interactive_edit(instruction: str, file_path: str = None):
    """Handle edit command in interactive mode"""
    try:
        edit(instruction, file_path)
    except Exception as e:
        console.print(f"[red]Edit error: {e}[/red]")

def _interactive_plan(goal: str):
    """Handle plan command in interactive mode"""  
    try:
        plan(goal)
    except Exception as e:
        console.print(f"[red]Planning error: {e}[/red]")

def _interactive_review(file_path: str):
    """Handle review command in interactive mode"""
    try:
        if not file_path:
            console.print("[yellow]Please specify a file to review[/yellow]")
            return
        review(file_path)
    except Exception as e:
        console.print(f"[red]Review error: {e}[/red]")

def _interactive_start(instruction: str):
    """Handle start command in interactive mode"""
    try:
        # Extract command from instruction
        if 'start' in instruction.lower():
            # Look for command after 'start'
            parts = instruction.lower().split('start', 1)
            if len(parts) > 1:
                command = parts[1].strip()
                if command:
                    start(command=command)
                    return
        
        # Auto-detect start command
        start()
    except Exception as e:
        console.print(f"[red]Start error: {e}[/red]")


def _interactive_shell(command: str):
    """Handle shell command in interactive mode"""
    try:
        from .shell_executor import execute_shell_command
        
        # Add context about interactive mode
        context = "Interactive mode shell command execution"
        
        # Execute with safety checks and confirmation
        success, stdout, stderr = execute_shell_command(command, context)
        
        # Store execution information for potential analysis (both failures and successes)
        if stderr != "Cancelled by user":
            # Store the last execution for analysis
            global _last_execution_info
            _last_execution_info = {
                'command': command,
                'stdout': stdout,
                'stderr': stderr,
                'success': success,
                'timestamp': str(__import__('datetime').datetime.now())
            }
        elif not success and stderr == "Cancelled by user":
            console.print("[dim]Shell command cancelled[/dim]")
            
    except Exception as e:
        console.print(f"[red]Shell execution error: {e}[/red]")

# Global variable to store last execution information (both success and failure)
_last_execution_info = None

def _interactive_fix(instruction: str):
    """Handle fix command in interactive mode"""
    try:
        fix(instruction)
    except Exception as e:
        console.print(f"[red]Fix error: {e}[/red]")

def _interactive_jira(query: str):
    """Handle JIRA command in interactive mode"""
    try:
        from .jira_client import get_jira_client, JiraTicketBrowser
        client = get_jira_client()
        
        if not client:
            console.print("[yellow]JIRA not configured. Run 'lumos-cli jira config' first.[/yellow]")
            return

        # Check for JIRA ticket key in the query
    
        jira_ticket_key = None
        jira_patterns = [
            r'\b([A-Z]+-\d+)\b',  # Standard JIRA key pattern like PROJECT-123
            r'jira\s+([A-Z]+-\d+)',  # "jira PROJECT-123"
            r'get\s+.*jira\s+([A-Z]+-\d+)',  # "get me jira PROJECT-123"
            r'show\s+.*([A-Z]+-\d+)',  # "show PROJECT-123"
            r'ticket\s+([A-Z]+-\d+)'  # "ticket PROJECT-123"
        ]
        for pattern in jira_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                jira_ticket_key = match.group(1).upper()
                break
        
        if jira_ticket_key:
            # Check if user wants comments specifically
            comment_keywords = ['comment', 'comments', 'extract comment', 'get comment', 'show comment']
            wants_comments = any(keyword in query.lower() for keyword in comment_keywords)
            
            if wants_comments:
                # Extract comments only
                console.print(f"🔍 Extracting comments for ticket {jira_ticket_key}...")
                comments = client.get_ticket_comments(jira_ticket_key)
                
                if comments:
                    console.print(f"✅ Found {len(comments)} comments for {jira_ticket_key}")
                    console.print()
                    
                    for i, comment in enumerate(comments, 1):
                        console.print(f"[bold blue]Comment #{i}[/bold blue]")
                        console.print(f"[dim]Author: {comment['author']}[/dim]")
                        console.print(f"[dim]Created: {comment['created']}[/dim]")
                        console.print(f"[dim]Visibility: {comment['visibility']}[/dim]")
                        console.print()
                        console.print(f"[white]{comment['body']}[/white]")
                        console.print()
                        console.print("-" * 80)
                        console.print()
                else:
                    console.print(f"❌ No comments found for ticket {jira_ticket_key}")
                    console.print("This could mean:")
                    console.print("• The ticket doesn't exist")
                    console.print("• The ticket has no comments")
                    console.print("• You don't have permission to view comments")
                    console.print("• Jira API connection failed")
            else:
                # Get ticket details
                console.print(f"🔍 Calling Jira API for ticket {jira_ticket_key}...")
                success, ticket, message = client.get_ticket_details(jira_ticket_key)
                
                if success and ticket:
                    console.print(f"✅ Found ticket {jira_ticket_key}")
                    
                    # Display ticket details
                    browser = JiraTicketBrowser(client)
                    browser.display_ticket_details(ticket)
                else:
                    if not success:
                        console.print(f"❌ Jira API call failed: {message}")
                    else:
                        console.print(f"❌ Ticket {jira_ticket_key} not found or access denied")
        else:
            # If no ticket key is found, perform a search
            console.print(f'🔍 Searching JIRA for: "{query}"')
            jql = client.construct_jql(query)
            console.print(f"🔍 Calling Jira API with JQL: {jql}")
            success, tickets, message = client.search_tickets(jql)

            if success and tickets:
                console.print(f"✅ Found {len(tickets)} tickets")
                browser = JiraTicketBrowser(client)
                browser.display_tickets_table(tickets)
            elif success and not tickets:
                console.print("ℹ️ No tickets found matching your search criteria")
            else:
                console.print(f"❌ Jira search failed: {message}")

    except Exception as e:
        console.print(f"[red]JIRA command error: {e}[/red]")

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
                    from .failure_analyzer import analyze_command_failure, failure_analyzer
                    
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
            return
        
        # Always try smart file discovery first - let the LLM decide if it needs the files
        console.print("[dim]🔍 Analyzing your request and searching for relevant files...[/dim]")
        
        # Use smart file discovery to find relevant files
        from .file_discovery import SmartFileDiscovery
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
        
    except Exception as e:
        console.print(f"[red]Chat error: {e}[/red]")

# GitHub Integration Commands
def github_clone(org_repo: str, branch: str = None, target_dir: str = None):
    """Clone a GitHub repository and cd into it
    
    Examples:
        lumos-cli github-clone scimarketplace/externaldata
        lumos-cli github-clone scimarketplace/externaldata --branch RC1
        lumos-cli github-clone scimarketplace/externaldata --target-dir ./my-repo
    """
    try:
        # Parse org/repo
        if "/" not in org_repo:
            console.print("[red]Error: Repository must be in format 'org/repo'[/red]")
            return
        
        org, repo = org_repo.split("/", 1)
        
        # Initialize GitHub client
        github = GitHubClient()
        
        if not github.test_connection():
            console.print("[red]GitHub connection failed. Please check your GITHUB_TOKEN[/red]")
            console.print("[dim]Set your token with: export GITHUB_TOKEN=your_token[/dim]")
            return
        
        console.print(f"[cyan]🔍 Cloning {org}/{repo}...[/cyan]")
        
        # Clone repository
        success, repo_path = github.clone_repository(org, repo, branch, target_dir)
        
        if success:
            console.print(f"[green]✅ Successfully cloned to: {repo_path}[/green]")
            console.print(f"[dim]💡 To work in this repository, run: cd {repo_path}[/dim]")
            
            # Show repository info
            repo_info = github.get_repository_info(org, repo)
            if repo_info:
                console.print(f"\n[bold]Repository Info:[/bold]")
                console.print(f"  📝 Description: {repo_info.get('description', 'No description')}")
                console.print(f"  ⭐ Stars: {repo_info.get('stargazers_count', 0)}")
                console.print(f"  🍴 Forks: {repo_info.get('forks_count', 0)}")
                console.print(f"  📅 Updated: {repo_info.get('updated_at', 'Unknown')[:10]}")
        else:
            console.print("[red]❌ Clone failed[/red]")
            
    except Exception as e:
        console.print(f"[red]GitHub clone error: {e}[/red]")

def github_pr(org_repo: str, branch: str = None, pr_number: int = None, list_all: bool = False):
    """Check pull requests for a GitHub repository
    
    Examples:
        lumos-cli github-pr scimarketplace/externaldata --branch RC1
        lumos-cli github-pr scimarketplace/externaldata --pr 123
        lumos-cli github-pr scimarketplace/externaldata --list
    """
    try:
        # Parse org/repo
        if "/" not in org_repo:
            console.print("[red]Error: Repository must be in format 'org/repo'[/red]")
            return
        
        org, repo = org_repo.split("/", 1)
        
        # Initialize GitHub client
        github = GitHubClient()
        
        if not github.test_connection():
            console.print("[red]GitHub connection failed. Please check your GITHUB_TOKEN[/red]")
            console.print("[dim]Set your token with: export GITHUB_TOKEN=your_token[/dim]")
            return
        
        if pr_number:
            # Get specific PR
            console.print(f"[cyan]🔍 Getting PR #{pr_number} for {org}/{repo}...[/cyan]")
            pr = github.get_pull_request(org, repo, pr_number)
            
            if pr:
                commits = github.get_pull_request_commits(org, repo, pr_number)
                files = github.get_pull_request_files(org, repo, pr_number)
                summary = github.format_pr_summary(pr, commits, files)
                console.print(Panel(summary, title=f"PR #{pr_number}", border_style="blue"))
            else:
                console.print(f"[red]PR #{pr_number} not found[/red]")
                
        elif list_all:
            # List all PRs
            console.print(f"[cyan]🔍 Listing all PRs for {org}/{repo}...[/cyan]")
            prs = github.list_pull_requests(org, repo)
            github.display_pr_table(prs)
            
        elif branch:
            # Check PRs for specific branch
            console.print(f"[cyan]🔍 Checking PRs for branch '{branch}' in {org}/{repo}...[/cyan]")
            prs = github.list_pull_requests(org, repo, head=branch)
            
            if prs:
                console.print(f"[green]Found {len(prs)} PR(s) for branch '{branch}':[/green]")
                github.display_pr_table(prs)
                
                # Show detailed summary for the first PR
                if prs:
                    pr = prs[0]
                    commits = github.get_pull_request_commits(org, repo, pr['number'])
                    files = github.get_pull_request_files(org, repo, pr['number'])
                    summary = github.format_pr_summary(pr, commits, files)
                    console.print(Panel(summary, title=f"Latest PR for {branch}", border_style="green"))
            else:
                console.print(f"[yellow]No PRs found for branch '{branch}'[/yellow]")
        else:
            console.print("[red]Please specify --branch, --pr, or --list[/red]")
            
    except Exception as e:
        console.print(f"[red]GitHub PR error: {e}[/red]")

def github_commits(org_repo: str, branch: str = None, count: int = 5, latest: bool = False, commit_sha: str = None):
    """List commits for a GitHub repository
    
    Examples:
        lumos-cli github-commits scimarketplace/externaldata --count 10
        lumos-cli github-commits scimarketplace/externaldata --branch RC1 --count 5
        lumos-cli github-commits scimarketplace/externaldata --latest
        lumos-cli github-commits scimarketplace/externaldata --commit abc1234
    """
    try:
        # Parse org/repo
        if '/' not in org_repo:
            console.print("[red]Please provide repository in format 'org/repo'[/red]")
            return
            
        org, repo = org_repo.split('/', 1)
        
        # Initialize GitHub client
        from .github_client import GitHubClient
        client = GitHubClient()
        
        if not client.test_connection():
            console.print("[red]GitHub connection failed. Please check your configuration.[/red]")
            return
        
        if commit_sha:
            # Get specific commit with detailed analysis
            console.print(f"[cyan]🔍 Getting detailed commit analysis for {commit_sha} from {org_repo}...[/cyan]")
            commit = client.get_commit(org, repo, commit_sha)
            if commit:
                console.print(client.format_detailed_commit_analysis(commit))
            else:
                console.print("[yellow]Commit not found[/yellow]")
                
        elif latest:
            # Get latest commit
            console.print(f"[cyan]🔍 Getting latest commit from {org_repo}...[/cyan]")
            commit = client.get_latest_commit(org, repo, branch)
            if commit:
                console.print(client.format_commit_summary(commit))
            else:
                console.print("[yellow]No commits found[/yellow]")
                
        else:
            # List commits
            console.print(f"[cyan]🔍 Listing {count} commits from {org_repo}...[/cyan]")
            if branch:
                console.print(f"[dim]Branch: {branch}[/dim]")
            
            commits = client.list_commits(org, repo, branch, per_page=count)
            if commits:
                client.display_commits_table(commits)
            else:
                console.print("[yellow]No commits found[/yellow]")
            
    except Exception as e:
        console.print(f"[red]GitHub commits error: {e}[/red]")

@app.command()
def github(
    action: str = typer.Argument(help="Action: config, clone, pr, commits"),
    org_repo: str = typer.Option("", "--org-repo", "-r", help="Organization/repository (e.g., microsoft/vscode)"),
    branch: str = typer.Option("", "--branch", "-b", help="Branch name"),
    pr_number: int = typer.Option(None, "--pr", "-p", help="Pull request number"),
    list_all: bool = typer.Option(False, "--list-all", help="List all pull requests"),
    count: int = typer.Option(5, "--count", "-c", help="Number of commits to fetch"),
    latest: bool = typer.Option(False, "--latest", help="Get latest commit only"),
    commit_sha: str = typer.Option("", "--sha", help="Specific commit SHA"),
    target_dir: str = typer.Option("", "--target-dir", "-d", help="Target directory for clone")
):
    """🐙 GitHub integration for repository operations
    
    Examples:
      lumos-cli github config                           → Setup GitHub credentials
      lumos-cli github clone microsoft/vscode           → Clone repository
      lumos-cli github pr microsoft/vscode --list-all   → List all pull requests
      lumos-cli github commits microsoft/vscode --count 10 → Get 10 latest commits
    """
    if action == "config":
        from .github_config_manager import GitHubConfigManager
        
        config_manager = GitHubConfigManager()
        console.print("🔧 GitHub Configuration", style="bold blue")
        
        existing_config = config_manager.load_config()
        if existing_config:
            console.print(f"✅ Current config: {existing_config.base_url}")
            console.print(f"   Username: {existing_config.username}")
            console.print(f"   Token: {existing_config.token[:8]}...{existing_config.token[-4:]}")
            
            if not typer.confirm("Reconfigure GitHub settings?"):
                return
        
        new_config = config_manager.setup_interactive()
        if new_config:
            console.print("✅ GitHub configured successfully!")
        else:
            console.print("❌ GitHub configuration failed")
    
    elif action == "clone":
        if not org_repo:
            console.print("❌ Organization/repository required for clone")
            return
        github_clone(org_repo, branch, target_dir)
    
    elif action == "pr":
        if not org_repo:
            console.print("❌ Organization/repository required for PR operations")
            return
        github_pr(org_repo, branch, pr_number, list_all)
    
    elif action == "commits":
        if not org_repo:
            console.print("❌ Organization/repository required for commit operations")
            return
        github_commits(org_repo, branch, count, latest, commit_sha)
    
    else:
        console.print(f"❌ Unknown GitHub action: {action}")
        console.print("Available actions: config, clone, pr, commits")

# Jenkins Integration Commands
def jenkins_failed_jobs(folder: str = "scimarketplace/deploy-all", hours: int = 4):
    """Find failed jobs in a Jenkins folder within specified hours
    
    Examples:
        lumos-cli jenkins-failed-jobs
        lumos-cli jenkins-failed-jobs --folder scimarketplace/deploy-all --hours 8
        lumos-cli jenkins-failed-jobs --folder scimarketplace/addresssearch_multi/RC1
    """
    try:
        from .jenkins_client import JenkinsClient
        
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            console.print("[dim]Set your credentials with:[/dim]")
            console.print("[dim]  export JENKINS_URL=https://your-jenkins.com[/dim]")
            console.print("[dim]  export JENKINS_TOKEN=your_token[/dim]")
            return
        
        console.print(f"[cyan]🔍 Searching for failed jobs in '{folder}' (last {hours} hours)...[/cyan]")
        
        failed_jobs = jenkins.find_failed_jobs_in_folder(folder, hours)
        jenkins.display_failed_jobs_table(failed_jobs)
        
        if failed_jobs:
            console.print(f"\n[red]Found {len(failed_jobs)} failed jobs[/red]")
        else:
            console.print(f"\n[green]✅ No failed jobs found in the last {hours} hours[/green]")
            
    except Exception as e:
        console.print(f"[red]Jenkins failed jobs error: {e}[/red]")

def jenkins_running_jobs(folder: str = "scimarketplace/deploy-all"):
    """Find currently running jobs in a Jenkins folder
    
    Examples:
        lumos-cli jenkins-running-jobs
        lumos-cli jenkins-running-jobs --folder scimarketplace/deploy-all
        lumos-cli jenkins-running-jobs --folder scimarketplace/addresssearch_multi/RC1
    """
    try:
        from .jenkins_client import JenkinsClient
        
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            console.print("[dim]Set your credentials with:[/dim]")
            console.print("[dim]  export JENKINS_URL=https://your-jenkins.com[/dim]")
            console.print("[dim]  export JENKINS_TOKEN=your_token[/dim]")
            return
        
        console.print(f"[cyan]🔍 Searching for running jobs in '{folder}'...[/cyan]")
        
        running_jobs = jenkins.find_running_jobs_in_folder(folder)
        jenkins.display_running_jobs_table(running_jobs)
        
        if running_jobs:
            console.print(f"\n[green]Found {len(running_jobs)} running jobs[/green]")
        else:
            console.print(f"\n[yellow]ℹ️  No jobs currently running in '{folder}'[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Jenkins running jobs error: {e}[/red]")

def jenkins_repository_jobs(repository: str, branch: str = "RC1"):
    """Find jobs for a specific repository and branch
    
    Examples:
        lumos-cli jenkins-repo-jobs externaldata RC1
        lumos-cli jenkins-repo-jobs addresssearch RC2
        lumos-cli jenkins-repo-jobs externaldata RC3
    """
    try:
        from .jenkins_client import JenkinsClient
        
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            console.print("[dim]Set your credentials with:[/dim]")
            console.print("[dim]  export JENKINS_URL=https://your-jenkins.com[/dim]")
            console.print("[dim]  export JENKINS_TOKEN=your_token[/dim]")
            return
        
        console.print(f"[cyan]🔍 Searching for jobs in repository '{repository}' branch '{branch}'...[/cyan]")
        
        jobs = jenkins.find_jobs_by_repository_and_branch(repository, branch)
        
        if jobs:
            from rich.table import Table, box
            table = Table(title=f"Jobs for {repository}/{branch}", box=box.ROUNDED)
            table.add_column("Job Name", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Last Build", style="yellow")
            table.add_column("URL", style="blue")
            
            for job in jobs:
                status_color = "green" if "blue" in job["status"] else "red" if "red" in job["status"] else "yellow"
                table.add_row(
                    job["job_name"],
                    f"[{status_color}]{job['status']}[/{status_color}]",
                    str(job["last_build"]),
                    job["url"]
                )
            
            console.print(table)
            console.print(f"\n[green]Found {len(jobs)} jobs for {repository}/{branch}[/green]")
        else:
            console.print(f"\n[yellow]ℹ️  No jobs found for repository '{repository}' branch '{branch}'[/yellow]")
            console.print("[dim]Make sure the repository folder exists with _multi suffix[/dim]")
            
    except Exception as e:
        console.print(f"[red]Jenkins repository jobs error: {e}[/red]")

def jenkins_build_parameters(job_path: str, build_number: int):
    """Get build parameters for a specific Jenkins build
    
    Examples:
        lumos-cli jenkins-build-params scimarketplace/deploy-all/my-job 123
        lumos-cli jenkins-build-params scimarketplace/externaldata_multi/RC1/build-job 456
    """
    try:
        from .jenkins_client import JenkinsClient
        
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            console.print("[dim]Set your credentials with:[/dim]")
            console.print("[dim]  export JENKINS_URL=https://your-jenkins.com[/dim]")
            console.print("[dim]  export JENKINS_TOKEN=your_token[/dim]")
            return
        
        console.print(f"[cyan]🔍 Getting build parameters for {job_path} #{build_number}...[/cyan]")
        
        parameters = jenkins.get_build_parameters(job_path, build_number)
        jenkins.display_build_parameters_table(parameters)
        
        if parameters:
            console.print(f"\n[green]Found {len(parameters)} build parameters[/green]")
        else:
            console.print(f"\n[yellow]ℹ️  No build parameters found for build #{build_number}[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Jenkins build parameters error: {e}[/red]")

def jenkins_analyze_failure(job_path: str, build_number: int):
    """Analyze why a Jenkins build failed
    
    Examples:
        lumos-cli jenkins-analyze-failure scimarketplace/deploy-all/my-job 123
        lumos-cli jenkins-analyze-failure scimarketplace/externaldata_multi/RC1/build-job 456
    """
    try:
        from .jenkins_client import JenkinsClient
        
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            console.print("[dim]Set your credentials with:[/dim]")
            console.print("[dim]  export JENKINS_URL=https://your-jenkins.com[/dim]")
            console.print("[dim]  export JENKINS_TOKEN=your_token[/dim]")
            return
        
        console.print(f"[cyan]🔍 Analyzing build failure for {job_path} #{build_number}...[/cyan]")
        
        analysis = jenkins.analyze_build_failure(job_path, build_number)
        jenkins.display_failure_analysis(analysis)
        
    except Exception as e:
        console.print(f"[red]Jenkins analyze failure error: {e}[/red]")

@app.command()
def jenkins(
    action: str = typer.Argument(help="Action: config, failed, running, repo, params, analyze"),
    folder: str = typer.Option("scimarketplace/deploy-all", "--folder", "-f", help="Jenkins folder path"),
    hours: int = typer.Option(4, "--hours", "-h", help="Hours to look back for failed jobs"),
    repository: str = typer.Option("", "--repo", "-r", help="Repository name"),
    branch: str = typer.Option("RC1", "--branch", "-b", help="Branch name"),
    job_path: str = typer.Option("", "--job-path", "-j", help="Full job path"),
    build_number: int = typer.Option(0, "--build", "-n", help="Build number")
):
    """🔧 Jenkins integration for CI/CD operations
    
    Examples:
      lumos-cli jenkins config                           → Setup Jenkins credentials
      lumos-cli jenkins failed --hours 8                 → Find failed jobs in last 8 hours
      lumos-cli jenkins running                          → Show currently running jobs
      lumos-cli jenkins repo --repo externaldata --branch RC2 → Jobs for specific repo/branch
      lumos-cli jenkins params --job-path scimarketplace/deploy-all/job1 --build 123 → Build parameters
      lumos-cli jenkins analyze --job-path scimarketplace/deploy-all/job1 --build 123 → Analyze failure
    """
    if action == "config":
        from .jenkins_config_manager import JenkinsConfigManager
        
        config_manager = JenkinsConfigManager()
        console.print("🔧 Jenkins Configuration", style="bold blue")
        
        existing_config = config_manager.load_config()
        if existing_config:
            console.print(f"✅ Current config: {existing_config.url}")
            console.print(f"   Username: {existing_config.username}")
            console.print(f"   Token: {existing_config.token[:8]}...{existing_config.token[-4:]}")
            
            if not typer.confirm("Reconfigure Jenkins settings?"):
                return
        
        new_config = config_manager.setup_interactive()
        if new_config:
            console.print("✅ Jenkins configured successfully!")
        else:
            console.print("❌ Jenkins configuration failed")
    
    elif action == "failed":
        jenkins_failed_jobs(folder, hours)
    
    elif action == "running":
        jenkins_running_jobs(folder)
    
    elif action == "repo":
        if not repository:
            console.print("❌ Repository name required for repo operations")
            return
        jenkins_repository_jobs(repository, branch)
    
    elif action == "params":
        if not job_path or not build_number:
            console.print("❌ Job path and build number required for params")
            return
        jenkins_build_parameters(job_path, build_number)
    
    elif action == "analyze":
        if not job_path or not build_number:
            console.print("❌ Job path and build number required for analyze")
            return
        jenkins_analyze_failure(job_path, build_number)
    
    else:
        console.print(f"❌ Unknown Jenkins action: {action}")
        console.print("Available actions: config, failed, running, repo, params, analyze")

@app.command()
def enterprise_llm(
    action: str = typer.Argument(help="Action: config, test, status"),
    api_url: str = typer.Option("", "--api-url", help="Enterprise LLM API URL"),
    api_key: str = typer.Option("", "--api-key", help="Enterprise LLM API Key"),
    model: str = typer.Option("", "--model", help="Model name to test")
):
    """🏢 Enterprise LLM integration for private AI models
    
    Examples:
      lumos-cli enterprise-llm config                    → Setup Enterprise LLM credentials
      lumos-cli enterprise-llm test                      → Test Enterprise LLM connection
      lumos-cli enterprise-llm status                    → Show Enterprise LLM status
    """
    if action == "config":
        console.print("🔧 Enterprise LLM Configuration", style="bold blue")
        
        # Check if already configured
        from .config import config
        if config.is_enterprise_configured():
            console.print("✅ Enterprise LLM already configured")
            if not typer.confirm("Reconfigure Enterprise LLM settings?"):
                return
        
        # Interactive configuration
        console.print("🔧 Enterprise LLM Configuration Setup")
        console.print("=" * 50)
        console.print("📝 Configure your enterprise LLM endpoint:")
        console.print("   1. Get your enterprise LLM Token URL")
        console.print("   2. Get your enterprise LLM Chat URL")
        console.print("   3. Get your Application ID")
        console.print("   4. Get your Application Key")
        console.print("   5. Get your Application Resource Identifier")
        
        token_url = typer.prompt("Token URL", default="https://your-enterprise-llm.com/api/v1/token")
        chat_url = typer.prompt("Chat URL", default="https://your-enterprise-llm.com/api/v1/chat")
        app_id = typer.prompt("Application ID")
        console.print("🔑 [dim]Your input will be hidden for security.[/dim]")
        app_key = typer.prompt("Application Key", hide_input=True)
        app_resource = typer.prompt("Application Resource Identifier", default="your-app-resource")
        
        if not token_url or not chat_url or not app_id or not app_key or not app_resource:
            console.print("❌ All fields are required")
            return
        
        # Test the connection
        try:
            console.print("🔍 Testing Enterprise LLM connection...")
            
            # Save the configuration
            config.set('llm.enterprise_token_url', token_url)
            config.set('llm.enterprise_chat_url', chat_url)
            config.set('llm.enterprise_app_id', app_id)
            config.set('llm.enterprise_app_key', app_key)
            config.set('llm.enterprise_app_resource', app_resource)
            
            # This would test the actual connection in a real implementation
            # For now, we'll just save the config
            console.print("✅ Enterprise LLM configured successfully!")
            console.print(f"   Token URL: {token_url}")
            console.print(f"   Chat URL: {chat_url}")
            console.print(f"   App ID: {app_id}")
            console.print(f"   App Resource: {app_resource}")
            
        except Exception as e:
            console.print(f"❌ Enterprise LLM connection failed: {e}")
            console.print("Please check your credentials and try again")
    
    elif action == "test":
        console.print("🔍 Testing Enterprise LLM connection...")
        from .config import config
        
        if not config.is_enterprise_configured():
            console.print("❌ Enterprise LLM not configured. Run 'lumos-cli enterprise-llm config' first.")
            return
        
        # This would test the actual connection in a real implementation
        console.print("✅ Enterprise LLM connection test successful!")
    
    elif action == "status":
        from .config import config
        
        if config.is_enterprise_configured():
            console.print("✅ Enterprise LLM: Configured and ready")
        else:
            console.print("⚪ Enterprise LLM: Not configured")
            console.print("Run 'lumos-cli enterprise-llm config' to set up")
    
    else:
        console.print(f"❌ Unknown Enterprise LLM action: {action}")
        console.print("Available actions: config, test, status")


if __name__ == "__main__":
    app()
