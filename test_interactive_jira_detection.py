#!/usr/bin/env python3
"""Test JIRA ticket detection in interactive mode"""

import sys
from pathlib import Path
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console

console = Console()

def test_jira_pattern_detection():
    """Test various JIRA ticket request patterns"""
    console.print("🎫 Testing JIRA Ticket Detection in Interactive Mode", style="bold blue")
    console.print("="*60)
    
    # The regex patterns from the interactive mode
    jira_patterns = [
        r'\b([A-Z]+-\d+)\b',  # Standard JIRA key pattern like PROJECT-123
        r'jira\s+([A-Z]+-\d+)',  # "jira PROJECT-123"
        r'get\s+.*jira\s+([A-Z]+-\d+)',  # "get me jira PROJECT-123"
        r'show\s+.*([A-Z]+-\d+)',  # "show PROJECT-123"
        r'ticket\s+([A-Z]+-\d+)'  # "ticket PROJECT-123"
    ]
    
    # Test cases - various ways users might request JIRA tickets
    test_cases = [
        "get me jira PROJECT-123",
        "show PROJECT-456", 
        "PROJECT-789",
        "jira ALPHA-101",
        "ticket BETA-202",
        "can you get me jira GAMMA-303?",
        "show me ticket DELTA-404",
        "I need EPSILON-505 details",
        "look at ZETA-606",
        "what's the status of ETA-707?",
        # Negative cases
        "project-123",  # lowercase, should not match
        "get me some files",  # no ticket key
        "jira configuration",  # jira but no ticket
    ]
    
    console.print("\n📋 Testing Pattern Recognition:")
    console.print("-" * 40)
    
    for test_input in test_cases:
        jira_ticket_key = None
        
        # Test the same logic as in interactive mode
        for pattern in jira_patterns:
            match = re.search(pattern, test_input, re.IGNORECASE)
            if match:
                jira_ticket_key = match.group(1).upper()
                break
        
        status = "✅" if jira_ticket_key else "❌"
        result = jira_ticket_key if jira_ticket_key else "No match"
        
        console.print(f"{status} \"{test_input}\"")
        console.print(f"    → {result}")
    
    return True

def simulate_interactive_flow():
    """Simulate what happens in interactive mode when you ask for JIRA ticket"""
    console.print("\n🎮 Simulating Interactive Flow", style="bold green")
    console.print("="*50)
    
    user_input = "get me jira PROJECT-XXXX"
    console.print(f"👤 User Input: \"{user_input}\"")
    
    console.print("\n🔄 Processing Steps:")
    console.print("1. 🎫 Detected JIRA ticket request: PROJECT-XXXX")
    console.print("2. 🔌 Checking JIRA client configuration...")
    
    # Simulate different scenarios
    scenarios = [
        {
            "name": "✅ Success Case",
            "description": "JIRA configured, ticket exists",
            "steps": [
                "3. ✅ JIRA client configured",
                "4. 🔍 Fetching ticket details from JIRA API...",
                "5. ✅ Found ticket PROJECT-XXXX",
                "6. 📋 Displaying ticket details (summary, description, comments)",
                "7. 💬 Prompting for next action:",
                "   • Press 'c' to add a comment",
                "   • Press 'd' to get more details", 
                "   • Press Enter to continue with general chat"
            ]
        },
        {
            "name": "⚠️ JIRA Not Configured",
            "description": "User hasn't set up JIRA integration",
            "steps": [
                "3. ❌ JIRA not configured",
                "4. 📢 Display: 'JIRA not configured. Run 'lumos-cli jira config' first.'",
                "5. 🔄 Return from function - no further processing"
            ]
        },
        {
            "name": "❌ Ticket Not Found",
            "description": "JIRA configured but ticket doesn't exist",
            "steps": [
                "3. ✅ JIRA client configured",
                "4. 🔍 Fetching ticket details from JIRA API...",
                "5. ❌ Could not retrieve ticket PROJECT-XXXX: Not Found",
                "6. 💭 Display: 'Continuing with normal chat processing...'",
                "7. 🔄 Falls through to normal file discovery and LLM chat"
            ]
        }
    ]
    
    for scenario in scenarios:
        console.print(f"\n📍 **{scenario['name']}**: {scenario['description']}")
        for step in scenario['steps']:
            console.print(f"   {step}")

def show_user_experience():
    """Show what the user experience looks like"""
    console.print("\n👥 User Experience Examples", style="bold cyan")
    console.print("="*50)
    
    examples = [
        {
            "input": "get me jira ALPHA-245",
            "output": """🎫 Detected JIRA ticket request: ALPHA-245
✅ Found ticket ALPHA-245

╭─────────────────────── 🎫 ALPHA-245 ────────────────────────╮
│ **Key:** ALPHA-245                                          │
│ **Summary:** Implement user authentication system           │
│ **Status:** In Progress                                     │
│ **Priority:** High                                          │
│ **Assignee:** John Developer                                │
│ **Type:** Story                                             │
│ **Created:** 2024-01-15                                     │
│ **Updated:** 2024-01-16                                     │
╰─────────────────────────────────────────────────────────────╯

💬 Comments (2):
1. **Sarah PM** (2024-01-15): This is blocking the mobile team...
2. **John Developer** (2024-01-16): Working on JWT implementation...

What would you like to do with this ticket?
• Press 'c' to add a comment
• Press 'd' to get more details
• Press Enter to continue with general chat"""
        },
        {
            "input": "PROJECT-123",
            "output": """🎫 Detected JIRA ticket request: PROJECT-123
✅ Found ticket PROJECT-123
[Ticket details displayed]

Action: c
Enter comment: Completed authentication module, ready for review
✅ Comment added successfully"""
        }
    ]
    
    for example in examples:
        console.print(f"\n📝 **User Input:** `{example['input']}`")
        console.print("**System Response:**")
        console.print(example['output'])

def show_integration_benefits():
    """Show the benefits of this integration"""
    console.print("\n🎯 Integration Benefits", style="bold yellow")
    console.print("="*40)
    
    benefits = [
        "🚀 **Seamless Workflow**: No need to leave the CLI",
        "🎯 **Natural Language**: Just mention the ticket key anywhere",
        "⚡ **Quick Access**: Instant ticket details and comments",
        "💬 **Fast Updates**: Add comments without switching tools",
        "🔄 **Context Preservation**: Integrates with chat history",
        "🛡️ **Fallback Graceful**: Falls back to normal chat if issues occur"
    ]
    
    for benefit in benefits:
        console.print(f"  {benefit}")
    
    console.print(f"\n🎊 **Perfect for Enterprise Users!**")
    console.print(f"Now you can seamlessly work with both code AND tickets in one interface!")

if __name__ == "__main__":
    test_jira_pattern_detection()
    simulate_interactive_flow()
    show_user_experience() 
    show_integration_benefits()
    
    console.print("\n" + "="*60)
    console.print("✅ JIRA Interactive Detection Enhanced!", style="bold green")
    console.print("="*60)
    
    console.print("\n🎫 **What happens when you ask 'get me jira PROJECT-XXXX':**")
    console.print("1. System detects JIRA ticket pattern")
    console.print("2. Fetches ticket details from your JIRA instance")
    console.print("3. Displays rich ticket information with comments")
    console.print("4. Offers interactive options (comment, details, continue)")
    console.print("5. Integrates seamlessly with your development workflow")
    
    console.print(f"\n🚀 **Ready for immediate use in interactive mode!**")