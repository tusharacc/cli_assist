"""
Neo4j interactive mode handlers
"""

import re
from rich.console import Console
from rich.table import Table
from ...clients.neo4j_client import Neo4jClient
from ...config.neo4j_config import Neo4jConfigManager
from ...core.keyword_detector import UnifiedKeywordDetector
from ...utils.debug_logger import debug_logger

console = Console()

def interactive_neo4j(query: str):
    """Handle Neo4j commands in interactive mode"""
    try:
        console.print(f"[cyan]🔗 Neo4j Analysis: {query}[/cyan]")
        
        # Use LLM-based keyword detection
        keyword_detector = UnifiedKeywordDetector()
        detection_result = keyword_detector.detect_keywords('neo4j', query)
        
        console.print(f"[dim]🤖 Detected action: {detection_result.action} (confidence: {detection_result.confidence})[/dim]")
        
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
        
        # Handle different actions based on LLM detection
        if detection_result.action == 'list_repositories':
            handle_list_repositories(client)
        elif detection_result.action == 'stats':
            handle_repository_stats(client)
        elif detection_result.action == 'dependencies':
            handle_dependencies(client, detection_result.extracted_values)
        elif detection_result.action == 'impact':
            handle_impact_analysis(client, detection_result.extracted_values)
        elif detection_result.action == 'query':
            handle_custom_query(client, detection_result.extracted_values)
        elif detection_result.action == 'llm_query':
            handle_llm_generated_query(client, query)
        else:
            # Fallback to LLM-generated query for complex natural language queries
            handle_llm_generated_query(client, query)
        
        client.close()
        
    except Exception as e:
        console.print(f"[red]Neo4j command error: {e}[/red]")

def handle_list_repositories(client: Neo4jClient):
    """Handle listing all repositories"""
    console.print("[bold]📋 Listing all repositories...[/bold]")
    
    repositories = client.list_all_repositories()
    
    if not repositories:
        console.print("[yellow]No repositories found in the graph[/yellow]")
        return
    
    # Show the Cypher query
    console.print("\n[dim]🔍 Cypher Query:[/dim]")
    console.print("[dim]MATCH (r:Repository) RETURN r.organization as organization, r.name as name, r.url as url, r.created_at as created_at, r.updated_at as updated_at ORDER BY r.organization, r.name[/dim]")
    
    # Display results in a table
    table = Table(title=f"Repositories ({len(repositories)})")
    table.add_column("Organization", style="cyan")
    table.add_column("Repository", style="yellow")
    table.add_column("URL", style="blue")
    table.add_column("Created", style="green")
    table.add_column("Updated", style="magenta")
    
    for repo in repositories:
        table.add_row(
            repo.get('organization', 'Unknown'),
            repo.get('name', 'Unknown'),
            repo.get('url', 'N/A'),
            repo.get('created_at', 'N/A')[:10] if repo.get('created_at') else 'N/A',
            repo.get('updated_at', 'N/A')[:10] if repo.get('updated_at') else 'N/A'
        )
    
    console.print(table)

def handle_repository_stats(client: Neo4jClient):
    """Handle repository statistics"""
    console.print("[bold]📊 Repository Statistics...[/bold]")
    
    stats = client.get_repository_stats()
    
    if not stats:
        console.print("[yellow]No statistics available[/yellow]")
        return
    
    # Show the Cypher query
    console.print("\n[dim]🔍 Cypher Query:[/dim]")
    console.print("[dim]MATCH (r:Repository) WITH count(r) as repo_count MATCH (c:Class) WITH repo_count, count(c) as class_count MATCH (m:Method) WITH repo_count, class_count, count(m) as method_count MATCH (f:File) WITH repo_count, class_count, method_count, count(f) as file_count MATCH ()-[rel]->() WITH repo_count, class_count, method_count, file_count, count(rel) as relationship_count RETURN repo_count, class_count, method_count, file_count, relationship_count[/dim]")
    
    # Display statistics
    console.print(f"\n[bold]📈 Graph Statistics:[/bold]")
    console.print(f"  📁 Repositories: [cyan]{stats.get('repo_count', 0)}[/cyan]")
    console.print(f"  🏗️ Classes: [yellow]{stats.get('class_count', 0)}[/yellow]")
    console.print(f"  ⚙️ Methods: [green]{stats.get('method_count', 0)}[/green]")
    console.print(f"  📄 Files: [blue]{stats.get('file_count', 0)}[/blue]")
    console.print(f"  🔗 Relationships: [magenta]{stats.get('relationship_count', 0)}[/magenta]")

def handle_dependencies(client: Neo4jClient, extracted_values: dict):
    """Handle dependency analysis"""
    class_name = extracted_values.get('class_name')
    if not class_name:
        console.print("[yellow]⚠️ No class name found for dependency analysis[/yellow]")
        return
    
    console.print(f"[bold]🔍 Dependencies for class: {class_name}[/bold]")
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

def handle_impact_analysis(client: Neo4jClient, extracted_values: dict):
    """Handle impact analysis"""
    class_name = extracted_values.get('class_name')
    if not class_name:
        console.print("[yellow]⚠️ No class name found for impact analysis[/yellow]")
        return
    
    console.print(f"[bold]🔍 Impact analysis for class: {class_name}[/bold]")
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

def handle_custom_query(client: Neo4jClient, extracted_values: dict):
    """Handle custom Cypher queries"""
    query = extracted_values.get('query')
    if not query:
        console.print("[yellow]⚠️ No query found[/yellow]")
        return
    
    console.print(f"[bold]🔍 Executing custom query...[/bold]")
    console.print(f"[dim]Query: {query}[/dim]")
    
    result = client.execute_query(query)
    
    if result:
        console.print(f"[green]✅ Query executed successfully. Found {len(result)} records.[/green]")
        
        # Display results in a simple format
        for i, record in enumerate(result[:10]):  # Show first 10 records
            console.print(f"\n[bold]Record {i+1}:[/bold]")
            for key, value in record.items():
                console.print(f"  {key}: {value}")
        
        if len(result) > 10:
            console.print(f"\n[dim]... and {len(result) - 10} more records[/dim]")
    else:
        console.print("[yellow]No results found[/yellow]")

def handle_llm_generated_query(client: Neo4jClient, user_intent: str):
    """Handle LLM-generated Cypher queries based on natural language"""
    console.print(f"[bold]🤖 Generating Cypher query using Enterprise LLM...[/bold]")
    console.print(f"[dim]Intent: {user_intent}[/dim]")
    
    # Generate and execute query using LLM
    result = client.execute_llm_generated_query(user_intent)
    
    if not result['success']:
        console.print(f"[red]❌ Failed to generate or execute query: {result['error']}[/red]")
        return
    
    query = result['query']
    results = result['results']
    schema_info = result['schema_info']
    
    # Display the generated query
    console.print(f"\n[bold]🔍 Generated Cypher Query:[/bold]")
    console.print(f"[dim]{query}[/dim]")
    
    # Display schema information
    if schema_info:
        console.print(f"\n[bold]📊 Schema Context:[/bold]")
        console.print(f"[dim]Labels: {', '.join(schema_info.get('node_labels', [])[:5])}[/dim]")
        console.print(f"[dim]Relationships: {', '.join(schema_info.get('relationship_types', [])[:5])}[/dim]")
    
    if results:
        console.print(f"\n[green]✅ Query executed successfully. Found {len(results)} records.[/green]")
        
        # Display results in a table format if possible
        if results and isinstance(results[0], dict):
            # Try to create a table
            try:
                table = Table(title=f"Query Results ({len(results)})")
                
                # Get column names from first record
                columns = list(results[0].keys())
                for col in columns[:6]:  # Limit to 6 columns for readability
                    table.add_column(col, style="cyan")
                
                # Add rows
                for record in results[:20]:  # Show first 20 records
                    row_data = []
                    for col in columns[:6]:
                        value = record.get(col, 'N/A')
                        # Truncate long values
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:47] + "..."
                        row_data.append(str(value))
                    table.add_row(*row_data)
                
                console.print(table)
                
                if len(results) > 20:
                    console.print(f"\n[dim]... and {len(results) - 20} more records[/dim]")
                    
            except Exception as e:
                # Fallback to simple display
                console.print(f"[yellow]⚠️ Could not format as table: {e}[/yellow]")
                for i, record in enumerate(results[:10]):
                    console.print(f"\n[bold]Record {i+1}:[/bold]")
                    for key, value in record.items():
                        console.print(f"  {key}: {value}")
                
                if len(results) > 10:
                    console.print(f"\n[dim]... and {len(results) - 10} more records[/dim]")
    else:
        console.print("[yellow]No results found[/yellow]")

def handle_class_method_analysis(client: Neo4jClient, query: str):
    """Handle class/method analysis (fallback)"""
    # Extract class/method name from query
    class_pattern = r'\b([A-Z][a-zA-Z0-9]+(?:[A-Z][a-zA-Z0-9]*)*)\b'
    class_matches = re.findall(class_pattern, query)
    
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
    
    # Handle class analysis
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
    
    # Handle method analysis
    if method_names:
        for method_name in method_names:
            console.print(f"\n[bold]🔍 Analysis for method: {method_name}[/bold]")
            console.print(f"[dim]Method analysis not yet implemented for {method_name}[/dim]")