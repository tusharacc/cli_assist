"""
Integration tests for GitHub functionality
"""

import pytest
from unittest.mock import Mock, patch
from src.lumos_cli.clients.github_client import GitHubClient
from src.lumos_cli.interactive.handlers.github_handler import interactive_github

class TestGitHubIntegration:
    """Integration tests for GitHub functionality"""
    
    @patch('src.lumos_cli.clients.github_client.requests.get')
    def test_github_client_integration(self, mock_get):
        """Test GitHub client integration"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'test-repo',
            'full_name': 'test-org/test-repo',
            'description': 'A test repository',
            'html_url': 'https://github.com/test-org/test-repo',
            'stargazers_count': 100,
            'forks_count': 25
        }
        mock_get.return_value = mock_response
        
        client = GitHubClient()
        
        # Test connection
        assert client.test_connection() is True
        
        # Test repository info
        repo_info = client.get_repository_info("test-org", "test-repo")
        assert repo_info is not None
        assert repo_info['name'] == 'test-repo'
    
    @patch('src.lumos_cli.clients.github_client.requests.get')
    def test_github_pr_integration(self, mock_get):
        """Test GitHub PR integration"""
        # Mock PR response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'number': 1,
                'title': 'Test PR',
                'state': 'open',
                'user': {'login': 'testuser'},
                'created_at': '2024-01-01T00:00:00Z',
                'html_url': 'https://github.com/test-org/test-repo/pull/1'
            }
        ]
        mock_get.return_value = mock_response
        
        client = GitHubClient()
        prs = client.get_pull_requests("test-org", "test-repo")
        
        assert len(prs) == 1
        assert prs[0]['number'] == 1
        assert prs[0]['title'] == 'Test PR'
    
    @patch('src.lumos_cli.clients.github_client.requests.get')
    def test_github_commits_integration(self, mock_get):
        """Test GitHub commits integration"""
        # Mock commits response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'sha': 'abc123',
                'commit': {
                    'message': 'Test commit',
                    'author': {'name': 'Test Author', 'date': '2024-01-01T00:00:00Z'}
                },
                'html_url': 'https://github.com/test-org/test-repo/commit/abc123'
            }
        ]
        mock_get.return_value = mock_response
        
        client = GitHubClient()
        commits = client.get_commits("test-org", "test-repo", count=1)
        
        assert len(commits) == 1
        assert commits[0]['sha'] == 'abc123'
        assert commits[0]['commit']['message'] == 'Test commit'
    
    @patch('src.lumos_cli.interactive.handlers.github_handler.GitHubClient')
    def test_interactive_github_handler(self, mock_client_class):
        """Test interactive GitHub handler"""
        # Mock GitHub client
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.get_pull_requests.return_value = [
            {
                'number': 1,
                'title': 'Test PR',
                'state': 'open',
                'user': {'login': 'testuser'},
                'created_at': '2024-01-01T00:00:00Z',
                'html_url': 'https://github.com/test-org/test-repo/pull/1'
            }
        ]
        mock_client_class.return_value = mock_client
        
        # Test interactive handler
        with patch('src.lumos_cli.interactive.handlers.github_handler.console') as mock_console:
            interactive_github("get PRs from test-org/test-repo")
            
            # Verify client methods were called
            mock_client.test_connection.assert_called_once()
            mock_client.get_pull_requests.assert_called_once()
            
            # Verify console output
            assert mock_console.print.called
    
    @patch('src.lumos_cli.interactive.handlers.github_handler.GitHubClient')
    def test_interactive_github_clone(self, mock_client_class):
        """Test interactive GitHub clone functionality"""
        # Mock GitHub client
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.clone_repository.return_value = (True, "/path/to/repo")
        mock_client.get_repository_info.return_value = {
            'description': 'Test repo',
            'stargazers_count': 100,
            'forks_count': 25,
            'updated_at': '2024-01-01T00:00:00Z'
        }
        mock_client_class.return_value = mock_client
        
        # Test interactive handler
        with patch('src.lumos_cli.interactive.handlers.github_handler.console') as mock_console:
            interactive_github("clone test-org/test-repo")
            
            # Verify client methods were called
            mock_client.test_connection.assert_called_once()
            mock_client.clone_repository.assert_called_once()
            mock_client.get_repository_info.assert_called_once()
            
            # Verify console output
            assert mock_console.print.called
    
    @patch('src.lumos_cli.interactive.handlers.github_handler.GitHubClient')
    def test_interactive_github_commits(self, mock_client_class):
        """Test interactive GitHub commits functionality"""
        # Mock GitHub client
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.get_commits.return_value = [
            {
                'sha': 'abc123',
                'commit': {
                    'message': 'Test commit',
                    'author': {'name': 'Test Author', 'date': '2024-01-01T00:00:00Z'}
                },
                'html_url': 'https://github.com/test-org/test-repo/commit/abc123'
            }
        ]
        mock_client_class.return_value = mock_client
        
        # Test interactive handler
        with patch('src.lumos_cli.interactive.handlers.github_handler.console') as mock_console:
            interactive_github("get commits from test-org/test-repo")
            
            # Verify client methods were called
            mock_client.test_connection.assert_called_once()
            mock_client.get_commits.assert_called_once()
            
            # Verify console output
            assert mock_console.print.called
