"""
Jenkins interactive mode handlers
"""

import re
from rich.console import Console
from ..jenkins_client import JenkinsClient
from ..debug_logger import get_debug_logger

console = Console()
debug_logger = get_debug_logger()

def interactive_jenkins(query: str):
    """Handle Jenkins commands in interactive mode"""
    debug_logger.log_function_call("interactive_jenkins", kwargs={"query": query})
    
    try:
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            debug_logger.error("Jenkins connection failed - JENKINS_URL or JENKINS_TOKEN not configured")
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            return
        
        # Parse the query to determine what Jenkins operation to perform
        lower_query = query.lower()
        
        # Check for build status queries (last N builds)
        if any(keyword in lower_query for keyword in ["build status", "last", "recent", "latest"]) and any(keyword in lower_query for keyword in ["builds", "jobs"]):
            debug_logger.info("Processing build status query")
            
            # Extract number of builds
            number_match = re.search(r"(\d+)\s*(?:builds?|jobs?)", lower_query)
            num_builds = int(number_match.group(1)) if number_match else 5
            
            # Extract folder
            if "deploy-all" in lower_query:
                folder = "scimarketplace/deploy-all"
            else:
                folder_match = re.search(r"folder\s+([a-zA-Z0-9_/]+)", lower_query)
                folder = folder_match.group(1) if folder_match else "scimarketplace/deploy-all"
            
            debug_logger.info(f"Build status query: {num_builds} builds from {folder}")
            console.print(f"[cyan]🔍 Getting last {num_builds} build status from '{folder}'...[/cyan]")
            
            # Get all jobs in the folder
            jobs = jenkins.get_folder_jobs(folder)
            if not jobs:
                console.print(f"[yellow]ℹ️  No jobs found in folder '{folder}'[/yellow]")
                return
            
            # Get recent builds for each job
            all_recent_builds = []
            for job in jobs:
                job_name = job.get("name", "")
                job_path = f"{folder}/{job_name}" if folder else job_name
                
                # Get recent builds (last 24 hours to ensure we have enough data)
                recent_builds = jenkins.get_recent_builds(job_path, 24)
                for build in recent_builds:
                    build["job_name"] = job_name
                    build["job_path"] = job_path
                
                all_recent_builds.extend(recent_builds)
            
            # Sort by timestamp (most recent first) and take the requested number
            all_recent_builds.sort(key=lambda x: x["timestamp"], reverse=True)
            recent_builds = all_recent_builds[:num_builds]
            
            if recent_builds:
                from rich.table import Table, box
                table = Table(title=f"Last {len(recent_builds)} Build Status from {folder}", box=box.ROUNDED)
                table.add_column("Job Name", style="cyan")
                table.add_column("Build #", style="yellow")
                table.add_column("Status", style="green")
                table.add_column("Timestamp", style="blue")
                table.add_column("Duration", style="magenta")
                
                for build in recent_builds:
                    status_color = "green" if build["status"] == "SUCCESS" else "red" if build["status"] in ["FAILURE", "UNSTABLE", "ABORTED"] else "yellow"
                    table.add_row(
                        build["job_name"],
                        str(build["number"]),
                        f"[{status_color}]{build['status']}[/{status_color}]",
                        build["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                        f"{build['duration']/1000:.1f}s" if build['duration'] else "N/A"
                    )
                
                console.print(table)
            else:
                console.print(f"[yellow]ℹ️  No recent builds found in folder '{folder}'[/yellow]")
                
        # Check for failed jobs queries
        elif any(keyword in lower_query for keyword in ["failed", "failure", "broken", "error"]):
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
            debug_logger.info("Processing build parameters query")
            
            # Extract job path and build number
            job_match = re.search(r"job\s+([a-zA-Z0-9_/]+)", lower_query)
            build_match = re.search(r"(\d+)", lower_query)
            
            if job_match and build_match:
                job_path = job_match.group(1)
                build_number = int(build_match.group(1))
                
                debug_logger.info(f"Build parameters query: {job_path} #{build_number}")
                console.print(f"[cyan]🔍 Getting build parameters for {job_path} #{build_number}...[/cyan]")
                parameters = jenkins.get_build_parameters(job_path, build_number)
                jenkins.display_build_parameters_table(parameters)
            else:
                debug_logger.warning("Could not identify job path and build number in query")
                console.print("[red]Could not identify job path and build number in query[/red]")
                
        # Check for failure analysis queries
        elif any(keyword in lower_query for keyword in ["why", "failed", "console", "analyze", "failure"]):
            debug_logger.info("Processing failure analysis query")
            
            # Extract job path and build number with better patterns
            job_match = re.search(r"(?:job|folder)\s+([a-zA-Z0-9_/]+)", lower_query)
            build_match = re.search(r"(?:build\s+number\s+)?(\d+)", lower_query)
            
            if job_match and build_match:
                job_path = job_match.group(1)
                build_number = int(build_match.group(1))
                
                # Auto-prepend scimarketplace if not present
                if not job_path.startswith("scimarketplace/"):
                    job_path = f"scimarketplace/{job_path}"
                
                debug_logger.info(f"Failure analysis query: {job_path} #{build_number}")
                console.print(f"[cyan]🔍 Analyzing build failure for {job_path} #{build_number}...[/cyan]")
                console.print("[dim]Using efficient streaming analysis for large console logs...[/dim]")
                
                analysis = jenkins.analyze_build_failure(job_path, build_number)
                jenkins.display_failure_analysis(analysis)
            else:
                debug_logger.warning("Could not identify job path and build number in query")
                console.print("[red]Could not identify job path and build number in query[/red]")
                console.print("[dim]Try: 'why did build number 20 in folder deploy-all failed'[/dim]")
                
        else:
            console.print("[yellow]ℹ️  I can help you with Jenkins queries like:[/yellow]")
            console.print("• 'Are there failed jobs in last 4 hours in folder deploy-all'")
            console.print("• 'Is there any job running for repository externaldata in branch RC1'")
            console.print("• 'Give me the build parameters of job number 123 under folder deploy-all'")
            console.print("• 'Why did build number 20 in folder deploy-all failed'")
            console.print("• 'Analyze failure for build 456 in folder deploy-all'")
            console.print("• 'Get me the last 5 build status from jenkins in folder deploy-all'")
            
    except Exception as e:
        debug_logger.error(f"Jenkins interactive error: {e}")
        console.print(f"[red]Jenkins interactive error: {e}[/red]")
