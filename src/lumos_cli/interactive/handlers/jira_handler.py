"""
Jira interactive mode handlers
"""

import re
from rich.console import Console
from ...clients.jira_client import get_jira_client, JiraTicketBrowser
from ...utils.debug_logger import debug_logger

console = Console()

def interactive_jira(query: str):
    """Handle JIRA command in interactive mode"""
    try:
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
