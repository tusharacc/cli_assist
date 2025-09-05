import typer, os
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
def edit(instruction: str, path: str = None, backend: str = "auto", model: str = "devstral", 
         preview: bool = True, force: bool = False):
    """Edit file(s) with AI assistance and smart file discovery"""
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
        
        ctx = db.search(instruction, top_k=3)
        snippets = "\n\n".join(c for _,c,_ in ctx)
        
        user_content = f"""FILE PATH: {file_path}
CURRENT CONTENTS:
<<<
{contents}
>>>
INSTRUCTION:
{instruction}

RELATED SNIPPETS:
{snippets}
"""
        
        # Add to history
        history.add_message("user", user_content, command="edit", file_path=file_path)
        
        # Get conversation context and enhance with persona
        conversation_history = history.get_recent_context(max_tokens=4000)
        enhanced_messages = persona.get_enhanced_messages(conversation_history, context, "edit")
        
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
def review(path: str, backend: str = "auto", model: str = "devstral"):
    """Review code for bugs, improvements, and best practices"""
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

def _auto_detect_start_command(context) -> str:
    """Auto-detect the appropriate start command based on project context"""
    
    # Check for common startup files
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
    
    # Check for Flask
    if 'python' in context.primary_languages:
        # Look for Flask app
        for file in ['app.py', 'main.py', 'server.py']:
            if os.path.exists(file):
                try:
                    with open(file, 'r') as f:
                        content = f.read()
                        if 'Flask' in content and 'app.run' in content:
                            return f'python {file}'
                        elif 'Flask' in content:
                            return f'flask run'
                except:
                    continue
    
    # Check for framework-specific commands
    if 'django' in context.frameworks:
        return 'python manage.py runserver'
    
    return None

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
        "🌐 REST API": {
            "status": "configured" if "rest" in available_backends else "missing", 
            "details": f"Remote API - {config.get('llm.rest_api_url', 'Not configured')}"
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
        
        debug_table.add_row("REST API URL", config.get('llm.rest_api_url') or '[dim]Not set[/dim]')
        debug_table.add_row("REST API Key", '[green]✓ Set[/green]' if config.get('llm.rest_api_key') else '[red]✗ Not set[/red]')
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
            console.print("🚀 Testing REST API connection...")
            
            # Enable debug mode for this test
            response = router._chat_rest(messages, debug=True)
            console.print(f"✅ REST API Response: {response}")
        except Exception as e:
            console.print(f"❌ REST API Error: {str(e)}")
    else:
        console.print("⚠️ REST API not configured")
    
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
    value: str = typer.Argument("", help="Value to set (for 'set' action)")
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
            ("llm.rest_api_url", "REST API URL"),
            ("llm.rest_api_key", "REST API Key"), 
            ("llm.rest_model", "REST Model"),
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
        console.print("• Config stored in: %APPDATA%\\Lumos")
        console.print("• Logs stored in: %LOCALAPPDATA%\\Lumos\\Logs") 
        console.print("• Ollama typically installed in: Program Files\\Ollama")
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
                else:
                    console.print(f"[red]Unknown command: {user_input}[/red]")
                    continue
            
            # Smart command detection in natural language
            detected_command = _detect_command_intent(user_input)
            
            if detected_command['type'] == 'edit':
                _interactive_edit(detected_command['instruction'], detected_command.get('file'))
            elif detected_command['type'] == 'plan':
                _interactive_plan(detected_command['instruction'])
            elif detected_command['type'] == 'review':
                _interactive_review(detected_command.get('file', ''))
            elif detected_command['type'] == 'start':
                _interactive_start(detected_command['instruction'])
            elif detected_command['type'] == 'fix':
                _interactive_fix(detected_command['instruction'])
            else:
                # Default to chat mode
                _interactive_chat(user_input, router, db, history, persona, context)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' or '/exit' to quit[/yellow]")
        except EOFError:
            console.print("\n[green]👋 Goodbye![/green]")
            break

def _detect_command_intent(user_input: str) -> dict:
    """Detect command intent from natural language"""
    lower_input = user_input.lower()
    
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
        r'^(steps|approach|strategy) (for|to)\s+(.+)'
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
    
    # Error/Fix patterns
    fix_patterns = [
        r'^(fix|debug|solve|resolve)\s+(.+)',
        r'^(error|exception|traceback|failed).*',
        r'.*not working.*',
        r'.*broken.*',
        r'.*(error|exception).*'
    ]
    
    import re
    
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

[bold]General:[/bold]
  Just ask questions naturally - I'll understand the intent!
  Use /exit or Ctrl+C to quit
""")

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

def _interactive_fix(instruction: str):
    """Handle fix command in interactive mode"""
    try:
        fix(instruction)
    except Exception as e:
        console.print(f"[red]Fix error: {e}[/red]")

def _interactive_chat(user_input: str, router, db, history, persona, context):
    """Handle general chat in interactive mode"""
    try:
        # Search for relevant context
        ctx = db.search(user_input, top_k=3)
        snippets = "\n\n".join(c for _,c,_ in ctx)
        
        user_content = f"""{user_input}
        
RELATED CODE:
{snippets}
"""
        
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

if __name__ == "__main__":
    app()
