#!/usr/bin/env python3
"""
Populate Neo4j with .NET Core fake data matching the specific schema
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.neo4j_dotnet_client import Neo4jDotNetClient
from lumos_cli.neo4j_config import Neo4jConfigManager
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import time

console = Console()

def create_dotnet_fake_data():
    """Create fake .NET Core data matching the schema"""
    return {
        "repositories": {
            "UserManagement": {
                "namespace": "Company.UserManagement",
                "type": "Repository",
                "source": "github",
                "classes": {
                    "UserController": {
                        "namespace": "Company.UserManagement.Controllers",
                        "type": "Controller",
                        "methods": ["GetUser", "CreateUser", "UpdateUser", "DeleteUser"],
                        "calls_sp": ["GetUserById", "CreateUserRecord", "UpdateUserRecord", "DeleteUserRecord"]
                    },
                    "UserService": {
                        "namespace": "Company.UserManagement.Services",
                        "type": "Class",
                        "methods": ["ValidateUser", "ProcessUserData", "SendUserNotification"],
                        "calls_sp": ["GetUserById", "CreateUserRecord", "UpdateUserRecord"]
                    },
                    "UserRepository": {
                        "namespace": "Company.UserManagement.Repositories",
                        "type": "Class",
                        "methods": ["FindById", "Save", "Delete", "FindAll"],
                        "calls_sp": ["GetUserById", "CreateUserRecord", "UpdateUserRecord", "DeleteUserRecord"]
                    },
                    "UserModel": {
                        "namespace": "Company.UserManagement.Models",
                        "type": "Class",
                        "methods": ["Validate", "ToJson", "FromJson"],
                        "calls_sp": []
                    }
                },
                "enums": {
                    "UserStatus": {
                        "namespace": "Company.UserManagement.Enums",
                        "values": ["Active", "Inactive", "Pending", "Suspended"]
                    },
                    "UserRole": {
                        "namespace": "Company.UserManagement.Enums",
                        "values": ["Admin", "User", "Moderator", "Guest"]
                    }
                },
                "constants": {
                    "UserConstants": {
                        "namespace": "Company.UserManagement.Constants",
                        "values": ["MAX_LOGIN_ATTEMPTS", "DEFAULT_PASSWORD_LENGTH", "SESSION_TIMEOUT"]
                    },
                    "ApiConstants": {
                        "namespace": "Company.UserManagement.Constants",
                        "values": ["API_VERSION", "DEFAULT_PAGE_SIZE", "MAX_PAGE_SIZE"]
                    }
                }
            },
            "OrderManagement": {
                "namespace": "Company.OrderManagement",
                "type": "Repository",
                "source": "github",
                "classes": {
                    "OrderController": {
                        "namespace": "Company.OrderManagement.Controllers",
                        "type": "Controller",
                        "methods": ["GetOrder", "CreateOrder", "UpdateOrder", "CancelOrder"],
                        "calls_sp": ["GetOrderById", "CreateOrderRecord", "UpdateOrderRecord", "CancelOrderRecord"]
                    },
                    "OrderService": {
                        "namespace": "Company.OrderManagement.Services",
                        "type": "Class",
                        "methods": ["CalculateTotal", "ValidateOrder", "ProcessPayment"],
                        "calls_sp": ["GetOrderById", "CreateOrderRecord", "UpdateOrderRecord"]
                    },
                    "OrderRepository": {
                        "namespace": "Company.OrderManagement.Repositories",
                        "type": "Class",
                        "methods": ["FindById", "Save", "Delete", "FindByUserId"],
                        "calls_sp": ["GetOrderById", "CreateOrderRecord", "UpdateOrderRecord", "GetOrdersByUser"]
                    },
                    "OrderModel": {
                        "namespace": "Company.OrderManagement.Models",
                        "type": "Class",
                        "methods": ["Validate", "CalculateTax", "ToJson"],
                        "calls_sp": []
                    }
                },
                "enums": {
                    "OrderStatus": {
                        "namespace": "Company.OrderManagement.Enums",
                        "values": ["Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"]
                    },
                    "PaymentStatus": {
                        "namespace": "Company.OrderManagement.Enums",
                        "values": ["Pending", "Paid", "Failed", "Refunded"]
                    }
                },
                "constants": {
                    "OrderConstants": {
                        "namespace": "Company.OrderManagement.Constants",
                        "values": ["DEFAULT_TAX_RATE", "MAX_ORDER_ITEMS", "ORDER_TIMEOUT"]
                    }
                }
            },
            "InventoryManagement": {
                "namespace": "Company.InventoryManagement",
                "type": "Repository",
                "source": "github",
                "classes": {
                    "ProductController": {
                        "namespace": "Company.InventoryManagement.Controllers",
                        "type": "Controller",
                        "methods": ["GetProduct", "CreateProduct", "UpdateProduct", "DeleteProduct"],
                        "calls_sp": ["GetProductById", "CreateProductRecord", "UpdateProductRecord", "DeleteProductRecord"]
                    },
                    "InventoryService": {
                        "namespace": "Company.InventoryManagement.Services",
                        "type": "Class",
                        "methods": ["CheckStock", "UpdateStock", "ReserveItem"],
                        "calls_sp": ["GetProductById", "UpdateProductRecord", "ReserveProduct"]
                    },
                    "ProductRepository": {
                        "namespace": "Company.InventoryManagement.Repositories",
                        "type": "Class",
                        "methods": ["FindById", "Save", "Delete", "FindByCategory"],
                        "calls_sp": ["GetProductById", "CreateProductRecord", "UpdateProductRecord", "GetProductsByCategory"]
                    }
                },
                "enums": {
                    "ProductStatus": {
                        "namespace": "Company.InventoryManagement.Enums",
                        "values": ["Available", "OutOfStock", "Discontinued", "ComingSoon"]
                    }
                },
                "constants": {
                    "InventoryConstants": {
                        "namespace": "Company.InventoryManagement.Constants",
                        "values": ["LOW_STOCK_THRESHOLD", "MAX_STOCK_LEVEL", "DEFAULT_CATEGORY"]
                    }
                }
            }
        },
        "stored_procedures": {
            "GetUserById": {
                "namespace": "dbo",
                "tables": ["Users", "UserProfiles"]
            },
            "CreateUserRecord": {
                "namespace": "dbo",
                "tables": ["Users", "UserProfiles", "UserRoles"]
            },
            "UpdateUserRecord": {
                "namespace": "dbo",
                "tables": ["Users", "UserProfiles"]
            },
            "DeleteUserRecord": {
                "namespace": "dbo",
                "tables": ["Users", "UserProfiles"]
            },
            "GetOrderById": {
                "namespace": "dbo",
                "tables": ["Orders", "OrderItems", "OrderStatus"]
            },
            "CreateOrderRecord": {
                "namespace": "dbo",
                "tables": ["Orders", "OrderItems", "OrderStatus"]
            },
            "UpdateOrderRecord": {
                "namespace": "dbo",
                "tables": ["Orders", "OrderItems", "OrderStatus"]
            },
            "CancelOrderRecord": {
                "namespace": "dbo",
                "tables": ["Orders", "OrderItems", "OrderStatus"]
            },
            "GetOrdersByUser": {
                "namespace": "dbo",
                "tables": ["Orders", "OrderItems", "Users"]
            },
            "GetProductById": {
                "namespace": "dbo",
                "tables": ["Products", "ProductCategories"]
            },
            "CreateProductRecord": {
                "namespace": "dbo",
                "tables": ["Products", "ProductCategories"]
            },
            "UpdateProductRecord": {
                "namespace": "dbo",
                "tables": ["Products", "ProductCategories"]
            },
            "DeleteProductRecord": {
                "namespace": "dbo",
                "tables": ["Products", "ProductCategories"]
            },
            "GetProductsByCategory": {
                "namespace": "dbo",
                "tables": ["Products", "ProductCategories"]
            },
            "ReserveProduct": {
                "namespace": "dbo",
                "tables": ["Products", "ProductReservations"]
            }
        },
        "tables": {
            "Users": {"namespace": "dbo"},
            "UserProfiles": {"namespace": "dbo"},
            "UserRoles": {"namespace": "dbo"},
            "Orders": {"namespace": "dbo"},
            "OrderItems": {"namespace": "dbo"},
            "OrderStatus": {"namespace": "dbo"},
            "Products": {"namespace": "dbo"},
            "ProductCategories": {"namespace": "dbo"},
            "ProductReservations": {"namespace": "dbo"}
        }
    }

def populate_neo4j_dotnet_data():
    """Populate Neo4j with .NET Core fake data"""
    console.print("[bold blue]🗄️  Populating Neo4j with .NET Core Data[/bold blue]")
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
    client = Neo4jDotNetClient(config.uri, config.username, config.password)
    if not client.connect():
        console.print("[red]❌ Failed to connect to Neo4j.[/red]")
        return False
    
    # Get fake data
    fake_data = create_dotnet_fake_data()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Clear existing data
        task1 = progress.add_task("Clearing existing data...", total=None)
        for repo_name, repo_data in fake_data["repositories"].items():
            client.clear_repository_data(repo_name, repo_data["namespace"])
        progress.update(task1, description="✅ Existing data cleared")
        
        # Create repositories
        task2 = progress.add_task("Creating repositories...", total=len(fake_data["repositories"]))
        for repo_name, repo_data in fake_data["repositories"].items():
            client.create_repository_node(
                repo_name, 
                repo_data["namespace"], 
                repo_data["type"], 
                repo_data["source"]
            )
            progress.advance(task2)
        
        # Create stored procedures
        task3 = progress.add_task("Creating stored procedures...", total=len(fake_data["stored_procedures"]))
        for sp_name, sp_data in fake_data["stored_procedures"].items():
            client.create_stored_procedure_node(
                sp_name, 
                sp_data["namespace"], 
                "StoredProcedure", 
                "database"
            )
            progress.advance(task3)
        
        # Create tables
        task4 = progress.add_task("Creating tables...", total=len(fake_data["tables"]))
        for table_name, table_data in fake_data["tables"].items():
            client.create_table_node(
                table_name, 
                table_data["namespace"], 
                "Table", 
                "database"
            )
            progress.advance(task4)
        
        # Create classes and relationships
        task5 = progress.add_task("Creating classes and relationships...", total=20)
        for repo_name, repo_data in fake_data["repositories"].items():
            # Create classes
            for class_name, class_data in repo_data["classes"].items():
                client.create_class_node(
                    class_name, 
                    class_data["namespace"], 
                    class_data["type"], 
                    "dotnet"
                )
                
                # Create repository has class relationship
                client.create_repository_has_class(
                    repo_name, 
                    repo_data["namespace"],
                    class_name, 
                    class_data["namespace"]
                )
                
                # Create methods
                for method_name in class_data["methods"]:
                    method_namespace = f"{class_data['namespace']}.{method_name}"
                    client.create_method_node(
                        method_name, 
                        method_namespace, 
                        "Method", 
                        "dotnet"
                    )
                    
                    # Create class has method relationship
                    client.create_class_has_method(
                        class_name, 
                        class_data["namespace"],
                        method_name, 
                        method_namespace
                    )
                
                # Create class calls stored procedure relationships
                for sp_name in class_data["calls_sp"]:
                    client.create_class_calls_sp(
                        class_name, 
                        class_data["namespace"],
                        sp_name, 
                        "dbo"
                    )
                
                # Create method calls method relationships (simplified - methods call other methods in same class)
                for i, method_name in enumerate(class_data["methods"]):
                    for j, other_method_name in enumerate(class_data["methods"]):
                        if i != j:  # Don't create self-references
                            method_namespace = f"{class_data['namespace']}.{method_name}"
                            other_method_namespace = f"{class_data['namespace']}.{other_method_name}"
                            client.create_method_calls_method(
                                method_name, 
                                method_namespace,
                                other_method_name, 
                                other_method_namespace
                            )
                
                progress.advance(task5)
        
        # Create enums and relationships
        task6 = progress.add_task("Creating enums and relationships...", total=10)
        for repo_name, repo_data in fake_data["repositories"].items():
            for enum_name, enum_data in repo_data["enums"].items():
                client.create_enum_node(
                    enum_name, 
                    enum_data["namespace"], 
                    "Enum", 
                    "dotnet"
                )
                
                # Create repository has enum relationship
                client.create_repository_has_enum(
                    repo_name, 
                    repo_data["namespace"],
                    enum_name, 
                    enum_data["namespace"]
                )
                progress.advance(task6)
        
        # Create constants and relationships
        task7 = progress.add_task("Creating constants and relationships...", total=10)
        for repo_name, repo_data in fake_data["repositories"].items():
            for const_name, const_data in repo_data["constants"].items():
                client.create_constant_node(
                    const_name, 
                    const_data["namespace"], 
                    "Constant", 
                    "dotnet"
                )
                
                # Create repository has constant relationship
                client.create_repository_has_constant(
                    repo_name, 
                    repo_data["namespace"],
                    const_name, 
                    const_data["namespace"]
                )
                progress.advance(task7)
        
        # Create stored procedure has table relationships
        task8 = progress.add_task("Creating stored procedure relationships...", total=15)
        for sp_name, sp_data in fake_data["stored_procedures"].items():
            for table_name in sp_data["tables"]:
                client.create_sp_has_table(
                    sp_name, 
                    "dbo",
                    table_name, 
                    "dbo"
                )
                progress.advance(task8)
    
    # Show summary
    console.print("\n[bold green]✅ .NET Data Population Complete![/bold green]")
    
    # Display summary table
    table = Table(title="Populated .NET Data Summary")
    table.add_column("Repository", style="cyan")
    table.add_column("Classes", style="yellow")
    table.add_column("Methods", style="green")
    table.add_column("Enums", style="blue")
    table.add_column("Constants", style="magenta")
    table.add_column("Stored Procedures", style="red")
    
    for repo_name, repo_data in fake_data["repositories"].items():
        class_count = len(repo_data["classes"])
        method_count = sum(len(class_data["methods"]) for class_data in repo_data["classes"].values())
        enum_count = len(repo_data["enums"])
        const_count = len(repo_data["constants"])
        sp_count = len([sp for sp in fake_data["stored_procedures"].keys() 
                       if any(sp in class_data["calls_sp"] for class_data in repo_data["classes"].values())])
        
        table.add_row(
            repo_name, 
            str(class_count), 
            str(method_count), 
            str(enum_count), 
            str(const_count),
            str(sp_count)
        )
    
    console.print(table)
    
    # Test some queries
    console.print("\n[bold cyan]🧪 Testing .NET Graph Queries[/bold cyan]")
    
    # Test controller calling stored procedure
    controllers = client.find_controllers_calling_sp("GetUserById", "dbo")
    console.print(f"Controllers calling GetUserById: {len(controllers)}")
    for controller in controllers[:3]:  # Show first 3
        console.print(f"  • {controller['controller_name']} ({controller['controller_namespace']})")
    
    # Repository overview
    overview = client.get_repository_overview("UserManagement", "Company.UserManagement")
    console.print(f"UserManagement repository: {overview['class_count']} classes, {overview['method_count']} methods, {overview['controller_count']} controllers")
    
    client.close()
    console.print("\n[bold green]🎉 .NET Neo4j population completed successfully![/bold green]")
    return True

if __name__ == "__main__":
    success = populate_neo4j_dotnet_data()
    sys.exit(0 if success else 1)
