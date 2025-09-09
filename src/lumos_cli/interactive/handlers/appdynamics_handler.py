"""
AppDynamics interactive mode handlers
"""

from rich.console import Console
from ...clients.appdynamics_client import AppDynamicsClient
from ...config.appdynamics_config import AppDynamicsConfigManager
from ...utils.debug_logger import debug_logger

console = Console()

def interactive_appdynamics(query: str):
    """Handle AppDynamics commands in interactive mode"""
    try:
        console.print(f"[cyan]📊 AppDynamics Analysis: {query}[/cyan]")
        
        # Check if AppDynamics is configured
        config_manager = AppDynamicsConfigManager()
        if not config_manager.is_configured():
            console.print("[yellow]⚠️ AppDynamics not configured. Run 'lumos-cli appdynamics config' first.[/yellow]")
            return
        
        config = config_manager.load_config()
        if not config:
            console.print("[red]❌ Failed to load AppDynamics configuration[/red]")
            return
        
        client = AppDynamicsClient(
            config.base_url,
            config.client_id,
            config.client_secret
        )
        
        if not client.test_connection():
            console.print("❌ Failed to connect to AppDynamics")
            return
        
        # Parse query to determine what to show
        query_lower = query.lower()
        
        if 'resource' in query_lower or 'utilization' in query_lower or 'health' in query_lower:
            # Resource utilization and application health
            console.print("[bold]📊 Application Health & Resource Utilization[/bold]")
            
            # Try to extract application name from query
            app_name = None
            if 'SCI Market Place PROD Azure' in query:
                app_name = 'SCI Market Place PROD Azure'
            elif 'SCI Market Place PROD' in query:
                app_name = 'SCI Market Place PROD'
            else:
                # Try to find any application name in the query
                words = query.split()
                for i, word in enumerate(words):
                    if word.lower() in ['for', 'of', 'in'] and i + 1 < len(words):
                        app_name = ' '.join(words[i+1:])
                        break
            
            if app_name:
                console.print(f"[cyan]Looking for application: {app_name}[/cyan]")
                app_id = client.get_application_id(app_name)
                if app_id:
                    console.print(f"[green]✅ Found application ID: {app_id}[/green]")
                    
                    # Get servers for this application
                    servers = client.get_servers(app_id)
                    if servers:
                        console.print(f"[blue]Found {len(servers)} servers[/blue]")
                        
                        from rich.table import Table
                        table = Table(title=f"Resource Utilization - {app_name}")
                        table.add_column("Server", style="cyan")
                        table.add_column("CPU %", style="yellow")
                        table.add_column("Memory %", style="green")
                        table.add_column("Disk %", style="magenta")
                        table.add_column("Status", style="blue")
                        
                        for server in servers[:10]:  # Show first 10 servers
                            server_id = server.get('id')
                            server_name = server.get('name', 'Unknown')
                            
                            if server_id:
                                # Get resource utilization for this server
                                utilization = client.get_resource_utilization(app_id, server_id)
                                
                                # Extract metrics
                                cpu = utilization.get('cpu', {})
                                memory = utilization.get('memory', {})
                                disk = utilization.get('disk', {})
                                
                                cpu_usage = cpu.get('usage_percent', 0) or 0
                                memory_usage = memory.get('usage_percent', 0) or 0
                                disk_usage = disk.get('usage_percent', 0) or 0
                                
                                # Determine overall status
                                if cpu_usage > 95 or memory_usage > 95 or disk_usage > 95:
                                    status = "🔴 Critical"
                                elif cpu_usage > 80 or memory_usage > 80 or disk_usage > 80:
                                    status = "🟡 High"
                                else:
                                    status = "🟢 Normal"
                                
                                table.add_row(
                                    server_name,
                                    f"{cpu_usage:.1f}%",
                                    f"{memory_usage:.1f}%",
                                    f"{disk_usage:.1f}%",
                                    status
                                )
                        
                        console.print(table)
                    else:
                        console.print("[yellow]No servers found for this application[/yellow]")
                else:
                    console.print(f"[red]❌ Application '{app_name}' not found[/red]")
                    console.print("[dim]Available applications:[/dim]")
                    applications = client.get_applications()
                    for app in applications[:5]:
                        console.print(f"  • {app.get('name', 'Unknown')}")
            else:
                console.print("[yellow]No specific application mentioned. Showing all applications:[/yellow]")
                applications = client.get_applications()
                if applications:
                    from rich.table import Table
                    table = Table(title="Available Applications")
                    table.add_column("ID", style="cyan")
                    table.add_column("Name", style="magenta")
                    table.add_column("Description", style="dim")
                    
                    for app in applications[:10]:
                        table.add_row(
                            str(app.get('id', 'N/A')),
                            app.get('name', 'Unknown'),
                            app.get('description', 'No description')[:50] + "..." if len(app.get('description', '')) > 50 else app.get('description', 'No description')
                        )
                    console.print(table)
        
        elif 'business' in query_lower or 'transaction' in query_lower:
            # Business transactions
            console.print("[bold]💼 Business Transactions[/bold]")
            
            # Try to extract application name from query
            app_name = None
            if 'SCI Market Place PROD Azure' in query:
                app_name = 'SCI Market Place PROD Azure'
            elif 'SCI Market Place PROD' in query:
                app_name = 'SCI Market Place PROD'
            else:
                # Try to find any application name in the query
                words = query.split()
                for i, word in enumerate(words):
                    if word.lower() in ['for', 'of', 'in'] and i + 1 < len(words):
                        app_name = ' '.join(words[i+1:])
                        break
            
            if app_name:
                console.print(f"[cyan]Looking for business transactions for: {app_name}[/cyan]")
                app_id = client.get_application_id(app_name)
                if app_id:
                    transactions = client.get_business_transactions(app_id)
                    if transactions:
                        from rich.table import Table
                        table = Table(title=f"Business Transactions - {app_name}")
                        table.add_column("Transaction", style="cyan")
                        table.add_column("Error Rate", style="red")
                        table.add_column("Avg Response Time", style="yellow")
                        table.add_column("Calls/min", style="green")
                        table.add_column("Status", style="blue")
                        
                        for tx in transactions[:10]:  # Show first 10
                            error_rate = tx.get('errorRate', 0) or 0
                            avg_response_time = tx.get('avgResponseTime', 0) or 0
                            calls_per_minute = tx.get('callsPerMinute', 0) or 0
                            
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
                                tx.get('name', 'Unknown'),
                                f"{error_rate:.2f}%",
                                f"{avg_response_time:.0f}ms",
                                f"{calls_per_minute:.0f}",
                                status
                            )
                        console.print(table)
                    else:
                        console.print("[yellow]No transaction data available for this application[/yellow]")
                else:
                    console.print(f"[red]❌ Application '{app_name}' not found[/red]")
            else:
                console.print("[yellow]No specific application mentioned. Please specify an application name.[/yellow]")
                console.print("[dim]Example: /appdynamics show business transactions for SCI Market Place PROD Azure[/dim]")
        
        elif 'alert' in query_lower:
            # Alerts
            console.print("[bold]🚨 AppDynamics Alerts[/bold]")
            
            # Try to extract application name from query
            app_name = None
            app_id = None
            if 'SCI Market Place PROD Azure' in query:
                app_name = 'SCI Market Place PROD Azure'
            elif 'SCI Market Place PROD' in query:
                app_name = 'SCI Market Place PROD'
            else:
                # Try to find any application name in the query
                words = query.split()
                for i, word in enumerate(words):
                    if word.lower() in ['for', 'of', 'in'] and i + 1 < len(words):
                        app_name = ' '.join(words[i+1:])
                        break
            
            if app_name:
                console.print(f"[cyan]Looking for alerts for: {app_name}[/cyan]")
                app_id = client.get_application_id(app_name)
                if not app_id:
                    console.print(f"[red]❌ Application '{app_name}' not found[/red]")
                    app_id = None
            
            alerts = client.get_alerts(app_id=app_id)
            if alerts:
                from rich.table import Table
                table = Table(title=f"Active Alerts - {app_name if app_name else 'All Applications'}")
                table.add_column("Time", style="cyan")
                table.add_column("Severity", style="red")
                table.add_column("Message", style="yellow")
                table.add_column("Entity", style="blue")
                
                for alert in alerts[:20]:  # Show first 20
                    timestamp = alert.get('eventTime', 0)
                    if timestamp:
                        from datetime import datetime
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
            else:
                console.print("[green]✅ No active alerts[/green]")
        
        else:
            # Default - show summary
            console.print("[bold]📊 AppDynamics Summary[/bold]")
            
            # Get applications
            applications = client.get_applications()
            if applications:
                console.print(f"[green]✅ {len(applications)} applications monitored[/green]")
                
                # Show first few applications
                console.print("[dim]Available applications:[/dim]")
                for app in applications[:5]:
                    console.print(f"  • {app.get('name', 'Unknown')}")
                if len(applications) > 5:
                    console.print(f"  ... and {len(applications) - 5} more")
            else:
                console.print("[yellow]No applications found[/yellow]")
            
            # Get alerts (global)
            alerts = client.get_alerts()
            if alerts:
                console.print(f"[red]🚨 {len(alerts)} active alerts[/red]")
            else:
                console.print("[green]✅ No active alerts[/green]")
            
            console.print("\n[dim]Usage examples:[/dim]")
            console.print("  /appdynamics show health for SCI Market Place PROD Azure")
            console.print("  /appdynamics get business transactions for SCI Market Place PROD")
            console.print("  /appdynamics show alerts for SCI Market Place PROD Azure")
        
    except Exception as e:
        console.print(f"[red]AppDynamics command error: {e}[/red]")
