#!/usr/bin/env python3
"""
Test Neo4j list repositories functionality
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lumos_cli.interactive.handlers.neo4j_handler import interactive_neo4j
from lumos_cli.clients.neo4j_client import Neo4jClient

class TestNeo4jListRepositories(unittest.TestCase):
    """Test Neo4j list repositories functionality"""
    
    @patch('lumos_cli.interactive.handlers.neo4j_handler.Neo4jConfigManager')
    @patch('lumos_cli.interactive.handlers.neo4j_handler.UnifiedKeywordDetector')
    def test_list_repositories_command(self, mock_keyword_detector_class, mock_config_manager_class):
        """Test that list repositories command works correctly"""
        # Mock the keyword detector
        mock_detector = MagicMock()
        mock_detector.detect_keywords.return_value = MagicMock(
            action='list_repositories',
            confidence=0.9,
            extracted_values={}
        )
        mock_keyword_detector_class.return_value = mock_detector
        
        # Mock the config manager
        mock_config_manager = MagicMock()
        mock_config_manager.is_configured.return_value = True
        mock_config_manager.load_config.return_value = MagicMock(
            uri='bolt://localhost:7687',
            username='neo4j',
            password='password'
        )
        mock_config_manager_class.return_value = mock_config_manager
        
        # Mock the Neo4j client
        with patch('lumos_cli.interactive.handlers.neo4j_handler.Neo4jClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.connect.return_value = True
            mock_client.list_all_repositories.return_value = [
                {
                    'organization': 'testorg',
                    'name': 'testrepo',
                    'url': 'https://github.com/testorg/testrepo',
                    'created_at': '2024-01-15T10:30:00Z',
                    'updated_at': '2024-01-16T11:30:00Z'
                },
                {
                    'organization': 'testorg2',
                    'name': 'testrepo2',
                    'url': 'https://github.com/testorg2/testrepo2',
                    'created_at': '2024-01-10T09:00:00Z',
                    'updated_at': '2024-01-12T14:00:00Z'
                }
            ]
            mock_client_class.return_value = mock_client
            
            # Test the command
            interactive_neo4j("list all repositories")
            
            # Verify the client was called correctly
            mock_client.connect.assert_called_once()
            mock_client.list_all_repositories.assert_called_once()
            mock_client.close.assert_called_once()
    
    @patch('lumos_cli.interactive.handlers.neo4j_handler.Neo4jConfigManager')
    @patch('lumos_cli.interactive.handlers.neo4j_handler.UnifiedKeywordDetector')
    def test_stats_command(self, mock_keyword_detector_class, mock_config_manager_class):
        """Test that stats command works correctly"""
        # Mock the keyword detector
        mock_detector = MagicMock()
        mock_detector.detect_keywords.return_value = MagicMock(
            action='stats',
            confidence=0.9,
            extracted_values={}
        )
        mock_keyword_detector_class.return_value = mock_detector
        
        # Mock the config manager
        mock_config_manager = MagicMock()
        mock_config_manager.is_configured.return_value = True
        mock_config_manager.load_config.return_value = MagicMock(
            uri='bolt://localhost:7687',
            username='neo4j',
            password='password'
        )
        mock_config_manager_class.return_value = mock_config_manager
        
        # Mock the Neo4j client
        with patch('lumos_cli.interactive.handlers.neo4j_handler.Neo4jClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client.connect.return_value = True
            mock_client.get_repository_stats.return_value = {
                'repo_count': 5,
                'class_count': 150,
                'method_count': 500,
                'file_count': 200,
                'relationship_count': 1000
            }
            mock_client_class.return_value = mock_client
            
            # Test the command
            interactive_neo4j("show repository statistics")
            
            # Verify the client was called correctly
            mock_client.connect.assert_called_once()
            mock_client.get_repository_stats.assert_called_once()
            mock_client.close.assert_called_once()
    
    @patch('lumos_cli.interactive.handlers.neo4j_handler.Neo4jConfigManager')
    def test_neo4j_not_configured(self, mock_config_manager_class):
        """Test behavior when Neo4j is not configured"""
        # Mock the config manager to return not configured
        mock_config_manager = MagicMock()
        mock_config_manager.is_configured.return_value = False
        mock_config_manager_class.return_value = mock_config_manager
        
        # Test the command
        interactive_neo4j("list all repositories")
        
        # Verify config check was called
        mock_config_manager.is_configured.assert_called_once()
    
    def test_neo4j_client_methods_exist(self):
        """Test that Neo4j client has the required methods"""
        client = Neo4jClient()
        
        # Check that required methods exist
        self.assertTrue(hasattr(client, 'list_all_repositories'))
        self.assertTrue(hasattr(client, 'get_repository_stats'))
        self.assertTrue(hasattr(client, 'execute_query'))
        
        # Check that methods are callable
        self.assertTrue(callable(getattr(client, 'list_all_repositories')))
        self.assertTrue(callable(getattr(client, 'get_repository_stats')))
        self.assertTrue(callable(getattr(client, 'execute_query')))

if __name__ == '__main__':
    unittest.main()
