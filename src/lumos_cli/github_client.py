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
from .neo4j_dotnet_client import Neo4jDotNetClient
from .neo4j_config import Neo4jConfigManager

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
        elif operation == "list_commits":
            org = kwargs.get('org', '')
            repo = kwargs.get('repo', '')
            endpoint = f"/repos/{org}/{repo}/commits"
            debug_logger.debug(f"Constructed list_commits endpoint: {endpoint}")
            debug_logger.log_function_return("GitHubClient._get_fallback_endpoint", endpoint)
            return endpoint
        elif operation == "get_commit":
            org = kwargs.get('org', '')
            repo = kwargs.get('repo', '')
            commit_sha = kwargs.get('commit_sha', '')
            endpoint = f"/repos/{org}/{repo}/commits/{commit_sha}"
            debug_logger.debug(f"Constructed get_commit endpoint: {endpoint}")
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
    
    def list_commits(self, org: str, repo: str, branch: str = None, 
                    per_page: int = 30, page: int = 1) -> List[Dict]:
        """List commits for a repository"""
        debug_logger.log_function_call("GitHubClient.list_commits", kwargs={"org": org, "repo": repo, "branch": branch, "per_page": per_page, "page": page})
        
        endpoint = self._get_api_endpoint("list_commits", org=org, repo=repo, branch=branch)
        params = {"per_page": per_page, "page": page}
        if branch:
            params["sha"] = branch
            
        result = self._make_request(endpoint, params)
        debug_logger.log_function_return("GitHubClient.list_commits", f"Found {len(result)} commits")
        return result
    
    def get_commit(self, org: str, repo: str, commit_sha: str) -> Dict:
        """Get specific commit details"""
        debug_logger.log_function_call("GitHubClient.get_commit", kwargs={"org": org, "repo": repo, "commit_sha": commit_sha})
        endpoint = self._get_api_endpoint("get_commit", org=org, repo=repo, commit_sha=commit_sha)
        result = self._make_request(endpoint)
        debug_logger.log_function_return("GitHubClient.get_commit", f"Commit: {result.get('sha', 'unknown')[:7]}")
        return result
    
    def get_latest_commit(self, org: str, repo: str, branch: str = None) -> Dict:
        """Get the latest commit for a repository or branch"""
        debug_logger.log_function_call("GitHubClient.get_latest_commit", kwargs={"org": org, "repo": repo, "branch": branch})
        
        # Get the latest commit from the default branch or specified branch
        commits = self.list_commits(org, repo, branch, per_page=1)
        if commits:
            latest_commit = commits[0]
            debug_logger.log_function_return("GitHubClient.get_latest_commit", f"Latest commit: {latest_commit.get('sha', 'unknown')[:7]}")
            return latest_commit
        else:
            debug_logger.log_function_return("GitHubClient.get_latest_commit", "No commits found")
            return {}
    
    def clone_repository(self, org: str, repo: str, branch: str = None, 
                        target_dir: str = None) -> Tuple[bool, str]:
        """Clone repository and return success status and path"""
        try:
            # Construct clone URL using the configured base URL
            base_url = self.base_url.replace('/api/v3', '').replace('/api', '')
            if self.token:
                clone_url = f"https://{self.token}@{base_url.replace('https://', '')}/{org}/{repo}.git"
            else:
                clone_url = f"{base_url}/{org}/{repo}.git"
            
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
    
    def format_commit_summary(self, commit: Dict) -> str:
        """Format commit details for display"""
        sha = commit.get('sha', 'unknown')[:7]
        author = commit.get('commit', {}).get('author', {}).get('name', 'Unknown')
        date = commit.get('commit', {}).get('author', {}).get('date', 'Unknown')[:10]
        message = commit.get('commit', {}).get('message', 'No message').split('\n')[0]
        
        # Get stats if available
        stats = commit.get('stats', {})
        additions = stats.get('additions', 0)
        deletions = stats.get('deletions', 0)
        files_changed = stats.get('total', 0)
        
        summary = f"""
🔹 Commit: {sha}
👤 Author: {author}
📅 Date: {date}
📝 Message: {message}
📊 Changes: +{additions} -{deletions} ({files_changed} files)
"""
        return summary.strip()
    
    def format_detailed_commit_analysis(self, commit: Dict) -> str:
        """Format detailed commit analysis with file changes and code analysis"""
        sha = commit.get('sha', 'unknown')[:7]
        author = commit.get('commit', {}).get('author', {}).get('name', 'Unknown')
        date = commit.get('commit', {}).get('author', {}).get('date', 'Unknown')[:10]
        message = commit.get('commit', {}).get('message', 'No message')
        
        # Get stats
        stats = commit.get('stats', {})
        additions = stats.get('additions', 0)
        deletions = stats.get('deletions', 0)
        files_changed = stats.get('total', 0)
        
        # Get files changed
        files = commit.get('files', [])
        
        # Analyze file changes
        file_analysis = self._analyze_file_changes(files)
        
        # Build detailed summary
        summary = f"""
[bold blue]🔹 Commit Details: {sha}[/bold blue]
[dim]👤 Author: {author} | 📅 Date: {date}[/dim]

[bold]📝 Message:[/bold]
{message}

[bold]📊 Statistics:[/bold]
• Lines added: [green]+{additions}[/green]
• Lines deleted: [red]-{deletions}[/red]
• Files changed: [blue]{files_changed}[/blue]
• Net change: [yellow]{additions - deletions:+d}[/yellow]

[bold]📁 Files Changed:[/bold]
{file_analysis['file_summary']}

[bold]🔍 Code Analysis:[/bold]
{file_analysis['code_analysis']}

[bold]🔧 Method & Class Changes:[/bold]
{file_analysis['method_class_changes']}

{file_analysis['dependency_analysis']}

[bold]📈 Impact Summary:[/bold]
{file_analysis['impact_summary']}
"""
        return summary.strip()
    
    def _analyze_file_changes(self, files: List[Dict]) -> Dict[str, str]:
        """Analyze file changes to extract meaningful information including method and class changes"""
        if not files:
            return {
                'file_summary': "No file changes detected",
                'code_analysis': "No code changes to analyze",
                'impact_summary': "No changes detected",
                'method_class_changes': "No method or class changes detected"
            }
        
        # Extract method and class changes from diffs
        method_class_result = self._extract_method_class_changes(files)
        method_class_changes_data = method_class_result['data']
        method_class_changes_formatted = method_class_result['formatted']
        
        # Analyze dependencies with Neo4j
        dependency_analysis = self.analyze_dependencies_with_neo4j(method_class_changes_data)
        
        # Categorize files
        file_categories = {
            'source_files': [],
            'test_files': [],
            'config_files': [],
            'documentation': [],
            'other': []
        }
        
        for file_info in files:
            filename = file_info.get('filename', '')
            status = file_info.get('status', '')
            additions = file_info.get('additions', 0)
            deletions = file_info.get('deletions', 0)
            
            # Categorize file
            if any(ext in filename.lower() for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.cs']):
                if 'test' in filename.lower() or 'spec' in filename.lower():
                    file_categories['test_files'].append((filename, status, additions, deletions))
                else:
                    file_categories['source_files'].append((filename, status, additions, deletions))
            elif any(ext in filename.lower() for ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf']):
                file_categories['config_files'].append((filename, status, additions, deletions))
            elif any(ext in filename.lower() for ext in ['.md', '.txt', '.rst', '.adoc']):
                file_categories['documentation'].append((filename, status, additions, deletions))
            else:
                file_categories['other'].append((filename, status, additions, deletions))
        
        # Build file summary
        file_summary = ""
        for category, files_list in file_categories.items():
            if files_list:
                category_name = category.replace('_', ' ').title()
                file_summary += f"\n[bold]{category_name}:[/bold]\n"
                for filename, status, additions, deletions in files_list:
                    status_icon = {"added": "🆕", "modified": "✏️", "removed": "🗑️", "renamed": "📝"}.get(status, "📄")
                    changes = f"+{additions} -{deletions}" if additions > 0 or deletions > 0 else ""
                    file_summary += f"  {status_icon} {filename} {changes}\n"
        
        # Analyze code changes
        code_analysis = self._analyze_code_patterns(files)
        
        # Generate impact summary
        impact_summary = self._generate_impact_summary(files, file_categories)
        
        return {
            'file_summary': file_summary.strip(),
            'code_analysis': code_analysis,
            'impact_summary': impact_summary,
            'method_class_changes': method_class_changes_formatted,
            'dependency_analysis': dependency_analysis
        }
    
    def _extract_method_class_changes(self, files: List[Dict]) -> Dict:
        """Extract method and class changes from file diffs"""
        method_class_changes = {
            'classes_added': [],
            'classes_modified': [],
            'classes_removed': [],
            'methods_added': [],
            'methods_modified': [],
            'methods_removed': []
        }
        
        for file_info in files:
            filename = file_info.get('filename', '')
            status = file_info.get('status', '')
            patch = file_info.get('patch', '')
            
            # Only analyze source code files
            if not any(ext in filename.lower() for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.cs']):
                continue
                
            if not patch:
                continue
            
            # Extract changes from patch
            changes = self._parse_patch_for_methods_classes(patch, filename, status)
            
            # Merge changes
            for change_type, items in changes.items():
                method_class_changes[change_type].extend(items)
        
        # Build summary
        summary_parts = []
        
        if method_class_changes['classes_added']:
            summary_parts.append(f"\n[bold green]🆕 Classes Added:[/bold green]")
            for class_info in method_class_changes['classes_added']:
                summary_parts.append(f"  • {class_info['class_name']} in {class_info['file']}")
        
        if method_class_changes['classes_modified']:
            summary_parts.append(f"\n[bold yellow]✏️ Classes Modified:[/bold yellow]")
            for class_info in method_class_changes['classes_modified']:
                summary_parts.append(f"  • {class_info['class_name']} in {class_info['file']}")
                if class_info.get('methods_changed'):
                    for method in class_info['methods_changed']:
                        summary_parts.append(f"    - {method}")
        
        if method_class_changes['classes_removed']:
            summary_parts.append(f"\n[bold red]🗑️ Classes Removed:[/bold red]")
            for class_info in method_class_changes['classes_removed']:
                summary_parts.append(f"  • {class_info['class_name']} in {class_info['file']}")
        
        if method_class_changes['methods_added']:
            summary_parts.append(f"\n[bold green]🆕 Methods Added:[/bold green]")
            for method_info in method_class_changes['methods_added']:
                summary_parts.append(f"  • {method_info['method_name']} in {method_info['class_name']} ({method_info['file']})")
        
        if method_class_changes['methods_modified']:
            summary_parts.append(f"\n[bold yellow]✏️ Methods Modified:[/bold yellow]")
            for method_info in method_class_changes['methods_modified']:
                summary_parts.append(f"  • {method_info['method_name']} in {method_info['class_name']} ({method_info['file']})")
        
        if method_class_changes['methods_removed']:
            summary_parts.append(f"\n[bold red]🗑️ Methods Removed:[/bold red]")
            for method_info in method_class_changes['methods_removed']:
                summary_parts.append(f"  • {method_info['method_name']} in {method_info['class_name']} ({method_info['file']})")
        
        if not any(method_class_changes.values()):
            return {
                'data': method_class_changes,
                'formatted': "No method or class changes detected"
            }
        
        return {
            'data': method_class_changes,
            'formatted': "\n".join(summary_parts)
        }
    
    def _parse_patch_for_methods_classes(self, patch: str, filename: str, status: str) -> Dict[str, List[Dict]]:
        """Parse git patch to extract method and class changes"""
        changes = {
            'classes_added': [],
            'classes_modified': [],
            'classes_removed': [],
            'methods_added': [],
            'methods_modified': [],
            'methods_removed': []
        }
        
        lines = patch.split('\n')
        current_class = None
        current_method = None
        in_class = False
        in_method = False
        
        # Determine file type for parsing
        file_ext = filename.split('.')[-1].lower()
        
        for line in lines:
            if line.startswith('@@'):
                # Reset context for new hunk
                current_class = None
                current_method = None
                in_class = False
                in_method = False
                continue
            
            if line.startswith('+') or line.startswith('-'):
                # This is a changed line
                content = line[1:].strip()
                
                # Parse based on file type
                if file_ext in ['py']:
                    self._parse_python_changes(line, content, filename, current_class, current_method, changes)
                elif file_ext in ['cs']:
                    self._parse_csharp_changes(line, content, filename, current_class, current_method, changes)
                elif file_ext in ['js', 'ts']:
                    self._parse_javascript_changes(line, content, filename, current_class, current_method, changes)
                elif file_ext in ['java']:
                    self._parse_java_changes(line, content, filename, current_class, current_method, changes)
        
        return changes
    
    def _parse_python_changes(self, line: str, content: str, filename: str, current_class: str, current_method: str, changes: Dict):
        """Parse Python code changes"""
        is_addition = line.startswith('+')
        
        # Class detection
        if content.startswith('class ') and ':' in content:
            class_name = content.split('class ')[1].split('(')[0].split(':')[0].strip()
            if is_addition:
                changes['classes_added'].append({
                    'class_name': class_name,
                    'file': filename
                })
            else:
                changes['classes_removed'].append({
                    'class_name': class_name,
                    'file': filename
                })
        
        # Method detection
        elif content.startswith('def ') and '(' in content and ':' in content:
            method_name = content.split('def ')[1].split('(')[0].strip()
            if is_addition:
                changes['methods_added'].append({
                    'method_name': method_name,
                    'class_name': current_class or 'Global',
                    'file': filename
                })
            else:
                changes['methods_removed'].append({
                    'method_name': method_name,
                    'class_name': current_class or 'Global',
                    'file': filename
                })
    
    def _parse_csharp_changes(self, line: str, content: str, filename: str, current_class: str, current_method: str, changes: Dict):
        """Parse C# code changes"""
        is_addition = line.startswith('+')
        
        # Class detection
        if 'class ' in content and ('{' in content or ':' in content):
            class_name = content.split('class ')[1].split(' ')[0].split('{')[0].split(':')[0].strip()
            if is_addition:
                changes['classes_added'].append({
                    'class_name': class_name,
                    'file': filename
                })
            else:
                changes['classes_removed'].append({
                    'class_name': class_name,
                    'file': filename
                })
        
        # Method detection
        elif any(keyword in content for keyword in ['public ', 'private ', 'protected ', 'internal ']) and '(' in content and '{' in content:
            # Extract method name
            parts = content.split('(')[0].strip().split()
            if len(parts) >= 2:
                method_name = parts[-1]
                if is_addition:
                    changes['methods_added'].append({
                        'method_name': method_name,
                        'class_name': current_class or 'Global',
                        'file': filename
                    })
                else:
                    changes['methods_removed'].append({
                        'method_name': method_name,
                        'class_name': current_class or 'Global',
                        'file': filename
                    })
    
    def _parse_javascript_changes(self, line: str, content: str, filename: str, current_class: str, current_method: str, changes: Dict):
        """Parse JavaScript/TypeScript code changes"""
        is_addition = line.startswith('+')
        
        # Class detection
        if 'class ' in content and ('{' in content or 'extends' in content):
            class_name = content.split('class ')[1].split(' ')[0].split('{')[0].split('extends')[0].strip()
            if is_addition:
                changes['classes_added'].append({
                    'class_name': class_name,
                    'file': filename
                })
            else:
                changes['classes_removed'].append({
                    'class_name': class_name,
                    'file': filename
                })
        
        # Method detection
        elif ('function ' in content or '=>' in content) and '(' in content:
            if 'function ' in content:
                method_name = content.split('function ')[1].split('(')[0].strip()
            else:
                # Arrow function
                method_name = content.split('(')[0].strip().split('=')[0].strip()
            
            if is_addition:
                changes['methods_added'].append({
                    'method_name': method_name,
                    'class_name': current_class or 'Global',
                    'file': filename
                })
            else:
                changes['methods_removed'].append({
                    'method_name': method_name,
                    'class_name': current_class or 'Global',
                    'file': filename
                })
    
    def _parse_java_changes(self, line: str, content: str, filename: str, current_class: str, current_method: str, changes: Dict):
        """Parse Java code changes"""
        is_addition = line.startswith('+')
        
        # Class detection
        if 'class ' in content and '{' in content:
            class_name = content.split('class ')[1].split(' ')[0].split('{')[0].strip()
            if is_addition:
                changes['classes_added'].append({
                    'class_name': class_name,
                    'file': filename
                })
            else:
                changes['classes_removed'].append({
                    'class_name': class_name,
                    'file': filename
                })
        
        # Method detection
        elif any(keyword in content for keyword in ['public ', 'private ', 'protected ']) and '(' in content and '{' in content:
            # Extract method name
            parts = content.split('(')[0].strip().split()
            if len(parts) >= 2:
                method_name = parts[-1]
                if is_addition:
                    changes['methods_added'].append({
                        'method_name': method_name,
                        'class_name': current_class or 'Global',
                        'file': filename
                    })
                else:
                    changes['methods_removed'].append({
                        'method_name': method_name,
                        'class_name': current_class or 'Global',
                    'file': filename
                })
    
    def analyze_dependencies_with_neo4j(self, method_class_changes: Dict) -> str:
        """Analyze dependencies using Neo4j for changed methods and classes"""
        try:
            # Check if Neo4j is configured
            config_manager = Neo4jConfigManager()
            if not config_manager.is_configured():
                return "[dim]Neo4j not configured - dependency analysis unavailable[/dim]"
            
            config = config_manager.load_config()
            if not config:
                return "[dim]Neo4j configuration not found[/dim]"
            
            client = Neo4jDotNetClient(config.uri, config.username, config.password)
            if not client.connect():
                return "[dim]Failed to connect to Neo4j[/dim]"
            
            dependency_analysis = []
            
            # Analyze changed methods for dependencies
            for method_info in method_class_changes.get('methods_added', []) + method_class_changes.get('methods_modified', []):
                method_name = method_info['method_name']
                class_name = method_info['class_name']
                file_path = method_info['file']
                
                # Find classes that call this method
                calling_classes = client.find_classes_using_constant(method_name, "Global")
                if calling_classes:
                    dependency_analysis.append(f"  • {method_name} is called by {len(calling_classes)} classes")
            
            # Analyze changed classes for dependencies
            for class_info in method_class_changes.get('classes_added', []) + method_class_changes.get('classes_modified', []):
                class_name = class_info['class_name']
                file_path = class_info['file']
                
                # Get repository overview to understand class context
                # Extract org/repo from file path if possible
                if '/' in file_path:
                    parts = file_path.split('/')
                    if len(parts) >= 2:
                        repo_name = parts[-2] if parts[-2] != 'src' else parts[-3]
                        namespace = f"Company.{repo_name}"
                        
                        overview = client.get_repository_overview(repo_name, namespace)
                        if overview:
                            dependency_analysis.append(f"  • {class_name} is part of {repo_name} ({overview.get('method_count', 0)} methods)")
            
            client.close()
            
            if dependency_analysis:
                return "\n[bold cyan]🔗 Dependency Analysis:[/bold cyan]\n" + "\n".join(dependency_analysis)
            else:
                return "[dim]No dependency information available in Neo4j[/dim]"
                
        except Exception as e:
            debug_logger.error(f"Neo4j dependency analysis failed: {e}")
            return f"[dim]Dependency analysis failed: {e}[/dim]"
    
    def _analyze_code_patterns(self, files: List[Dict]) -> str:
        """Analyze code patterns in changed files"""
        patterns = {
            'new_features': 0,
            'bug_fixes': 0,
            'refactoring': 0,
            'tests': 0,
            'configuration': 0
        }
        
        for file_info in files:
            filename = file_info.get('filename', '')
            status = file_info.get('status', '')
            additions = file_info.get('additions', 0)
            deletions = file_info.get('deletions', 0)
            
            # Analyze based on filename and changes
            if 'test' in filename.lower() or 'spec' in filename.lower():
                patterns['tests'] += 1
            elif any(ext in filename.lower() for ext in ['.json', '.yaml', '.yml', '.toml', '.ini']):
                patterns['configuration'] += 1
            elif status == 'added' and additions > 50:
                patterns['new_features'] += 1
            elif additions < 20 and deletions < 20 and additions > 0:
                patterns['bug_fixes'] += 1
            elif additions > 30 and deletions > 30:
                patterns['refactoring'] += 1
        
        # Build analysis text
        analysis_parts = []
        if patterns['new_features'] > 0:
            analysis_parts.append(f"• [green]New features: {patterns['new_features']} files[/green]")
        if patterns['bug_fixes'] > 0:
            analysis_parts.append(f"• [yellow]Bug fixes: {patterns['bug_fixes']} files[/yellow]")
        if patterns['refactoring'] > 0:
            analysis_parts.append(f"• [blue]Refactoring: {patterns['refactoring']} files[/blue]")
        if patterns['tests'] > 0:
            analysis_parts.append(f"• [cyan]Test changes: {patterns['tests']} files[/cyan]")
        if patterns['configuration'] > 0:
            analysis_parts.append(f"• [magenta]Configuration: {patterns['configuration']} files[/magenta]")
        
        if not analysis_parts:
            return "• [dim]No significant code patterns detected[/dim]"
        
        return "\n".join(analysis_parts)
    
    def _generate_impact_summary(self, files: List[Dict], file_categories: Dict) -> str:
        """Generate impact summary based on file changes"""
        total_files = len(files)
        source_files = len(file_categories['source_files'])
        test_files = len(file_categories['test_files'])
        config_files = len(file_categories['config_files'])
        
        # Calculate impact level
        if source_files > 5:
            impact_level = "High"
            impact_color = "red"
        elif source_files > 2:
            impact_level = "Medium"
            impact_color = "yellow"
        else:
            impact_level = "Low"
            impact_color = "green"
        
        summary_parts = [
            f"• [bold {impact_color}]Impact Level: {impact_level}[/bold {impact_color}]",
            f"• Source files: {source_files}",
            f"• Test files: {test_files}",
            f"• Config files: {config_files}",
            f"• Total files: {total_files}"
        ]
        
        return "\n".join(summary_parts)
    
    def display_commits_table(self, commits: List[Dict]):
        """Display commits in a table format"""
        if not commits:
            console.print("[yellow]No commits found[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("SHA", style="dim", width=8)
        table.add_column("Message", style="cyan", min_width=40)
        table.add_column("Author", style="green", width=15)
        table.add_column("Date", style="dim", width=12)
        table.add_column("Changes", style="blue", width=12)
        
        for commit in commits:
            sha = commit.get('sha', 'unknown')[:7]
            message = commit.get('commit', {}).get('message', 'No message').split('\n')[0]
            author = commit.get('commit', {}).get('author', {}).get('name', 'Unknown')
            date = commit.get('commit', {}).get('author', {}).get('date', 'Unknown')[:10]
            
            # Get stats
            stats = commit.get('stats', {})
            additions = stats.get('additions', 0)
            deletions = stats.get('deletions', 0)
            changes = f"+{additions} -{deletions}"
            
            # Truncate long messages
            if len(message) > 50:
                message = message[:47] + "..."
            
            table.add_row(
                sha,
                message,
                author,
                date,
                changes
            )
        
        console.print(table)
