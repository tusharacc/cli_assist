"""
Neo4j client for Lumos CLI
Handles graph database operations for code analysis and impact assessment
"""

import os
import json
from typing import List, Dict, Optional, Any
from neo4j import GraphDatabase
from rich.console import Console
from .debug_logger import get_debug_logger

console = Console()
debug_logger = get_debug_logger()

class Neo4jClient:
    """Client for Neo4j graph database operations"""
    
    def __init__(self, uri: str = None, username: str = None, password: str = None):
        """Initialize Neo4j client"""
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.username = username or os.getenv('NEO4J_USERNAME', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'password')
        self.driver = None
        
        debug_logger.log_function_call("Neo4jClient.__init__", kwargs={
            "uri": self.uri,
            "username": self.username
        })
    
    def connect(self) -> bool:
        """Connect to Neo4j database"""
        debug_logger.log_function_call("Neo4jClient.connect")
        
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value == 1:
                    debug_logger.info("Neo4j connection successful")
                    debug_logger.log_function_return("Neo4jClient.connect", "Success")
                    return True
        except Exception as e:
            debug_logger.error(f"Neo4j connection failed: {e}")
            debug_logger.log_function_return("Neo4jClient.connect", "Failed")
            return False
        
        return False
    
    def test_connection(self) -> bool:
        """Test if Neo4j connection is working"""
        debug_logger.log_function_call("Neo4jClient.test_connection")
        
        if not self.driver:
            if not self.connect():
                debug_logger.log_function_return("Neo4jClient.test_connection", "No connection")
                return False
        
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                success = test_value == 1
                debug_logger.log_function_return("Neo4jClient.test_connection", f"Success: {success}")
                return success
        except Exception as e:
            debug_logger.error(f"Neo4j connection test failed: {e}")
            debug_logger.log_function_return("Neo4jClient.test_connection", "Failed")
            return False
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            debug_logger.info("Neo4j connection closed")
    
    def create_repository_node(self, org: str, repo: str, metadata: Dict = None) -> bool:
        """Create a repository node in the graph"""
        debug_logger.log_function_call("Neo4jClient.create_repository_node", kwargs={
            "org": org, "repo": repo, "metadata": metadata
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (r:Repository {name: $repo, organization: $org})
                SET r.url = $url,
                    r.created_at = datetime(),
                    r.metadata = $metadata
                RETURN r
                """
                
                result = session.run(query, {
                    "repo": repo,
                    "org": org,
                    "url": f"https://github.com/{org}/{repo}",
                    "metadata": json.dumps(metadata) if metadata else None
                })
                
                debug_logger.info(f"Created repository node: {org}/{repo}")
                debug_logger.log_function_return("Neo4jClient.create_repository_node", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create repository node: {e}")
            debug_logger.log_function_return("Neo4jClient.create_repository_node", "Failed")
            return False
    
    def create_file_node(self, org: str, repo: str, file_path: str, file_type: str = None) -> bool:
        """Create a file node in the graph"""
        debug_logger.log_function_call("Neo4jClient.create_file_node", kwargs={
            "org": org, "repo": repo, "file_path": file_path, "file_type": file_type
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (r:Repository {name: $repo, organization: $org})
                MERGE (f:File {path: $file_path, repository: $repo, organization: $org})
                SET f.type = $file_type,
                    f.extension = $extension,
                    f.created_at = datetime()
                MERGE (r)-[:CONTAINS]->(f)
                RETURN f
                """
                
                extension = file_path.split('.')[-1] if '.' in file_path else None
                
                result = session.run(query, {
                    "repo": repo,
                    "org": org,
                    "file_path": file_path,
                    "file_type": file_type or "unknown",
                    "extension": extension
                })
                
                debug_logger.info(f"Created file node: {file_path}")
                debug_logger.log_function_return("Neo4jClient.create_file_node", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create file node: {e}")
            debug_logger.log_function_return("Neo4jClient.create_file_node", "Failed")
            return False
    
    def create_class_node(self, org: str, repo: str, file_path: str, class_name: str, 
                         class_type: str = "class", metadata: Dict = None) -> bool:
        """Create a class node in the graph"""
        debug_logger.log_function_call("Neo4jClient.create_class_node", kwargs={
            "org": org, "repo": repo, "file_path": file_path, 
            "class_name": class_name, "class_type": class_type
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (r:Repository {name: $repo, organization: $org})
                MERGE (c:Class {name: $class_name, namespace: $namespace})
                SET c.type = $class_type,
                    c.file_path = $file_path,
                    c.source = $repo,
                    c.metadata = $metadata,
                    c.created_at = datetime()
                MERGE (r)-[:HAS_CLASSES]->(c)
                RETURN c
                """
                
                # Generate namespace from org and repo
                namespace = f"{org}.{repo}"
                
                result = session.run(query, {
                    "repo": repo,
                    "org": org,
                    "file_path": file_path,
                    "class_name": class_name,
                    "class_type": class_type,
                    "namespace": namespace,
                    "metadata": json.dumps(metadata) if metadata else None
                })
                
                debug_logger.info(f"Created class node: {class_name}")
                debug_logger.log_function_return("Neo4jClient.create_class_node", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create class node: {e}")
            debug_logger.log_function_return("Neo4jClient.create_class_node", "Failed")
            return False
    
    def create_method_node(self, org: str, repo: str, file_path: str, class_name: str, 
                          method_name: str, metadata: Dict = None) -> bool:
        """Create a method node in the graph"""
        debug_logger.log_function_call("Neo4jClient.create_method_node", kwargs={
            "org": org, "repo": repo, "file_path": file_path, 
            "class_name": class_name, "method_name": method_name
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (r:Repository {name: $repo, organization: $org})
                MATCH (r)-[:HAS_CLASSES]->(c:Class {name: $class_name, namespace: $namespace})
                MERGE (m:Method {name: $method_name, namespace: $method_namespace})
                SET m.class_name = $class_name,
                    m.file_path = $file_path,
                    m.source = $repo,
                    m.metadata = $metadata,
                    m.created_at = datetime()
                MERGE (c)-[:HAS_METHOD]->(m)
                RETURN m
                """
                
                # Generate namespaces
                namespace = f"{org}.{repo}"
                method_namespace = f"{org}.{repo}.{class_name}.{method_name}"
                
                result = session.run(query, {
                    "repo": repo,
                    "org": org,
                    "file_path": file_path,
                    "class_name": class_name,
                    "method_name": method_name,
                    "namespace": namespace,
                    "method_namespace": method_namespace,
                    "metadata": json.dumps(metadata) if metadata else None
                })
                
                debug_logger.info(f"Created method node: {class_name}.{method_name}")
                debug_logger.log_function_return("Neo4jClient.create_method_node", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create method node: {e}")
            debug_logger.log_function_return("Neo4jClient.create_method_node", "Failed")
            return False
    
    def create_dependency_relationship(self, from_class: str, to_class: str, 
                                     org: str, repo: str, dep_type: str = "USES") -> bool:
        """Create a dependency relationship between classes"""
        debug_logger.log_function_call("Neo4jClient.create_dependency_relationship", kwargs={
            "from_class": from_class, "to_class": to_class, 
            "org": org, "repo": repo, "dep_type": dep_type
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (r:Repository {name: $repo, organization: $org})
                MATCH (r)-[:HAS_CLASSES]->(from:Class {name: $from_class, namespace: $namespace})
                MATCH (r)-[:HAS_CLASSES]->(to:Class {name: $to_class, namespace: $namespace})
                MERGE (from)-[rel:DEPENDS_ON {type: $dep_type}]->(to)
                SET rel.created_at = datetime()
                RETURN rel
                """
                
                # Generate namespace
                namespace = f"{org}.{repo}"
                
                result = session.run(query, {
                    "from_class": from_class,
                    "to_class": to_class,
                    "repo": repo,
                    "org": org,
                    "namespace": namespace,
                    "dep_type": dep_type
                })
                
                debug_logger.info(f"Created dependency: {from_class} -> {to_class}")
                debug_logger.log_function_return("Neo4jClient.create_dependency_relationship", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to create dependency relationship: {e}")
            debug_logger.log_function_return("Neo4jClient.create_dependency_relationship", "Failed")
            return False
    
    def find_impact_analysis(self, org: str, repo: str, class_name: str) -> List[Dict]:
        """Find what classes/methods are impacted by changes to a class"""
        debug_logger.log_function_call("Neo4jClient.find_impact_analysis", kwargs={
            "org": org, "repo": repo, "class_name": class_name
        })
        
        try:
            with self.driver.session() as session:
                # Enterprise schema uses namespace and source properties
                query = """
                MATCH (target:Class {name: $class_name, source: $repo})
                MATCH (dependent:Class)-[:DEPENDS_ON]->(target)
                OPTIONAL MATCH (dependent)<-[:HAS_CLASSES]-(dependent_repo:Repository)
                RETURN dependent.name as dependent_class,
                       dependent.type as class_type,
                       dependent.file_path as file_path,
                       dependent.namespace as dependent_namespace,
                       COALESCE(dependent_repo.name, dependent.source) as repository
                ORDER BY dependent.name
                """
                
                result = session.run(query, {
                    "class_name": class_name,
                    "repo": repo,
                    "org": org
                })
                
                impacts = []
                for record in result:
                    impacts.append({
                        "class_name": record["dependent_class"],
                        "class_type": record["class_type"],
                        "file_path": record["file_path"],
                        "namespace": record["dependent_namespace"],
                        "repository": record["repository"]
                    })
                
                debug_logger.info(f"Found {len(impacts)} dependent classes for {class_name}")
                debug_logger.log_function_return("Neo4jClient.find_impact_analysis", f"Found {len(impacts)} impacts")
                return impacts
                
        except Exception as e:
            debug_logger.error(f"Failed to find impact analysis: {e}")
            debug_logger.log_function_return("Neo4jClient.find_impact_analysis", "Failed")
            return []
    
    def find_dependencies(self, org: str, repo: str, class_name: str) -> List[Dict]:
        """Find what classes a given class depends on"""
        debug_logger.log_function_call("Neo4jClient.find_dependencies", kwargs={
            "org": org, "repo": repo, "class_name": class_name
        })
        
        try:
            with self.driver.session() as session:
                # Enterprise schema uses namespace and source properties
                query = """
                MATCH (source:Class {name: $class_name, source: $repo})
                MATCH (source)-[r:DEPENDS_ON]->(target:Class)
                OPTIONAL MATCH (target)<-[:HAS_CLASSES]-(target_repo:Repository)
                RETURN target.name as target_class,
                       target.type as class_type,
                       target.file_path as file_path,
                       target.namespace as target_namespace,
                       r.type as dependency_type,
                       COALESCE(target_repo.name, target.source) as repository
                ORDER BY target.name
                """
                
                result = session.run(query, {
                    "class_name": class_name,
                    "repo": repo,
                    "org": org
                })
                
                dependencies = []
                for record in result:
                    dependencies.append({
                        "class_name": record["target_class"],
                        "class_type": record["class_type"],
                        "file_path": record["file_path"],
                        "namespace": record["target_namespace"],
                        "dependency_type": record["dependency_type"],
                        "repository": record["repository"]
                    })
                
                debug_logger.info(f"Found {len(dependencies)} dependencies for {class_name}")
                debug_logger.log_function_return("Neo4jClient.find_dependencies", f"Found {len(dependencies)} dependencies")
                return dependencies
                
        except Exception as e:
            debug_logger.error(f"Failed to find dependencies: {e}")
            debug_logger.log_function_return("Neo4jClient.find_dependencies", "Failed")
            return []
    
    def get_repository_overview(self, org: str, repo: str) -> Dict:
        """Get overview of repository structure"""
        debug_logger.log_function_call("Neo4jClient.get_repository_overview", kwargs={
            "org": org, "repo": repo
        })
        
        try:
            with self.driver.session() as session:
                # Enterprise schema uses source property instead of organization
                count_query = """
                MATCH (r:Repository {name: $repo})
                OPTIONAL MATCH (r)-[:HAS_CLASSES]->(c:Class)
                OPTIONAL MATCH (c)-[:HAS_METHOD]->(m:Method)
                OPTIONAL MATCH (r)-[:HAS_CONSTANTS]->(const:Constant)
                OPTIONAL MATCH (r)-[:HAS_ENUMS]->(e:Enum)
                OPTIONAL MATCH (r)-[:HAS_ROUTES]->(ctrl)
                RETURN count(DISTINCT c) as class_count,
                       count(DISTINCT m) as method_count,
                       count(DISTINCT const) as constant_count,
                       count(DISTINCT e) as enum_count,
                       count(DISTINCT ctrl) as controller_count
                """
                
                result = session.run(count_query, {"repo": repo, "org": org})
                record = result.single()
                
                overview = {
                    "class_count": record["class_count"] or 0,
                    "method_count": record["method_count"] or 0,
                    "constant_count": record["constant_count"] or 0,
                    "enum_count": record["enum_count"] or 0,
                    "controller_count": record["controller_count"] or 0
                }
                
                debug_logger.info(f"Repository overview: {overview}")
                debug_logger.log_function_return("Neo4jClient.get_repository_overview", f"Overview: {overview}")
                return overview
                
        except Exception as e:
            debug_logger.error(f"Failed to get repository overview: {e}")
            debug_logger.log_function_return("Neo4jClient.get_repository_overview", "Failed")
            return {}
    
    def clear_repository_data(self, org: str, repo: str) -> bool:
        """Clear all data for a specific repository"""
        debug_logger.log_function_call("Neo4jClient.clear_repository_data", kwargs={
            "org": org, "repo": repo
        })
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (r:Repository {name: $repo, organization: $org})
                DETACH DELETE r
                """
                
                session.run(query, {"repo": repo, "org": org})
                
                debug_logger.info(f"Cleared all data for repository: {org}/{repo}")
                debug_logger.log_function_return("Neo4jClient.clear_repository_data", "Success")
                return True
                
        except Exception as e:
            debug_logger.error(f"Failed to clear repository data: {e}")
            debug_logger.log_function_return("Neo4jClient.clear_repository_data", "Failed")
            return False