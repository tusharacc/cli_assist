#!/usr/bin/env python3
"""
Neo4j client for graph database operations
"""

import json
from typing import Dict, List, Optional
from .debug_logger import debug_logger

class Neo4jClient:
    """Client for Neo4j graph database operations"""
    
    def __init__(self):
        self.uri = "bolt://localhost:7687"  # Default Neo4j URI
        self.username = "neo4j"
        self.password = "password"
        self.driver = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Neo4j connection"""
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            debug_logger.info("Neo4j connection initialized")
        except ImportError:
            debug_logger.warning("Neo4j driver not installed. Install with: pip install neo4j")
        except Exception as e:
            debug_logger.warning(f"Neo4j connection failed: {e}")
    
    def analyze_impact(self, changed_items: List[Dict]) -> Dict:
        """Analyze impact of changes using graph database"""
        debug_logger.log_function_call("Neo4jClient.analyze_impact", kwargs={"changed_items": len(changed_items)})
        
        if not self.driver:
            return self._mock_impact_analysis(changed_items)
        
        try:
            with self.driver.session() as session:
                # Query for affected repositories
                affected_repos = self._find_affected_repositories(session, changed_items)
                
                # Query for affected classes
                affected_classes = self._find_affected_classes(session, changed_items)
                
                # Query for affected functions
                affected_functions = self._find_affected_functions(session, changed_items)
                
                # Analyze dependency chain
                dependency_chain = self._analyze_dependency_chain(session, changed_items)
                
                # Assess risk level
                risk_assessment = self._assess_risk(affected_repos, affected_classes, affected_functions)
                
                result = {
                    'affected_repositories': affected_repos,
                    'affected_classes': affected_classes,
                    'affected_functions': affected_functions,
                    'dependency_chain': dependency_chain,
                    'risk_assessment': risk_assessment
                }
                
                debug_logger.log_function_return("Neo4jClient.analyze_impact", f"Found {len(affected_repos)} repos, {len(affected_classes)} classes")
                return result
                
        except Exception as e:
            debug_logger.error(f"Neo4j impact analysis failed: {e}")
            return self._mock_impact_analysis(changed_items)
    
    def _find_affected_repositories(self, session, changed_items: List[Dict]) -> List[Dict]:
        """Find repositories that might be affected by changes"""
        query = """
        MATCH (r:Repository)-[:CONTAINS]->(f:File)
        WHERE f.name IN $changed_files
        RETURN DISTINCT r.name as repository, r.url as url, count(f) as affected_files
        ORDER BY affected_files DESC
        """
        
        changed_files = [item['file'] for item in changed_items]
        result = session.run(query, changed_files=changed_files)
        
        return [dict(record) for record in result]
    
    def _find_affected_classes(self, session, changed_items: List[Dict]) -> List[Dict]:
        """Find classes that might be affected by changes"""
        query = """
        MATCH (c:Class)-[:DEFINED_IN]->(f:File)
        WHERE f.name IN $changed_files
        OPTIONAL MATCH (c)-[:INHERITS_FROM]->(parent:Class)
        OPTIONAL MATCH (c)-[:IMPLEMENTS]->(interface:Interface)
        RETURN DISTINCT c.name as class_name, c.type as class_type, 
               parent.name as parent_class, interface.name as interface,
               f.name as file_name
        """
        
        changed_files = [item['file'] for item in changed_items]
        result = session.run(query, changed_files=changed_files)
        
        return [dict(record) for record in result]
    
    def _find_affected_functions(self, session, changed_items: List[Dict]) -> List[Dict]:
        """Find functions that might be affected by changes"""
        query = """
        MATCH (func:Function)-[:DEFINED_IN]->(f:File)
        WHERE f.name IN $changed_files
        OPTIONAL MATCH (func)-[:CALLS]->(called:Function)
        RETURN DISTINCT func.name as function_name, func.signature as signature,
               f.name as file_name, count(called) as call_count
        ORDER BY call_count DESC
        """
        
        changed_files = [item['file'] for item in changed_items]
        result = session.run(query, changed_files=changed_files)
        
        return [dict(record) for record in result]
    
    def _analyze_dependency_chain(self, session, changed_items: List[Dict]) -> List[Dict]:
        """Analyze the dependency chain of changes"""
        query = """
        MATCH path = (start:File)-[:DEPENDS_ON*1..3]->(end:File)
        WHERE start.name IN $changed_files
        RETURN DISTINCT 
               [node IN nodes(path) | node.name] as dependency_path,
               length(path) as depth
        ORDER BY depth DESC
        LIMIT 10
        """
        
        changed_files = [item['file'] for item in changed_items]
        result = session.run(query, changed_files=changed_files)
        
        return [dict(record) for record in result]
    
    def _assess_risk(self, affected_repos: List[Dict], affected_classes: List[Dict], 
                    affected_functions: List[Dict]) -> str:
        """Assess the risk level of changes"""
        repo_count = len(affected_repos)
        class_count = len(affected_classes)
        function_count = len(affected_functions)
        
        if repo_count > 5 or class_count > 20 or function_count > 50:
            return "high"
        elif repo_count > 2 or class_count > 10 or function_count > 20:
            return "medium"
        else:
            return "low"
    
    def _mock_impact_analysis(self, changed_items: List[Dict]) -> Dict:
        """Mock impact analysis when Neo4j is not available"""
        debug_logger.info("Using mock impact analysis (Neo4j not available)")
        
        # Simulate impact analysis based on file patterns
        affected_repos = []
        affected_classes = []
        affected_functions = []
        
        for item in changed_items:
            file_path = item['file']
            
            # Simulate repository detection
            if 'src/' in file_path:
                repo_name = file_path.split('/')[0] if '/' in file_path else 'current_repo'
                affected_repos.append({
                    'repository': repo_name,
                    'url': f'https://github.com/org/{repo_name}',
                    'affected_files': 1
                })
            
            # Simulate class detection
            if file_path.endswith('.py'):
                class_name = file_path.split('/')[-1].replace('.py', '').title()
                affected_classes.append({
                    'class_name': class_name,
                    'class_type': 'Python Class',
                    'file_name': file_path
                })
            
            # Simulate function detection
            if 'test' in file_path.lower():
                affected_functions.append({
                    'function_name': 'test_function',
                    'signature': 'def test_function()',
                    'file_name': file_path,
                    'call_count': 5
                })
        
        return {
            'affected_repositories': affected_repos[:3],  # Limit for demo
            'affected_classes': affected_classes[:5],
            'affected_functions': affected_functions[:5],
            'dependency_chain': [
                {'dependency_path': ['file1.py', 'file2.py'], 'depth': 2},
                {'dependency_path': ['file2.py', 'file3.py'], 'depth': 1}
            ],
            'risk_assessment': 'medium' if len(affected_repos) > 1 else 'low'
        }
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            debug_logger.info("Neo4j connection closed")
