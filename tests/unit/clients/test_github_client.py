"""
Unit tests for GitHub Client
"""

import pytest
from unittest.mock import Mock, patch
from src.lumos_cli.clients.github_client import GitHubClient

class TestGitHubClient:
    """Test cases for GitHubClient"""
    
    def test_github_client_initialization(self):
        """Test GitHubClient initialization"""
        client = GitHubClient()
        assert client is not None
    
    @patch('src.lumos_cli.clients.github_client.requests.get')
    def test_test_connection_success(self, mock_get):
        """Test successful connection test"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "testuser"}
        mock_get.return_value = mock_response
        
        client = GitHubClient()
        result = client.test_connection()
        
        assert result is True
        mock_get.assert_called_once()
    
    @patch('src.lumos_cli.clients.github_client.requests.get')
    def test_test_connection_failure(self, mock_get):
        """Test failed connection test"""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        client = GitHubClient()
        result = client.test_connection()
        
        assert result is False
    
    @patch('src.lumos_cli.clients.github_client.requests.get')
    def test_get_repository_info(self, mock_get, mock_github_response):
        """Test getting repository information"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_github_response
        mock_get.return_value = mock_response
        
        client = GitHubClient()
        result = client.get_repository_info("test-org", "test-repo")
        
        assert result is not None
        assert result['name'] == 'test-repo'
        assert result['full_name'] == 'test-org/test-repo'
        mock_get.assert_called_once()
    
    @patch('src.lumos_cli.clients.github_client.requests.get')
    def test_get_pull_requests(self, mock_get):
        """Test getting pull requests"""
        # Mock successful response
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
        result = client.get_pull_requests("test-org", "test-repo")
        
        assert len(result) == 1
        assert result[0]['number'] == 1
        assert result[0]['title'] == 'Test PR'
        mock_get.assert_called_once()
    
    @patch('src.lumos_cli.clients.github_client.requests.get')
    def test_get_commits(self, mock_get):
        """Test getting commits"""
        # Mock successful response
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
        result = client.get_commits("test-org", "test-repo", count=1)
        
        assert len(result) == 1
        assert result[0]['sha'] == 'abc123'
        assert result[0]['commit']['message'] == 'Test commit'
        mock_get.assert_called_once()
    
    @patch('src.lumos_cli.clients.github_client.subprocess.run')
    def test_clone_repository(self, mock_run):
        """Test cloning repository"""
        # Mock successful git clone
        mock_run.return_value = Mock(returncode=0)
        
        client = GitHubClient()
        success, repo_path = client.clone_repository("test-org", "test-repo")
        
        assert success is True
        assert repo_path is not None
        mock_run.assert_called_once()
    
    @patch('src.lumos_cli.clients.github_client.subprocess.run')
    def test_clone_repository_failure(self, mock_run):
        """Test cloning repository failure"""
        # Mock failed git clone
        mock_run.return_value = Mock(returncode=1)
        
        client = GitHubClient()
        success, repo_path = client.clone_repository("test-org", "test-repo")
        
        assert success is False
        assert repo_path is None
