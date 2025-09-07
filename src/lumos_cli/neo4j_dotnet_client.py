"""
Neo4j client for .NET Core applications
Implements the specific schema for .NET repositories with Controllers, Classes, Methods, Enums, Constants, and Stored Procedures
"""

import os
import json
from typing import List, Dict, Optional, Any
from neo4j import GraphDatabase
from rich.console import Console
from .debug_logger import get_debug_logger

console = Console()
debug_logger = get_debug_logger()

class Neo4jDotNetClient:
    """Client for Neo4j graph database operations specific to .NET Core applications"""
    
    def __init__(self, uri: str = None, username: str = None, password: str = None):
        """Initialize Neo4j .NET client"""
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.username = username or os.getenv('NEO4J_USERNAME', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'password')
        self.driver = None
        
        debug_logger.log_function_call("Neo4jDotNetClient.__init__", kwargs={
            "uri": self.uri,
            "username": self.username
        })
    
    def connect(self) -> bool:
        """Connect to Neo4j database"""
        debug_logger.log_function_call("Neo4jDotNetClient.connect")
        
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value == 1:
                    debug_logger.info("Neo4j .NET connection successful")
                    debug_logger.log_function_return("Neo4jDotNetClient.connect", "Success")
                    return True
        except Exception as e:
            debug_logger.error(f"Neo4j .NET connection failed: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.connect", "Failed")
            return False
        
        return False
    
    def test_connection(self) -> bool:
        """Test if Neo4j connection is working"""
        debug_logger.log_function_call("Neo4jDotNetClient.test_connection")
        
        if not self.driver:
            if not self.connect():
                debug_logger.log_function_return("Neo4jDotNetClient.test_connection", "No connection")
                return False
        
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                success = test_value == 1
                debug_logger.log_function_return("Neo4jDotNetClient.test_connection", f"Success: {success}")
                return success
        except Exception as e:
            debug_logger.error(f"Neo4j .NET connection test failed: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.test_connection", "Failed")
            return False
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            debug_logger.info("Neo4j .NET connection closed")
    
    def create_repository_node(self, name: str, namespace: str, type: str = "Repository", source: str = "github") -> bool:
        """Create a Repository node"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_repository_node", kwargs={
            "name": name, "namespace": namespace, "type": type, "source": source
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (r:Repository {name: $name, namespace: $namespace})
                SET r.type = $type,
                    r.source = $source,
                    r.created_at = datetime()
                RETURN r
                """
                
                result = session.run(query, {
                    "name": name,
                    "namespace": namespace,
                    "type": type,
                    "source": source
                })
                
                debug_logger.info(f"Created repository node: {name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_repository_node", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create repository node: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_repository_node", "Failed")
            return False
    
    def create_class_node(self, name: str, namespace: str, type: str = "Class", source: str = "dotnet") -> bool:
        """Create a Class node"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_class_node", kwargs={
            "name": name, "namespace": namespace, "type": type, "source": source
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (c:Class {name: $name, namespace: $namespace})
                SET c.type = $type,
                    c.source = $source,
                    c.created_at = datetime()
                RETURN c
                """
                
                result = session.run(query, {
                    "name": name,
                    "namespace": namespace,
                    "type": type,
                    "source": source
                })
                
                debug_logger.info(f"Created class node: {name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_class_node", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create class node: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_class_node", "Failed")
            return False
    
    def create_method_node(self, name: str, namespace: str, type: str = "Method", source: str = "dotnet") -> bool:
        """Create a Method node"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_method_node", kwargs={
            "name": name, "namespace": namespace, "type": type, "source": source
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (m:Method {name: $name, namespace: $namespace})
                SET m.type = $type,
                    m.source = $source,
                    m.created_at = datetime()
                RETURN m
                """
                
                result = session.run(query, {
                    "name": name,
                    "namespace": namespace,
                    "type": type,
                    "source": source
                })
                
                debug_logger.info(f"Created method node: {name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_method_node", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create method node: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_method_node", "Failed")
            return False
    
    def create_enum_node(self, name: str, namespace: str, type: str = "Enum", source: str = "dotnet") -> bool:
        """Create an Enum node"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_enum_node", kwargs={
            "name": name, "namespace": namespace, "type": type, "source": source
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (e:Enum {name: $name, namespace: $namespace})
                SET e.type = $type,
                    e.source = $source,
                    e.created_at = datetime()
                RETURN e
                """
                
                result = session.run(query, {
                    "name": name,
                    "namespace": namespace,
                    "type": type,
                    "source": source
                })
                
                debug_logger.info(f"Created enum node: {name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_enum_node", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create enum node: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_enum_node", "Failed")
            return False
    
    def create_constant_node(self, name: str, namespace: str, type: str = "Constant", source: str = "dotnet") -> bool:
        """Create a Constant node"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_constant_node", kwargs={
            "name": name, "namespace": namespace, "type": type, "source": source
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (c:Constant {name: $name, namespace: $namespace})
                SET c.type = $type,
                    c.source = $source,
                    c.created_at = datetime()
                RETURN c
                """
                
                result = session.run(query, {
                    "name": name,
                    "namespace": namespace,
                    "type": type,
                    "source": source
                })
                
                debug_logger.info(f"Created constant node: {name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_constant_node", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create constant node: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_constant_node", "Failed")
            return False
    
    def create_controller_node(self, name: str, namespace: str, type: str = "Controller", source: str = "dotnet") -> bool:
        """Create a Controller node (represents API routes)"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_controller_node", kwargs={
            "name": name, "namespace": namespace, "type": type, "source": source
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (c:Controller {name: $name, namespace: $namespace})
                SET c.type = $type,
                    c.source = $source,
                    c.created_at = datetime()
                RETURN c
                """
                
                result = session.run(query, {
                    "name": name,
                    "namespace": namespace,
                    "type": type,
                    "source": source
                })
                
                debug_logger.info(f"Created controller node: {name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_controller_node", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create controller node: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_controller_node", "Failed")
            return False
    
    def create_stored_procedure_node(self, name: str, namespace: str, type: str = "StoredProcedure", source: str = "database") -> bool:
        """Create a StoredProcedure node"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_stored_procedure_node", kwargs={
            "name": name, "namespace": namespace, "type": type, "source": source
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (sp:StoredProcedure {name: $name, namespace: $namespace})
                SET sp.type = $type,
                    sp.source = $source,
                    sp.created_at = datetime()
                RETURN sp
                """
                
                result = session.run(query, {
                    "name": name,
                    "namespace": namespace,
                    "type": type,
                    "source": source
                })
                
                debug_logger.info(f"Created stored procedure node: {name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_stored_procedure_node", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create stored procedure node: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_stored_procedure_node", "Failed")
            return False
    
    def create_table_node(self, name: str, namespace: str, type: str = "Table", source: str = "database") -> bool:
        """Create a Table node"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_table_node", kwargs={
            "name": name, "namespace": namespace, "type": type, "source": source
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (t:Table {name: $name, namespace: $namespace})
                SET t.type = $type,
                    t.source = $source,
                    t.created_at = datetime()
                RETURN t
                """
                
                result = session.run(query, {
                    "name": name,
                    "namespace": namespace,
                    "type": type,
                    "source": source
                })
                
                debug_logger.info(f"Created table node: {name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_table_node", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create table node: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_table_node", "Failed")
            return False
    
    # Relationship creation methods
    def create_repository_dependency(self, from_repo: str, to_repo: str, from_namespace: str, to_namespace: str) -> bool:
        """Create Repository :DEPENDS_ON Repository relationship"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_repository_dependency", kwargs={
            "from_repo": from_repo, "to_repo": to_repo
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (from:Repository {name: $from_repo, namespace: $from_namespace})
                MATCH (to:Repository {name: $to_repo, namespace: $to_namespace})
                MERGE (from)-[r:DEPENDS_ON]->(to)
                SET r.created_at = datetime()
                RETURN r
                """
                
                result = session.run(query, {
                    "from_repo": from_repo,
                    "to_repo": to_repo,
                    "from_namespace": from_namespace,
                    "to_namespace": to_namespace
                })
                
                debug_logger.info(f"Created repository dependency: {from_repo} -> {to_repo}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_repository_dependency", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create repository dependency: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_repository_dependency", "Failed")
            return False
    
    def create_repository_has_class(self, repo_name: str, repo_namespace: str, class_name: str, class_namespace: str) -> bool:
        """Create Repository :HAS_CLASSES Class relationship"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_repository_has_class", kwargs={
            "repo_name": repo_name, "class_name": class_name
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (r:Repository {name: $repo_name, namespace: $repo_namespace})
                MATCH (c:Class {name: $class_name, namespace: $class_namespace})
                MERGE (r)-[r2c:HAS_CLASSES]->(c)
                SET r2c.created_at = datetime()
                RETURN r2c
                """
                
                result = session.run(query, {
                    "repo_name": repo_name,
                    "repo_namespace": repo_namespace,
                    "class_name": class_name,
                    "class_namespace": class_namespace
                })
                
                debug_logger.info(f"Created repository has class: {repo_name} -> {class_name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_repository_has_class", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create repository has class: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_repository_has_class", "Failed")
            return False
    
    def create_repository_has_constant(self, repo_name: str, repo_namespace: str, constant_name: str, constant_namespace: str) -> bool:
        """Create Repository :HAS_CONSTANTS Constant relationship"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_repository_has_constant", kwargs={
            "repo_name": repo_name, "constant_name": constant_name
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (r:Repository {name: $repo_name, namespace: $repo_namespace})
                MATCH (c:Constant {name: $constant_name, namespace: $constant_namespace})
                MERGE (r)-[r2c:HAS_CONSTANTS]->(c)
                SET r2c.created_at = datetime()
                RETURN r2c
                """
                
                result = session.run(query, {
                    "repo_name": repo_name,
                    "repo_namespace": repo_namespace,
                    "constant_name": constant_name,
                    "constant_namespace": constant_namespace
                })
                
                debug_logger.info(f"Created repository has constant: {repo_name} -> {constant_name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_repository_has_constant", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create repository has constant: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_repository_has_constant", "Failed")
            return False
    
    def create_repository_has_enum(self, repo_name: str, repo_namespace: str, enum_name: str, enum_namespace: str) -> bool:
        """Create Repository :HAS_ENUMS Enum relationship"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_repository_has_enum", kwargs={
            "repo_name": repo_name, "enum_name": enum_name
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (r:Repository {name: $repo_name, namespace: $repo_namespace})
                MATCH (e:Enum {name: $enum_name, namespace: $enum_namespace})
                MERGE (r)-[r2e:HAS_ENUMS]->(e)
                SET r2e.created_at = datetime()
                RETURN r2e
                """
                
                result = session.run(query, {
                    "repo_name": repo_name,
                    "repo_namespace": repo_namespace,
                    "enum_name": enum_name,
                    "enum_namespace": enum_namespace
                })
                
                debug_logger.info(f"Created repository has enum: {repo_name} -> {enum_name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_repository_has_enum", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create repository has enum: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_repository_has_enum", "Failed")
            return False
    
    def create_class_has_method(self, class_name: str, class_namespace: str, method_name: str, method_namespace: str) -> bool:
        """Create Class :HAS_METHOD Method relationship"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_class_has_method", kwargs={
            "class_name": class_name, "method_name": method_name
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (c:Class {name: $class_name, namespace: $class_namespace})
                MATCH (m:Method {name: $method_name, namespace: $method_namespace})
                MERGE (c)-[c2m:HAS_METHOD]->(m)
                SET c2m.created_at = datetime()
                RETURN c2m
                """
                
                result = session.run(query, {
                    "class_name": class_name,
                    "class_namespace": class_namespace,
                    "method_name": method_name,
                    "method_namespace": method_namespace
                })
                
                debug_logger.info(f"Created class has method: {class_name} -> {method_name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_class_has_method", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create class has method: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_class_has_method", "Failed")
            return False
    
    def create_method_calls_method(self, from_method: str, from_namespace: str, to_method: str, to_namespace: str) -> bool:
        """Create Method :CALLS_METHOD Method relationship"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_method_calls_method", kwargs={
            "from_method": from_method, "to_method": to_method
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (from:Method {name: $from_method, namespace: $from_namespace})
                MATCH (to:Method {name: $to_method, namespace: $to_namespace})
                MERGE (from)-[m2m:CALLS_METHOD]->(to)
                SET m2m.created_at = datetime()
                RETURN m2m
                """
                
                result = session.run(query, {
                    "from_method": from_method,
                    "from_namespace": from_namespace,
                    "to_method": to_method,
                    "to_namespace": to_namespace
                })
                
                debug_logger.info(f"Created method calls method: {from_method} -> {to_method}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_method_calls_method", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create method calls method: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_method_calls_method", "Failed")
            return False
    
    def create_class_calls_sp(self, class_name: str, class_namespace: str, sp_name: str, sp_namespace: str) -> bool:
        """Create Class :CALLS_SP StoredProcedure relationship"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_class_calls_sp", kwargs={
            "class_name": class_name, "sp_name": sp_name
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (c:Class {name: $class_name, namespace: $class_namespace})
                MATCH (sp:StoredProcedure {name: $sp_name, namespace: $sp_namespace})
                MERGE (c)-[c2sp:CALLS_SP]->(sp)
                SET c2sp.created_at = datetime()
                RETURN c2sp
                """
                
                result = session.run(query, {
                    "class_name": class_name,
                    "class_namespace": class_namespace,
                    "sp_name": sp_name,
                    "sp_namespace": sp_namespace
                })
                
                debug_logger.info(f"Created class calls stored procedure: {class_name} -> {sp_name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_class_calls_sp", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create class calls stored procedure: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_class_calls_sp", "Failed")
            return False
    
    def create_sp_has_table(self, sp_name: str, sp_namespace: str, table_name: str, table_namespace: str) -> bool:
        """Create StoredProcedure :HAS_TABLES Table relationship"""
        debug_logger.log_function_call("Neo4jDotNetClient.create_sp_has_table", kwargs={
            "sp_name": sp_name, "table_name": table_name
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (sp:StoredProcedure {name: $sp_name, namespace: $sp_namespace})
                MATCH (t:Table {name: $table_name, namespace: $table_namespace})
                MERGE (sp)-[sp2t:HAS_TABLES]->(t)
                SET sp2t.created_at = datetime()
                RETURN sp2t
                """
                
                result = session.run(query, {
                    "sp_name": sp_name,
                    "sp_namespace": sp_namespace,
                    "table_name": table_name,
                    "table_namespace": table_namespace
                })
                
                debug_logger.info(f"Created stored procedure has table: {sp_name} -> {table_name}")
                debug_logger.log_function_return("Neo4jDotNetClient.create_sp_has_table", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create stored procedure has table: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.create_sp_has_table", "Failed")
            return False
    
    # Query methods
    def find_controllers_calling_sp(self, sp_name: str, sp_namespace: str) -> List[Dict]:
        """Find all controllers that call a specific stored procedure"""
        debug_logger.log_function_call("Neo4jDotNetClient.find_controllers_calling_sp", kwargs={
            "sp_name": sp_name, "sp_namespace": sp_namespace
        })
        
        try:
            with self.driver.session() as session:
                # First try direct class to stored procedure relationship
                query = """
                MATCH (c:Class {type: "Controller"})-[:CALLS_SP]->(sp:StoredProcedure {name: $sp_name, namespace: $sp_namespace})
                RETURN DISTINCT c.name as controller_name, c.namespace as controller_namespace
                ORDER BY c.name
                """
                
                result = session.run(query, {
                    "sp_name": sp_name,
                    "sp_namespace": sp_namespace
                })
                
                controllers = []
                for record in result:
                    controllers.append({
                        "controller_name": record["controller_name"],
                        "controller_namespace": record["controller_namespace"]
                    })
                
                # If no direct relationships found, try through methods
                if not controllers:
                    query2 = """
                    MATCH (c:Class {type: "Controller"})-[:HAS_METHOD]->(m:Method)
                    MATCH (m)-[:CALLS_SP]->(sp:StoredProcedure {name: $sp_name, namespace: $sp_namespace})
                    RETURN DISTINCT c.name as controller_name, c.namespace as controller_namespace
                    ORDER BY c.name
                    """
                    
                    result2 = session.run(query2, {
                        "sp_name": sp_name,
                        "sp_namespace": sp_namespace
                    })
                    
                    for record in result2:
                        controllers.append({
                            "controller_name": record["controller_name"],
                            "controller_namespace": record["controller_namespace"]
                        })
                
                debug_logger.info(f"Found {len(controllers)} controllers calling {sp_name}")
                debug_logger.log_function_return("Neo4jDotNetClient.find_controllers_calling_sp", f"Found {len(controllers)} controllers")
                return controllers
                
        except Exception as e:
            debug_logger.error(f"Failed to find controllers calling stored procedure: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.find_controllers_calling_sp", "Failed")
            return []
    
    def find_classes_using_constant(self, constant_name: str, constant_namespace: str) -> List[Dict]:
        """Find all classes that use a specific constant"""
        debug_logger.log_function_call("Neo4jDotNetClient.find_classes_using_constant", kwargs={
            "constant_name": constant_name, "constant_namespace": constant_namespace
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
                MATCH (m)-[:CALLS_METHOD]->(m2:Method)
                MATCH (m2)-[:USES_CONSTANT]->(const:Constant {name: $constant_name, namespace: $constant_namespace})
                RETURN DISTINCT c.name as class_name, c.namespace as class_namespace
                ORDER BY c.name
                """
                
                result = session.run(query, {
                    "constant_name": constant_name,
                    "constant_namespace": constant_namespace
                })
                
                classes = []
                for record in result:
                    classes.append({
                        "class_name": record["class_name"],
                        "class_namespace": record["class_namespace"]
                    })
                
                debug_logger.info(f"Found {len(classes)} classes using {constant_name}")
                debug_logger.log_function_return("Neo4jDotNetClient.find_classes_using_constant", f"Found {len(classes)} classes")
                return classes
                
        except Exception as e:
            debug_logger.error(f"Failed to find classes using constant: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.find_classes_using_constant", "Failed")
            return []
    
    def get_repository_overview(self, repo_name: str, repo_namespace: str) -> Dict:
        """Get overview of repository structure"""
        debug_logger.log_function_call("Neo4jDotNetClient.get_repository_overview", kwargs={
            "repo_name": repo_name, "repo_namespace": repo_namespace
        })
        
        try:
            with self.driver.session() as session:
                # Get counts for each node type
                count_query = """
                MATCH (r:Repository {name: $repo_name, namespace: $repo_namespace})
                OPTIONAL MATCH (r)-[:HAS_CLASSES]->(c:Class)
                OPTIONAL MATCH (r)-[:HAS_CONSTANTS]->(const:Constant)
                OPTIONAL MATCH (r)-[:HAS_ENUMS]->(e:Enum)
                OPTIONAL MATCH (c)-[:HAS_METHOD]->(m:Method)
                OPTIONAL MATCH (r)-[:HAS_CLASSES]->(ctrl:Class {type: "Controller"})
                RETURN count(DISTINCT c) as class_count,
                       count(DISTINCT const) as constant_count,
                       count(DISTINCT e) as enum_count,
                       count(DISTINCT m) as method_count,
                       count(DISTINCT ctrl) as controller_count
                """
                
                result = session.run(count_query, {"repo_name": repo_name, "repo_namespace": repo_namespace})
                record = result.single()
                
                overview = {
                    "class_count": record["class_count"] or 0,
                    "constant_count": record["constant_count"] or 0,
                    "enum_count": record["enum_count"] or 0,
                    "method_count": record["method_count"] or 0,
                    "controller_count": record["controller_count"] or 0
                }
                
                debug_logger.info(f"Repository overview: {overview}")
                debug_logger.log_function_return("Neo4jDotNetClient.get_repository_overview", f"Overview: {overview}")
                return overview
                
        except Exception as e:
            debug_logger.error(f"Failed to get repository overview: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.get_repository_overview", "Failed")
            return {}
    
    def clear_repository_data(self, repo_name: str, repo_namespace: str) -> bool:
        """Clear all data for a specific repository"""
        debug_logger.log_function_call("Neo4jDotNetClient.clear_repository_data", kwargs={
            "repo_name": repo_name, "repo_namespace": repo_namespace
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (r:Repository {name: $repo_name, namespace: $repo_namespace})
                DETACH DELETE r
                """
                
                session.run(query, {"repo_name": repo_name, "repo_namespace": repo_namespace})
                
                debug_logger.info(f"Cleared all data for repository: {repo_name}")
                debug_logger.log_function_return("Neo4jDotNetClient.clear_repository_data", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to clear repository data: {e}")
            debug_logger.log_function_return("Neo4jDotNetClient.clear_repository_data", "Failed")
            return False
