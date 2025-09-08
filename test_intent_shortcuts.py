#!/usr/bin/env python3
"""
Test script for the new intent shortcuts feature
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lumos_cli.ui.input_prompt import (
    show_intent_shortcuts, 
    show_intent_hint,
    create_input_panel_with_shortcuts,
    display_claude_style_prompt
)
from lumos_cli.ui.console import console

def test_intent_shortcuts():
    """Test the intent shortcuts display"""
    console.print("[bold blue]🧪 Testing Intent Shortcuts Display[/bold blue]\n")
    
    # Test 1: Compact shortcuts
    console.print("[bold]1. Compact shortcuts:[/bold]")
    show_intent_shortcuts(compact=True)
    
    console.print("\n" + "="*50 + "\n")
    
    # Test 2: Detailed shortcuts  
    console.print("[bold]2. Detailed shortcuts:[/bold]")
    show_intent_shortcuts(compact=False)
    
    console.print("\n" + "="*50 + "\n")
    
    # Test 3: Claude-style hint
    console.print("[bold]3. Claude-style hint:[/bold]")
    show_intent_hint()
    
    console.print("\n" + "="*50 + "\n")
    
    # Test 4: Input panel with shortcuts
    console.print("[bold]4. Input panel with shortcuts:[/bold]")
    create_input_panel_with_shortcuts()
    
    console.print("\n" + "="*50 + "\n")
    
    # Test 5: Simulate the actual input prompt (without waiting for input)
    console.print("[bold]5. Simulated prompt display:[/bold]")
    console.print("This is how the prompt will look:")
    show_intent_hint()
    console.print("🤖 You: [dim](waiting for input...)[/dim]")
    
    console.print("\n[green]✅ All tests completed successfully![/green]")
    console.print("[yellow]💡 The new input prompt will display intent shortcuts below the input field[/yellow]")
    console.print("[cyan]Available intents: /code /github /jenkins /jira /neo4j /appdynamics[/cyan]")

if __name__ == "__main__":
    test_intent_shortcuts()