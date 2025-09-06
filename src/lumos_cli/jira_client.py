#!/usr/bin/env python3
"""JIRA integration for Lumos CLI - Enterprise workflow support"""

import json
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich.markdown import Markdown
import os
from datetime import datetime

console = Console()

@dataclass
class JiraTicket:
    """Represents a JIRA ticket with essential information"""
    key: str
    summary: str
    status: str
    assignee: str
    priority: str
    issue_type: str
    created: str
    updated: str
    description: str = ""
    comments: List[Dict] = None
    
    def __post_init__(self):
        if self.comments is None:
            self.comments = []

@dataclass
class JiraConfig:
    """JIRA configuration settings"""
    base_url: str
    username: str
    token: str
    default_project: str = ""

class JiraClient:
    """Enhanced JIRA client for enterprise workflows"""
    
    def __init__(self, config: Optional[JiraConfig] = None):
        self.config = config
        self.session = requests.Session()
        
        if config:
            self._setup_session()
    
    def _setup_session(self):
        """Setup authenticated session with JIRA"""
        self.session.headers.update({
            'Authorization': f'Bearer {self.config.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test JIRA connection and authentication"""
        try:
            response = self.session.get(f"{self.config.base_url}/rest/api/2/myself")
            
            if response.status_code == 200:
                user_info = response.json()
                return True, f"✅ Connected as {user_info.get('displayName', 'Unknown')}"
            else:
                return False, f"❌ Authentication failed: {response.status_code}"
                
        except requests.RequestException as e:
            return False, f"❌ Connection failed: {str(e)}"
    
    def construct_jql(self, query_text: str) -> str:
        """
        Construct JQL from natural language using intelligent parsing
        
        Common patterns:
        - "tickets assigned to me" -> "assignee = currentUser()"
        - "current sprint" -> "sprint in openSprints()"
        - "open tickets" -> "status not in (Done, Closed, Resolved)"
        """
        query_lower = query_text.lower()
        jql_parts = []
        
        # Assignee detection
        if any(phrase in query_lower for phrase in ["assigned to me", "my tickets", "mine"]):
            jql_parts.append("assignee = currentUser()")
        
        # Sprint detection
        if any(phrase in query_lower for phrase in ["current sprint", "open sprint", "active sprint"]):
            jql_parts.append("sprint in openSprints()")
        
        # Status detection
        if any(phrase in query_lower for phrase in ["open", "active", "in progress"]):
            jql_parts.append("status not in (Done, Closed, Resolved)")
        elif "todo" in query_lower or "to do" in query_lower:
            jql_parts.append("status = 'To Do'")
        elif "in progress" in query_lower:
            jql_parts.append("status = 'In Progress'")
        
        # Priority detection
        if "high priority" in query_lower or "urgent" in query_lower:
            jql_parts.append("priority in (High, Highest)")
        
        # Project detection
        if self.config.default_project and "project" not in query_lower:
            jql_parts.append(f"project = {self.config.default_project}")
        
        # Default fallback for common enterprise query
        if not jql_parts and any(phrase in query_lower for phrase in ["my", "tickets", "issues"]):
            jql_parts.extend([
                "assignee = currentUser()",
                "sprint in openSprints()",
                "status not in (Done, Closed, Resolved)"
            ])
        
        jql = " AND ".join(jql_parts) if jql_parts else query_text
        
        # Add default ordering
        if "order by" not in jql.lower():
            jql += " ORDER BY priority DESC, updated DESC"
        
        return jql
    
    def search_tickets(self, jql: str, max_results: int = 50) -> Tuple[bool, List[JiraTicket], str]:
        """Search for tickets using JQL"""
        try:
            url = f"{self.config.base_url}/rest/api/2/search"
            
            params = {
                'jql': jql,
                'maxResults': max_results,
                'fields': 'key,summary,status,assignee,priority,issuetype,created,updated,description'
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                return False, [], f"Search failed: {response.status_code} - {response.text}"
            
            data = response.json()
            tickets = []
            
            for issue in data.get('issues', []):
                fields = issue['fields']
                
                ticket = JiraTicket(
                    key=issue['key'],
                    summary=fields.get('summary', 'No summary'),
                    status=fields.get('status', {}).get('name', 'Unknown'),
                    assignee=fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                    priority=fields.get('priority', {}).get('name', 'None') if fields.get('priority') else 'None',
                    issue_type=fields.get('issuetype', {}).get('name', 'Unknown'),
                    created=fields.get('created', ''),
                    updated=fields.get('updated', ''),
                    description=fields.get('description', '')
                )
                tickets.append(ticket)
            
            return True, tickets, f"Found {len(tickets)} tickets"
            
        except requests.RequestException as e:
            return False, [], f"Request failed: {str(e)}"
    
    def get_ticket_details(self, ticket_key: str) -> Tuple[bool, Optional[JiraTicket], str]:
        """Get detailed information for a specific ticket including comments"""
        try:
            url = f"{self.config.base_url}/rest/api/2/issue/{ticket_key}"
            
            params = {
                'expand': 'comments',
                'fields': 'key,summary,status,assignee,priority,issuetype,created,updated,description,comment'
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code != 200:
                return False, None, f"Failed to get ticket: {response.status_code}"
            
            issue = response.json()
            fields = issue['fields']
            
            # Extract comments
            comments = []
            if 'comment' in fields and 'comments' in fields['comment']:
                for comment in fields['comment']['comments']:
                    comments.append({
                        'author': comment['author']['displayName'],
                        'created': comment['created'],
                        'body': comment['body']
                    })
            
            ticket = JiraTicket(
                key=issue['key'],
                summary=fields.get('summary', 'No summary'),
                status=fields.get('status', {}).get('name', 'Unknown'),
                assignee=fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                priority=fields.get('priority', {}).get('name', 'None') if fields.get('priority') else 'None',
                issue_type=fields.get('issuetype', {}).get('name', 'Unknown'),
                created=fields.get('created', ''),
                updated=fields.get('updated', ''),
                description=fields.get('description', ''),
                comments=comments
            )
            
            return True, ticket, "Success"
            
        except requests.RequestException as e:
            return False, None, f"Request failed: {str(e)}"
    
    def add_comment(self, ticket_key: str, comment: str) -> Tuple[bool, str]:
        """Add a comment to a JIRA ticket"""
        try:
            url = f"{self.config.base_url}/rest/api/2/issue/{ticket_key}/comment"
            
            payload = {
                'body': comment
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 201:
                return True, "✅ Comment added successfully"
            else:
                return False, f"❌ Failed to add comment: {response.status_code} - {response.text}"
                
        except requests.RequestException as e:
            return False, f"❌ Request failed: {str(e)}"

class JiraTicketBrowser:
    """Interactive ticket browser with scrolling and selection"""
    
    def __init__(self, jira_client: JiraClient):
        self.client = jira_client
        self.current_tickets = []
        self.selected_index = 0
    
    def display_tickets_table(self, tickets: List[JiraTicket], highlight_index: int = -1):
        """Display tickets in a formatted table"""
        if not tickets:
            console.print("[yellow]No tickets found[/yellow]")
            return
        
        table = Table(title="🎫 JIRA Tickets")
        table.add_column("#", style="dim", width=3)
        table.add_column("Key", style="cyan", width=12)
        table.add_column("Summary", style="white", width=50)
        table.add_column("Status", style="green", width=12)
        table.add_column("Priority", style="red", width=10)
        table.add_column("Updated", style="dim", width=12)
        
        for i, ticket in enumerate(tickets):
            style = "bold yellow" if i == highlight_index else None
            
            # Format date
            updated = ticket.updated[:10] if ticket.updated else "Unknown"
            
            # Truncate long summaries
            summary = ticket.summary[:47] + "..." if len(ticket.summary) > 50 else ticket.summary
            
            table.add_row(
                str(i + 1),
                ticket.key,
                summary,
                ticket.status,
                ticket.priority,
                updated,
                style=style
            )
        
        console.print(table)
    
    def browse_tickets(self, tickets: List[JiraTicket]) -> Optional[JiraTicket]:
        """Interactive ticket browser with keyboard navigation"""
        if not tickets:
            console.print("[yellow]No tickets to browse[/yellow]")
            return None
        
        self.current_tickets = tickets
        current_page = 0
        page_size = 10
        
        while True:
            console.clear()
            
            # Calculate pagination
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(tickets))
            page_tickets = tickets[start_idx:end_idx]
            
            console.print(f"📋 Tickets {start_idx + 1}-{end_idx} of {len(tickets)}")
            self.display_tickets_table(page_tickets)
            
            console.print("\n[dim]Navigation:[/dim]")
            console.print("[dim]• Enter ticket number (1-{}) to select[/dim]".format(len(page_tickets)))
            console.print("[dim]• 'n' for next page, 'p' for previous page[/dim]")
            console.print("[dim]• 'q' to quit[/dim]")
            
            choice = Prompt.ask("Select action").lower().strip()
            
            if choice == 'q':
                return None
            elif choice == 'n':
                if end_idx < len(tickets):
                    current_page += 1
                else:
                    console.print("[yellow]Already on last page[/yellow]")
                    console.input("Press Enter to continue...")
            elif choice == 'p':
                if current_page > 0:
                    current_page -= 1
                else:
                    console.print("[yellow]Already on first page[/yellow]")
                    console.input("Press Enter to continue...")
            else:
                try:
                    ticket_num = int(choice)
                    if 1 <= ticket_num <= len(page_tickets):
                        selected_ticket = page_tickets[ticket_num - 1]
                        return selected_ticket
                    else:
                        console.print(f"[red]Invalid number. Enter 1-{len(page_tickets)}[/red]")
                        console.input("Press Enter to continue...")
                except ValueError:
                    console.print("[red]Invalid input. Enter a number, 'n', 'p', or 'q'[/red]")
                    console.input("Press Enter to continue...")
    
    def display_ticket_details(self, ticket: JiraTicket):
        """Display detailed ticket information"""
        console.clear()
        
        # Main ticket info panel
        ticket_info = f"""
**Key:** {ticket.key}
**Summary:** {ticket.summary}
**Status:** {ticket.status}
**Priority:** {ticket.priority}
**Assignee:** {ticket.assignee}
**Type:** {ticket.issue_type}
**Created:** {ticket.created[:10] if ticket.created else 'Unknown'}
**Updated:** {ticket.updated[:10] if ticket.updated else 'Unknown'}
        """
        
        panel = Panel(
            Markdown(ticket_info),
            title=f"🎫 {ticket.key}",
            border_style="blue"
        )
        console.print(panel)
        
        # Description
        if ticket.description:
            desc_panel = Panel(
                Text(ticket.description[:500] + "..." if len(ticket.description) > 500 else ticket.description),
                title="📝 Description",
                border_style="green"
            )
            console.print(desc_panel)
        
        # Comments
        if ticket.comments:
            console.print(f"\n💬 Comments ({len(ticket.comments)}):")
            for i, comment in enumerate(ticket.comments[-5:], 1):  # Show last 5 comments
                comment_text = f"**{comment['author']}** ({comment['created'][:10]})\n{comment['body'][:200]}..."
                comment_panel = Panel(
                    Markdown(comment_text),
                    title=f"Comment {i}",
                    border_style="yellow"
                )
                console.print(comment_panel)

class JiraConfigManager:
    """Manages JIRA configuration settings"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.expanduser("~/.lumos_jira_config.json")
    
    def load_config(self) -> Optional[JiraConfig]:
        """Load JIRA configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return JiraConfig(**data)
            return None
        except Exception as e:
            console.print(f"[red]Error loading config: {e}[/red]")
            return None
    
    def save_config(self, config: JiraConfig) -> bool:
        """Save JIRA configuration to file"""
        try:
            data = {
                'base_url': config.base_url,
                'username': config.username,
                'token': config.token,
                'default_project': config.default_project
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Set secure permissions
            os.chmod(self.config_file, 0o600)
            return True
            
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
            return False
    
    def setup_interactive(self) -> Optional[JiraConfig]:
        """Interactive JIRA configuration setup"""
        console.print("🔧 JIRA Configuration Setup", style="bold blue")
        console.print("=" * 40)
        
        base_url = Prompt.ask("JIRA Base URL (e.g., https://company.atlassian.net)")
        username = Prompt.ask("Username/Email")
        console.print("🔑 [dim]Your input will be hidden for security.[/dim]")
        token = Prompt.ask("Personal Access Token", password=True)
        default_project = Prompt.ask("Default Project Key (optional)", default="")
        
        config = JiraConfig(
            base_url=base_url.rstrip('/'),
            username=username,
            token=token,
            default_project=default_project
        )
        
        # Test connection
        client = JiraClient(config)
        success, message = client.test_connection()
        
        if success:
            console.print(message)
            if self.save_config(config):
                console.print("✅ Configuration saved successfully")
                return config
            else:
                console.print("❌ Failed to save configuration")
        else:
            console.print(message)
            
        return None

# Global instances
_config_manager = JiraConfigManager()
_jira_client: Optional[JiraClient] = None

def get_jira_client() -> Optional[JiraClient]:
    """Get configured JIRA client"""
    global _jira_client
    
    if _jira_client is None:
        config = _config_manager.load_config()
        if config:
            _jira_client = JiraClient(config)
        else:
            console.print("[yellow]JIRA not configured. Run 'lumos-cli jira config' first.[/yellow]")
    
    return _jira_client