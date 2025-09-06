"""
Jenkins integration commands for Lumos CLI
"""

import typer
from rich.console import Console
from rich.panel import Panel
from ..jenkins_client import JenkinsClient

console = Console()

def jenkins_failed_jobs(folder: str = "scimarketplace/deploy-all", hours: int = 4):
    """Find failed jobs in a Jenkins folder within specified hours
    
    Examples:
        lumos-cli jenkins-failed-jobs
        lumos-cli jenkins-failed-jobs --folder scimarketplace/deploy-all --hours 8
        lumos-cli jenkins-failed-jobs --folder scimarketplace/addresssearch_multi/RC1
    """
    try:
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            console.print("[dim]Set your credentials with:[/dim]")
            console.print("[dim]  export JENKINS_URL=https://your-jenkins.com[/dim]")
            console.print("[dim]  export JENKINS_TOKEN=your_token[/dim]")
            return
        
        console.print(f"[cyan]🔍 Searching for failed jobs in '{folder}' (last {hours} hours)...[/cyan]")
        
        failed_jobs = jenkins.find_failed_jobs_in_folder(folder, hours)
        jenkins.display_failed_jobs_table(failed_jobs)
        
        if failed_jobs:
            console.print(f"\n[red]Found {len(failed_jobs)} failed jobs[/red]")
        else:
            console.print(f"\n[green]✅ No failed jobs found in the last {hours} hours[/green]")
            
    except Exception as e:
        console.print(f"[red]Jenkins failed jobs error: {e}[/red]")

def jenkins_running_jobs(folder: str = "scimarketplace/deploy-all"):
    """Find currently running jobs in a Jenkins folder
    
    Examples:
        lumos-cli jenkins-running-jobs
        lumos-cli jenkins-running-jobs --folder scimarketplace/deploy-all
        lumos-cli jenkins-running-jobs --folder scimarketplace/addresssearch_multi/RC1
    """
    try:
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            console.print("[dim]Set your credentials with:[/dim]")
            console.print("[dim]  export JENKINS_URL=https://your-jenkins.com[/dim]")
            console.print("[dim]  export JENKINS_TOKEN=your_token[/dim]")
            return
        
        console.print(f"[cyan]🔍 Searching for running jobs in '{folder}'...[/cyan]")
        
        running_jobs = jenkins.find_running_jobs_in_folder(folder)
        jenkins.display_running_jobs_table(running_jobs)
        
        if running_jobs:
            console.print(f"\n[green]Found {len(running_jobs)} running jobs[/green]")
        else:
            console.print(f"\n[yellow]ℹ️  No jobs currently running in '{folder}'[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Jenkins running jobs error: {e}[/red]")

def jenkins_repository_jobs(repository: str, branch: str = "RC1"):
    """Find jobs for a specific repository and branch
    
    Examples:
        lumos-cli jenkins-repo-jobs externaldata RC1
        lumos-cli jenkins-repo-jobs addresssearch RC2
        lumos-cli jenkins-repo-jobs externaldata RC3
    """
    try:
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            console.print("[dim]Set your credentials with:[/dim]")
            console.print("[dim]  export JENKINS_URL=https://your-jenkins.com[/dim]")
            console.print("[dim]  export JENKINS_TOKEN=your_token[/dim]")
            return
        
        console.print(f"[cyan]🔍 Searching for jobs in repository '{repository}' branch '{branch}'...[/cyan]")
        
        jobs = jenkins.find_jobs_by_repository_and_branch(repository, branch)
        
        if jobs:
            from rich.table import Table, box
            table = Table(title=f"Jobs for {repository}/{branch}", box=box.ROUNDED)
            table.add_column("Job Name", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Last Build", style="yellow")
            table.add_column("URL", style="blue")
            
            for job in jobs:
                status_color = "green" if "blue" in job["status"] else "red" if "red" in job["status"] else "yellow"
                table.add_row(
                    job["job_name"],
                    f"[{status_color}]{job['status']}[/{status_color}]",
                    str(job["last_build"]),
                    job["url"]
                )
            
            console.print(table)
            console.print(f"\n[green]Found {len(jobs)} jobs for {repository}/{branch}[/green]")
        else:
            console.print(f"\n[yellow]ℹ️  No jobs found for repository '{repository}' branch '{branch}'[/yellow]")
            console.print("[dim]Make sure the repository folder exists with _multi suffix[/dim]")
            
    except Exception as e:
        console.print(f"[red]Jenkins repository jobs error: {e}[/red]")

def jenkins_build_parameters(job_path: str, build_number: int):
    """Get build parameters for a specific Jenkins build
    
    Examples:
        lumos-cli jenkins-build-params scimarketplace/deploy-all/my-job 123
        lumos-cli jenkins-build-params scimarketplace/externaldata_multi/RC1/build-job 456
    """
    try:
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            console.print("[dim]Set your credentials with:[/dim]")
            console.print("[dim]  export JENKINS_URL=https://your-jenkins.com[/dim]")
            console.print("[dim]  export JENKINS_TOKEN=your_token[/dim]")
            return
        
        console.print(f"[cyan]🔍 Getting build parameters for {job_path} #{build_number}...[/cyan]")
        
        parameters = jenkins.get_build_parameters(job_path, build_number)
        jenkins.display_build_parameters_table(parameters)
        
        if parameters:
            console.print(f"\n[green]Found {len(parameters)} build parameters[/green]")
        else:
            console.print(f"\n[yellow]ℹ️  No build parameters found for build #{build_number}[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Jenkins build parameters error: {e}[/red]")

def jenkins_analyze_failure(job_path: str, build_number: int):
    """Analyze why a Jenkins build failed
    
    Examples:
        lumos-cli jenkins-analyze-failure scimarketplace/deploy-all/my-job 123
        lumos-cli jenkins-analyze-failure scimarketplace/externaldata_multi/RC1/build-job 456
    """
    try:
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            console.print("[dim]Set your credentials with:[/dim]")
            console.print("[dim]  export JENKINS_URL=https://your-jenkins.com[/dim]")
            console.print("[dim]  export JENKINS_TOKEN=your_token[/dim]")
            return
        
        console.print(f"[cyan]🔍 Analyzing build failure for {job_path} #{build_number}...[/cyan]")
        
        analysis = jenkins.analyze_build_failure(job_path, build_number)
        jenkins.display_failure_analysis(analysis)
        
    except Exception as e:
        console.print(f"[red]Jenkins analyze failure error: {e}[/red]")

def jenkins_config():
    """Configure Jenkins integration settings"""
    console.print("[bold cyan]🔧 Jenkins Configuration[/bold cyan]")
    
    # Check current configuration
    jenkins_url = os.getenv("JENKINS_URL")
    jenkins_token = os.getenv("JENKINS_TOKEN")
    jenkins_username = os.getenv("JENKINS_USERNAME")
    
    if jenkins_url:
        console.print(f"[green]✅ JENKINS_URL is set[/green]")
        console.print(f"[dim]URL: {jenkins_url}[/dim]")
    else:
        console.print("[yellow]⚠️  JENKINS_URL not set[/yellow]")
    
    if jenkins_token:
        console.print(f"[green]✅ JENKINS_TOKEN is set[/green]")
        console.print(f"[dim]Token: {jenkins_token[:8]}...{jenkins_token[-4:]}[/dim]")
    else:
        console.print("[yellow]⚠️  JENKINS_TOKEN not set[/yellow]")
    
    if jenkins_username:
        console.print(f"[green]✅ JENKINS_USERNAME is set[/green]")
        console.print(f"[dim]Username: {jenkins_username}[/dim]")
    else:
        console.print("[yellow]ℹ️  JENKINS_USERNAME not set (will use 'api')[/yellow]")
    
    # Test connection
    if jenkins_url and jenkins_token:
        try:
            jenkins = JenkinsClient()
            if jenkins.test_connection():
                console.print("[green]✅ Jenkins connection successful[/green]")
            else:
                console.print("[red]❌ Jenkins connection failed[/red]")
        except Exception as e:
            console.print(f"[red]❌ Jenkins connection error: {e}[/red]")
    else:
        console.print("\n[bold]To configure Jenkins integration:[/bold]")
        console.print("1. Get your Jenkins API token from User → Configure → API Token")
        console.print("2. Set the environment variables:")
        console.print("   [dim]export JENKINS_URL=https://your-jenkins.com[/dim]")
        console.print("   [dim]export JENKINS_TOKEN=your_token_here[/dim]")
        console.print("   [dim]export JENKINS_USERNAME=your_username[/dim]")
        console.print("   [dim]# Or add to your .env file:[/dim]")
        console.print("   [dim]echo 'JENKINS_URL=https://your-jenkins.com' >> .env[/dim]")
        console.print("   [dim]echo 'JENKINS_TOKEN=your_token_here' >> .env[/dim]")
        console.print("   [dim]echo 'JENKINS_USERNAME=your_username' >> .env[/dim]")
