"""
Jenkins interactive mode handlers
"""

import re
import json
from rich.console import Console
from ...clients.jenkins_client import JenkinsClient
from ...utils.debug_logger import get_debug_logger
from ...core.router import LLMRouter
from ...core.keyword_detector import keyword_detector

console = Console()
debug_logger = get_debug_logger()

def _extract_folder_path_with_llm(query: str) -> str:
    """Extract Jenkins folder path from natural language query using LLM with regex fallback"""
    try:
        # Initialize LLM router with Ollama backend for reliable local processing
        router = LLMRouter(backend="ollama")
        
        # Create a focused prompt for folder path extraction
        prompt = f"""You are a Jenkins folder path extractor. Extract the Jenkins folder path from the user query.

User Query: "{query}"

Jenkins folder structure examples:
- "scimarketplace/deploy-all" - Main deployment folder
- "scimarketplace/quote_multi/RC1" - Repository folder with branch
- "scimarketplace/externaldata_multi/RC2" - Repository folder with branch
- "scimarketplace/addresssearch_multi/RC3" - Repository folder with branch

Rules:
1. If user mentions "deploy-all", return "scimarketplace/deploy-all"
2. If user mentions a repository name (like "quote", "externaldata", "addresssearch"), add "_multi" suffix
3. If user mentions a branch (like "RC1", "RC2", "RC3", "RC4"), include it in the path
4. Always prefix with "scimarketplace/"
5. Use forward slashes to separate folder levels
6. Convert spaces to underscores in folder names

Examples:
- "folder quote and sub folder RC1" → "scimarketplace/quote_multi/RC1"
- "folder externaldata and sub folder RC2" → "scimarketplace/externaldata_multi/RC2"
- "folder addresssearch and sub folder RC3" → "scimarketplace/addresssearch_multi/RC3"
- "folder deploy-all" → "scimarketplace/deploy-all"
- "for scimarketplace and folder quote and sub folder RC1" → "scimarketplace/quote_multi/RC1"

Return ONLY the folder path, nothing else. No explanations, no quotes, just the path."""

        messages = [{"role": "user", "content": prompt}]
        response = router.chat(messages)
        
        # Clean the response
        folder_path = response.strip().replace('"', '').replace("'", "")
        
        # Validate the response
        if folder_path and folder_path.startswith("scimarketplace/"):
            debug_logger.info(f"LLM extracted folder path: {folder_path}")
            return folder_path
        else:
            debug_logger.warning(f"LLM returned invalid folder path: {folder_path}")
            # Fallback to regex-based extraction
            return _extract_folder_path_with_regex(query)
            
    except Exception as e:
        debug_logger.error(f"LLM folder path extraction failed: {e}")
        # Fallback to regex-based extraction
        return _extract_folder_path_with_regex(query)

def _extract_folder_path_with_regex(query: str) -> str:
    """Fallback regex-based folder path extraction"""
    debug_logger.info("Using regex fallback for folder path extraction")
    
    # Handle deploy-all case
    if "deploy-all" in query.lower():
        return "scimarketplace/deploy-all"
    
    # Extract repository and branch using regex (case-insensitive search but preserve case)
    # Pattern: folder <repo> and sub folder <branch>
    pattern = r"folder\s+([a-zA-Z0-9_]+)(?:\s+and\s+sub\s+folder\s+([a-zA-Z0-9_]+))?"
    match = re.search(pattern, query, re.IGNORECASE)
    
    if match:
        repo = match.group(1)
        branch = match.group(2)
        
        # Add _multi suffix if not present
        if not repo.endswith("_multi"):
            repo += "_multi"
        
        if branch:
            return f"scimarketplace/{repo}/{branch}"
        else:
            return f"scimarketplace/{repo}"
    
    # Fallback to default
    return "scimarketplace/deploy-all"

def interactive_jenkins(query: str):
    """Handle Jenkins commands in interactive mode"""
    debug_logger.log_function_call("interactive_jenkins", kwargs={"query": query})
    
    try:
        jenkins = JenkinsClient()
        
        if not jenkins.test_connection():
            debug_logger.error("Jenkins connection failed - JENKINS_URL or JENKINS_TOKEN not configured")
            console.print("[red]Jenkins connection failed. Please check your JENKINS_URL and JENKINS_TOKEN[/red]")
            return
        
        # Use LLM-based keyword detection
        detection_result = keyword_detector.detect_keywords('jenkins', query)
        
        # Show detection confidence for debugging
        if detection_result.confidence < 0.7:
            console.print(f"[dim]LLM detection confidence: {detection_result.confidence:.2f}[/dim]")
        
        # Handle the detected action
        action = detection_result.action
        extracted_values = detection_result.extracted_values
        
        if action == 'builds':
            debug_logger.info("Processing build status query")
            
            # Extract values from LLM detection
            num_builds = extracted_values.get('count', 5)
            folder = extracted_values.get('folder_path', 'scimarketplace/deploy-all')
            
            debug_logger.info(f"Build status query: {num_builds} builds from {folder}")
            console.print(f"[cyan]🔍 Getting last {num_builds} build status from '{folder}'...[/cyan]")
            
            # Handle deploy-all folder specially - it contains builds directly
            if "deploy-all" in folder:
                debug_logger.info("Processing deploy-all folder - getting builds directly")
                # For deploy-all, get builds directly from the folder
                all_recent_builds = jenkins.get_folder_builds(folder, 24)
                debug_logger.info(f"Found {len(all_recent_builds)} builds directly from deploy-all folder")
            else:
                # Regular folder processing - get jobs first, then builds from each job
                jobs = jenkins.get_folder_jobs(folder)
                if not jobs:
                    console.print(f"[yellow]ℹ️  No jobs found in folder '{folder}'[/yellow]")
                    return
                
                debug_logger.info(f"Found {len(jobs)} jobs in folder '{folder}'")
                
                # Get recent builds for each job
                all_recent_builds = []
                for job in jobs:
                    job_name = job.get("name", "")
                    job_path = f"{folder}/{job_name}" if folder else job_name
                    
                    debug_logger.info(f"Processing job: {job_name} (path: {job_path})")
                    
                    # Get recent builds (last 24 hours to ensure we have enough data)
                    recent_builds = jenkins.get_recent_builds(job_path, 24)
                    debug_logger.info(f"Found {len(recent_builds)} recent builds for job {job_name}")
                    
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
                    status_color = "green" if build["result"] == "SUCCESS" else "red" if build["result"] in ["FAILURE", "UNSTABLE", "ABORTED"] else "yellow"
                    table.add_row(
                        build["job_name"],
                        str(build["number"]),
                        f"[{status_color}]{build['result']}[/{status_color}]",
                        build["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                        f"{build['duration']/1000:.1f}s" if build['duration'] else "N/A"
                    )
                
                console.print(table)
            else:
                console.print(f"[yellow]ℹ️  No recent builds found in folder '{folder}'[/yellow]")
                
        elif action == 'failed_jobs':
            # Extract values from LLM detection
            folder = extracted_values.get('folder_path', 'scimarketplace/deploy-all')
            hours = extracted_values.get('hours', 4)
            
            console.print(f"[cyan]🔍 Searching for failed jobs in '{folder}' (last {hours} hours)...[/cyan]")
            failed_jobs = jenkins.find_failed_jobs_in_folder(folder, hours)
            jenkins.display_failed_jobs_table(failed_jobs)
            
        elif action == 'running_jobs':
            # Extract values from LLM detection
            folder = extracted_values.get('folder_path', 'scimarketplace/deploy-all')
            
            console.print(f"[cyan]🔍 Searching for running jobs in '{folder}'...[/cyan]")
            running_jobs = jenkins.find_running_jobs_in_folder(folder)
            jenkins.display_running_jobs_table(running_jobs)
            
        elif action == 'analyze_failure':
            # Extract values from LLM detection
            job_name = extracted_values.get('job_name')
            build_number = extracted_values.get('build_number')
            
            if job_name:
                console.print(f"[cyan]🔍 Analyzing failure for job '{job_name}'...[/cyan]")
                jenkins.analyze_job_failure(job_name, build_number)
            else:
                console.print("[red]Could not identify job name for failure analysis[/red]")
                
        else:
            # Default to build status for unknown actions
            debug_logger.info("Processing default build status query")
            
            # Extract values from LLM detection
            num_builds = extracted_values.get('count', 5)
            folder = extracted_values.get('folder_path', 'scimarketplace/deploy-all')
            
            debug_logger.info(f"Build status query: {num_builds} builds from {folder}")
            console.print(f"[cyan]🔍 Getting last {num_builds} build status from '{folder}'...[/cyan]")
            
            # Handle deploy-all folder specially - it contains builds directly
            if "deploy-all" in folder:
                debug_logger.info("Processing deploy-all folder - getting builds directly")
                # For deploy-all, get builds directly from the folder
                all_recent_builds = jenkins.get_folder_builds(folder, 24)
                debug_logger.info(f"Found {len(all_recent_builds)} builds directly from deploy-all folder")
            else:
                # Regular folder processing - get jobs first, then builds from each job
                jobs = jenkins.get_folder_jobs(folder)
                if not jobs:
                    console.print(f"[yellow]ℹ️  No jobs found in folder '{folder}'[/yellow]")
                    return
                
                debug_logger.info(f"Found {len(jobs)} jobs in folder '{folder}'")
                
                # Get recent builds for each job
                all_recent_builds = []
                for job in jobs:
                    job_name = job.get("name", "")
                    job_path = f"{folder}/{job_name}" if folder else job_name
                    
                    debug_logger.info(f"Processing job: {job_name} (path: {job_path})")
                    
                    # Get recent builds (last 24 hours to ensure we have enough data)
                    recent_builds = jenkins.get_recent_builds(job_path, 24)
                    debug_logger.info(f"Found {len(recent_builds)} recent builds for job {job_name}")
                    
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
                    status_color = "green" if build["result"] == "SUCCESS" else "red" if build["result"] in ["FAILURE", "UNSTABLE", "ABORTED"] else "yellow"
                    table.add_row(
                        build["job_name"],
                        str(build["number"]),
                        f"[{status_color}]{build['result']}[/{status_color}]",
                        build["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                        f"{build['duration']/1000:.1f}s" if build['duration'] else "N/A"
                    )
                
                console.print(table)
            else:
                console.print(f"[yellow]ℹ️  No recent builds found in folder '{folder}'[/yellow]")
            
    except Exception as e:
        debug_logger.error(f"Jenkins interactive error: {e}")
        console.print(f"[red]Jenkins interactive error: {e}[/red]")
