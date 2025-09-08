"""
Functional tests for CLI functionality
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from src.lumos_cli.cli_refactored_v2 import main
from src.lumos_cli.interactive.mode import interactive_mode

class TestCLIFunctionality:
    """Functional tests for CLI"""
    
    def test_cli_initialization(self):
        """Test CLI initialization"""
        # Test that the CLI can be imported and initialized
        from src.lumos_cli.cli_refactored_v2 import app
        assert app is not None
    
    @patch('src.lumos_cli.cli_refactored_v2.interactive_mode')
    def test_main_function_calls_interactive_mode(self, mock_interactive):
        """Test that main function calls interactive mode"""
        # Mock typer context
        mock_ctx = Mock()
        mock_ctx.invoked_subcommand = None
        
        # Call main function
        main(mock_ctx)
        
        # Verify interactive mode was called
        mock_interactive.assert_called_once()
    
    @patch('src.lumos_cli.cli_refactored_v2.plan')
    def test_plan_command(self, mock_plan):
        """Test plan command functionality"""
        from src.lumos_cli.cli_refactored_v2 import plan
        
        # Test plan command
        plan("create a new feature", "auto", "devstral")
        
        # Verify plan function was called
        mock_plan.assert_called_once_with("create a new feature", "auto", "devstral")
    
    @patch('src.lumos_cli.cli_refactored_v2.edit')
    def test_edit_command(self, mock_edit):
        """Test edit command functionality"""
        from src.lumos_cli.cli_refactored_v2 import edit
        
        # Test edit command
        edit("add error handling", "test.py")
        
        # Verify edit function was called
        mock_edit.assert_called_once_with("add error handling", "test.py")
    
    @patch('src.lumos_cli.cli_refactored_v2.review')
    def test_review_command(self, mock_review):
        """Test review command functionality"""
        from src.lumos_cli.cli_refactored_v2 import review
        
        # Test review command
        review("test.py")
        
        # Verify review function was called
        mock_review.assert_called_once_with("test.py")
    
    @patch('src.lumos_cli.cli_refactored_v2.github_clone')
    def test_github_clone_command(self, mock_github_clone):
        """Test GitHub clone command functionality"""
        from src.lumos_cli.cli_refactored_v2 import github_clone
        
        # Test GitHub clone command
        github_clone("test-org/test-repo", "main", "/tmp/test")
        
        # Verify github_clone function was called
        mock_github_clone.assert_called_once_with("test-org/test-repo", "main", "/tmp/test")
    
    @patch('src.lumos_cli.cli_refactored_v2.github_pr')
    def test_github_pr_command(self, mock_github_pr):
        """Test GitHub PR command functionality"""
        from src.lumos_cli.cli_refactored_v2 import github_pr
        
        # Test GitHub PR command
        github_pr("test-org/test-repo", "main", 1, False)
        
        # Verify github_pr function was called
        mock_github_pr.assert_called_once_with("test-org/test-repo", "main", 1, False)
    
    @patch('src.lumos_cli.cli_refactored_v2.jenkins_failed_jobs')
    def test_jenkins_failed_jobs_command(self, mock_jenkins_failed_jobs):
        """Test Jenkins failed jobs command functionality"""
        from src.lumos_cli.cli_refactored_v2 import jenkins_failed_jobs
        
        # Test Jenkins failed jobs command
        jenkins_failed_jobs(4)
        
        # Verify jenkins_failed_jobs function was called
        mock_jenkins_failed_jobs.assert_called_once_with(4)
    
    @patch('src.lumos_cli.cli_refactored_v2.jenkins_running_jobs')
    def test_jenkins_running_jobs_command(self, mock_jenkins_running_jobs):
        """Test Jenkins running jobs command functionality"""
        from src.lumos_cli.cli_refactored_v2 import jenkins_running_jobs
        
        # Test Jenkins running jobs command
        jenkins_running_jobs()
        
        # Verify jenkins_running_jobs function was called
        mock_jenkins_running_jobs.assert_called_once()
    
    def test_utility_commands(self):
        """Test utility commands"""
        from src.lumos_cli.cli_refactored_v2 import platform, logs, detect, cleanup
        
        # Test that utility commands are callable
        assert callable(platform)
        assert callable(logs)
        assert callable(detect)
        assert callable(cleanup)
    
    def test_project_commands(self):
        """Test project commands"""
        from src.lumos_cli.cli_refactored_v2 import scaffold, backups, restore
        
        # Test that project commands are callable
        assert callable(scaffold)
        assert callable(backups)
        assert callable(restore)
    
    def test_session_commands(self):
        """Test session commands"""
        from src.lumos_cli.cli_refactored_v2 import sessions, repos, context, search, history
        
        # Test that session commands are callable
        assert callable(sessions)
        assert callable(repos)
        assert callable(context)
        assert callable(search)
        assert callable(history)
