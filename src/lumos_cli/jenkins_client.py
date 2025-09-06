"""
Jenkins REST API client for enterprise CI/CD workflows
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

class JenkinsClient:
    """Jenkins REST API client for enterprise workflows"""
    
    def __init__(self, base_url: str = None, token: str = None, username: str = None):
        self.base_url = base_url or os.getenv("JENKINS_URL")
        self.token = token or os.getenv("JENKINS_TOKEN")
        self.username = username or os.getenv("JENKINS_USERNAME")
        
        if not self.base_url:
            raise ValueError("JENKINS_URL environment variable is required")
        if not self.token:
            raise ValueError("JENKINS_TOKEN environment variable is required")
        
        # Ensure base URL doesn't end with slash
        self.base_url = self.base_url.rstrip("/")
        
        # Setup session with authentication
        self.session = requests.Session()
        self.session.auth = (self.username or "api", self.token)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def test_connection(self) -> bool:
        """Test Jenkins connection and authentication"""
        try:
            response = self.session.get(f"{self.base_url}/api/json")
            return response.status_code == 200
        except Exception as e:
            console.print(f"[red]Jenkins connection error: {e}[/red]")
            return False
    
    def get_folder_jobs(self, folder_path: str) -> List[Dict]:
        """Get all jobs in a specific folder"""
        try:
            # Convert folder path to Jenkins API format
            api_path = folder_path.replace("/", "/job/")
            url = f"{self.base_url}/job/{api_path}/api/json"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            return data.get("jobs", [])
        except Exception as e:
            console.print(f"[red]Error getting folder jobs: {e}[/red]")
            return []
    
    def get_job_info(self, job_path: str) -> Optional[Dict]:
        """Get detailed information about a specific job"""
        try:
            api_path = job_path.replace("/", "/job/")
            url = f"{self.base_url}/job/{api_path}/api/json"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            console.print(f"[red]Error getting job info: {e}[/red]")
            return None
    
    def get_build_info(self, job_path: str, build_number: int) -> Optional[Dict]:
        """Get information about a specific build"""
        try:
            api_path = job_path.replace("/", "/job/")
            url = f"{self.base_url}/job/{api_path}/{build_number}/api/json"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            console.print(f"[red]Error getting build info: {e}[/red]")
            return None
    
    def get_build_console(self, job_path: str, build_number: int) -> Optional[str]:
        """Get console output for a specific build"""
        try:
            api_path = job_path.replace("/", "/job/")
            url = f"{self.base_url}/job/{api_path}/{build_number}/consoleText"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.text
        except Exception as e:
            console.print(f"[red]Error getting console output: {e}[/red]")
            return None
    
    def get_build_parameters(self, job_path: str, build_number: int) -> List[Dict]:
        """Get build parameters for a specific build"""
        try:
            api_path = job_path.replace("/", "/job/")
            url = f"{self.base_url}/job/{api_path}/{build_number}/api/json?tree=actions[parameters[*]]"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            parameters = []
            
            for action in data.get("actions", []):
                if "parameters" in action:
                    for param in action["parameters"]:
                        parameters.append({
                            "name": param.get("name", ""),
                            "value": param.get("value", ""),
                            "description": param.get("description", "")
                        })
            
            return parameters
        except Exception as e:
            console.print(f"[red]Error getting build parameters: {e}[/red]")
            return []
    
    def get_recent_builds(self, job_path: str, hours: int = 4) -> List[Dict]:
        """Get recent builds for a job within specified hours"""
        try:
            job_info = self.get_job_info(job_path)
            if not job_info:
                return []
            
            builds = job_info.get("builds", [])
            recent_builds = []
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            for build in builds:
                build_info = self.get_build_info(job_path, build["number"])
                if build_info:
                    timestamp = build_info.get("timestamp", 0)
                    build_time = datetime.fromtimestamp(timestamp / 1000)
                    
                    if build_time >= cutoff_time:
                        recent_builds.append({
                            "number": build["number"],
                            "status": build_info.get("result", "UNKNOWN"),
                            "timestamp": build_time,
                            "duration": build_info.get("duration", 0),
                            "url": build_info.get("url", "")
                        })
            
            return recent_builds
        except Exception as e:
            console.print(f"[red]Error getting recent builds: {e}[/red]")
            return []
    
    def find_failed_jobs_in_folder(self, folder_path: str, hours: int = 4) -> List[Dict]:
        """Find failed jobs in a folder within specified hours"""
        try:
            jobs = self.get_folder_jobs(folder_path)
            failed_jobs = []
            
            for job in jobs:
                job_name = job.get("name", "")
                job_path = f"{folder_path}/{job_name}" if folder_path else job_name
                
                recent_builds = self.get_recent_builds(job_path, hours)
                
                for build in recent_builds:
                    if build["status"] in ["FAILURE", "UNSTABLE", "ABORTED"]:
                        failed_jobs.append({
                            "job_name": job_name,
                            "job_path": job_path,
                            "build_number": build["number"],
                            "status": build["status"],
                            "timestamp": build["timestamp"],
                            "duration": build["duration"],
                            "url": build["url"]
                        })
            
            return failed_jobs
        except Exception as e:
            console.print(f"[red]Error finding failed jobs: {e}[/red]")
            return []
    
    def find_running_jobs_in_folder(self, folder_path: str) -> List[Dict]:
        """Find currently running jobs in a folder"""
        try:
            jobs = self.get_folder_jobs(folder_path)
            running_jobs = []
            
            for job in jobs:
                job_name = job.get("name", "")
                job_path = f"{folder_path}/{job_name}" if folder_path else job_name
                
                job_info = self.get_job_info(job_path)
                if job_info and job_info.get("color", "").startswith("blue_anime"):
                    # Job is currently running
                    last_build = job_info.get("lastBuild", {})
                    running_jobs.append({
                        "job_name": job_name,
                        "job_path": job_path,
                        "build_number": last_build.get("number", "N/A"),
                        "url": last_build.get("url", "")
                    })
            
            return running_jobs
        except Exception as e:
            console.print(f"[red]Error finding running jobs: {e}[/red]")
            return []
    
    def find_jobs_by_repository_and_branch(self, repository: str, branch: str) -> List[Dict]:
        """Find jobs for a specific repository and branch"""
        try:
            # Look in scimarketplace folder for repository with _multi suffix
            folder_path = f"scimarketplace/{repository}_multi"
            branch_folder = f"{folder_path}/{branch}"
            
            jobs = self.get_folder_jobs(branch_folder)
            job_list = []
            
            for job in jobs:
                job_name = job.get("name", "")
                job_path = f"{branch_folder}/{job_name}"
                
                job_info = self.get_job_info(job_path)
                if job_info:
                    job_list.append({
                        "job_name": job_name,
                        "job_path": job_path,
                        "status": job_info.get("color", "UNKNOWN"),
                        "last_build": job_info.get("lastBuild", {}).get("number", "N/A"),
                        "url": job_info.get("url", "")
                    })
            
            return job_list
        except Exception as e:
            console.print(f"[red]Error finding jobs by repository and branch: {e}[/red]")
            return []
    
    def analyze_build_failure(self, job_path: str, build_number: int) -> Dict:
        """Analyze why a build failed"""
        try:
            build_info = self.get_build_info(job_path, build_number)
            console_output = self.get_build_console(job_path, build_number)
            
            if not build_info:
                return {"error": "Build not found"}
            
            analysis = {
                "build_number": build_number,
                "status": build_info.get("result", "UNKNOWN"),
                "duration": build_info.get("duration", 0),
                "timestamp": datetime.fromtimestamp(build_info.get("timestamp", 0) / 1000),
                "url": build_info.get("url", ""),
                "console_output": console_output,
                "failure_analysis": self._analyze_console_output(console_output)
            }
            
            return analysis
        except Exception as e:
            console.print(f"[red]Error analyzing build failure: {e}[/red]")
            return {"error": str(e)}
    
    def _analyze_console_output(self, console_output: str) -> Dict:
        """Analyze console output to identify failure reasons"""
        if not console_output:
            return {"error": "No console output available"}
        
        lines = console_output.split('\n')
        error_lines = []
        warning_lines = []
        
        # Common error patterns
        error_patterns = [
            "ERROR", "FAILED", "Exception", "Error:", "Failed to",
            "BUILD FAILED", "Compilation failed", "Test failed"
        ]
        
        warning_patterns = [
            "WARNING", "WARN", "Deprecated", "Warning:"
        ]
        
        for i, line in enumerate(lines):
            line_upper = line.upper()
            
            for pattern in error_patterns:
                if pattern.upper() in line_upper:
                    error_lines.append({
                        "line_number": i + 1,
                        "content": line.strip(),
                        "context": lines[max(0, i-2):i+3]  # Include context
                    })
                    break
            
            for pattern in warning_patterns:
                if pattern.upper() in line_upper:
                    warning_lines.append({
                        "line_number": i + 1,
                        "content": line.strip()
                    })
                    break
        
        return {
            "error_count": len(error_lines),
            "warning_count": len(warning_lines),
            "errors": error_lines[-10:],  # Last 10 errors
            "warnings": warning_lines[-5:],  # Last 5 warnings
            "total_lines": len(lines)
        }
    
    def display_failed_jobs_table(self, failed_jobs: List[Dict]):
        """Display failed jobs in a formatted table"""
        if not failed_jobs:
            console.print("[green]✅ No failed jobs found in the specified time period[/green]")
            return
        
        table = Table(title="Failed Jobs", box=box.ROUNDED)
        table.add_column("Job Name", style="cyan")
        table.add_column("Build #", style="yellow")
        table.add_column("Status", style="red")
        table.add_column("Timestamp", style="blue")
        table.add_column("Duration", style="green")
        
        for job in failed_jobs:
            table.add_row(
                job["job_name"],
                str(job["build_number"]),
                job["status"],
                job["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                f"{job['duration']/1000:.1f}s" if job['duration'] else "N/A"
            )
        
        console.print(table)
    
    def display_running_jobs_table(self, running_jobs: List[Dict]):
        """Display running jobs in a formatted table"""
        if not running_jobs:
            console.print("[yellow]ℹ️  No jobs currently running[/yellow]")
            return
        
        table = Table(title="Running Jobs", box=box.ROUNDED)
        table.add_column("Job Name", style="cyan")
        table.add_column("Build #", style="yellow")
        table.add_column("Status", style="green")
        
        for job in running_jobs:
            table.add_row(
                job["job_name"],
                str(job["build_number"]),
                "RUNNING"
            )
        
        console.print(table)
    
    def display_build_parameters_table(self, parameters: List[Dict]):
        """Display build parameters in a formatted table"""
        if not parameters:
            console.print("[yellow]ℹ️  No build parameters found[/yellow]")
            return
        
        table = Table(title="Build Parameters", box=box.ROUNDED)
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Description", style="blue")
        
        for param in parameters:
            table.add_row(
                param["name"],
                str(param["value"]),
                param["description"] or "N/A"
            )
        
        console.print(table)
    
    def display_failure_analysis(self, analysis: Dict):
        """Display build failure analysis"""
        if "error" in analysis:
            console.print(f"[red]❌ Error: {analysis['error']}[/red]")
            return
        
        # Build info panel
        info_text = f"""
Build #{analysis['build_number']} - {analysis['status']}
Duration: {analysis['duration']/1000:.1f}s
Timestamp: {analysis['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
URL: {analysis['url']}
        """.strip()
        
        console.print(Panel(info_text, title="Build Information", border_style="blue"))
        
        # Failure analysis
        failure = analysis.get("failure_analysis", {})
        if failure.get("error_count", 0) > 0:
            console.print(f"\n[red]❌ Found {failure['error_count']} errors:[/red]")
            
            for error in failure.get("errors", []):
                console.print(f"[red]Line {error['line_number']}: {error['content']}[/red]")
                # Show context
                for ctx_line in error.get("context", []):
                    console.print(f"[dim]  {ctx_line}[/dim]")
                console.print()
        
        if failure.get("warning_count", 0) > 0:
            console.print(f"[yellow]⚠️  Found {failure['warning_count']} warnings[/yellow]")
        
        # Console output (last 50 lines)
        console_output = analysis.get("console_output", "")
        if console_output:
            lines = console_output.split('\n')
            last_lines = lines[-50:] if len(lines) > 50 else lines
            
            console.print(Panel(
                '\n'.join(last_lines),
                title="Console Output (Last 50 lines)",
                border_style="yellow"
            ))
