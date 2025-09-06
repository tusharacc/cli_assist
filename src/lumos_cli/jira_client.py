#!/usr/bin/env python3
"""
Jira client for ticket operations
"""

import json
import os
import requests
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
    
    def load_config(self) -> Dict:
        """Load Jira configuration from file (public method)"""
        return self._load_config()
    
    def get_config(self) -> Dict:
        """Get current Jira configuration"""
        return self.config
    
    def setup_interactive(self) -> Optional[Dict]:
        """Interactive Jira configuration setup"""
        from rich.console import Console
        from rich.prompt import Prompt
        
        console = Console()
        console.print("🔧 Jira Configuration Setup", style="bold blue")
        console.print("=" * 40)
        
        console.print("📝 [dim]To get your Jira API token:[/dim]")
        console.print("   1. Go to Jira → Profile → Personal Access Tokens")
        console.print("   2. Click 'Create API token'")
        console.print("   3. Give it a label and copy the generated token")
        console.print("   4. Or use your password for basic auth")
        console.print()
        
        base_url = Prompt.ask("Jira Base URL", default="https://your-company.atlassian.net")
        username = Prompt.ask("Jira Username/Email")
        console.print("🔑 [dim]Your input will be hidden for security.[/dim]")
        api_token = Prompt.ask("API Token or Password", password=True)
        
        config = {
            'base_url': base_url.rstrip('/'),
            'username': username,
            'api_token': api_token
        }
        
        # Test connection
        try:
            console.print("🔍 Testing Jira connection...")
            
            # Test the connection with a real API call
            import requests
            auth = (username, api_token)
            headers = {'Accept': 'application/json'}
            response = requests.get(f"{base_url}/rest/api/3/myself", auth=auth, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Save the config only if connection is successful
                self.save_config(config)
                
                console.print("✅ Jira configured successfully!")
                console.print(f"   Base URL: {base_url}")
                console.print(f"   Username: {username}")
                
                return config
            else:
                console.print(f"❌ Jira connection failed: HTTP {response.status_code}")
                console.print(f"   Response: {response.text}")
                console.print("Please check your credentials and try again")
                return None
            
        except Exception as e:
            console.print(f"❌ Jira connection failed: {e}")
            console.print("Please check your credentials and try again")
            return None

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
        
        if not self.username or not self.api_token:
            debug_logger.warning("Jira credentials not configured, returning mock data")
            return self._get_mock_ticket(ticket_id)
        
        try:
            # Make real API call to Jira
            url = f"{self.base_url}/rest/api/3/issue/{ticket_id}"
            auth = (self.username, self.api_token)
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            debug_logger.info(f"Making Jira API call to: {url}")
            response = requests.get(url, auth=auth, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                ticket = self._parse_jira_ticket(data)
                debug_logger.log_function_return("JiraClient.get_ticket", f"Retrieved real ticket {ticket_id}")
                return ticket
            elif response.status_code == 404:
                debug_logger.warning(f"Ticket {ticket_id} not found")
                return None
            else:
                debug_logger.error(f"Jira API error: {response.status_code} - {response.text}")
                return self._get_mock_ticket(ticket_id)
                
        except Exception as e:
            debug_logger.error(f"Error calling Jira API: {e}")
            return self._get_mock_ticket(ticket_id)
    
    def _get_mock_ticket(self, ticket_id: str) -> Dict:
        """Get mock ticket data as fallback"""
        return {
            'key': ticket_id,
            'summary': f'Mock ticket summary for {ticket_id}',
            'description': f'This is a mock description for ticket {ticket_id}. Jira API call failed or credentials not configured.',
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
    
    def _parse_jira_ticket(self, data: Dict) -> Dict:
        """Parse Jira API response into our ticket format"""
        fields = data.get('fields', {})
        
        # Extract assignee info
        assignee = fields.get('assignee', {})
        assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
        
        # Extract reporter info
        reporter = fields.get('reporter', {})
        reporter_name = reporter.get('displayName', 'Unknown') if reporter else 'Unknown'
        
        # Extract status info
        status = fields.get('status', {})
        status_name = status.get('name', 'Unknown') if status else 'Unknown'
        
        # Extract priority info
        priority = fields.get('priority', {})
        priority_name = priority.get('name', 'Medium') if priority else 'Medium'
        
        # Extract issue type
        issue_type = fields.get('issuetype', {})
        issue_type_name = issue_type.get('name', 'Task') if issue_type else 'Task'
        
        # Extract project info
        project = fields.get('project', {})
        project_key = project.get('key', 'UNKNOWN') if project else 'UNKNOWN'
        
        # Extract components
        components = fields.get('components', [])
        component_names = [comp.get('name', '') for comp in components if comp.get('name')]
        
        # Extract labels
        labels = fields.get('labels', [])
        
        return {
            'key': data.get('key', ''),
            'summary': fields.get('summary', 'No summary'),
            'description': fields.get('description', 'No description available'),
            'status': status_name,
            'assignee': assignee_name,
            'priority': priority_name,
            'labels': labels,
            'created': fields.get('created', ''),
            'updated': fields.get('updated', ''),
            'reporter': reporter_name,
            'project': project_key,
            'issuetype': issue_type_name,
            'components': component_names
        }
    
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
        
        if not self.username or not self.api_token:
            debug_logger.warning("Jira credentials not configured, returning mock data")
            return self._get_mock_search_results()
        
        try:
            # Make real API call to Jira
            url = f"{self.base_url}/rest/api/3/search"
            auth = (self.username, self.api_token)
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'jql': jql,
                'maxResults': max_results,
                'fields': ['key', 'summary', 'status', 'assignee', 'priority', 'reporter', 'created', 'updated']
            }
            
            debug_logger.info(f"Making Jira search API call with JQL: {jql}")
            response = requests.post(url, auth=auth, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get('issues', [])
                tickets = []
                
                for issue in issues:
                    ticket = self._parse_jira_ticket(issue)
                    tickets.append(ticket)
                
                debug_logger.log_function_return("JiraClient._search_tickets_impl", f"Found {len(tickets)} real tickets")
                return tickets
            else:
                debug_logger.error(f"Jira search API error: {response.status_code} - {response.text}")
                return self._get_mock_search_results()
                
        except Exception as e:
            debug_logger.error(f"Error calling Jira search API: {e}")
            return self._get_mock_search_results()
    
    def _get_mock_search_results(self) -> List[Dict]:
        """Get mock search results as fallback"""
        return [
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