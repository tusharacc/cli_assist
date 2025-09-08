#!/usr/bin/env python3
"""Demo of complete enterprise JIRA workflow with Lumos CLI"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

console = Console()

def show_enterprise_workflow_demo():
    """Show complete enterprise workflow demonstration"""
    
    console.print("🏢 Enterprise JIRA Workflow with Lumos CLI", style="bold blue")
    console.print("="*60)
    
    # Scenario Setup
    console.print("\n📋 **Scenario: Daily Developer Workflow**")
    console.print("You're a developer at TechCorp working on Project ALPHA")
    console.print("Your JIRA instance: https://techcorp.atlassian.net")
    console.print("Current sprint has 8 tickets assigned to you")
    
    # Step 1: Configuration
    console.print("\n" + "="*50)
    console.print("🔧 **STEP 1: One-Time Setup**")
    console.print("="*50)
    
    setup_panel = Panel(
        Markdown("""
**Command:** `lumos-cli jira config`

**Interactive Setup:**
```
JIRA Base URL: https://techcorp.atlassian.net
Username/Email: john.developer@techcorp.com
Personal Access Token: [secure input]
Default Project Key: ALPHA
```

**Result:** ✅ Configuration saved securely to ~/.lumos_jira_config.json (600 permissions)
        """),
        title="🔧 Configuration",
        border_style="blue"
    )
    console.print(setup_panel)
    
    # Step 2: Daily Workflow Start
    console.print("\n" + "="*50) 
    console.print("📅 **STEP 2: Start Your Work Day**")
    console.print("="*50)
    
    workflow_panel = Panel(
        Markdown("""
**Command:** `lumos-cli jira browse`

**Natural Language Processing:**
- Input: "my tickets in current sprint" (default query)
- Converts to JQL: `assignee = currentUser() AND sprint in openSprints() AND status not in (Done, Closed, Resolved) ORDER BY priority DESC, updated DESC`
- Fetches tickets from JIRA API
        """),
        title="🔍 Intelligent Query Construction",
        border_style="green"
    )
    console.print(workflow_panel)
    
    # Step 3: Ticket Browser
    console.print("\n" + "="*50)
    console.print("🎫 **STEP 3: Interactive Ticket Browsing**") 
    console.print("="*50)
    
    # Mock ticket table
    table = Table(title="📋 Your Current Sprint Tickets")
    table.add_column("#", style="dim", width=3)
    table.add_column("Key", style="cyan", width=12)
    table.add_column("Summary", style="white", width=40)
    table.add_column("Status", style="green", width=12)
    table.add_column("Priority", style="red", width=8)
    
    tickets_data = [
        ("1", "ALPHA-245", "Implement user authentication system", "In Progress", "High"),
        ("2", "ALPHA-246", "Fix database connection timeout", "To Do", "High"),
        ("3", "ALPHA-247", "Add logging to payment module", "To Do", "Medium"),
        ("4", "ALPHA-248", "Update API documentation", "To Do", "Low"),
        ("5", "ALPHA-249", "Refactor legacy code in utils", "To Do", "Medium")
    ]
    
    for row in tickets_data:
        style = "bold yellow" if row[0] == "1" else None
        table.add_row(*row, style=style)
    
    console.print(table)
    console.print("\n[dim]Navigation: Enter ticket number to select, 'n' for next page, 'q' to quit[/dim]")
    
    # Step 4: Ticket Details
    console.print("\n" + "="*50)
    console.print("📖 **STEP 4: Ticket Details & Context**")
    console.print("="*50)
    
    ticket_detail = Panel(
        Markdown("""
**🎫 ALPHA-245: Implement user authentication system**

**Status:** In Progress  
**Priority:** High  
**Assignee:** John Developer  
**Type:** Story  
**Created:** 2024-01-15  
**Updated:** 2024-01-16  

**📝 Description:**
Need to implement secure user authentication with JWT tokens. Should include:
- Login/logout endpoints
- JWT token generation and validation  
- Password hashing with bcrypt
- Session management

**💬 Recent Comments (2):**
1. **Sarah PM** (2024-01-15): "This is blocking the mobile team, please prioritize"
2. **John Developer** (2024-01-16): "Working on JWT implementation, 70% complete"
        """),
        title="🎫 Selected Ticket Details",
        border_style="cyan"
    )
    console.print(ticket_detail)
    
    # Step 5: Development Work
    console.print("\n" + "="*50)
    console.print("💻 **STEP 5: Development Work (Using Lumos CLI)**")
    console.print("="*50)
    
    dev_work = Panel(
        Markdown("""
**Development Commands:**
```bash
# Use Lumos CLI for code assistance
lumos-cli edit "implement JWT authentication in auth.py"
lumos-cli review "check security of password hashing"
lumos-cli fix "fix failing authentication tests"
```

**Code Changes Made:**
- ✅ Implemented JWT token generation
- ✅ Added password hashing with bcrypt  
- ✅ Created login/logout endpoints
- ✅ Added comprehensive tests
        """),
        title="💻 Development Work",
        border_style="green"
    )
    console.print(dev_work)
    
    # Step 6: Progress Update
    console.print("\n" + "="*50)
    console.print("💬 **STEP 6: Update Progress in JIRA**")
    console.print("="*50)
    
    comment_panel = Panel(
        Markdown("""
**Command:** 
```bash
lumos-cli jira comment ALPHA-245 -c "Completed JWT authentication implementation. All tests passing. Ready for code review."
```

**Result:** ✅ Comment added successfully

**Alternative - Interactive Mode:**
```bash
lumos-cli jira browse
# Select ticket → Press 'c' → Enter comment
```
        """),
        title="💬 Progress Updates",
        border_style="yellow"
    )
    console.print(comment_panel)
    
    # Step 7: Advanced Queries
    console.print("\n" + "="*50)
    console.print("🔍 **STEP 7: Advanced Search & Filtering**")
    console.print("="*50)
    
    search_examples = Table(title="🔍 Natural Language → JQL Examples")
    search_examples.add_column("Natural Language", style="cyan", width=30)
    search_examples.add_column("Generated JQL", style="green", width=50)
    
    search_data = [
        ("my high priority tickets", "assignee = currentUser() AND priority in (High, Highest)"),
        ("bugs assigned to me", "assignee = currentUser() AND issuetype = Bug"),
        ("tickets updated today", "assignee = currentUser() AND updated >= startOfDay()"),
        ("blocked tickets", "assignee = currentUser() AND status = Blocked")
    ]
    
    for query, jql in search_data:
        search_examples.add_row(query, jql[:47] + "..." if len(jql) > 50 else jql)
    
    console.print(search_examples)
    
    # Benefits Summary
    console.print("\n" + "="*60)
    console.print("✅ **Enterprise Benefits Achieved**")
    console.print("="*60)
    
    benefits = [
        "🔒 **Security**: Personal Access Token auth, secure local storage",
        "⚡ **Efficiency**: Natural language queries, no manual JQL writing", 
        "🎯 **Focus**: Quick access to 'my tickets in current sprint'",
        "📱 **Integration**: Seamless with existing Lumos CLI workflow",
        "🗂️ **Organization**: Paginated browsing, rich ticket details",
        "💬 **Communication**: Quick comment updates without leaving CLI",
        "🔄 **Workflow**: Perfect for sprint-based development cycles"
    ]
    
    for benefit in benefits:
        console.print(f"  {benefit}")
    
    # Final Commands Summary
    console.print("\n" + "="*40)
    console.print("🚀 **Daily Commands Summary**")
    console.print("="*40)
    
    commands_table = Table(title="📱 Essential JIRA Commands")
    commands_table.add_column("Command", style="cyan", width=35)
    commands_table.add_column("Purpose", style="white", width=25)
    
    commands = [
        ("lumos-cli jira browse", "Daily ticket browsing"),
        ("lumos-cli jira search -q 'high priority'", "Filtered ticket search"),
        ("lumos-cli jira comment ABC-123 -c 'Done'", "Quick progress updates"),
        ("lumos-cli jira config", "Setup/reconfigure")
    ]
    
    for cmd, purpose in commands:
        commands_table.add_row(cmd, purpose)
    
    console.print(commands_table)
    
    console.print(f"\n🎯 **Perfect for your use case:**")
    console.print(f"   'Get list of all tickets assigned to me in current open sprint'")
    console.print(f"\n✨ **Ready for immediate enterprise deployment!**")

if __name__ == "__main__":
    show_enterprise_workflow_demo()