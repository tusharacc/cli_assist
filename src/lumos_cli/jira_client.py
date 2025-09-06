#!/usr/bin/env python3
"""
Jira client for ticket operations
"""

import json
import os
from typing import Dict, Optional, List
from .debug_logger import debug_logger
from .platform_utils import get_config_directory

class JiraConfigManager:
    """Manages Jira configuration"""
    
    def __init__(self):
        self.config_file = os.path.join(get_config_directory(), "jira_config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load Jira configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                debug_logger.warning(f"Failed to load Jira config: {e}")
        return {}
    
    def save_config(self, config: Dict):
        """Save Jira configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            os.chmod(self.config_file, 0o600)  # Secure permissions
            debug_logger.info("Jira configuration saved")
        except Exception as e:
            debug_logger.error(f"Failed to save Jira config: {e}")
    
    def get_config(self) -> Dict:
        """Get current Jira configuration"""
        return self.config

class JiraTicketBrowser:
    """Browser for Jira tickets"""
    
    def __init__(self, client):
        self.client = client
    
    def browse_tickets(self, query: str = None, limit: int = 10):
        """Browse Jira tickets"""
        debug_logger.log_function_call("JiraTicketBrowser.browse_tickets", 
                                     kwargs={"query": query, "limit": limit})
        
        # Mock implementation - return sample tickets
        mock_tickets = [
            {
                'key': 'PLATFORM-16940',
                'summary': 'Mock ticket for PLATFORM-16940',
                'status': 'In Progress',
                'assignee': 'John Doe',
                'priority': 'High'
            },
            {
                'key': 'PLATFORM-16941',
                'summary': 'Mock ticket for PLATFORM-16941',
                'status': 'Open',
                'assignee': 'Jane Smith',
                'priority': 'Medium'
            }
        ]
        
        if query:
            # Filter by query
            filtered_tickets = [t for t in mock_tickets if query.lower() in t['key'].lower() or query.lower() in t['summary'].lower()]
            return filtered_tickets[:limit]
        
        return mock_tickets[:limit]
    
    def display_ticket_details(self, ticket: Dict):
        """Display detailed ticket information"""
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        
        console = Console()
        
        # Create a detailed ticket display
        table = Table(title=f"Ticket Details: {ticket.get('key', 'Unknown')}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Key", ticket.get('key', 'N/A'))
        table.add_row("Summary", ticket.get('summary', 'N/A'))
        table.add_row("Status", ticket.get('status', 'N/A'))
        table.add_row("Priority", ticket.get('priority', 'N/A'))
        table.add_row("Assignee", ticket.get('assignee', 'N/A'))
        table.add_row("Reporter", ticket.get('reporter', 'N/A'))
        table.add_row("Project", ticket.get('project', 'N/A'))
        table.add_row("Issue Type", ticket.get('issuetype', 'N/A'))
        
        if ticket.get('components'):
            table.add_row("Components", ", ".join(ticket.get('components', [])))
        
        if ticket.get('labels'):
            table.add_row("Labels", ", ".join(ticket.get('labels', [])))
        
        console.print(table)
        
        # Display description if available
        if ticket.get('description'):
            console.print("\n[bold]Description:[/bold]")
            console.print(Panel(ticket.get('description'), title="Description", border_style="blue"))

class JiraClient:
    """Client for Jira ticket operations"""
    
    def __init__(self, base_url: str = None, username: str = None, api_token: str = None):
        self.config_manager = JiraConfigManager()
        config = self.config_manager.get_config()
        
        self.base_url = base_url or config.get('base_url', "https://your-company.atlassian.net")
        self.username = username or config.get('username')
        self.api_token = api_token or config.get('api_token')
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Jira connection"""
        if self.username and self.api_token:
            debug_logger.info(f"Jira client initialized for {self.username} at {self.base_url}")
        else:
            debug_logger.warning("Jira client initialized without credentials (stub mode)")
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Get ticket details from Jira"""
        debug_logger.log_function_call("JiraClient.get_ticket", kwargs={"ticket_id": ticket_id})
        
        # Mock implementation - in real implementation, this would call Jira API
        mock_ticket = {
            'key': ticket_id,
            'summary': f'Mock ticket summary for {ticket_id}',
            'description': f'This is a mock description for ticket {ticket_id}. In a real implementation, this would fetch actual ticket details from Jira API.',
            'status': 'In Progress',
            'assignee': 'John Doe',
            'priority': 'Medium',
            'labels': ['bug', 'frontend'],
            'created': '2025-01-01T10:00:00.000Z',
            'updated': '2025-01-01T15:30:00.000Z',
            'reporter': 'Alice Johnson',
            'project': 'PLATFORM',
            'issuetype': 'Bug',
            'components': ['Frontend', 'Authentication']
        }
        
        debug_logger.log_function_return("JiraClient.get_ticket", f"Retrieved ticket {ticket_id}")
        return mock_ticket
    
    def search_tickets(self, jql: str, max_results: int = 50) -> List[Dict]:
        """Search tickets using JQL"""
        debug_logger.log_function_call("JiraClient.search_tickets", 
                                     kwargs={"jql": jql, "max_results": max_results})
        
        # Mock implementation
        mock_tickets = [
            {
                'key': 'PLATFORM-16940',
                'summary': 'Mock ticket for PLATFORM-16940',
                'status': 'In Progress',
                'assignee': 'John Doe',
                'priority': 'High'
            },
            {
                'key': 'PLATFORM-16941',
                'summary': 'Mock ticket for PLATFORM-16941',
                'status': 'Open',
                'assignee': 'Jane Smith',
                'priority': 'Medium'
            }
        ]
        
        debug_logger.log_function_return("JiraClient.search_tickets", f"Found {len(mock_tickets)} tickets")
        return mock_tickets[:max_results]
    
    def get_ticket_description(self, ticket_id: str) -> str:
        """Get ticket description"""
        ticket = self.get_ticket(ticket_id)
        if ticket:
            return ticket.get('description', 'No description available')
        return f"Ticket {ticket_id} not found"
    
    def get_ticket_details(self, ticket_id: str) -> tuple:
        """Get detailed ticket information (returns success, data, message tuple)"""
        try:
            ticket = self.get_ticket(ticket_id)
            if ticket:
                return True, ticket, f"Retrieved ticket {ticket_id}"
            else:
                return False, None, f"Ticket {ticket_id} not found"
        except Exception as e:
            return False, None, f"Error retrieving ticket {ticket_id}: {str(e)}"
    
    def search_tickets(self, jql: str, max_results: int = 50) -> tuple:
        """Search tickets using JQL (returns success, data, message tuple)"""
        try:
            tickets = self._search_tickets_impl(jql, max_results)
            return True, tickets, f"Found {len(tickets)} tickets"
        except Exception as e:
            return False, [], f"Error searching tickets: {str(e)}"
    
    def _search_tickets_impl(self, jql: str, max_results: int = 50) -> List[Dict]:
        """Internal implementation of search tickets"""
        debug_logger.log_function_call("JiraClient._search_tickets_impl", 
                                     kwargs={"jql": jql, "max_results": max_results})
        
        # Mock implementation
        mock_tickets = [
            {
                'key': 'PLATFORM-16940',
                'summary': 'Mock ticket for PLATFORM-16940',
                'status': 'In Progress',
                'assignee': 'John Doe',
                'priority': 'High'
            },
            {
                'key': 'PLATFORM-16941',
                'summary': 'Mock ticket for PLATFORM-16941',
                'status': 'Open',
                'assignee': 'Jane Smith',
                'priority': 'Medium'
            }
        ]
        
        debug_logger.log_function_return("JiraClient._search_tickets_impl", f"Found {len(mock_tickets)} tickets")
        return mock_tickets[:max_results]
    
    def construct_jql(self, query: str) -> str:
        """Construct JQL from natural language query"""
        # Simple JQL construction - in real implementation, this would be more sophisticated
        if 'description' in query.lower():
            return f"text ~ '{query}' ORDER BY updated DESC"
        elif 'status' in query.lower():
            return f"status in (Open, 'In Progress') ORDER BY updated DESC"
        else:
            return f"text ~ '{query}' ORDER BY updated DESC"

# Global instance
_jira_client = None

def get_jira_client() -> JiraClient:
    """Get or create Jira client instance"""
    global _jira_client
    if _jira_client is None:
        _jira_client = JiraClient()
    return _jira_client