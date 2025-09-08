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
            config.controller_url,
            config.client_id,
            config.client_secret
        )
        
        if not client.test_connection():
            console.print("❌ Failed to connect to AppDynamics")
            return
        
        # Parse query to determine what to show
        query_lower = query.lower()
        
        if 'resource' in query_lower or 'utilization' in query_lower:
            # Resource utilization
            console.print("[bold]📊 Resource Utilization[/bold]")
            resources = client.get_resource_utilization()
            if resources:
                from rich.table import Table
                table = Table(title="Resource Utilization")
                table.add_column("Server", style="cyan")
                table.add_column("CPU %", style="yellow")
                table.add_column("Memory %", style="green")
                table.add_column("Status", style="blue")
                
                for resource in resources[:10]:  # Show first 10
                    table.add_row(
                        resource.get('server_name', 'Unknown'),
                        f"{resource.get('cpu_usage', 0):.1f}%",
                        f"{resource.get('memory_usage', 0):.1f}%",
                        resource.get('status', 'Unknown')
                    )
                console.print(table)
            else:
                console.print("[yellow]No resource data available[/yellow]")
        
        elif 'business' in query_lower or 'transaction' in query_lower:
            # Business transactions
            console.print("[bold]💼 Business Transactions[/bold]")
            transactions = client.get_business_transactions()
            if transactions:
                from rich.table import Table
                table = Table(title="Business Transactions")
                table.add_column("Transaction", style="cyan")
                table.add_column("Errors", style="red")
                table.add_column("Slow", style="yellow")
                table.add_column("Throughput", style="green")
                
                for tx in transactions[:10]:  # Show first 10
                    table.add_row(
                        tx.get('name', 'Unknown'),
                        str(tx.get('error_count', 0)),
                        str(tx.get('slow_count', 0)),
                        f"{tx.get('throughput', 0):.1f}/min"
                    )
                console.print(table)
            else:
                console.print("[yellow]No transaction data available[/yellow]")
        
        elif 'alert' in query_lower:
            # Alerts
            console.print("[bold]🚨 AppDynamics Alerts[/bold]")
            alerts = client.get_alerts()
            if alerts:
                from rich.table import Table
                table = Table(title="Active Alerts")
                table.add_column("Alert", style="red")
                table.add_column("Severity", style="yellow")
                table.add_column("Time", style="blue")
                table.add_column("Description", style="white")
                
                for alert in alerts[:10]:  # Show first 10
                    table.add_row(
                        alert.get('name', 'Unknown'),
                        alert.get('severity', 'Unknown'),
                        alert.get('timestamp', 'Unknown'),
                        alert.get('description', 'No description')[:50] + "..."
                    )
                console.print(table)
            else:
                console.print("[green]✅ No active alerts[/green]")
        
        else:
            # Default - show summary
            console.print("[bold]📊 AppDynamics Summary[/bold]")
            
            # Get resource utilization
            resources = client.get_resource_utilization()
            if resources:
                console.print(f"[green]✅ {len(resources)} servers monitored[/green]")
            
            # Get business transactions
            transactions = client.get_business_transactions()
            if transactions:
                console.print(f"[blue]💼 {len(transactions)} business transactions[/blue]")
            
            # Get alerts
            alerts = client.get_alerts()
            if alerts:
                console.print(f"[red]🚨 {len(alerts)} active alerts[/red]")
            else:
                console.print("[green]✅ No active alerts[/green]")
        
    except Exception as e:
        console.print(f"[red]AppDynamics command error: {e}[/red]")
