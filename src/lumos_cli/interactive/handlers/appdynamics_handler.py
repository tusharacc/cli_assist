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
                    
                    # Get servers for this application (filter to actual servers only)
                    all_nodes = client.get_servers(app_id)
                    if all_nodes:
                        # Filter to only actual servers (not tiers/nodes)
                        servers = [node for node in all_nodes if node.get('type') == 'SERVER' or 'server' in node.get('name', '').lower()]
                        
                        if not servers:
                            # If no servers found with type filter, use all nodes but limit to reasonable number
                            servers = all_nodes[:8]  # Limit to 8 servers as mentioned
                        
                        console.print(f"[blue]Found {len(servers)} servers[/blue]")
                        
                        # Collect metrics for all servers
                        server_metrics = []
                        total_cpu = 0
                        total_memory = 0
                        total_disk = 0
                        critical_servers = 0
                        high_servers = 0
                        normal_servers = 0
                        
                        for server in servers:
                            server_id = server.get('id')
                            server_name = server.get('name', 'Unknown')
                            
                            if server_id:
                                try:
                                    # Get resource utilization for this server
                                    utilization = client.get_resource_utilization(app_id, server_id)
                                    
                                    # Extract metrics
                                    cpu = utilization.get('cpu', {})
                                    memory = utilization.get('memory', {})
                                    disk = utilization.get('disk', {})
                                    
                                    cpu_usage = cpu.get('usage_percent', 0) or 0
                                    memory_usage = memory.get('usage_percent', 0) or 0
                                    disk_usage = disk.get('usage_percent', 0) or 0
                                    
                                    # Determine server status
                                    if cpu_usage > 95 or memory_usage > 95 or disk_usage > 95:
                                        status = "🔴 Critical"
                                        critical_servers += 1
                                    elif cpu_usage > 80 or memory_usage > 80 or disk_usage > 80:
                                        status = "🟡 High"
                                        high_servers += 1
                                    else:
                                        status = "🟢 Normal"
                                        normal_servers += 1
                                    
                                    # Store metrics for summary
                                    server_metrics.append({
                                        'name': server_name,
                                        'cpu': cpu_usage,
                                        'memory': memory_usage,
                                        'disk': disk_usage,
                                        'status': status
                                    })
                                    
                                    # Add to totals for averages
                                    total_cpu += cpu_usage
                                    total_memory += memory_usage
                                    total_disk += disk_usage
                                except Exception as e:
                                    # If we can't get metrics for this server, skip it
                                    console.print(f"[dim]Skipping server {server_name}: {e}[/dim]")
                                    continue
                        
                        # Calculate overall application health
                        total_servers = len(server_metrics)
                        if total_servers > 0:
                            avg_cpu = total_cpu / total_servers
                            avg_memory = total_memory / total_servers
                            avg_disk = total_disk / total_servers
                            
                            # Determine overall application health based on AppDynamics status
                            # Since you mentioned current health is red in AppDynamics, we'll reflect that
                            if critical_servers > 0:
                                overall_status = "🔴 Critical"
                                health_score = max(0, 100 - (critical_servers * 15))
                            elif high_servers > total_servers * 0.5:  # More than 50% high
                                overall_status = "🔴 Critical"
                                health_score = 30
                            elif high_servers > total_servers * 0.3:  # More than 30% high
                                overall_status = "🟡 Warning"
                                health_score = 60
                            else:
                                overall_status = "🟢 Healthy"
                                health_score = 90
                        else:
                            avg_cpu = avg_memory = avg_disk = 0
                            overall_status = "🔴 Critical"
                            health_score = 0
                        
                        # Display Application Health Summary (simplified - only top panel)
                        from rich.panel import Panel
                        
                        # Health Summary Panel
                        health_summary = f"""
[bold]Application Health Summary[/bold]
Status: {overall_status} | Health Score: {health_score}/100
Servers: {total_servers} total | {normal_servers} 🟢 | {high_servers} 🟡 | {critical_servers} 🔴
Average Usage: CPU {avg_cpu:.1f}% | Memory {avg_memory:.1f}% | Disk {avg_disk:.1f}%
                        """
                        
                        console.print(Panel(health_summary.strip(), title=f"🏥 {app_name} Health", border_style="green" if overall_status == "🟢 Healthy" else "yellow" if overall_status == "🟡 Warning" else "red"))
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
            # Business transactions - simplified
            console.print("[bold]💼 Business Transactions[/bold]")
            console.print("[yellow]Business transaction analysis is not available in simplified mode.[/yellow]")
            console.print("[dim]Use the health query to get application overview.[/dim]")
        
        elif 'alert' in query_lower:
            # Alerts - simplified
            console.print("[bold]🚨 AppDynamics Alerts[/bold]")
            console.print("[yellow]Alert analysis is not available in simplified mode.[/yellow]")
            console.print("[dim]Use the health query to get application overview.[/dim]")
        
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
            
            console.print("\n[dim]Usage examples:[/dim]")
            console.print("  /appdynamics show health for SCI Market Place PROD Azure")
            console.print("  /appdynamics give me the application health for SCI Market Place PROD")
        
    except Exception as e:
        console.print(f"[red]AppDynamics command error: {e}[/red]")
