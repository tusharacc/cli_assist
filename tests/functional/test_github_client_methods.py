#!/usr/bin/env python3
"""
Test GitHub client methods to ensure all required methods exist
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lumos_cli.clients.github_client import GitHubClient

class TestGitHubClientMethods(unittest.TestCase):
    """Test that GitHub client has all required methods"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = GitHubClient(token="test_token")
    
    def test_github_client_has_required_methods(self):
        """Test that GitHub client has all methods called by handlers"""
        required_methods = [
            'get_commits',
            'get_commit_details', 
            'get_pull_requests',
            'get_pull_request',
            'get_repository_info',
            'list_commits',
            'get_commit',
            'get_latest_commit'
        ]
        
        for method_name in required_methods:
            with self.subTest(method=method_name):
                self.assertTrue(
                    hasattr(self.client, method_name),
                    f"GitHubClient missing method: {method_name}"
                )
                self.assertTrue(
                    callable(getattr(self.client, method_name)),
                    f"GitHubClient.{method_name} is not callable"
                )
    
    @patch('lumos_cli.clients.github_client.GitHubClient.list_commits')
    def test_get_commits_calls_list_commits(self, mock_list_commits):
        """Test that get_commits calls list_commits with correct parameters"""
        mock_list_commits.return_value = [{'sha': 'abc123', 'message': 'test commit'}]
        
        result = self.client.get_commits('testorg', 'testrepo', count=5, branch='main')
        
        mock_list_commits.assert_called_once_with('testorg', 'testrepo', 'main', per_page=5)
        self.assertEqual(result, [{'sha': 'abc123', 'message': 'test commit'}])
    
    @patch('lumos_cli.clients.github_client.GitHubClient.get_commit')
    def test_get_commit_details_calls_get_commit(self, mock_get_commit):
        """Test that get_commit_details calls get_commit with correct parameters"""
        mock_get_commit.return_value = {'sha': 'abc123', 'message': 'test commit'}
        
        result = self.client.get_commit_details('testorg', 'testrepo', 'abc123')
        
        mock_get_commit.assert_called_once_with('testorg', 'testrepo', 'abc123')
        self.assertEqual(result, {'sha': 'abc123', 'message': 'test commit'})
    
    @patch('lumos_cli.clients.github_client.GitHubClient._make_request')
    def test_get_pull_requests_makes_correct_request(self, mock_make_request):
        """Test that get_pull_requests makes correct API request"""
        mock_make_request.return_value = [{'number': 1, 'title': 'Test PR'}]
        
        result = self.client.get_pull_requests('testorg', 'testrepo', branch='main', state='open')
        
        # Verify the request was made
        self.assertEqual(mock_make_request.call_count, 1)
        call_args = mock_make_request.call_args
        self.assertEqual(call_args[0][0], '/repos/testorg/testrepo/pulls')
        self.assertEqual(call_args[0][1], {'state': 'open', 'per_page': 100, 'head': 'testorg:main'})
        self.assertEqual(result, [{'number': 1, 'title': 'Test PR'}])
    
    @patch('lumos_cli.clients.github_client.GitHubClient._make_request')
    def test_get_pull_requests_without_branch(self, mock_make_request):
        """Test that get_pull_requests works without branch parameter"""
        mock_make_request.return_value = [{'number': 1, 'title': 'Test PR'}]
        
        result = self.client.get_pull_requests('testorg', 'testrepo')
        
        call_args = mock_make_request.call_args
        self.assertEqual(call_args[0][1], {'state': 'open', 'per_page': 100})
        self.assertEqual(result, [{'number': 1, 'title': 'Test PR'}])
    
    def test_method_signatures(self):
        """Test that methods have correct signatures"""
        # Test get_commits signature
        import inspect
        sig = inspect.signature(self.client.get_commits)
        params = list(sig.parameters.keys())
        self.assertIn('org', params)
        self.assertIn('repo', params)
        self.assertIn('count', params)
        self.assertIn('branch', params)
        
        # Test get_commit_details signature
        sig = inspect.signature(self.client.get_commit_details)
        params = list(sig.parameters.keys())
        self.assertIn('org', params)
        self.assertIn('repo', params)
        self.assertIn('commit_sha', params)
        
        # Test get_pull_requests signature
        sig = inspect.signature(self.client.get_pull_requests)
        params = list(sig.parameters.keys())
        self.assertIn('org', params)
        self.assertIn('repo', params)
        self.assertIn('branch', params)
        self.assertIn('state', params)

if __name__ == '__main__':
    unittest.main()
