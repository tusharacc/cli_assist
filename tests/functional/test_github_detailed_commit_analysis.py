#!/usr/bin/env python3
"""
Test GitHub detailed commit analysis functionality
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lumos_cli.clients.github_client import GitHubClient

class TestGitHubDetailedCommitAnalysis(unittest.TestCase):
    """Test detailed commit analysis functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = GitHubClient(token="test_token")
    
    def test_format_detailed_commit_analysis_exists(self):
        """Test that format_detailed_commit_analysis method exists"""
        self.assertTrue(hasattr(self.client, 'format_detailed_commit_analysis'))
        self.assertTrue(callable(getattr(self.client, 'format_detailed_commit_analysis')))
    
    def test_format_detailed_commit_analysis_basic_info(self):
        """Test that detailed analysis includes basic commit information"""
        mock_commit = {
            'sha': 'abc123def456',
            'commit': {
                'author': {'name': 'Test Author'},
                'date': '2024-01-15T10:30:00Z',
                'message': 'Test commit message'
            },
            'html_url': 'https://github.com/test/repo/commit/abc123',
            'stats': {
                'additions': 10,
                'deletions': 5,
                'total': 2
            },
            'files': []
        }
        
        result = self.client.format_detailed_commit_analysis(mock_commit)
        
        # Check that basic information is included
        self.assertIn('abc123', result)  # SHA
        self.assertIn('Test Author', result)  # Author
        self.assertIn('2024-01-15', result)  # Date
        self.assertIn('Test commit message', result)  # Message
        self.assertIn('+10', result)  # Additions
        self.assertIn('-5', result)  # Deletions
        self.assertIn('2', result)  # Files changed
    
    def test_format_detailed_commit_analysis_with_files(self):
        """Test detailed analysis with file changes"""
        mock_commit = {
            'sha': 'abc123def456',
            'commit': {
                'author': {'name': 'Test Author'},
                'date': '2024-01-15T10:30:00Z',
                'message': 'Add new feature'
            },
            'html_url': 'https://github.com/test/repo/commit/abc123',
            'stats': {
                'additions': 25,
                'deletions': 10,
                'total': 3
            },
            'files': [
                {
                    'filename': 'src/main.py',
                    'status': 'added',
                    'additions': 20,
                    'deletions': 0,
                    'patch': '@@ -0,0 +1,20 @@\n+def new_function():\n+    pass'
                },
                {
                    'filename': 'tests/test_main.py',
                    'status': 'added',
                    'additions': 5,
                    'deletions': 0,
                    'patch': '@@ -0,0 +1,5 @@\n+def test_new_function():\n+    pass'
                }
            ]
        }
        
        result = self.client.format_detailed_commit_analysis(mock_commit)
        
        # Check that file information is included
        self.assertIn('Files Changed', result)
        self.assertIn('src/main.py', result)
        self.assertIn('tests/test_main.py', result)
        self.assertIn('Code Analysis', result)
    
    def test_analyze_file_changes_method_exists(self):
        """Test that _analyze_file_changes method exists"""
        self.assertTrue(hasattr(self.client, '_analyze_file_changes'))
        self.assertTrue(callable(getattr(self.client, '_analyze_file_changes')))
    
    def test_analyze_file_changes_with_empty_files(self):
        """Test file analysis with empty files list"""
        result = self.client._analyze_file_changes([])
        
        self.assertIn('file_summary', result)
        self.assertIn('code_analysis', result)
        self.assertIn('impact_summary', result)
        self.assertIn('method_class_changes', result)
        self.assertIn('No file changes detected', result['file_summary'])
    
    def test_analyze_file_changes_with_files(self):
        """Test file analysis with actual files"""
        mock_files = [
            {
                'filename': 'src/main.py',
                'status': 'modified',
                'additions': 10,
                'deletions': 5,
                'patch': '@@ -1,5 +1,10 @@\n def existing_function():\n     pass\n+\n+def new_function():\n+    pass'
            },
            {
                'filename': 'tests/test_main.py',
                'status': 'added',
                'additions': 15,
                'deletions': 0,
                'patch': '@@ -0,0 +1,15 @@\n+def test_new_function():\n+    pass'
            }
        ]
        
        result = self.client._analyze_file_changes(mock_files)
        
        # Check that all required keys are present
        required_keys = ['file_summary', 'code_analysis', 'impact_summary', 'method_class_changes']
        for key in required_keys:
            self.assertIn(key, result)
            self.assertIsInstance(result[key], str)
        
        # Check that file information is included
        self.assertIn('src/main.py', result['file_summary'])
        self.assertIn('tests/test_main.py', result['file_summary'])
    
    def test_commit_analysis_includes_all_sections(self):
        """Test that commit analysis includes all expected sections"""
        mock_commit = {
            'sha': 'abc123def456',
            'commit': {
                'author': {'name': 'Test Author'},
                'date': '2024-01-15T10:30:00Z',
                'message': 'Test commit with multiple changes'
            },
            'html_url': 'https://github.com/test/repo/commit/abc123',
            'stats': {
                'additions': 50,
                'deletions': 20,
                'total': 5
            },
            'files': [
                {
                    'filename': 'src/feature.py',
                    'status': 'added',
                    'additions': 30,
                    'deletions': 0
                },
                {
                    'filename': 'src/utils.py',
                    'status': 'modified',
                    'additions': 20,
                    'deletions': 20
                }
            ]
        }
        
        result = self.client.format_detailed_commit_analysis(mock_commit)
        
        # Check for all expected sections
        expected_sections = [
            'Commit Details',
            'Author',
            'Date',
            'Message',
            'Statistics',
            'Files Changed',
            'Code Analysis',
            'Method & Class Changes',
            'Impact Summary'
        ]
        
        for section in expected_sections:
            self.assertIn(section, result, f"Missing section: {section}")

if __name__ == '__main__':
    unittest.main()
