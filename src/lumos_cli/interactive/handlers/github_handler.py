"""
GitHub interactive mode handlers
"""

import re
from rich.console import Console
from ...utils.github_query_parser import GitHubQueryParser
from ...clients.github_client import GitHubClient
from ...utils.debug_logger import debug_logger
from ...core.keyword_detector import keyword_detector

console = Console()

def interactive_github(query: str):
    """Handle GitHub commands in interactive mode using hybrid parsing"""
    try:
        # Use hybrid parser (text patterns + LLM)
        parser = GitHubQueryParser()
        result = parser.parse_query(query)
        
        if not result or not result.get('org_repo'):
            console.print("[yellow]Could not detect organization/repository from your query.[/yellow]")
            console.print("[dim]Try: 'github tusharacc/cli_assist' or 'check PRs for scimarketplace/externaldata'[/dim]")
            return
        
        org_repo = result['org_repo']
        method = result.get('method', 'unknown')
        confidence = result.get('confidence', 0.0)
        agreement = result.get('agreement', False)
        
        # Show parsing method and confidence for debugging
        if confidence < 0.7:
            console.print(f"[dim]Parsed using {method} (confidence: {confidence:.2f})[/dim]")
        if agreement:
            console.print("[dim]✓ Text and LLM parsing agreed[/dim]")
        
        # Use LLM-based keyword detection
        detection_result = keyword_detector.detect_keywords('github', query)
        
        # Show detection confidence for debugging
        if detection_result.confidence < 0.7:
            console.print(f"[dim]LLM detection confidence: {detection_result.confidence:.2f}[/dim]")
        
        # Handle the detected action
        action = detection_result.action
        extracted_values = detection_result.extracted_values
        
        if action == 'commits':
            # Handle commit-related queries
            count = extracted_values.get('count', 5)
            branch = extracted_values.get('branch')
            commit_sha = extracted_values.get('commit_sha')
            
            if commit_sha:
                console.print(f"[cyan]🔍 Getting detailed commit analysis for {commit_sha} from {org_repo}...[/cyan]")
                _github_commits(org_repo, commit_sha=commit_sha)
            elif count == 1:
                console.print(f"[cyan]🔍 Getting latest commit from {org_repo}...[/cyan]")
                _github_commits(org_repo, latest=True)
            else:
                console.print(f"[cyan]🔍 Getting last {count} commits from {org_repo}...[/cyan]")
                _github_commits(org_repo, count=count)
                
        elif action == 'pr':
            # Handle PR-related queries
            branch = extracted_values.get('branch')
            
            if branch:
                console.print(f"[cyan]🔍 Checking PRs for branch '{branch}' in {org_repo}...[/cyan]")
                _github_pr(org_repo, branch=branch)
            else:
                console.print(f"[cyan]🔍 Listing all PRs for {org_repo}...[/cyan]")
                _github_pr(org_repo, list_all=True)
                
        elif action == 'clone':
            # Handle clone-related queries
            branch = extracted_values.get('branch')
            console.print(f"[cyan]🔍 Cloning {org_repo}...[/cyan]")
            _github_clone(org_repo, branch=branch)
            
        else:
            # Default to listing PRs for unknown actions
            console.print(f"[cyan]🔍 Listing all PRs for {org_repo}...[/cyan]")
            _github_pr(org_repo, list_all=True)
            
    except Exception as e:
        console.print(f"[red]GitHub error: {e}[/red]")

def _github_clone(org_repo: str, branch: str = None, target_dir: str = None):
    """Clone a GitHub repository and cd into it"""
    try:
        # Parse org/repo
        if "/" not in org_repo:
            console.print("[red]Error: Repository must be in format 'org/repo'[/red]")
            return
        
        org, repo = org_repo.split("/", 1)
        
        # Initialize GitHub client
        github = GitHubClient()
        
        if not github.test_connection():
            console.print("[red]GitHub connection failed. Please check your GITHUB_TOKEN[/red]")
            console.print("[dim]Set your token with: export GITHUB_TOKEN=your_token[/dim]")
            return
        
        console.print(f"[cyan]🔍 Cloning {org}/{repo}...[/cyan]")
        
        # Clone repository
        success, repo_path = github.clone_repository(org, repo, branch, target_dir)
        
        if success:
            console.print(f"[green]✅ Successfully cloned to: {repo_path}[/green]")
            console.print(f"[dim]💡 To work in this repository, run: cd {repo_path}[/dim]")
            
            # Show repository info
            repo_info = github.get_repository_info(org, repo)
            if repo_info:
                console.print(f"\n[bold]Repository Info:[/bold]")
                console.print(f"  📝 Description: {repo_info.get('description', 'No description')}")
                console.print(f"  ⭐ Stars: {repo_info.get('stargazers_count', 0)}")
                console.print(f"  🍴 Forks: {repo_info.get('forks_count', 0)}")
                console.print(f"  📅 Updated: {repo_info.get('updated_at', 'Unknown')[:10]}")
        else:
            console.print("[red]❌ Clone failed[/red]")
            
    except Exception as e:
        console.print(f"[red]GitHub clone error: {e}[/red]")

def _github_pr(org_repo: str, branch: str = None, pr_number: int = None, list_all: bool = False):
    """Check pull requests for a GitHub repository"""
    try:
        # Parse org/repo
        if "/" not in org_repo:
            console.print("[red]Error: Repository must be in format 'org/repo'[/red]")
            return
        
        org, repo = org_repo.split("/", 1)
        
        # Initialize GitHub client
        github = GitHubClient()
        
        if not github.test_connection():
            console.print("[red]GitHub connection failed. Please check your GITHUB_TOKEN[/red]")
            return
        
        if pr_number:
            # Get specific PR
            console.print(f"[cyan]🔍 Getting PR #{pr_number} for {org}/{repo}...[/cyan]")
            pr_info = github.get_pull_request(org, repo, pr_number)
            
            if pr_info:
                console.print(f"\n[bold]Pull Request #{pr_number}[/bold]")
                console.print(f"  📝 Title: {pr_info.get('title', 'No title')}")
                console.print(f"  👤 Author: {pr_info.get('user', {}).get('login', 'Unknown')}")
                console.print(f"  📅 Created: {pr_info.get('created_at', 'Unknown')[:10]}")
                console.print(f"  🔄 Status: {pr_info.get('state', 'Unknown')}")
                console.print(f"  🔗 URL: {pr_info.get('html_url', 'No URL')}")
                
                if pr_info.get('body'):
                    console.print(f"\n[bold]Description:[/bold]")
                    console.print(pr_info['body'][:500] + "..." if len(pr_info['body']) > 500 else pr_info['body'])
            else:
                console.print(f"[red]❌ PR #{pr_number} not found[/red]")
                
        elif branch:
            # Get PRs for specific branch
            console.print(f"[cyan]🔍 Getting PRs for branch '{branch}' in {org}/{repo}...[/cyan]")
            prs = github.get_pull_requests(org, repo, branch=branch)
            
            if prs:
                console.print(f"\n[bold]Pull Requests for branch '{branch}':[/bold]")
                for pr in prs[:10]:  # Show first 10
                    console.print(f"  #{pr['number']}: {pr['title']} ({pr['state']})")
                    console.print(f"    👤 {pr['user']['login']} | 📅 {pr['created_at'][:10]}")
                    console.print(f"    🔗 {pr['html_url']}\n")
            else:
                console.print(f"[yellow]No PRs found for branch '{branch}'[/yellow]")
                
        elif list_all:
            # List all PRs
            console.print(f"[cyan]🔍 Getting all PRs for {org}/{repo}...[/cyan]")
            prs = github.get_pull_requests(org, repo)
            
            if prs:
                console.print(f"\n[bold]All Pull Requests:[/bold]")
                for pr in prs[:10]:  # Show first 10
                    console.print(f"  #{pr['number']}: {pr['title']} ({pr['state']})")
                    console.print(f"    👤 {pr['user']['login']} | 📅 {pr['created_at'][:10]}")
                    console.print(f"    🔗 {pr['html_url']}\n")
            else:
                console.print(f"[yellow]No PRs found[/yellow]")
        else:
            console.print("[yellow]Please specify what you want to do with PRs[/yellow]")
            
    except Exception as e:
        console.print(f"[red]GitHub PR error: {e}[/red]")

def _github_commits(org_repo: str, count: int = 5, latest: bool = False, commit_sha: str = None):
    """Get commit information for a GitHub repository"""
    try:
        # Parse org/repo
        if "/" not in org_repo:
            console.print("[red]Error: Repository must be in format 'org/repo'[/red]")
            return
        
        org, repo = org_repo.split("/", 1)
        
        # Initialize GitHub client
        github = GitHubClient()
        
        if not github.test_connection():
            console.print("[red]GitHub connection failed. Please check your GITHUB_TOKEN[/red]")
            return
        
        if commit_sha:
            # Get specific commit with detailed analysis
            console.print(f"[cyan]🔍 Getting commit {commit_sha} for {org}/{repo}...[/cyan]")
            commit_info = github.get_commit_details(org, repo, commit_sha)
            
            if commit_info:
                # Use the detailed commit analysis instead of basic formatting
                detailed_analysis = github.format_detailed_commit_analysis(commit_info)
                console.print(detailed_analysis)
            else:
                console.print(f"[red]❌ Commit {commit_sha} not found[/red]")
                
        elif latest:
            # Get latest commit with detailed analysis
            console.print(f"[cyan]🔍 Getting latest commit for {org}/{repo}...[/cyan]")
            commits = github.get_commits(org, repo, count=1)
            
            if commits:
                commit = commits[0]
                # Use detailed analysis for latest commit too
                detailed_analysis = github.format_detailed_commit_analysis(commit)
                console.print(detailed_analysis)
            else:
                console.print(f"[yellow]No commits found[/yellow]")
                
        else:
            # Get multiple commits
            console.print(f"[cyan]🔍 Getting last {count} commits for {org}/{repo}...[/cyan]")
            commits = github.get_commits(org, repo, count=count)
            
            if commits:
                console.print(f"\n[bold]Last {len(commits)} Commits:[/bold]")
                for i, commit in enumerate(commits, 1):
                    sha = commit.get('sha', 'Unknown')[:8]
                    message = commit.get('commit', {}).get('message', 'No message')
                    author = commit.get('commit', {}).get('author', {}).get('name', 'Unknown')
                    date = commit.get('commit', {}).get('author', {}).get('date', 'Unknown')[:10]
                    
                    console.print(f"  {i}. {sha} - {message}")
                    console.print(f"     👤 {author} | 📅 {date}")
                    console.print(f"     🔗 {commit.get('html_url', 'No URL')}\n")
            else:
                console.print(f"[yellow]No commits found[/yellow]")
                
    except Exception as e:
        console.print(f"[red]GitHub commits error: {e}[/red]")
