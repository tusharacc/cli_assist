"""
GitHub REST API client for repository and pull request operations
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from .debug_logger import get_debug_logger

console = Console()
debug_logger = get_debug_logger()

class GitHubClient:
    """GitHub REST API client for enterprise workflows"""
    
    def __init__(self, token: str = None, base_url: str = None):
        debug_logger.log_function_call("GitHubClient.__init__", kwargs={"token": token, "base_url": base_url})
        
        # Try to get from config manager first, then environment variables
        from .github_config_manager import get_github_config
        config = get_github_config()
        
        if config:
            self.token = token or config.token
            self.base_url = base_url or config.base_url
            debug_logger.info(f"Using config file: base_url={self.base_url}, token={'***' if self.token else 'None'}")
        else:
            self.token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
            self.base_url = (base_url or "https://api.github.com").rstrip("/")
            debug_logger.info(f"Using environment variables: base_url={self.base_url}, token={'***' if self.token else 'None'}")
        
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Lumos-CLI/1.0"
            })
            debug_logger.debug(f"Session headers set: {dict(self.session.headers)}")
        
        debug_logger.log_function_return("GitHubClient.__init__", f"base_url={self.base_url}")
    
    def _get_api_endpoint(self, operation: str, **kwargs) -> str:
        """Construct the correct GitHub API endpoint"""
        debug_logger.log_function_call("GitHubClient._get_api_endpoint", kwargs={"operation": operation, **kwargs})
        
        # For now, use the standard GitHub REST API v3 endpoints
        # This can be enhanced later with LLM-based construction for custom enterprise APIs
        result = self._get_fallback_endpoint(operation, **kwargs)
        debug_logger.log_function_return("GitHubClient._get_api_endpoint", result)
        return result
    
    def _get_fallback_endpoint(self, operation: str, **kwargs) -> str:
        """Fallback to hardcoded endpoints if LLM fails"""
        debug_logger.log_function_call("GitHubClient._get_fallback_endpoint", kwargs={"operation": operation, **kwargs})
        
        if operation == "list_pull_requests":
            org = kwargs.get('org', '')
            repo = kwargs.get('repo', '')
            endpoint = f"/repos/{org}/{repo}/pulls"
            debug_logger.debug(f"Constructed list_pull_requests endpoint: {endpoint}")
            debug_logger.log_function_return("GitHubClient._get_fallback_endpoint", endpoint)
            return endpoint
        elif operation == "get_pull_request":
            org = kwargs.get('org', '')
            repo = kwargs.get('repo', '')
            pr_number = kwargs.get('pr_number', '')
            endpoint = f"/repos/{org}/{repo}/pulls/{pr_number}"
            debug_logger.debug(f"Constructed get_pull_request endpoint: {endpoint}")
            debug_logger.log_function_return("GitHubClient._get_fallback_endpoint", endpoint)
            return endpoint
        elif operation == "get_repository":
            org = kwargs.get('org', '')
            repo = kwargs.get('repo', '')
            endpoint = f"/repos/{org}/{repo}"
            debug_logger.debug(f"Constructed get_repository endpoint: {endpoint}")
            debug_logger.log_function_return("GitHubClient._get_fallback_endpoint", endpoint)
            return endpoint
        elif operation == "get_pull_request_commits":
            org = kwargs.get('org', '')
            repo = kwargs.get('repo', '')
            pr_number = kwargs.get('pr_number', '')
            endpoint = f"/repos/{org}/{repo}/pulls/{pr_number}/commits"
            debug_logger.debug(f"Constructed get_pull_request_commits endpoint: {endpoint}")
            debug_logger.log_function_return("GitHubClient._get_fallback_endpoint", endpoint)
            return endpoint
        elif operation == "get_pull_request_files":
            org = kwargs.get('org', '')
            repo = kwargs.get('repo', '')
            pr_number = kwargs.get('pr_number', '')
            endpoint = f"/repos/{org}/{repo}/pulls/{pr_number}/files"
            debug_logger.debug(f"Constructed get_pull_request_files endpoint: {endpoint}")
            debug_logger.log_function_return("GitHubClient._get_fallback_endpoint", endpoint)
            return endpoint
        else:
            org = kwargs.get('org', '')
            repo = kwargs.get('repo', '')
            endpoint = f"/repos/{org}/{repo}"
            debug_logger.debug(f"Constructed default endpoint: {endpoint}")
            debug_logger.log_function_return("GitHubClient._get_fallback_endpoint", endpoint)
            return endpoint

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to GitHub API"""
        debug_logger.log_function_call("GitHubClient._make_request", kwargs={"endpoint": endpoint, "params": params})
        
        url = f"{self.base_url}{endpoint}"
        debug_logger.log_url_construction(self.base_url, endpoint, params)
        
        try:
            debug_logger.debug(f"Making HTTP GET request to: {url}")
            response = self.session.get(url, params=params)
            debug_logger.debug(f"Response status: {response.status_code}")
            debug_logger.debug(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            result = response.json()
            debug_logger.debug(f"Response JSON keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            debug_logger.log_function_return("GitHubClient._make_request", f"Success: {len(result) if isinstance(result, list) else 'dict'}")
            return result
        except requests.exceptions.RequestException as e:
            debug_logger.error(f"GitHub API Error: {e}")
            console.print(f"[red]GitHub API Error: {e}[/red]")
            debug_logger.log_function_return("GitHubClient._make_request", "Error")
            return {}
    
    def test_connection(self) -> bool:
        """Test GitHub API connection"""
        try:
            response = self._make_request("/user")
            return "login" in response
        except:
            return False
    
    def get_repository_info(self, org: str, repo: str) -> Dict:
        """Get repository information"""
        endpoint = self._get_api_endpoint("get_repository", org=org, repo=repo)
        return self._make_request(endpoint)
    
    def list_pull_requests(self, org: str, repo: str, state: str = "open", 
                          head: str = None, base: str = None) -> List[Dict]:
        """List pull requests for a repository"""
        debug_logger.log_function_call("GitHubClient.list_pull_requests", 
                                     kwargs={"org": org, "repo": repo, "state": state, "head": head, "base": base})
        
        params = {"state": state}
        if head:
            params["head"] = f"{org}:{head}"
            debug_logger.debug(f"Added head parameter: {params['head']}")
        if base:
            params["base"] = base
            debug_logger.debug(f"Added base parameter: {params['base']}")
        
        debug_logger.debug(f"Final params: {params}")
        
        # Use LLM to construct the correct API endpoint
        endpoint = self._get_api_endpoint("list_pull_requests", org=org, repo=repo)
        result = self._make_request(endpoint, params) or []
        debug_logger.log_function_return("GitHubClient.list_pull_requests", f"Found {len(result)} PRs")
        return result
    
    def get_pull_request(self, org: str, repo: str, pr_number: int) -> Dict:
        """Get specific pull request details"""
        endpoint = self._get_api_endpoint("get_pull_request", org=org, repo=repo, pr_number=pr_number)
        return self._make_request(endpoint)
    
    def get_pull_request_commits(self, org: str, repo: str, pr_number: int) -> List[Dict]:
        """Get commits for a pull request"""
        endpoint = self._get_api_endpoint("get_pull_request_commits", org=org, repo=repo, pr_number=pr_number)
        return self._make_request(endpoint) or []
    
    def get_pull_request_files(self, org: str, repo: str, pr_number: int) -> List[Dict]:
        """Get files changed in a pull request"""
        endpoint = self._get_api_endpoint("get_pull_request_files", org=org, repo=repo, pr_number=pr_number)
        return self._make_request(endpoint) or []
    
    def clone_repository(self, org: str, repo: str, branch: str = None, 
                        target_dir: str = None) -> Tuple[bool, str]:
        """Clone repository and return success status and path"""
        try:
            # Construct clone URL
            if self.token:
                clone_url = f"https://{self.token}@github.com/{org}/{repo}.git"
            else:
                clone_url = f"https://github.com/{org}/{repo}.git"
            
            # Determine target directory
            if not target_dir:
                target_dir = os.path.join(os.getcwd(), repo)
            
            # Clone command
            cmd = ["git", "clone"]
            if branch:
                cmd.extend(["-b", branch])
            cmd.extend([clone_url, target_dir])
            
            # Execute clone
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                return True, target_dir
            else:
                console.print(f"[red]Clone failed: {result.stderr}[/red]")
                return False, ""
                
        except Exception as e:
            console.print(f"[red]Clone error: {e}[/red]")
            return False, ""
    
    def format_pr_summary(self, pr: Dict, commits: List[Dict] = None, 
                         files: List[Dict] = None) -> str:
        """Format pull request summary"""
        summary = f"""
[bold]PR #{pr['number']}: {pr['title']}[/bold]
[dim]Author: {pr['user']['login']} | State: {pr['state']} | Created: {pr['created_at'][:10]}[/dim]

[bold]Description:[/bold]
{pr['body'] or 'No description provided'}

[bold]Branch:[/bold] {pr['head']['ref']} → {pr['base']['ref']}
[bold]Commits:[/bold] {pr['commits']}
[bold]Additions:[/bold] +{pr['additions']} | [bold]Deletions:[/bold] -{pr['deletions']}
[bold]Changed Files:[/bold] {pr['changed_files']}
"""
        
        if commits:
            summary += f"\n[bold]Recent Commits:[/bold]\n"
            for commit in commits[-3:]:  # Show last 3 commits
                summary += f"• {commit['commit']['message'][:60]}...\n"
        
        if files:
            summary += f"\n[bold]Key Files Changed:[/bold]\n"
            for file in files[:5]:  # Show first 5 files
                status = file['status']
                summary += f"• {status.upper()}: {file['filename']}\n"
        
        return summary.strip()
    
    def display_pr_table(self, prs: List[Dict]):
        """Display pull requests in a table format"""
        if not prs:
            console.print("[yellow]No pull requests found[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Title", style="cyan", min_width=30)
        table.add_column("Author", style="green", width=12)
        table.add_column("State", style="yellow", width=8)
        table.add_column("Created", style="dim", width=12)
        table.add_column("Branch", style="blue", width=15)
        
        for pr in prs:
            state_color = "green" if pr['state'] == "open" else "red"
            table.add_row(
                str(pr['number']),
                pr['title'][:50] + "..." if len(pr['title']) > 50 else pr['title'],
                pr['user']['login'],
                f"[{state_color}]{pr['state']}[/{state_color}]",
                pr['created_at'][:10],
                f"{pr['head']['ref']} → {pr['base']['ref']}"
            )
        
        console.print(table)
