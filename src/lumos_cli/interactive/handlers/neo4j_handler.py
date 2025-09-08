"""
Neo4j interactive mode handlers
"""

import re
from rich.console import Console
from rich.table import Table
from ...clients.neo4j_client import Neo4jClient
from ...config.neo4j_config import Neo4jConfigManager
from ...utils.debug_logger import debug_logger

console = Console()

def interactive_neo4j(query: str):
    """Handle Neo4j commands in interactive mode"""
    try:
        console.print(f"[cyan]🔗 Neo4j Analysis: {query}[/cyan]")
        
        # Extract class/method name from query
        # Look for class names (PascalCase)
        class_pattern = r'\b([A-Z][a-zA-Z0-9]+(?:[A-Z][a-zA-Z0-9]*)*)\b'
        class_matches = re.findall(class_pattern, query)
        
        # Look for method names (camelCase or snake_case)
        method_pattern = r'\b([a-z][a-zA-Z0-9]*(?:[A-Z][a-zA-Z0-9]*)*)\b'
        method_matches = re.findall(method_pattern, query)
        
        # Filter out common words
        common_words = {'can', 'you', 'identify', 'dependencies', 'impact', 'affected', 'class', 'method', 'function', 'from', 'neo4j', 'graph', 'database', 'which', 'what', 'show', 'get', 'find', 'analyze', 'check', 'of', 'for', 'in', 'the', 'a', 'an', 'and', 'or', 'but', 'with', 'by', 'to', 'from'}
        
        class_names = [name for name in class_matches if name not in common_words and len(name) > 3]
        method_names = [name for name in method_matches if name not in common_words and len(name) > 3]
        
        if not class_names and not method_names:
            console.print("[yellow]⚠️ No class or method names found in query. Please specify a class or method name.[/yellow]")
            console.print("Examples:")
            console.print("  • 'dependencies of class UserService'")
            console.print("  • 'impact analysis for method ValidateUser'")
            console.print("  • 'which classes depend on PaymentController'")
            return
        
        # Check if Neo4j is configured
        config_manager = Neo4jConfigManager()
        if not config_manager.is_configured():
            console.print("[yellow]⚠️ Neo4j not configured. Run 'lumos-cli neo4j config' first.[/yellow]")
            return
        
        config = config_manager.load_config()
        if not config:
            console.print("[red]❌ Failed to load Neo4j configuration[/red]")
            return
        
        client = Neo4jClient(config.uri, config.username, config.password)
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j")
            return
        
        # Determine query type
        query_lower = query.lower()
        
        if 'dependencies' in query_lower or 'depend' in query_lower:
            # Dependency analysis
            if class_names:
                for class_name in class_names:
                    console.print(f"\n[bold]🔍 Dependencies for class: {class_name}[/bold]")
                    dependencies = client.find_dependencies("", "", class_name)
                    if dependencies:
                        table = Table(title=f"Dependencies of {class_name}")
                        table.add_column("Dependent Class", style="cyan")
                        table.add_column("Repository", style="yellow")
                        table.add_column("Relationship", style="green")
                        
                        for dep in dependencies:
                            table.add_row(
                                dep.get('class_name', 'Unknown'),
                                dep.get('repository', 'Unknown'),
                                dep.get('dependency_type', 'Unknown')
                            )
                        console.print(table)
                    else:
                        console.print(f"[yellow]No dependencies found for {class_name}[/yellow]")
            
            if method_names:
                for method_name in method_names:
                    console.print(f"\n[bold]🔍 Dependencies for method: {method_name}[/bold]")
                    # For methods, we might need to find the class first
                    console.print(f"[dim]Method dependency analysis not yet implemented for {method_name}[/dim]")
        
        elif 'impact' in query_lower or 'affected' in query_lower:
            # Impact analysis
            if class_names:
                for class_name in class_names:
                    console.print(f"\n[bold]🔍 Impact analysis for class: {class_name}[/bold]")
                    impact = client.find_impact_analysis("", "", class_name)
                    if impact:
                        table = Table(title=f"Impact Analysis for {class_name}")
                        table.add_column("Affected Class", style="cyan")
                        table.add_column("Repository", style="yellow")
                        table.add_column("Impact Type", style="red")
                        
                        for item in impact:
                            table.add_row(
                                item.get('class_name', 'Unknown'),
                                item.get('repository', 'Unknown'),
                                item.get('class_type', 'Unknown')
                            )
                        console.print(table)
                    else:
                        console.print(f"[yellow]No impact analysis found for {class_name}[/yellow]")
        
        else:
            # General analysis - show both dependencies and impact
            if class_names:
                for class_name in class_names:
                    console.print(f"\n[bold]🔍 Analysis for class: {class_name}[/bold]")
                    
                    # Dependencies
                    dependencies = client.find_dependencies("", "", class_name)
                    if dependencies:
                        console.print(f"[green]✅ Found {len(dependencies)} dependencies[/green]")
                        for dep in dependencies[:5]:  # Show first 5
                            console.print(f"  • {dep.get('class_name', 'Unknown')} in {dep.get('repository', 'Unknown')}")
                        if len(dependencies) > 5:
                            console.print(f"  ... and {len(dependencies) - 5} more")
                    else:
                        console.print(f"[yellow]No dependencies found for {class_name}[/yellow]")
                    
                    # Impact
                    impact = client.find_impact_analysis("", "", class_name)
                    if impact:
                        console.print(f"[red]⚠️ Found {len(impact)} affected classes[/red]")
                        for item in impact[:5]:  # Show first 5
                            console.print(f"  • {item.get('class_name', 'Unknown')} in {item.get('repository', 'Unknown')}")
                        if len(impact) > 5:
                            console.print(f"  ... and {len(impact) - 5} more")
                    else:
                        console.print(f"[green]No impact found for {class_name}[/green]")
        
        client.close()
        
    except Exception as e:
        console.print(f"[red]Neo4j command error: {e}[/red]")
