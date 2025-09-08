#!/usr/bin/env python3
"""
Populate Neo4j with fake data for testing Lumos CLI integration
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.neo4j_client import Neo4jClient
from lumos_cli.neo4j_config import Neo4jConfigManager
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import time

console = Console()

def create_fake_repository_data():
    """Create fake repository data for testing"""
    return {
        "scimarketplace": {
            "repositories": {
                "quoteapp": {
                    "files": [
                        "src/main/java/com/company/quote/QuoteController.java",
                        "src/main/java/com/company/quote/QuoteService.java",
                        "src/main/java/com/company/quote/QuoteRepository.java",
                        "src/main/java/com/company/quote/model/Quote.java",
                        "src/main/java/com/company/quote/model/QuoteItem.java",
                        "src/main/java/com/company/quote/util/QuoteCalculator.java",
                        "src/test/java/com/company/quote/QuoteControllerTest.java",
                        "src/test/java/com/company/quote/QuoteServiceTest.java"
                    ],
                    "classes": {
                        "QuoteController": {
                            "type": "class",
                            "file": "src/main/java/com/company/quote/QuoteController.java",
                            "methods": ["createQuote", "getQuote", "updateQuote", "deleteQuote"],
                            "dependencies": ["QuoteService", "QuoteRepository"]
                        },
                        "QuoteService": {
                            "type": "class",
                            "file": "src/main/java/com/company/quote/QuoteService.java",
                            "methods": ["calculateQuote", "validateQuote", "processQuote"],
                            "dependencies": ["QuoteRepository", "QuoteCalculator", "Quote"]
                        },
                        "QuoteRepository": {
                            "type": "interface",
                            "file": "src/main/java/com/company/quote/QuoteRepository.java",
                            "methods": ["save", "findById", "findAll", "delete"],
                            "dependencies": ["Quote"]
                        },
                        "Quote": {
                            "type": "class",
                            "file": "src/main/java/com/company/quote/model/Quote.java",
                            "methods": ["getId", "getCustomerId", "getTotal", "addItem"],
                            "dependencies": ["QuoteItem"]
                        },
                        "QuoteItem": {
                            "type": "class",
                            "file": "src/main/java/com/company/quote/model/QuoteItem.java",
                            "methods": ["getProductId", "getQuantity", "getPrice", "getTotal"],
                            "dependencies": []
                        },
                        "QuoteCalculator": {
                            "type": "class",
                            "file": "src/main/java/com/company/quote/util/QuoteCalculator.java",
                            "methods": ["calculateTotal", "calculateTax", "calculateDiscount"],
                            "dependencies": ["Quote", "QuoteItem"]
                        }
                    }
                },
                "externaldata": {
                    "files": [
                        "src/main/java/com/company/external/ExternalDataController.java",
                        "src/main/java/com/company/external/ExternalDataService.java",
                        "src/main/java/com/company/external/ExternalDataRepository.java",
                        "src/main/java/com/company/external/model/ExternalData.java",
                        "src/main/java/com/company/external/integration/QuoteIntegration.java",
                        "src/main/java/com/company/external/util/DataValidator.java"
                    ],
                    "classes": {
                        "ExternalDataController": {
                            "type": "class",
                            "file": "src/main/java/com/company/external/ExternalDataController.java",
                            "methods": ["fetchData", "syncData", "getDataStatus"],
                            "dependencies": ["ExternalDataService"]
                        },
                        "ExternalDataService": {
                            "type": "class",
                            "file": "src/main/java/com/company/external/ExternalDataService.java",
                            "methods": ["processExternalData", "validateData", "transformData"],
                            "dependencies": ["ExternalDataRepository", "DataValidator", "QuoteIntegration"]
                        },
                        "ExternalDataRepository": {
                            "type": "interface",
                            "file": "src/main/java/com/company/external/ExternalDataRepository.java",
                            "methods": ["save", "findBySource", "findAll", "delete"],
                            "dependencies": ["ExternalData"]
                        },
                        "ExternalData": {
                            "type": "class",
                            "file": "src/main/java/com/company/external/model/ExternalData.java",
                            "methods": ["getId", "getSource", "getData", "getTimestamp"],
                            "dependencies": []
                        },
                        "QuoteIntegration": {
                            "type": "class",
                            "file": "src/main/java/com/company/external/integration/QuoteIntegration.java",
                            "methods": ["sendQuoteData", "receiveQuoteData", "validateQuoteData"],
                            "dependencies": ["Quote", "ExternalData"]
                        },
                        "DataValidator": {
                            "type": "class",
                            "file": "src/main/java/com/company/external/util/DataValidator.java",
                            "methods": ["validate", "sanitize", "checkFormat"],
                            "dependencies": ["ExternalData"]
                        }
                    }
                },
                "addresssearch": {
                    "files": [
                        "src/main/java/com/company/address/AddressController.java",
                        "src/main/java/com/company/address/AddressService.java",
                        "src/main/java/com/company/address/AddressRepository.java",
                        "src/main/java/com/company/address/model/Address.java",
                        "src/main/java/com/company/address/util/AddressValidator.java",
                        "src/main/java/com/company/address/integration/ExternalDataIntegration.java"
                    ],
                    "classes": {
                        "AddressController": {
                            "type": "class",
                            "file": "src/main/java/com/company/address/AddressController.java",
                            "methods": ["searchAddress", "validateAddress", "getAddressDetails"],
                            "dependencies": ["AddressService"]
                        },
                        "AddressService": {
                            "type": "class",
                            "file": "src/main/java/com/company/address/AddressService.java",
                            "methods": ["findAddresses", "validateAddress", "processAddress"],
                            "dependencies": ["AddressRepository", "AddressValidator", "ExternalDataIntegration"]
                        },
                        "AddressRepository": {
                            "type": "interface",
                            "file": "src/main/java/com/company/address/AddressRepository.java",
                            "methods": ["findByPostalCode", "findByCity", "save", "delete"],
                            "dependencies": ["Address"]
                        },
                        "Address": {
                            "type": "class",
                            "file": "src/main/java/com/company/address/model/Address.java",
                            "methods": ["getStreet", "getCity", "getPostalCode", "getCountry"],
                            "dependencies": []
                        },
                        "AddressValidator": {
                            "type": "class",
                            "file": "src/main/java/com/company/address/util/AddressValidator.java",
                            "methods": ["validatePostalCode", "validateCity", "validateFormat"],
                            "dependencies": ["Address"]
                        },
                        "ExternalDataIntegration": {
                            "type": "class",
                            "file": "src/main/java/com/company/address/integration/ExternalDataIntegration.java",
                            "methods": ["fetchAddressData", "syncAddressData"],
                            "dependencies": ["ExternalData", "Address"]
                        }
                    }
                }
            }
        }
    }

def populate_neo4j_data():
    """Populate Neo4j with fake data"""
    console.print("[bold blue]🗄️  Populating Neo4j with Fake Data[/bold blue]")
    console.print("=" * 60)
    
    # Check if Neo4j is configured
    config_manager = Neo4jConfigManager()
    if not config_manager.is_configured():
        console.print("[red]❌ Neo4j is not configured. Please run 'lumos-cli neo4j config' first.[/red]")
        return False
    
    # Load configuration
    config = config_manager.load_config()
    if not config:
        console.print("[red]❌ Failed to load Neo4j configuration.[/red]")
        return False
    
    # Create client
    client = Neo4jClient(config.uri, config.username, config.password)
    if not client.connect():
        console.print("[red]❌ Failed to connect to Neo4j.[/red]")
        return False
    
    # Get fake data
    fake_data = create_fake_repository_data()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Clear existing data
        task1 = progress.add_task("Clearing existing data...", total=None)
        for org, org_data in fake_data.items():
            for repo_name in org_data["repositories"].keys():
                client.clear_repository_data(org, repo_name)
        progress.update(task1, description="✅ Existing data cleared")
        
        # Create repositories
        task2 = progress.add_task("Creating repositories...", total=3)
        for org, org_data in fake_data.items():
            for repo_name, repo_data in org_data["repositories"].items():
                client.create_repository_node(org, repo_name, {
                    "description": f"Fake {repo_name} repository for testing",
                    "language": "Java",
                    "framework": "Spring Boot"
                })
                progress.advance(task2)
        
        # Create files and classes
        task3 = progress.add_task("Creating files and classes...", total=20)
        for org, org_data in fake_data.items():
            for repo_name, repo_data in org_data["repositories"].items():
                # Create files
                for file_path in repo_data["files"]:
                    file_type = "java" if file_path.endswith('.java') else "unknown"
                    client.create_file_node(org, repo_name, file_path, file_type)
                
                # Create classes
                for class_name, class_data in repo_data["classes"].items():
                    client.create_class_node(
                        org, repo_name, class_data["file"], 
                        class_name, class_data["type"],
                        {"description": f"Fake {class_name} class for testing"}
                    )
                    progress.advance(task3)
        
        # Create methods
        task4 = progress.add_task("Creating methods...", total=30)
        for org, org_data in fake_data.items():
            for repo_name, repo_data in org_data["repositories"].items():
                for class_name, class_data in repo_data["classes"].items():
                    for method_name in class_data["methods"]:
                        client.create_method_node(
                            org, repo_name, class_data["file"],
                            class_name, method_name,
                            {"description": f"Fake {method_name} method for testing"}
                        )
                        progress.advance(task4)
        
        # Create dependencies
        task5 = progress.add_task("Creating dependencies...", total=20)
        for org, org_data in fake_data.items():
            for repo_name, repo_data in org_data["repositories"].items():
                for class_name, class_data in repo_data["classes"].items():
                    for dep_class in class_data["dependencies"]:
                        client.create_dependency_relationship(
                            class_name, dep_class, org, repo_name, "USES"
                        )
                        progress.advance(task5)
        
        # Create cross-repository dependencies
        task6 = progress.add_task("Creating cross-repository dependencies...", total=5)
        # QuoteIntegration depends on Quote from quoteapp
        client.create_dependency_relationship("QuoteIntegration", "Quote", "scimarketplace", "externaldata", "USES")
        # ExternalDataIntegration depends on ExternalData from externaldata
        client.create_dependency_relationship("ExternalDataIntegration", "ExternalData", "scimarketplace", "addresssearch", "USES")
        # AddressService depends on ExternalDataIntegration
        client.create_dependency_relationship("AddressService", "ExternalDataIntegration", "scimarketplace", "addresssearch", "USES")
        progress.advance(task6, 3)
    
    # Show summary
    console.print("\n[bold green]✅ Data Population Complete![/bold green]")
    
    # Display summary table
    table = Table(title="Populated Data Summary")
    table.add_column("Organization", style="cyan")
    table.add_column("Repository", style="yellow")
    table.add_column("Files", style="green")
    table.add_column("Classes", style="blue")
    table.add_column("Methods", style="magenta")
    
    for org, org_data in fake_data.items():
        for repo_name, repo_data in org_data["repositories"].items():
            file_count = len(repo_data["files"])
            class_count = len(repo_data["classes"])
            method_count = sum(len(class_data["methods"]) for class_data in repo_data["classes"].values())
            
            table.add_row(org, repo_name, str(file_count), str(class_count), str(method_count))
    
    console.print(table)
    
    # Test some queries
    console.print("\n[bold cyan]🧪 Testing Graph Queries[/bold cyan]")
    
    # Test impact analysis
    impacts = client.find_impact_analysis("scimarketplace", "quoteapp", "QuoteService")
    console.print(f"Classes impacted by QuoteService changes: {len(impacts)}")
    for impact in impacts[:3]:  # Show first 3
        console.print(f"  • {impact['class_name']} ({impact['file_path']})")
    
    # Test dependencies
    deps = client.find_dependencies("scimarketplace", "quoteapp", "QuoteController")
    console.print(f"Dependencies of QuoteController: {len(deps)}")
    for dep in deps[:3]:  # Show first 3
        console.print(f"  • {dep['class_name']} ({dep['file_path']})")
    
    # Repository overview
    overview = client.get_repository_overview("scimarketplace", "quoteapp")
    console.print(f"QuoteApp repository: {overview['file_count']} files, {overview['class_count']} classes, {overview['method_count']} methods")
    
    client.close()
    console.print("\n[bold green]🎉 Neo4j population completed successfully![/bold green]")
    return True

if __name__ == "__main__":
    success = populate_neo4j_data()
    sys.exit(0 if success else 1)
