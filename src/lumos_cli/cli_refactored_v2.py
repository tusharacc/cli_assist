"""
Refactored Lumos CLI - Main entry point (Version 2)
"""

import typer
import os
from rich.console import Console
from .core import LLMRouter, TaskType, EmbeddingDB, SafeFileEditor, HistoryManager
from .ui import console, create_header, create_welcome_panel, show_footer
from .core.persona_manager import PersonaManager
# from .config import config, setup_wizard  # TODO: Implement these functions

# Import command modules
from .commands import (
    github_clone as github_clone_impl, github_pr as github_pr_impl, github_config as github_config_impl,
    jenkins_failed_jobs as jenkins_failed_jobs_impl, jenkins_running_jobs as jenkins_running_jobs_impl, 
    jenkins_repository_jobs as jenkins_repository_jobs_impl, 
    jenkins_build_parameters as jenkins_build_parameters_impl, 
    jenkins_analyze_failure as jenkins_analyze_failure_impl, 
    jenkins_config as jenkins_config_impl
)

# Import config managers for interactive setup
from .config.github_config_manager import GitHubConfigManager
from .config.jenkins_config_manager import JenkinsConfigManager

# Import interactive mode
from .interactive import interactive_mode

app = typer.Typer(invoke_without_command=True, no_args_is_help=False)

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

def update_status_async():
    """Update status indicators asynchronously"""
    import threading
    import time
    
    def update_status():
        time.sleep(1)  # Wait a bit for initial display
        # Update status indicators here
        pass
    
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

# Core commands
@app.command()
def plan(goal: str, backend: str = "auto", model: str = "devstral"):
    """Create a step-by-step plan for achieving a goal"""
    plan(goal, backend, model)

@app.command()
def edit(instruction: str, file_path: str = None):
    """Edit code with AI assistance"""
    edit(instruction, file_path)

@app.command()
def review(file_path: str):
    """Review code quality and suggest improvements"""
    review(file_path)

@app.command()
def debug(description: str):
    """Debug issues with AI assistance"""
    debug(description)

@app.command()
def chat(message: str):
    """Chat with the AI assistant"""
    chat(message)

# GitHub commands
@app.command()
def github_clone(org_repo: str, branch: str = None, target_dir: str = None):
    """Clone a GitHub repository"""
    github_clone_impl(org_repo, branch, target_dir)

@app.command()
def github_pr(org_repo: str, branch: str = None, pr_number: int = None, list_all: bool = False):
    """Check pull requests for a GitHub repository"""
    github_pr_impl(org_repo, branch, pr_number, list_all)

@app.command()
def github_config():
    """View GitHub integration configuration status"""
    github_config_impl()

@app.command("github")
def github_interactive_config(
    ctx: typer.Context,
    action: str = typer.Argument(..., help="Action: 'config' for interactive setup")
):
    """Interactive GitHub configuration"""
    if action == "config":
        config_manager = GitHubConfigManager()
        config_manager.setup_interactive()
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("[yellow]Usage: lumos-cli github config[/yellow]")

# Jenkins commands
@app.command()
def jenkins_failed_jobs(hours: int = 4):
    """Get failed Jenkins jobs from the last N hours"""
    jenkins_failed_jobs_impl(hours)

@app.command()
def jenkins_running_jobs():
    """Get currently running Jenkins jobs"""
    jenkins_running_jobs_impl()

@app.command()
def jenkins_repository_jobs(repository: str, branch: str = None):
    """Get Jenkins jobs for a specific repository"""
    jenkins_repository_jobs_impl(repository, branch)

@app.command()
def jenkins_build_parameters(folder: str, job_name: str, build_number: int):
    """Get build parameters for a specific Jenkins job"""
    jenkins_build_parameters_impl(folder, job_name, build_number)

@app.command()
def jenkins_analyze_failure(folder: str, job_name: str, build_number: int):
    """Analyze why a Jenkins build failed"""
    jenkins_analyze_failure_impl(folder, job_name, build_number)

@app.command()
def jenkins_config():
    """View Jenkins integration configuration status"""
    jenkins_config_impl()

@app.command("jenkins")
def jenkins_interactive_config(
    ctx: typer.Context,
    action: str = typer.Argument(..., help="Action: 'config' for interactive setup")
):
    """Interactive Jenkins configuration"""
    if action == "config":
        config_manager = JenkinsConfigManager()
        config_manager.setup_interactive()
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("[yellow]Usage: lumos-cli jenkins config[/yellow]")

# Utility commands
@app.command()
def platform():
    """Show platform information"""
    platform()

@app.command()
def logs():
    """Show recent logs"""
    logs()

@app.command()
def detect():
    """Detect project type and technologies"""
    detect()

@app.command()
def start(instruction: str):
    """Start a new project or application"""
    start(instruction)

@app.command()
def fix(instruction: str):
    """Fix issues in code"""
    fix(instruction)

@app.command()
def preview(instruction: str, file_path: str = None):
    """Preview changes before applying"""
    preview(instruction, file_path)

@app.command()
def index():
    """Index the current repository for semantic search"""
    index()

@app.command()
def cleanup():
    """Clean up temporary files and caches"""
    cleanup()

@app.command()
def sessions():
    """Manage chat sessions"""
    sessions()

@app.command()
def repos():
    """Manage repositories"""
    repos()

@app.command()
def context():
    """Show current context"""
    context()

@app.command()
def search(query: str):
    """Search the codebase"""
    search(query)

@app.command()
def history():
    """Show command history"""
    history()

@app.command()
def persona():
    """Manage AI personas"""
    persona()

@app.command()
def shell(command: str):
    """Execute shell commands"""
    shell(command)

@app.command()
def templates():
    """Manage code templates"""
    templates()

@app.command()
def welcome():
    """Show welcome message"""
    welcome()

# Project commands
@app.command()
def scaffold(project_type: str, project_name: str = None):
    """Scaffold a new project"""
    scaffold(project_type, project_name)

@app.command()
def backups():
    """Manage backups"""
    backups()

@app.command()
def restore(backup_name: str):
    """Restore from backup"""
    restore(backup_name)

if __name__ == "__main__":
    app()
