#!/usr/bin/env python3
"""
Test Neo4j LLM query generation functionality
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lumos_cli.clients.neo4j_client import Neo4jClient
from lumos_cli.interactive.handlers.neo4j_handler import handle_llm_generated_query

class TestNeo4jLLMQueryGeneration(unittest.TestCase):
    """Test Neo4j LLM query generation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = Neo4jClient()
    
    def test_neo4j_client_has_llm_methods(self):
        """Test that Neo4j client has LLM query generation methods"""
        required_methods = [
            'get_schema_info',
            'generate_cypher_query',
            'execute_llm_generated_query',
            '_format_schema_for_llm'
        ]
        
        for method_name in required_methods:
            with self.subTest(method=method_name):
                self.assertTrue(hasattr(self.client, method_name))
                self.assertTrue(callable(getattr(self.client, method_name)))
    
    @patch('lumos_cli.core.router.LLMRouter')
    def test_generate_cypher_query_with_mock_llm(self, mock_router_class):
        """Test Cypher query generation with mocked LLM"""
        # Mock the LLM router
        mock_router = MagicMock()
        mock_router._chat_enterprise_llm.return_value = "MATCH (c:Class) RETURN c.name as class_name, c.repository as repository ORDER BY c.name"
        mock_router_class.return_value = mock_router
        
        # Mock schema info
        schema_info = {
            'node_labels': ['Class', 'Method', 'Repository'],
            'relationship_types': ['DEPENDS_ON', 'CONTAINS'],
            'node_properties': {
                'Class': [{'property': 'name', 'count': 100}, {'property': 'repository', 'count': 100}]
            }
        }
        
        # Test query generation
        query = self.client.generate_cypher_query("find all classes", schema_info)
        
        # Verify the query was generated
        self.assertIsInstance(query, str)
        self.assertIn("MATCH", query)
        self.assertIn("Class", query)
        
        # Verify LLM was called
        mock_router._chat_enterprise_llm.assert_called_once()
    
    @patch('lumos_cli.core.router.LLMRouter')
    def test_generate_cypher_query_without_schema(self, mock_router_class):
        """Test Cypher query generation without provided schema"""
        # Mock the LLM router
        mock_router = MagicMock()
        mock_router._chat_enterprise_llm.return_value = "MATCH (c:Class) RETURN c.name LIMIT 10"
        mock_router_class.return_value = mock_router
        
        # Mock get_schema_info method
        with patch.object(self.client, 'get_schema_info') as mock_get_schema:
            mock_get_schema.return_value = {
                'node_labels': ['Class'],
                'relationship_types': ['DEPENDS_ON']
            }
            
            # Test query generation
            query = self.client.generate_cypher_query("find all classes")
            
            # Verify the query was generated
            self.assertIsInstance(query, str)
            self.assertIn("MATCH", query)
            
            # Verify schema was fetched
            mock_get_schema.assert_called_once()
    
    def test_format_schema_for_llm(self):
        """Test schema formatting for LLM consumption"""
        schema_info = {
            'node_labels': ['Class', 'Method', 'Repository'],
            'relationship_types': ['DEPENDS_ON', 'CONTAINS'],
            'node_properties': {
                'Class': [{'property': 'name', 'count': 100}, {'property': 'repository', 'count': 100}],
                'Method': [{'property': 'name', 'count': 500}]
            },
            'constraints': [
                {'description': 'Class name unique constraint', 'type': 'UNIQUE'}
            ]
        }
        
        formatted = self.client._format_schema_for_llm(schema_info)
        
        # Check that all sections are included
        self.assertIn("Node Labels:", formatted)
        self.assertIn("Relationship Types:", formatted)
        self.assertIn("Node Properties:", formatted)
        self.assertIn("Constraints:", formatted)
        
        # Check specific content
        self.assertIn("Class", formatted)
        self.assertIn("DEPENDS_ON", formatted)
        self.assertIn("name (count: 100)", formatted)
        self.assertIn("Class name unique constraint", formatted)
    
    @patch('lumos_cli.core.router.LLMRouter')
    def test_execute_llm_generated_query_success(self, mock_router_class):
        """Test successful execution of LLM-generated query"""
        # Mock the LLM router
        mock_router = MagicMock()
        mock_router._chat_enterprise_llm.return_value = "MATCH (c:Class) RETURN c.name as class_name LIMIT 5"
        mock_router_class.return_value = mock_router
        
        # Mock schema and query execution
        with patch.object(self.client, 'get_schema_info') as mock_get_schema, \
             patch.object(self.client, 'execute_query') as mock_execute:
            
            mock_get_schema.return_value = {'node_labels': ['Class']}
            mock_execute.return_value = [
                {'class_name': 'UserService'},
                {'class_name': 'PaymentService'}
            ]
            
            # Test execution
            result = self.client.execute_llm_generated_query("find all classes")
            
            # Verify result structure
            self.assertTrue(result['success'])
            self.assertIsNone(result['error'])
            self.assertIn('MATCH', result['query'])
            self.assertEqual(len(result['results']), 2)
            self.assertIn('node_labels', result['schema_info'])
    
    @patch('lumos_cli.core.router.LLMRouter')
    def test_execute_llm_generated_query_failure(self, mock_router_class):
        """Test failure handling in LLM query execution"""
        # Mock the LLM router to return empty response
        mock_router = MagicMock()
        mock_router._chat_enterprise_llm.return_value = ""
        mock_router_class.return_value = mock_router
        
        # Mock schema
        with patch.object(self.client, 'get_schema_info') as mock_get_schema:
            mock_get_schema.return_value = {'node_labels': ['Class']}
            
            # Test execution
            result = self.client.execute_llm_generated_query("find all classes")
            
            # Verify failure handling
            self.assertFalse(result['success'])
            self.assertIn('Failed to generate query', result['error'])
            self.assertEqual(result['query'], '')
            self.assertEqual(result['results'], [])
    
    @patch('lumos_cli.interactive.handlers.neo4j_handler.console')
    def test_handle_llm_generated_query_success(self, mock_console):
        """Test successful handling of LLM-generated query"""
        # Mock the client
        mock_client = MagicMock()
        mock_client.execute_llm_generated_query.return_value = {
            'success': True,
            'error': None,
            'query': 'MATCH (c:Class) RETURN c.name as class_name LIMIT 5',
            'results': [
                {'class_name': 'UserService', 'repository': 'test-repo'},
                {'class_name': 'PaymentService', 'repository': 'test-repo'}
            ],
            'schema_info': {
                'node_labels': ['Class', 'Method'],
                'relationship_types': ['DEPENDS_ON']
            }
        }
        
        # Test the handler
        handle_llm_generated_query(mock_client, "find all classes")
        
        # Verify client was called
        mock_client.execute_llm_generated_query.assert_called_once_with("find all classes")
        
        # Verify console output was called
        self.assertTrue(mock_console.print.called)
    
    @patch('lumos_cli.interactive.handlers.neo4j_handler.console')
    def test_handle_llm_generated_query_failure(self, mock_console):
        """Test failure handling in LLM-generated query handler"""
        # Mock the client to return failure
        mock_client = MagicMock()
        mock_client.execute_llm_generated_query.return_value = {
            'success': False,
            'error': 'LLM service unavailable',
            'query': '',
            'results': [],
            'schema_info': {}
        }
        
        # Test the handler
        handle_llm_generated_query(mock_client, "find all classes")
        
        # Verify client was called
        mock_client.execute_llm_generated_query.assert_called_once_with("find all classes")
        
        # Verify error message was printed
        error_calls = [call for call in mock_console.print.call_args_list if 'Failed to generate' in str(call)]
        self.assertTrue(len(error_calls) > 0)
    
    def test_schema_info_structure(self):
        """Test that schema info has the expected structure"""
        # This test doesn't require actual Neo4j connection
        expected_keys = ['node_labels', 'relationship_types', 'node_properties', 'relationship_properties', 'constraints', 'indexes']
        
        # Mock execute_query to return empty results
        with patch.object(self.client, 'execute_query') as mock_execute:
            mock_execute.return_value = []
            
            schema_info = self.client.get_schema_info()
            
            # Check structure
            for key in expected_keys:
                self.assertIn(key, schema_info)
                self.assertIsInstance(schema_info[key], (list, dict))

if __name__ == '__main__':
    unittest.main()
