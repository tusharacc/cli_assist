"""
Refactored Lumos CLI - Main entry point
"""

import typer
import os
from rich.console import Console
from .client import LLMRouter, TaskType
from .embeddings import EmbeddingDB
from .safety import SafeFileEditor
from .history import HistoryManager
from .persona_manager import PersonaManager
from .config import config, setup_wizard
from .ui import create_header, create_welcome_panel, create_command_help_panel, create_status_panel, create_config_panel, print_brand_footer

# Import command modules
from .commands import (
    github_clone, github_pr, github_config,
    edit, review, plan, debug, chat,
    scaffold, backups, restore,
    platform, logs, detect, start, fix, preview, index, 
    cleanup, sessions, repos, context, search, history, 
    persona, shell, templates, welcome
)

# Import interactive mode
from .interactive import interactive_mode

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
        # Show welcome screen
        console.clear()
        create_header(console, subtitle="Interactive AI Assistant")
        create_welcome_panel(console)
        create_command_help_panel(console)
        print_brand_footer(console)
        
        # Start interactive mode
        interactive_mode()

# Register all commands
app.command()(github_clone)
app.command()(github_pr)
app.command()(github_config)
app.command()(edit)
app.command()(review)
app.command()(plan)
app.command()(debug)
app.command()(chat)
app.command()(scaffold)
app.command()(backups)
app.command()(restore)
app.command()(platform)
app.command()(logs)
app.command()(detect)
app.command()(start)
app.command()(fix)
app.command()(preview)
app.command()(index)
app.command()(cleanup)
app.command()(sessions)
app.command()(repos)
app.command()(context)
app.command()(search)
app.command()(history)
app.command()(persona)
app.command()(shell)
app.command()(templates)
app.command()(welcome)
app.command()(interactive_mode)

# Configuration commands
app.command()(config_show)
app.command()(config_setup)

if __name__ == "__main__":
    app()
