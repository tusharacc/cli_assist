"""
Jenkins interactive mode handlers
"""

import re
from rich.console import Console
from ..jenkins_client import JenkinsClient

console = Console()

def interactive_jenkins(query: str):
    """Handle Jenkins commands in interactive mode"""
    try:
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            return
        
        # Parse the query to determine what Jenkins operation to perform
        lower_query = query.lower()
        
        # Check for failed jobs queries
        if any(keyword in lower_query for keyword in ["failed", "failure", "broken", "error"]):
            if "deploy-all" in lower_query:
                folder = "scimarketplace/deploy-all"
            else:
                # Try to extract folder from query
                folder_match = re.search(r"folder\s+([a-zA-Z0-9_/]+)", lower_query)
                folder = folder_match.group(1) if folder_match else "scimarketplace/deploy-all"
            
            # Extract hours
            hours_match = re.search(r"(\d+)\s*hours?", lower_query)
            hours = int(hours_match.group(1)) if hours_match else 4
            
            console.print(f"[cyan]🔍 Searching for failed jobs in '{folder}' (last {hours} hours)...[/cyan]")
            failed_jobs = jenkins.find_failed_jobs_in_folder(folder, hours)
            jenkins.display_failed_jobs_table(failed_jobs)
            
        # Check for running jobs queries
        elif any(keyword in lower_query for keyword in ["running", "executing", "building", "in progress"]):
            if "deploy-all" in lower_query:
                folder = "scimarketplace/deploy-all"
            else:
                folder_match = re.search(r"folder\s+([a-zA-Z0-9_/]+)", lower_query)
                folder = folder_match.group(1) if folder_match else "scimarketplace/deploy-all"
            
            console.print(f"[cyan]🔍 Searching for running jobs in '{folder}'...[/cyan]")
            running_jobs = jenkins.find_running_jobs_in_folder(folder)
            jenkins.display_running_jobs_table(running_jobs)
            
        # Check for repository and branch queries
        elif any(keyword in lower_query for keyword in ["repository", "repo", "branch"]):
            # Extract repository name
            repo_match = re.search(r"(?:repository|repo)\s+([a-zA-Z0-9_]+)", lower_query)
            if not repo_match:
                # Try alternative patterns
                repo_match = re.search(r"for\s+([a-zA-Z0-9_]+)", lower_query)
            
            if repo_match:
                repository = repo_match.group(1)
                
                # Extract branch
                branch_match = re.search(r"branch\s+([A-Z0-9]+)", lower_query)
                branch = branch_match.group(1) if branch_match else "RC1"
                
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
                else:
                    console.print(f"[yellow]ℹ️  No jobs found for repository '{repository}' branch '{branch}'[/yellow]")
            else:
                console.print("[red]Could not identify repository name in query[/red]")
                
        # Check for build parameters queries
        elif any(keyword in lower_query for keyword in ["parameters", "params", "build parameters"]):
            # Extract job path and build number
            job_match = re.search(r"job\s+([a-zA-Z0-9_/]+)", lower_query)
            build_match = re.search(r"(\d+)", lower_query)
            
            if job_match and build_match:
                job_path = job_match.group(1)
                build_number = int(build_match.group(1))
                
                console.print(f"[cyan]🔍 Getting build parameters for {job_path} #{build_number}...[/cyan]")
                parameters = jenkins.get_build_parameters(job_path, build_number)
                jenkins.display_build_parameters_table(parameters)
            else:
                console.print("[red]Could not identify job path and build number in query[/red]")
                
        # Check for failure analysis queries
        elif any(keyword in lower_query for keyword in ["why", "failed", "console", "analyze", "failure"]):
            # Extract job path and build number
            job_match = re.search(r"job\s+([a-zA-Z0-9_/]+)", lower_query)
            build_match = re.search(r"(\d+)", lower_query)
            
            if job_match and build_match:
                job_path = job_match.group(1)
                build_number = int(build_match.group(1))
                
                console.print(f"[cyan]🔍 Analyzing build failure for {job_path} #{build_number}...[/cyan]")
                analysis = jenkins.analyze_build_failure(job_path, build_number)
                jenkins.display_failure_analysis(analysis)
            else:
                console.print("[red]Could not identify job path and build number in query[/red]")
                
        else:
            console.print("[yellow]ℹ️  I can help you with Jenkins queries like:[/yellow]")
            console.print("• 'Are there failed jobs in last 4 hours in folder deploy-all'")
            console.print("• 'Is there any job running for repository externaldata in branch RC1'")
            console.print("• 'Give me the build parameters of job number 123 under folder deploy-all'")
            console.print("• 'Check console text and let me know why job 456 failed'")
            
    except Exception as e:
        console.print(f"[red]Jenkins interactive error: {e}[/red]")
