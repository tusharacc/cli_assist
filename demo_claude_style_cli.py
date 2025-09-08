#!/usr/bin/env python3
"""
Demo of the Claude-style CLI with intent shortcuts
This shows how the new input prompt looks and behaves
"""

import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lumos_cli.ui.input_prompt import show_intent_hint
from lumos_cli.ui.console import console, create_header

def demo_claude_style_cli():
    """Demo the Claude-style CLI interface"""
    
    # Show header
    create_header(console, "Lumos CLI", "Interactive AI Assistant with Intent Shortcuts")
    
    console.print("[bold green]🎉 New Feature: Claude-style Intent Shortcuts![/bold green]\n")
    
    console.print("The CLI now displays available intents below the input prompt, similar to Claude CLI's '? for help'.\n")
    
    # Show what it looks like
    console.print("[bold]Here's how the new input prompt appears:[/bold]\n")
    
    # Simulate the interactive session
    for i in range(3):
        console.print(f"[dim]--- Example input #{i+1} ---[/dim]")
        show_intent_hint()
        
        example_commands = [
            "🤖 You: /github show me latest PRs from microsoft/vscode",
            "🤖 You: /jenkins get me failed builds in the last hour", 
            "🤖 You: /code generate a REST API for user management"
        ]
        
        console.print(example_commands[i])
        console.print("[green]✓ Intent detected and processed[/green]\n")
        time.sleep(0.5)
    
    console.print("[bold]Available intent shortcuts:[/bold]")
    console.print("• [cyan]/code[/cyan] - Code operations (generate, edit, review, test)")
    console.print("• [green]/github[/green] - Repository management (PRs, commits, clone)")  
    console.print("• [blue]/jenkins[/blue] - CI/CD operations (builds, jobs, status)")
    console.print("• [yellow]/jira[/yellow] - Project management (tickets, issues)")
    console.print("• [magenta]/neo4j[/magenta] - Graph database (dependencies, impact)")
    console.print("• [red]/appdynamics[/red] - Monitoring (resources, alerts)")
    
    console.print("\n[bold blue]💡 Benefits of this approach:[/bold blue]")
    console.print("✅ Always visible intent shortcuts")
    console.print("✅ Similar UX to Claude CLI") 
    console.print("✅ Reduced cognitive load - no need to remember commands")
    console.print("✅ Color-coded intents for easy recognition")
    console.print("✅ Compact display doesn't clutter the interface")
    
    console.print(f"\n[green]🚀 Ready to use! Run `lumos-cli` to try it out.[/green]")

if __name__ == "__main__":
    demo_claude_style_cli()