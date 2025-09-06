"""
GitHub integration commands for Lumos CLI
"""

import os
import typer
from rich.console import Console
from rich.panel import Panel
from ..github_client import GitHubClient

console = Console()

def github_clone(org_repo: str, branch: str = None, target_dir: str = None):
    """Clone a GitHub repository and cd into it
    
    Examples:
        lumos-cli github-clone scimarketplace/externaldata
        lumos-cli github-clone scimarketplace/externaldata --branch RC1
        lumos-cli github-clone scimarketplace/externaldata --target-dir ./my-repo
    """
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

def github_pr(org_repo: str, branch: str = None, pr_number: int = None, list_all: bool = False):
    """Check pull requests for a GitHub repository
    
    Examples:
        lumos-cli github-pr scimarketplace/externaldata --branch RC1
        lumos-cli github-pr scimarketplace/externaldata --pr 123
        lumos-cli github-pr scimarketplace/externaldata --list
    """
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
        
        if pr_number:
            # Get specific PR
            console.print(f"[cyan]🔍 Getting PR #{pr_number} for {org}/{repo}...[/cyan]")
            pr = github.get_pull_request(org, repo, pr_number)
            
            if pr:
                commits = github.get_pull_request_commits(org, repo, pr_number)
                files = github.get_pull_request_files(org, repo, pr_number)
                summary = github.format_pr_summary(pr, commits, files)
                console.print(Panel(summary, title=f"PR #{pr_number}", border_style="blue"))
            else:
                console.print(f"[red]PR #{pr_number} not found[/red]")
                
        elif list_all:
            # List all PRs
            console.print(f"[cyan]🔍 Listing all PRs for {org}/{repo}...[/cyan]")
            prs = github.list_pull_requests(org, repo)
            github.display_pr_table(prs)
            
        elif branch:
            # Check PRs for specific branch
            console.print(f"[cyan]🔍 Checking PRs for branch '{branch}' in {org}/{repo}...[/cyan]")
            prs = github.list_pull_requests(org, repo, head=branch)
            
            if prs:
                console.print(f"[green]Found {len(prs)} PR(s) for branch '{branch}':[/green]")
                github.display_pr_table(prs)
                
                # Show detailed summary for the first PR
                if prs:
                    pr = prs[0]
                    commits = github.get_pull_request_commits(org, repo, pr['number'])
                    files = github.get_pull_request_files(org, repo, pr['number'])
                    summary = github.format_pr_summary(pr, commits, files)
                    console.print(Panel(summary, title=f"Latest PR for {branch}", border_style="green"))
            else:
                console.print(f"[yellow]No PRs found for branch '{branch}'[/yellow]")
        else:
            console.print("[red]Please specify --branch, --pr, or --list[/red]")
            
    except Exception as e:
        console.print(f"[red]GitHub PR error: {e}[/red]")

def github_config():
    """Configure GitHub integration settings"""
    console.print("[bold cyan]🔧 GitHub Configuration[/bold cyan]")
    
    # Check current token
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
    if token:
        console.print(f"[green]✅ GITHUB_TOKEN is set[/green]")
        console.print(f"[dim]Token: {token[:8]}...{token[-4:]}[/dim]")
        
        # Test connection
        github = GitHubClient()
        if github.test_connection():
            console.print("[green]✅ GitHub connection successful[/green]")
        else:
            console.print("[red]❌ GitHub connection failed[/red]")
    else:
        console.print("[yellow]⚠️  GITHUB_TOKEN not set[/yellow]")
        console.print("\n[bold]To configure GitHub integration:[/bold]")
        console.print("1. Go to GitHub → Settings → Developer settings → Personal access tokens")
        console.print("2. Generate a new token with 'repo' scope")
        console.print("3. Set the token:")
        console.print("   [dim]export GITHUB_TOKEN=your_token_here[/dim]")
        console.print("   [dim]# Or add to your .env file:[/dim]")
        console.print("   [dim]echo 'GITHUB_TOKEN=your_token_here' >> .env[/dim]")
