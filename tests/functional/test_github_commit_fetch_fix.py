#!/usr/bin/env python3
"""
Test GitHub commit fetching functionality to ensure it doesn't trigger cloning
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lumos_cli.interactive.handlers.github_handler import interactive_github

class TestGitHubCommitFetchFix(unittest.TestCase):
    """Test that GitHub commit fetching works correctly and doesn't trigger cloning"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_queries = [
            "/github please fetch the last 5 commits from repo quote in org scimarketplace",
            "github fetch commits for scimarketplace/quote",
            "get latest commits from scimarketplace/quote",
            "show last 3 commits for scimarketplace/quote",
            "fetch recent commits from scimarketplace/quote"
        ]
        
        self.clone_queries = [
            "github clone scimarketplace/quote",
            "pull scimarketplace/quote",
            "download scimarketplace/quote"
        ]
    
    @patch('lumos_cli.interactive.handlers.github_handler._github_commits')
    @patch('lumos_cli.interactive.handlers.github_handler._github_clone')
    @patch('lumos_cli.interactive.handlers.github_handler.console')
    def test_commit_queries_trigger_commits_not_clone(self, mock_console, mock_clone, mock_commits):
        """Test that commit-related queries trigger commit fetching, not cloning"""
        
        for query in self.test_queries:
            with self.subTest(query=query):
                # Reset mocks
                mock_commits.reset_mock()
                mock_clone.reset_mock()
                mock_console.reset_mock()
                
                # Mock the GitHubQueryParser to return a valid org/repo
                with patch('lumos_cli.interactive.handlers.github_handler.GitHubQueryParser') as mock_parser_class:
                    mock_parser = MagicMock()
                    mock_parser_class.return_value = mock_parser
                    mock_parser.parse_query.return_value = {
                        'org_repo': 'scimarketplace/quote',
                        'method': 'text',
                        'confidence': 0.9,
                        'agreement': True
                    }
                    
                    # Call the function
                    interactive_github(query)
                    
                    # Verify that _github_commits was called, not _github_clone
                    mock_commits.assert_called_once()
                    mock_clone.assert_not_called()
                    
                    # Verify the correct message was printed (it might be "latest" or "last X commits")
                    print_calls = [call[0][0] for call in mock_console.print.call_args_list]
                    self.assertTrue(any("Getting" in call and ("commits" in call or "commit" in call) for call in print_calls))
    
    @patch('lumos_cli.interactive.handlers.github_handler._github_commits')
    @patch('lumos_cli.interactive.handlers.github_handler._github_clone')
    @patch('lumos_cli.interactive.handlers.github_handler.console')
    def test_clone_queries_trigger_clone_not_commits(self, mock_console, mock_clone, mock_commits):
        """Test that clone-related queries trigger cloning, not commit fetching"""
        
        for query in self.clone_queries:
            with self.subTest(query=query):
                # Reset mocks
                mock_commits.reset_mock()
                mock_clone.reset_mock()
                mock_console.reset_mock()
                
                # Mock the GitHubQueryParser to return a valid org/repo
                with patch('lumos_cli.interactive.handlers.github_handler.GitHubQueryParser') as mock_parser_class:
                    mock_parser = MagicMock()
                    mock_parser_class.return_value = mock_parser
                    mock_parser.parse_query.return_value = {
                        'org_repo': 'scimarketplace/quote',
                        'method': 'text',
                        'confidence': 0.9,
                        'agreement': True
                    }
                    
                    # Call the function
                    interactive_github(query)
                    
                    # Verify that _github_clone was called, not _github_commits
                    mock_clone.assert_called_once()
                    mock_commits.assert_not_called()
                    
                    # Verify the correct message was printed
                    mock_console.print.assert_any_call("[cyan]🔍 Cloning scimarketplace/quote...[/cyan]")
    
    @patch('lumos_cli.interactive.handlers.github_handler._github_commits')
    @patch('lumos_cli.interactive.handlers.github_handler._github_clone')
    @patch('lumos_cli.interactive.handlers.github_handler.console')
    def test_fetch_with_commits_prioritizes_commits(self, mock_console, mock_clone, mock_commits):
        """Test that 'fetch commits' prioritizes commit fetching over cloning"""
        
        query = "github fetch the last 5 commits from scimarketplace/quote"
        
        # Mock the GitHubQueryParser to return a valid org/repo
        with patch('lumos_cli.interactive.handlers.github_handler.GitHubQueryParser') as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser_class.return_value = mock_parser
            mock_parser.parse_query.return_value = {
                'org_repo': 'scimarketplace/quote',
                'method': 'text',
                'confidence': 0.9,
                'agreement': True
            }
            
            # Call the function
            interactive_github(query)
            
            # Verify that _github_commits was called, not _github_clone
            mock_commits.assert_called_once()
            mock_clone.assert_not_called()
            
            # Verify the correct message was printed
            mock_console.print.assert_any_call("[cyan]🔍 Getting last 5 commits from scimarketplace/quote...[/cyan]")
    
    @patch('lumos_cli.interactive.handlers.github_handler._github_commits')
    @patch('lumos_cli.interactive.handlers.github_handler._github_clone')
    @patch('lumos_cli.interactive.handlers.github_handler.console')
    def test_fetch_without_commits_triggers_clone(self, mock_console, mock_clone, mock_commits):
        """Test that 'fetch' without 'commits' triggers cloning"""
        
        query = "github fetch scimarketplace/quote"
        
        # Mock the GitHubQueryParser to return a valid org/repo
        with patch('lumos_cli.interactive.handlers.github_handler.GitHubQueryParser') as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser_class.return_value = mock_parser
            mock_parser.parse_query.return_value = {
                'org_repo': 'scimarketplace/quote',
                'method': 'text',
                'confidence': 0.9,
                'agreement': True
            }
            
            # Call the function
            interactive_github(query)
            
            # Verify that _github_clone was called, not _github_commits
            mock_clone.assert_called_once()
            mock_commits.assert_not_called()
            
            # Verify the correct message was printed
            mock_console.print.assert_any_call("[cyan]🔍 Cloning scimarketplace/quote...[/cyan]")

if __name__ == '__main__':
    unittest.main()
