"""
AppDynamics REST API client for SRE monitoring and alerting
"""

import os
import requests
import urllib3
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from ..utils.debug_logger import get_debug_logger

# Disable SSL warnings for enterprise environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()
debug_logger = get_debug_logger()

class AppDynamicsClient:
    """Client for AppDynamics REST API operations"""
    
    def __init__(self, base_url: str = None, client_id: str = None, client_secret: str = None):
        """Initialize AppDynamics client with OAuth2 authentication"""
        self.base_url = base_url or os.getenv('APPDYNAMICS_BASE_URL', '')
        self.client_id = client_id or os.getenv('APPDYNAMICS_CLIENT_ID', '')
        self.client_secret = client_secret or os.getenv('APPDYNAMICS_CLIENT_SECRET', '')
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for enterprise environments
        self.access_token = None
        self.token_expires_at = None
        
        debug_logger.log_function_call("AppDynamicsClient.__init__", kwargs={
            "base_url": self.base_url,
            "client_id": self.client_id
        })
    
    def _get_access_token(self) -> Optional[str]:
        """Get OAuth2 access token using client credentials flow"""
        debug_logger.log_function_call("AppDynamicsClient._get_access_token")
        
        # Check if we have a valid token
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            debug_logger.log_function_return("AppDynamicsClient._get_access_token", "Using cached token")
            return self.access_token
        
        try:
            # Prepare OAuth2 token request
            token_url = f"{self.base_url}/controller/api/oauth/access_token"
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            debug_logger.info(f"Requesting OAuth2 token from: {token_url}")
            response = self.session.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)  # Default to 1 hour
            
            # Set expiration time (subtract 5 minutes for safety)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
            
            # Set up session headers for subsequent requests
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/vnd.appd.events+text;v=2'
            })
            
            debug_logger.info("OAuth2 token obtained successfully")
            debug_logger.log_function_return("AppDynamicsClient._get_access_token", "Success")
            return self.access_token
            
        except Exception as e:
            debug_logger.error(f"Failed to get OAuth2 token: {e}")
            debug_logger.log_function_return("AppDynamicsClient._get_access_token", "Failed")
            return None
    
    def test_connection(self) -> bool:
        """Test AppDynamics connection"""
        debug_logger.log_function_call("AppDynamicsClient.test_connection")
        
        try:
            # Get OAuth2 token first
            if not self._get_access_token():
                debug_logger.error("Failed to obtain OAuth2 token")
                debug_logger.log_function_return("AppDynamicsClient.test_connection", "Token failed")
                return False
            
            # Test with a simple API call
            response = self.session.get(f"{self.base_url}/controller/rest/applications?output=JSON")
            if response.status_code == 200:
                debug_logger.info("AppDynamics connection successful")
                debug_logger.log_function_return("AppDynamicsClient.test_connection", "Success")
                return True
            else:
                debug_logger.error(f"AppDynamics connection failed: {response.status_code}")
                debug_logger.log_function_return("AppDynamicsClient.test_connection", "Failed")
                return False
        except Exception as e:
            debug_logger.error(f"AppDynamics connection error: {e}")
            debug_logger.log_function_return("AppDynamicsClient.test_connection", "Error")
            return False
    
    def get_applications(self) -> List[Dict]:
        """Get list of applications"""
        debug_logger.log_function_call("AppDynamicsClient.get_applications")
        
        try:
            # Ensure we have a valid token
            if not self._get_access_token():
                debug_logger.error("Failed to obtain OAuth2 token")
                debug_logger.log_function_return("AppDynamicsClient.get_applications", "Token failed")
                return []
            
            response = self.session.get(f"{self.base_url}/controller/rest/applications?output=JSON")
            response.raise_for_status()
            applications = response.json()
            
            debug_logger.info(f"Retrieved {len(applications)} applications")
            debug_logger.log_function_return("AppDynamicsClient.get_applications", f"Found {len(applications)} apps")
            return applications
        except Exception as e:
            debug_logger.error(f"Failed to get applications: {e}")
            debug_logger.log_function_return("AppDynamicsClient.get_applications", "Failed")
            return []
    
    def get_application_id(self, app_name: str) -> Optional[int]:
        """Get application ID by name"""
        debug_logger.log_function_call("AppDynamicsClient.get_application_id", kwargs={"app_name": app_name})
        
        applications = self.get_applications()
        for app in applications:
            if app.get('name', '').lower() == app_name.lower():
                app_id = app.get('id')
                debug_logger.log_function_return("AppDynamicsClient.get_application_id", f"Found ID: {app_id}")
                return app_id
        
        debug_logger.warning(f"Application '{app_name}' not found")
        debug_logger.log_function_return("AppDynamicsClient.get_application_id", "Not found")
        return None
    
    def get_servers(self, app_id: int) -> List[Dict]:
        """Get servers for an application"""
        debug_logger.log_function_call("AppDynamicsClient.get_servers", kwargs={"app_id": app_id})
        
        try:
            response = self.session.get(f"{self.base_url}/controller/rest/applications/{app_id}/nodes?output=JSON")
            response.raise_for_status()
            servers = response.json()
            
            debug_logger.info(f"Retrieved {len(servers)} servers for app {app_id}")
            debug_logger.log_function_return("AppDynamicsClient.get_servers", f"Found {len(servers)} servers")
            return servers
        except Exception as e:
            debug_logger.error(f"Failed to get servers: {e}")
            debug_logger.log_function_return("AppDynamicsClient.get_servers", "Failed")
            return []
    
    def get_server_metrics(self, app_id: int, server_id: int, metric_path: str = "Application Infrastructure Performance|Machine Agent|Hardware Resources|*", duration_in_mins: int = 60) -> List[Dict]:
        """Get server metrics"""
        debug_logger.log_function_call("AppDynamicsClient.get_server_metrics", kwargs={
            "app_id": app_id, "server_id": server_id, "metric_path": metric_path, "duration_in_mins": duration_in_mins
        })
        
        try:
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = end_time - (duration_in_mins * 60 * 1000)
            
            params = {
                'application-id': app_id,
                'metric-path': metric_path,
                'time-range-type': 'BEFORE_NOW',
                'duration-in-mins': duration_in_mins,
                'rollup': 'true',
                'output': 'JSON'
            }
            
            response = self.session.get(f"{self.base_url}/controller/rest/applications/{app_id}/nodes/{server_id}/metrics", params=params)
            response.raise_for_status()
            metrics = response.json()
            
            debug_logger.info(f"Retrieved {len(metrics)} metrics for server {server_id}")
            debug_logger.log_function_return("AppDynamicsClient.get_server_metrics", f"Found {len(metrics)} metrics")
            return metrics
        except Exception as e:
            debug_logger.error(f"Failed to get server metrics: {e}")
            debug_logger.log_function_return("AppDynamicsClient.get_server_metrics", "Failed")
            return []
    
    def get_resource_utilization(self, app_id: int, server_id: int, duration_in_mins: int = 60) -> Dict[str, Any]:
        """Get comprehensive resource utilization for a server
        
        Uses correct AppDynamics metric paths:
        - CPU: Application Infrastructure Performance|Machine Agent|Hardware Resources|CPU|*
          - %busy (overall CPU usage)
          - %System (system CPU time)
          - %User (user CPU time)
        - Memory: Application Infrastructure Performance|Machine Agent|Hardware Resources|Memory|*
          - Used % (memory usage percentage)
          - Used MB (used memory in MB)
          - Free MB (free memory in MB)
          - Total MB (total memory in MB)
        - Disk: Application Infrastructure Performance|Machine Agent|Hardware Resources|Disk|*
          - Used % (disk usage percentage)
          - Used GB (used disk space in GB)
          - Free GB (free disk space in GB)
          - Total GB (total disk space in GB)
        - Network: Application Infrastructure Performance|Machine Agent|Hardware Resources|Network|*
          - Bytes Received/sec (bytes received per second)
          - Bytes Transmitted/sec (bytes transmitted per second)
          - Packets Received/sec (packets received per second)
          - Packets Transmitted/sec (packets transmitted per second)
        """
        debug_logger.log_function_call("AppDynamicsClient.get_resource_utilization", kwargs={
            "app_id": app_id, "server_id": server_id, "duration_in_mins": duration_in_mins
        })
        
        try:
            # Get CPU metrics using correct AppDynamics metric path
            cpu_metrics = self.get_server_metrics(app_id, server_id, "Application Infrastructure Performance|Machine Agent|Hardware Resources|CPU|*", duration_in_mins)
            
            # Get Memory metrics using correct AppDynamics metric path
            memory_metrics = self.get_server_metrics(app_id, server_id, "Application Infrastructure Performance|Machine Agent|Hardware Resources|Memory|*", duration_in_mins)
            
            # Get Disk metrics using correct AppDynamics metric path
            disk_metrics = self.get_server_metrics(app_id, server_id, "Application Infrastructure Performance|Machine Agent|Hardware Resources|Disk|*", duration_in_mins)
            
            # Get Network metrics using correct AppDynamics metric path
            network_metrics = self.get_server_metrics(app_id, server_id, "Application Infrastructure Performance|Machine Agent|Hardware Resources|Network|*", duration_in_mins)
            
            utilization = {
                'cpu': self._extract_cpu_metrics(cpu_metrics),
                'memory': self._extract_memory_metrics(memory_metrics),
                'disk': self._extract_disk_metrics(disk_metrics),
                'network': self._extract_network_metrics(network_metrics),
                'timestamp': datetime.now().isoformat()
            }
            
            debug_logger.log_function_return("AppDynamicsClient.get_resource_utilization", "Success")
            return utilization
        except Exception as e:
            debug_logger.error(f"Failed to get resource utilization: {e}")
            debug_logger.log_function_return("AppDynamicsClient.get_resource_utilization", "Failed")
            return {}
    
    def _extract_cpu_metrics(self, cpu_metrics: List[Dict]) -> Dict[str, Any]:
        """Extract CPU metrics from raw data using correct AppDynamics metric names"""
        cpu_data = {}
        
        # Debug: Log all available metric names
        debug_logger.info(f"Available CPU metrics: {[m.get('metricName', '') for m in cpu_metrics]}")
        
        for metric in cpu_metrics:
            metric_name = metric.get('metricName', '')
            metric_values = metric.get('metricValues', [])
            
            # Debug: Log each metric name and value
            latest_value = self._get_latest_value(metric_values)
            debug_logger.info(f"CPU metric: '{metric_name}' = {latest_value}")
            
            # Look for %busy (overall CPU usage)
            if '%busy' in metric_name.lower():
                cpu_data['usage_percent'] = latest_value
                debug_logger.info(f"Found %busy metric: {latest_value}")
            # Look for %System (system CPU time)
            elif '%system' in metric_name.lower():
                cpu_data['system_time_percent'] = latest_value
                debug_logger.info(f"Found %system metric: {latest_value}")
            # Look for %User (user CPU time)
            elif '%user' in metric_name.lower():
                cpu_data['user_time_percent'] = latest_value
                debug_logger.info(f"Found %user metric: {latest_value}")
            # Look for any CPU percentage metric
            elif 'cpu' in metric_name.lower() and '%' in metric_name.lower():
                if 'usage_percent' not in cpu_data:  # Use first CPU percentage found as usage
                    cpu_data['usage_percent'] = latest_value
                    debug_logger.info(f"Found CPU percentage metric: {latest_value}")
            # Look for any metric with "used" and percentage
            elif 'used' in metric_name.lower() and '%' in metric_name.lower():
                if 'usage_percent' not in cpu_data:  # Use first usage percentage found
                    cpu_data['usage_percent'] = latest_value
                    debug_logger.info(f"Found usage percentage metric: {latest_value}")
            # Look for any metric with "utilization" and percentage
            elif 'utilization' in metric_name.lower() and '%' in metric_name.lower():
                if 'usage_percent' not in cpu_data:  # Use first utilization percentage found
                    cpu_data['usage_percent'] = latest_value
                    debug_logger.info(f"Found utilization percentage metric: {latest_value}")
        
        # If still no usage_percent found, try to use any percentage value
        if 'usage_percent' not in cpu_data:
            for metric in cpu_metrics:
                metric_name = metric.get('metricName', '')
                metric_values = metric.get('metricValues', [])
                latest_value = self._get_latest_value(metric_values)
                
                if '%' in metric_name and latest_value is not None:
                    cpu_data['usage_percent'] = latest_value
                    debug_logger.info(f"Using fallback CPU metric: {metric_name} = {latest_value}")
                    break
        
        debug_logger.info(f"Final CPU data: {cpu_data}")
        return cpu_data
    
    def _extract_memory_metrics(self, memory_metrics: List[Dict]) -> Dict[str, Any]:
        """Extract Memory metrics from raw data using correct AppDynamics metric names"""
        memory_data = {}
        for metric in memory_metrics:
            metric_name = metric.get('metricName', '')
            metric_values = metric.get('metricValues', [])
            
            # Look for memory usage percentage
            if 'used %' in metric_name.lower() or 'usage %' in metric_name.lower():
                memory_data['usage_percent'] = self._get_latest_value(metric_values)
            # Look for used memory in MB
            elif 'used' in metric_name.lower() and 'mb' in metric_name.lower():
                memory_data['used_mb'] = self._get_latest_value(metric_values)
            # Look for free memory in MB
            elif 'free' in metric_name.lower() and 'mb' in metric_name.lower():
                memory_data['free_mb'] = self._get_latest_value(metric_values)
            # Look for total memory
            elif 'total' in metric_name.lower() and 'mb' in metric_name.lower():
                memory_data['total_mb'] = self._get_latest_value(metric_values)
        
        return memory_data
    
    def _extract_disk_metrics(self, disk_metrics: List[Dict]) -> Dict[str, Any]:
        """Extract Disk metrics from raw data using correct AppDynamics metric names"""
        disk_data = {}
        for metric in disk_metrics:
            metric_name = metric.get('metricName', '')
            metric_values = metric.get('metricValues', [])
            
            # Look for disk usage percentage
            if 'used %' in metric_name.lower() or 'usage %' in metric_name.lower():
                disk_data['usage_percent'] = self._get_latest_value(metric_values)
            # Look for used disk space in GB
            elif 'used' in metric_name.lower() and ('gb' in metric_name.lower() or 'gigabytes' in metric_name.lower()):
                disk_data['used_gb'] = self._get_latest_value(metric_values)
            # Look for free disk space in GB
            elif 'free' in metric_name.lower() and ('gb' in metric_name.lower() or 'gigabytes' in metric_name.lower()):
                disk_data['free_gb'] = self._get_latest_value(metric_values)
            # Look for total disk space
            elif 'total' in metric_name.lower() and ('gb' in metric_name.lower() or 'gigabytes' in metric_name.lower()):
                disk_data['total_gb'] = self._get_latest_value(metric_values)
        
        return disk_data
    
    def _extract_network_metrics(self, network_metrics: List[Dict]) -> Dict[str, Any]:
        """Extract Network metrics from raw data using correct AppDynamics metric names"""
        network_data = {}
        for metric in network_metrics:
            metric_name = metric.get('metricName', '')
            metric_values = metric.get('metricValues', [])
            
            # Look for bytes received per second
            if 'received' in metric_name.lower() and ('bytes/sec' in metric_name.lower() or 'bytes per second' in metric_name.lower()):
                network_data['bytes_received_per_sec'] = self._get_latest_value(metric_values)
            # Look for bytes transmitted per second
            elif 'transmitted' in metric_name.lower() and ('bytes/sec' in metric_name.lower() or 'bytes per second' in metric_name.lower()):
                network_data['bytes_transmitted_per_sec'] = self._get_latest_value(metric_values)
            # Look for packets received per second
            elif 'received' in metric_name.lower() and ('packets/sec' in metric_name.lower() or 'packets per second' in metric_name.lower()):
                network_data['packets_received_per_sec'] = self._get_latest_value(metric_values)
            # Look for packets transmitted per second
            elif 'transmitted' in metric_name.lower() and ('packets/sec' in metric_name.lower() or 'packets per second' in metric_name.lower()):
                network_data['packets_transmitted_per_sec'] = self._get_latest_value(metric_values)
        
        return network_data
    
    def _get_latest_value(self, metric_values: List[Dict]) -> Optional[float]:
        """Get the latest value from metric values"""
        if not metric_values:
            return None
        
        # Sort by timestamp and get the latest
        sorted_values = sorted(metric_values, key=lambda x: x.get('startTimeInMillis', 0), reverse=True)
        return sorted_values[0].get('value') if sorted_values else None
    
    def get_business_transactions(self, app_id: int, duration_in_mins: int = 60) -> List[Dict]:
        """Get business transaction metrics"""
        debug_logger.log_function_call("AppDynamicsClient.get_business_transactions", kwargs={
            "app_id": app_id, "duration_in_mins": duration_in_mins
        })
        
        try:
            params = {
                'application-id': app_id,
                'time-range-type': 'BEFORE_NOW',
                'duration-in-mins': duration_in_mins,
                'rollup': 'true',
                'output': 'JSON'
            }
            
            response = self.session.get(f"{self.base_url}/controller/rest/applications/{app_id}/business-transactions", params=params)
            response.raise_for_status()
            transactions = response.json()
            
            debug_logger.info(f"Retrieved {len(transactions)} business transactions")
            debug_logger.log_function_return("AppDynamicsClient.get_business_transactions", f"Found {len(transactions)} transactions")
            return transactions
        except Exception as e:
            debug_logger.error(f"Failed to get business transactions: {e}")
            debug_logger.log_function_return("AppDynamicsClient.get_business_transactions", "Failed")
            return []
    
    def get_business_transaction_metrics(self, app_id: int, bt_id: int, duration_in_mins: int = 60) -> Dict[str, Any]:
        """Get detailed metrics for a specific business transaction"""
        debug_logger.log_function_call("AppDynamicsClient.get_business_transaction_metrics", kwargs={
            "app_id": app_id, "bt_id": bt_id, "duration_in_mins": duration_in_mins
        })
        
        try:
            params = {
                'application-id': app_id,
                'time-range-type': 'BEFORE_NOW',
                'duration-in-mins': duration_in_mins,
                'rollup': 'true',
                'output': 'JSON'
            }
            
            # Get error rate
            error_response = self.session.get(f"{self.base_url}/controller/rest/applications/{app_id}/business-transactions/{bt_id}/metric-data", 
                                            params={**params, 'metric-path': 'Business Transaction|*|*|Error Rate'})
            
            # Get average response time
            response_time_response = self.session.get(f"{self.base_url}/controller/rest/applications/{app_id}/business-transactions/{bt_id}/metric-data",
                                                    params={**params, 'metric-path': 'Business Transaction|*|*|Average Response Time (ms)'})
            
            # Get calls per minute
            calls_response = self.session.get(f"{self.base_url}/controller/rest/applications/{app_id}/business-transactions/{bt_id}/metric-data",
                                            params={**params, 'metric-path': 'Business Transaction|*|*|Calls per Minute'})
            
            metrics = {
                'error_rate': self._extract_metric_value(error_response.json()) if error_response.status_code == 200 else None,
                'avg_response_time': self._extract_metric_value(response_time_response.json()) if response_time_response.status_code == 200 else None,
                'calls_per_minute': self._extract_metric_value(calls_response.json()) if calls_response.status_code == 200 else None
            }
            
            debug_logger.log_function_return("AppDynamicsClient.get_business_transaction_metrics", "Success")
            return metrics
        except Exception as e:
            debug_logger.error(f"Failed to get business transaction metrics: {e}")
            debug_logger.log_function_return("AppDynamicsClient.get_business_transaction_metrics", "Failed")
            return {}
    
    def _extract_metric_value(self, metric_data: List[Dict]) -> Optional[float]:
        """Extract the latest value from metric data"""
        if not metric_data:
            return None
        
        for metric in metric_data:
            metric_values = metric.get('metricValues', [])
            if metric_values:
                # Get the latest value
                latest_value = self._get_latest_value(metric_values)
                if latest_value is not None:
                    return latest_value
        
        return None
    
    def get_alerts(self, app_id: int = None, severity: str = None, duration_in_mins: int = 60) -> List[Dict]:
        """Get alerts from AppDynamics"""
        debug_logger.log_function_call("AppDynamicsClient.get_alerts", kwargs={
            "app_id": app_id, "severity": severity, "duration_in_mins": duration_in_mins
        })
        
        try:
            params = {
                'time-range-type': 'BEFORE_NOW',
                'duration-in-mins': duration_in_mins,
                'output': 'JSON'
            }
            
            if app_id:
                params['application-id'] = app_id
            
            if severity:
                params['severity'] = severity.upper()
            
            # Use the correct alerts endpoint
            if app_id:
                response = self.session.get(f"{self.base_url}/controller/rest/applications/{app_id}/events", params=params)
            else:
                response = self.session.get(f"{self.base_url}/controller/rest/events", params=params)
            response.raise_for_status()
            alerts = response.json()
            
            debug_logger.info(f"Retrieved {len(alerts)} alerts")
            debug_logger.log_function_return("AppDynamicsClient.get_alerts", f"Found {len(alerts)} alerts")
            return alerts
        except Exception as e:
            debug_logger.error(f"Failed to get alerts: {e}")
            debug_logger.log_function_return("AppDynamicsClient.get_alerts", "Failed")
            return []
    
    def display_resource_utilization(self, utilization: Dict[str, Any], server_name: str):
        """Display resource utilization in a formatted table"""
        table = Table(title=f"Resource Utilization - {server_name}")
        table.add_column("Resource", style="cyan")
        table.add_column("Current Value", style="yellow")
        table.add_column("Status", style="green")
        
        # CPU
        cpu = utilization.get('cpu', {})
        cpu_usage = cpu.get('usage_percent', 0) or 0
        cpu_status = "🟢 Normal" if cpu_usage < 80 else "🟡 High" if cpu_usage < 95 else "🔴 Critical"
        table.add_row("CPU Usage", f"{cpu_usage:.1f}%", cpu_status)
        
        # Memory
        memory = utilization.get('memory', {})
        memory_usage = memory.get('usage_percent', 0) or 0
        memory_status = "🟢 Normal" if memory_usage < 80 else "🟡 High" if memory_usage < 95 else "🔴 Critical"
        table.add_row("Memory Usage", f"{memory_usage:.1f}%", memory_status)
        
        # Disk
        disk = utilization.get('disk', {})
        disk_usage = disk.get('usage_percent', 0) or 0
        disk_status = "🟢 Normal" if disk_usage < 80 else "🟡 High" if disk_usage < 95 else "🔴 Critical"
        table.add_row("Disk Usage", f"{disk_usage:.1f}%", disk_status)
        
        console.print(table)
    
    def display_business_transactions(self, transactions: List[Dict], app_name: str):
        """Display business transaction health in a formatted table"""
        table = Table(title=f"Business Transactions - {app_name}")
        table.add_column("Transaction", style="cyan")
        table.add_column("Error Rate", style="red")
        table.add_column("Avg Response Time", style="yellow")
        table.add_column("Calls/min", style="blue")
        table.add_column("Status", style="green")
        
        for transaction in transactions[:10]:  # Show top 10
            name = transaction.get('name', 'Unknown')
            error_rate = transaction.get('errorRate', 0) or 0
            avg_response_time = transaction.get('avgResponseTime', 0) or 0
            calls_per_minute = transaction.get('callsPerMinute', 0) or 0
            
            # Determine status
            if error_rate > 5:
                status = "🔴 High Errors"
            elif avg_response_time > 2000:  # 2 seconds
                status = "🟡 Slow"
            elif error_rate > 1:
                status = "🟡 Some Errors"
            else:
                status = "🟢 Healthy"
            
            table.add_row(
                name,
                f"{error_rate:.2f}%",
                f"{avg_response_time:.0f}ms",
                f"{calls_per_minute:.0f}",
                status
            )
        
        console.print(table)
    
    def display_alerts(self, alerts: List[Dict], app_name: str = "All Applications"):
        """Display alerts in a formatted table"""
        if not alerts:
            console.print(f"[green]✅ No alerts found for {app_name}[/green]")
            return
        
        table = Table(title=f"Active Alerts - {app_name}")
        table.add_column("Time", style="cyan")
        table.add_column("Severity", style="red")
        table.add_column("Message", style="yellow")
        table.add_column("Entity", style="blue")
        
        for alert in alerts[:20]:  # Show latest 20
            timestamp = alert.get('eventTime', 0)
            if timestamp:
                time_str = datetime.fromtimestamp(timestamp / 1000).strftime("%H:%M:%S")
            else:
                time_str = "Unknown"
            
            severity = alert.get('severity', 'UNKNOWN')
            message = alert.get('summary', 'No message')
            entity = alert.get('affectedEntityType', 'Unknown')
            
            severity_color = {
                'CRITICAL': 'red',
                'WARNING': 'yellow',
                'INFO': 'blue'
            }.get(severity, 'white')
            
            table.add_row(
                time_str,
                f"[{severity_color}]{severity}[/{severity_color}]",
                message[:50] + "..." if len(message) > 50 else message,
                entity
            )
        
        console.print(table)
    
    def debug_metrics(self, app_id: int, server_id: int, duration_in_mins: int = 60):
        """Debug method to see what metrics are available"""
        debug_logger.log_function_call("AppDynamicsClient.debug_metrics", kwargs={
            "app_id": app_id, "server_id": server_id, "duration_in_mins": duration_in_mins
        })
        
        try:
            # Get all available metrics for this server
            all_metrics = self.get_server_metrics(app_id, server_id, "Application Infrastructure Performance|Machine Agent|Hardware Resources|*", duration_in_mins)
            
            console.print(f"[bold]🔍 Debug: Available metrics for server {server_id}[/bold]")
            console.print(f"Total metrics found: {len(all_metrics)}")
            
            # Group metrics by resource type
            cpu_metrics = []
            memory_metrics = []
            disk_metrics = []
            network_metrics = []
            other_metrics = []
            
            for metric in all_metrics:
                metric_name = metric.get('metricName', '')
                if 'CPU' in metric_name:
                    cpu_metrics.append(metric)
                elif 'Memory' in metric_name:
                    memory_metrics.append(metric)
                elif 'Disk' in metric_name:
                    disk_metrics.append(metric)
                elif 'Network' in metric_name:
                    network_metrics.append(metric)
                else:
                    other_metrics.append(metric)
            
            # Display CPU metrics
            if cpu_metrics:
                console.print(f"\n[bold cyan]CPU Metrics ({len(cpu_metrics)}):[/bold cyan]")
                for metric in cpu_metrics:
                    metric_name = metric.get('metricName', '')
                    metric_values = metric.get('metricValues', [])
                    latest_value = self._get_latest_value(metric_values)
                    console.print(f"  • {metric_name}: {latest_value}")
            
            # Display Memory metrics
            if memory_metrics:
                console.print(f"\n[bold green]Memory Metrics ({len(memory_metrics)}):[/bold green]")
                for metric in memory_metrics:
                    metric_name = metric.get('metricName', '')
                    metric_values = metric.get('metricValues', [])
                    latest_value = self._get_latest_value(metric_values)
                    console.print(f"  • {metric_name}: {latest_value}")
            
            # Display Disk metrics
            if disk_metrics:
                console.print(f"\n[bold yellow]Disk Metrics ({len(disk_metrics)}):[/bold yellow]")
                for metric in disk_metrics:
                    metric_name = metric.get('metricName', '')
                    metric_values = metric.get('metricValues', [])
                    latest_value = self._get_latest_value(metric_values)
                    console.print(f"  • {metric_name}: {latest_value}")
            
            # Display Network metrics
            if network_metrics:
                console.print(f"\n[bold magenta]Network Metrics ({len(network_metrics)}):[/bold magenta]")
                for metric in network_metrics:
                    metric_name = metric.get('metricName', '')
                    metric_values = metric.get('metricValues', [])
                    latest_value = self._get_latest_value(metric_values)
                    console.print(f"  • {metric_name}: {latest_value}")
            
            # Display other metrics
            if other_metrics:
                console.print(f"\n[bold dim]Other Metrics ({len(other_metrics)}):[/bold dim]")
                for metric in other_metrics[:10]:  # Show first 10
                    metric_name = metric.get('metricName', '')
                    metric_values = metric.get('metricValues', [])
                    latest_value = self._get_latest_value(metric_values)
                    console.print(f"  • {metric_name}: {latest_value}")
                if len(other_metrics) > 10:
                    console.print(f"  ... and {len(other_metrics) - 10} more")
            
            debug_logger.log_function_return("AppDynamicsClient.debug_metrics", "Success")
            return all_metrics
            
        except Exception as e:
            console.print(f"[red]Debug metrics error: {e}[/red]")
            debug_logger.error(f"Debug metrics error: {e}")
            debug_logger.log_function_return("AppDynamicsClient.debug_metrics", "Failed")
            return []
