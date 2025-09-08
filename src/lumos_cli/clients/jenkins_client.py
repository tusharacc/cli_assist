"""
Jenkins REST API client for enterprise CI/CD workflows
"""

import os
import requests
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, NamedTuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from ..utils.debug_logger import get_debug_logger

class Error(NamedTuple):
    """Represents a build error with context"""
    line_number: int
    content: str
    type: str
    priority: str = 'medium'

class Warning(NamedTuple):
    """Represents a build warning"""
    line_number: int
    content: str
    type: str

console = Console()
debug_logger = get_debug_logger()

class JenkinsClient:
    """Jenkins REST API client for enterprise workflows"""
    
    def __init__(self, base_url: str = None, token: str = None, username: str = None):
        debug_logger.log_function_call("JenkinsClient.__init__", 
                                     kwargs={"base_url": base_url, "token": token, "username": username})
        
        # Try to get from config manager first, then environment variables
        from ..config.jenkins_config_manager import get_jenkins_config
        config = get_jenkins_config()
        
        if config:
            self.base_url = base_url or config.url
            self.token = token or config.token
            self.username = username or config.username
            debug_logger.info(f"Using Jenkins config file: base_url={self.base_url}, username={self.username}, token={'***' if self.token else 'None'}")
        else:
            self.base_url = base_url or os.getenv("JENKINS_URL")
            self.token = token or os.getenv("JENKINS_TOKEN")
            self.username = username or os.getenv("JENKINS_USERNAME")
            debug_logger.info(f"Using Jenkins environment variables: base_url={self.base_url}, username={self.username}, token={'***' if self.token else 'None'}")
        
        if not self.base_url:
            debug_logger.error("JENKINS_URL environment variable is required")
            raise ValueError("JENKINS_URL environment variable is required")
        if not self.token:
            debug_logger.error("JENKINS_TOKEN environment variable is required")
            raise ValueError("JENKINS_TOKEN environment variable is required")
        
        # Ensure base URL doesn't end with slash
        self.base_url = self.base_url.rstrip("/")
        debug_logger.debug(f"Normalized base URL: {self.base_url}")
        
        # Setup session with authentication
        self.session = requests.Session()
        self.session.auth = (self.username or "api", self.token)
        debug_logger.debug(f"Session auth set: username={self.username or 'api'}")
        
        debug_logger.log_function_return("JenkinsClient.__init__", f"base_url={self.base_url}")
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def test_connection(self) -> bool:
        """Test Jenkins connection and authentication"""
        debug_logger.log_function_call("JenkinsClient.test_connection")
        
        url = f"{self.base_url}/api/json"
        debug_logger.debug(f"Testing Jenkins connection: {url}")
        
        try:
            response = self.session.get(url)
            debug_logger.debug(f"Jenkins connection response: {response.status_code}")
            success = response.status_code == 200
            debug_logger.log_function_return("JenkinsClient.test_connection", success)
            return success
        except Exception as e:
            debug_logger.error(f"Jenkins connection error: {e}")
            console.print(f"[red]Jenkins connection error: {e}[/red]")
            debug_logger.log_function_return("JenkinsClient.test_connection", False)
            return False
    
    def get_folder_jobs(self, folder_path: str) -> List[Dict]:
        """Get all jobs in a specific folder"""
        debug_logger.log_function_call("JenkinsClient.get_folder_jobs", kwargs={"folder_path": folder_path})
        
        try:
            # Convert folder path to Jenkins API format
            api_path = folder_path.replace("/", "/job/")
            url = f"{self.base_url}/job/{api_path}/api/json"
            
            debug_logger.debug(f"Jenkins API path: {api_path}")
            debug_logger.debug(f"Jenkins URL: {url}")
            
            response = self.session.get(url)
            debug_logger.debug(f"Jenkins response status: {response.status_code}")
            
            response.raise_for_status()
            
            data = response.json()
            debug_logger.debug(f"Raw Jenkins API response keys: {list(data.keys())}")
            debug_logger.debug(f"Full Jenkins API response: {json.dumps(data, indent=2)}")
            
            # Handle different Jenkins API response structures
            jobs = data.get("jobs", [])
            
            # If no jobs found, check for alternative structures
            if not jobs:
                debug_logger.warning("No 'jobs' key found in response, checking alternative structures")
                
                # Check if it's a single job (not a folder)
                if data.get("_class") and "job" in data.get("_class", "").lower():
                    debug_logger.info("Response appears to be a single job, not a folder")
                    # Return the job itself as a single-item list
                    jobs = [{"name": data.get("name", "unknown"), "url": data.get("url", ""), "buildable": data.get("buildable", False)}]
                else:
                    # Check for other possible keys
                    possible_keys = ["children", "items", "results"]
                    for key in possible_keys:
                        if key in data and isinstance(data[key], list):
                            debug_logger.info(f"Found jobs under '{key}' key")
                            jobs = data[key]
                            break
                    
                    if not jobs:
                        debug_logger.warning("No jobs found in any expected structure")
                        debug_logger.debug(f"Available keys: {list(data.keys())}")
            
            debug_logger.debug(f"Found {len(jobs)} jobs in folder")
            debug_logger.log_function_return("JenkinsClient.get_folder_jobs", f"Found {len(jobs)} jobs")
            return jobs
        except Exception as e:
            debug_logger.error(f"Error getting folder jobs: {e}")
            console.print(f"[red]Error getting folder jobs: {e}[/red]")
            debug_logger.log_function_return("JenkinsClient.get_folder_jobs", "Error")
            return []
    
    def get_job_info(self, job_path: str) -> Optional[Dict]:
        """Get detailed information about a specific job"""
        debug_logger.log_function_call("JenkinsClient.get_job_info", kwargs={"job_path": job_path})
        
        try:
            api_path = job_path.replace("/", "/job/")
            url = f"{self.base_url}/job/{api_path}/api/json"
            
            debug_logger.debug(f"Job API path: {api_path}")
            debug_logger.debug(f"Job URL: {url}")
            
            response = self.session.get(url)
            debug_logger.debug(f"Job response status: {response.status_code}")
            
            response.raise_for_status()
            
            data = response.json()
            debug_logger.debug(f"Job response keys: {list(data.keys())}")
            debug_logger.debug(f"Job builds count: {len(data.get('builds', []))}")
            
            return data
        except Exception as e:
            debug_logger.error(f"Error getting job info: {e}")
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
    
    def get_folder_builds(self, folder_path: str, hours: int = 24) -> List[Dict]:
        """Get builds directly from a folder (like deploy-all)"""
        debug_logger.log_function_call("JenkinsClient.get_folder_builds", kwargs={"folder_path": folder_path, "hours": hours})
        
        try:
            # Convert folder path to Jenkins API format
            api_path = folder_path.replace("/", "/job/")
            url = f"{self.base_url}/job/{api_path}/api/json"
            
            debug_logger.debug(f"Jenkins folder API path: {api_path}")
            debug_logger.debug(f"Jenkins folder URL: {url}")
            
            response = self.session.get(url)
            debug_logger.debug(f"Jenkins folder response status: {response.status_code}")
            
            response.raise_for_status()
            
            data = response.json()
            debug_logger.debug(f"Raw Jenkins folder API response keys: {list(data.keys())}")
            debug_logger.debug(f"Full Jenkins folder API response: {json.dumps(data, indent=2)}")
            
            # Look for builds directly in the folder
            builds = data.get("builds", [])
            debug_logger.debug(f"Found {len(builds)} builds in folder")
            
            if not builds:
                debug_logger.warning("No builds found in folder response")
                return []
            
            # Process builds and filter by time
            recent_builds = []
            cutoff_time = datetime.now() - timedelta(hours=hours)
            debug_logger.debug(f"Cutoff time: {cutoff_time}")
            
            for i, build in enumerate(builds):
                debug_logger.debug(f"Processing build {i+1}/{len(builds)}: {build}")
                build_info = self.get_build_info(folder_path, build["number"])
                if build_info:
                    build_timestamp = datetime.fromtimestamp(build_info.get("timestamp", 0) / 1000)
                    debug_logger.debug(f"Build timestamp: {build_timestamp}")
                    
                    if build_timestamp >= cutoff_time:
                        build_info["timestamp"] = build_timestamp
                        build_info["job_name"] = folder_path.split("/")[-1]  # Use folder name as job name
                        build_info["job_path"] = folder_path
                        recent_builds.append(build_info)
                        debug_logger.debug(f"Added build {build['number']} to recent builds")
                    else:
                        debug_logger.debug(f"Build {build['number']} is too old, skipping")
                else:
                    debug_logger.warning(f"Could not get build info for build {build['number']}")
            
            debug_logger.info(f"Found {len(recent_builds)} recent builds in folder")
            debug_logger.log_function_return("JenkinsClient.get_folder_builds", f"Found {len(recent_builds)} builds")
            return recent_builds
            
        except Exception as e:
            debug_logger.error(f"Error getting folder builds: {e}")
            console.print(f"[red]Error getting folder builds: {e}[/red]")
            debug_logger.log_function_return("JenkinsClient.get_folder_builds", "Error")
            return []

    def get_recent_builds(self, job_path: str, hours: int = 4) -> List[Dict]:
        """Get recent builds for a job within specified hours"""
        debug_logger.log_function_call("JenkinsClient.get_recent_builds", kwargs={"job_path": job_path, "hours": hours})
        
        try:
            job_info = self.get_job_info(job_path)
            if not job_info:
                debug_logger.warning(f"No job info found for {job_path}")
                return []
            
            builds = job_info.get("builds", [])
            debug_logger.debug(f"Found {len(builds)} total builds for job {job_path}")
            
            recent_builds = []
            cutoff_time = datetime.now() - timedelta(hours=hours)
            debug_logger.debug(f"Cutoff time: {cutoff_time}")
            
            for i, build in enumerate(builds):
                debug_logger.debug(f"Processing build {i+1}/{len(builds)}: {build}")
                build_info = self.get_build_info(job_path, build["number"])
                if build_info:
                    timestamp = build_info.get("timestamp", 0)
                    build_time = datetime.fromtimestamp(timestamp / 1000)
                    debug_logger.debug(f"Build {build['number']} time: {build_time}")
                    
                    if build_time >= cutoff_time:
                        recent_builds.append({
                            "number": build["number"],
                            "status": build_info.get("result", "UNKNOWN"),
                            "timestamp": build_time,
                            "duration": build_info.get("duration", 0),
                            "url": build_info.get("url", "")
                        })
                        debug_logger.debug(f"Added build {build['number']} to recent builds")
                    else:
                        debug_logger.debug(f"Build {build['number']} too old, skipping")
                else:
                    debug_logger.warning(f"Could not get build info for {build['number']}")
            
            debug_logger.debug(f"Found {len(recent_builds)} recent builds")
            debug_logger.log_function_return("JenkinsClient.get_recent_builds", f"Found {len(recent_builds)} recent builds")
            return recent_builds
        except Exception as e:
            debug_logger.error(f"Error getting recent builds: {e}")
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
        """Analyze why a build failed using efficient streaming for large console logs"""
        try:
            build_info = self.get_build_info(job_path, build_number)
            
            if not build_info:
                return {"error": "Build not found"}
            
            # Use efficient streaming analysis for large console logs
            console_url = f"{self.base_url}/job/{job_path.replace('/', '/job/')}/{build_number}/consoleText"
            error_analysis = self._stream_analyze_console(console_url)
            
            analysis = {
                "build_number": build_number,
                "status": build_info.get("result", "UNKNOWN"),
                "duration": build_info.get("duration", 0),
                "timestamp": datetime.fromtimestamp(build_info.get("timestamp", 0) / 1000),
                "url": build_info.get("url", ""),
                "error_analysis": error_analysis
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
    
    def _stream_analyze_console(self, console_url: str) -> Dict:
        """Stream analyze console output for errors efficiently"""
        debug_logger.log_function_call("JenkinsClient._stream_analyze_console", kwargs={"console_url": console_url})
        
        errors = []
        warnings = []
        line_number = 0
        
        try:
            with requests.get(console_url, stream=True, timeout=30) as response:
                response.raise_for_status()
                
                current_chunk = ""
                for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
                    current_chunk += chunk
                    
                    # Process complete lines
                    while '\n' in current_chunk:
                        line, current_chunk = current_chunk.split('\n', 1)
                        line_number += 1
                        
                        # Quick error detection
                        error = self._quick_error_detect(line, line_number)
                        if error:
                            errors.append(error)
                        
                        # Quick warning detection
                        warning = self._quick_warning_detect(line, line_number)
                        if warning:
                            warnings.append(warning)
                
                # Process remaining chunk
                if current_chunk.strip():
                    line_number += 1
                    error = self._quick_error_detect(current_chunk, line_number)
                    if error:
                        errors.append(error)
                    
                    warning = self._quick_warning_detect(current_chunk, line_number)
                    if warning:
                        warnings.append(warning)
            
            # Analyze collected errors
            analysis = self._analyze_errors(errors, warnings)
            debug_logger.log_function_return("JenkinsClient._stream_analyze_console", f"Found {len(errors)} errors, {len(warnings)} warnings")
            return analysis
            
        except Exception as e:
            debug_logger.error(f"Stream analysis failed: {e}")
            return {"error": f"Console analysis failed: {str(e)}"}
    
    def _quick_error_detect(self, line: str, line_number: int) -> Optional[Error]:
        """Fast error detection for streaming analysis"""
        
        # Critical error patterns (most common and important)
        critical_patterns = [
            (r'\[ERROR\]', 'error'),
            (r'BUILD FAILED', 'build_failed'),
            (r'Exception in thread', 'exception'),
            (r'FATAL', 'fatal'),
            (r'Compilation failed', 'compilation'),
            (r'Test failure', 'test_failure'),
            (r'Could not resolve', 'dependency'),
            (r'Missing dependency', 'dependency'),
            (r'Failed to', 'failed'),
            (r'Error:', 'error'),
            (r'Cannot', 'cannot'),
            (r'Unable to', 'unable')
        ]
        
        # Check patterns in order of priority
        for pattern, error_type in critical_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                priority = 'high' if error_type in ['build_failed', 'fatal', 'exception'] else 'medium'
                return Error(
                    line_number=line_number,
                    content=line.strip(),
                    type=error_type,
                    priority=priority
                )
        
        return None
    
    def _quick_warning_detect(self, line: str, line_number: int) -> Optional[Warning]:
        """Fast warning detection for streaming analysis"""
        
        warning_patterns = [
            (r'\[WARNING\]', 'warning'),
            (r'\[WARN\]', 'warning'),
            (r'Deprecated', 'deprecated'),
            (r'Warning:', 'warning'),
            (r'Note:', 'note')
        ]
        
        for pattern, warning_type in warning_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return Warning(
                    line_number=line_number,
                    content=line.strip(),
                    type=warning_type
                )
        
        return None
    
    def _analyze_errors(self, errors: List[Error], warnings: List[Warning]) -> Dict:
        """Analyze errors with smart context extraction"""
        
        if not errors:
            return {
                "error_count": 0,
                "warning_count": len(warnings),
                "analysis": "No errors found",
                "warnings": [{"line": w.line_number, "content": w.content, "type": w.type} for w in warnings[-5:]]
            }
        
        # Group errors by type
        error_groups = self._group_errors_by_type(errors)
        
        # Find root cause (first high-priority error)
        root_cause = self._find_root_cause(errors)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(error_groups)
        
        analysis = {
            "error_count": len(errors),
            "warning_count": len(warnings),
            "root_cause": {
                "line_number": root_cause.line_number,
                "content": root_cause.content,
                "type": root_cause.type,
                "priority": root_cause.priority
            } if root_cause else None,
            "error_groups": error_groups,
            "suggestions": suggestions,
            "warnings": [{"line": w.line_number, "content": w.content, "type": w.type} for w in warnings[-5:]]
        }
        
        return analysis
    
    def _group_errors_by_type(self, errors: List[Error]) -> Dict[str, List[Dict]]:
        """Group errors by type for better analysis"""
        
        groups = {}
        for error in errors:
            error_type = error.type
            if error_type not in groups:
                groups[error_type] = []
            groups[error_type].append({
                "line_number": error.line_number,
                "content": error.content,
                "priority": error.priority
            })
        
        # Sort each group by priority and line number
        for error_type in groups:
            groups[error_type].sort(key=lambda x: (x['priority'], x['line_number']))
        
        return groups
    
    def _find_root_cause(self, errors: List[Error]) -> Optional[Error]:
        """Find the root cause error (first high-priority error)"""
        
        # Sort by priority and line number
        sorted_errors = sorted(errors, key=lambda x: (x.priority, x.line_number))
        
        # Return first high-priority error
        for error in sorted_errors:
            if error.priority == 'high':
                return error
        
        # Fallback to first error
        return sorted_errors[0] if sorted_errors else None
    
    def _generate_suggestions(self, error_groups: Dict[str, List[Dict]]) -> List[str]:
        """Generate suggestions based on error types"""
        
        suggestions = []
        
        if 'compilation' in error_groups:
            suggestions.append("Check compilation errors - verify syntax and dependencies")
        
        if 'test_failure' in error_groups:
            suggestions.append("Review test failures - check test data and assertions")
        
        if 'dependency' in error_groups:
            suggestions.append("Resolve dependency issues - check repository access and versions")
        
        if 'build_failed' in error_groups:
            suggestions.append("Build process failed - check build configuration and environment")
        
        if 'exception' in error_groups:
            suggestions.append("Runtime exception occurred - check application logs and configuration")
        
        if 'fatal' in error_groups:
            suggestions.append("Fatal error detected - check system resources and critical dependencies")
        
        return suggestions
    
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
        """Display build failure analysis with enhanced error reporting"""
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
        
        # Enhanced failure analysis
        error_analysis = analysis.get("error_analysis", {})
        
        if error_analysis.get("error_count", 0) > 0:
            console.print(f"\n[red]❌ Found {error_analysis['error_count']} errors, {error_analysis.get('warning_count', 0)} warnings[/red]")
            
            # Show root cause
            root_cause = error_analysis.get("root_cause")
            if root_cause:
                console.print(f"\n[red]🎯 Root Cause (Line {root_cause['line_number']}):[/red]")
                console.print(f"[red]{root_cause['content']}[/red]")
                console.print(f"[dim]Type: {root_cause['type']} | Priority: {root_cause['priority']}[/dim]")
            
            # Show error groups
            error_groups = error_analysis.get("error_groups", {})
            for error_type, errors in error_groups.items():
                console.print(f"\n[yellow]📋 {error_type.replace('_', ' ').title()} Errors:[/yellow]")
                for error in errors[:5]:  # Show first 5 errors of each type
                    console.print(f"[red]  Line {error['line_number']}: {error['content'][:100]}{'...' if len(error['content']) > 100 else ''}[/red]")
            
            # Show suggestions
            suggestions = error_analysis.get("suggestions", [])
            if suggestions:
                console.print(f"\n[blue]💡 Suggestions:[/blue]")
                for suggestion in suggestions:
                    console.print(f"[blue]  • {suggestion}[/blue]")
        
        elif error_analysis.get("warning_count", 0) > 0:
            console.print(f"\n[yellow]⚠️  Found {error_analysis['warning_count']} warnings (no errors)[/yellow]")
            warnings = error_analysis.get("warnings", [])
            for warning in warnings[:5]:
                console.print(f"[yellow]  Line {warning['line']}: {warning['content'][:100]}{'...' if len(warning['content']) > 100 else ''}[/yellow]")
        
        else:
            console.print(f"\n[green]✅ No errors or warnings found in console output[/green]")
