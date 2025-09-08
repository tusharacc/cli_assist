"""
Test GitHub query parsing to ensure correct org/repo extraction
This file is useful for regression testing of GitHub natural language parsing.
"""

import pytest
from src.lumos_cli.utils.github_query_parser import GitHubQueryParser

class TestGitHubParsing:
    """Test cases for GitHub query parsing"""
    
    def test_exact_org_repo_format(self):
        """Test exact org/repo format parsing"""
        parser = GitHubQueryParser()
        
        test_cases = [
            "tusharacc/cli_assist",
            "scimarketplace/externaldata",
            "microsoft/vscode",
            "facebook/react"
        ]
        
        for query in test_cases:
            result = parser.parse_query(query)
            assert result is not None
            assert result['org_repo'] == query
            assert result['confidence'] > 0.8
    
    def test_natural_language_parsing(self):
        """Test natural language parsing"""
        parser = GitHubQueryParser()
        
        test_cases = [
            ("get me the latest pull request for repository externaldata in organization scimarketplace", 
             "scimarketplace/externaldata"),
            ("show PRs from microsoft vscode", 
             "microsoft/vscode"),
            ("check commits in facebook react repo", 
             "facebook/react"),
            ("clone the tusharacc cli_assist repository", 
             "tusharacc/cli_assist")
        ]
        
        for query, expected_org_repo in test_cases:
            result = parser.parse_query(query)
            assert result is not None
            assert result['org_repo'] == expected_org_repo
            assert result['confidence'] > 0.5
    
    def test_branch_extraction(self):
        """Test branch name extraction"""
        parser = GitHubQueryParser()
        
        test_cases = [
            ("get PRs from scimarketplace/externaldata branch RC1", "RC1"),
            ("show commits in microsoft/vscode main branch", "main"),
            ("check latest changes in facebook/react develop", "develop")
        ]
        
        for query, expected_branch in test_cases:
            result = parser.parse_query(query)
            assert result is not None
            assert result.get('branch') == expected_branch
    
    def test_commit_sha_extraction(self):
        """Test commit SHA extraction"""
        parser = GitHubQueryParser()
        
        test_cases = [
            ("get commit abc123def from scimarketplace/externaldata", "abc123def"),
            ("show details for commit 456789abc in microsoft/vscode", "456789abc"),
            ("analyze commit fedcba987 from facebook/react", "fedcba987")
        ]
        
        for query, expected_sha in test_cases:
            result = parser.parse_query(query)
            assert result is not None
            assert result.get('commit_sha') == expected_sha
    
    def test_confidence_scoring(self):
        """Test confidence scoring"""
        parser = GitHubQueryParser()
        
        # High confidence cases
        high_confidence_cases = [
            "get PRs from scimarketplace/externaldata",
            "show commits in microsoft/vscode",
            "clone facebook/react"
        ]
        
        for query in high_confidence_cases:
            result = parser.parse_query(query)
            assert result is not None
            assert result['confidence'] > 0.7
        
        # Low confidence cases
        low_confidence_cases = [
            "hello world",
            "what is the weather",
            "unrelated query"
        ]
        
        for query in low_confidence_cases:
            result = parser.parse_query(query)
            if result:
                assert result['confidence'] < 0.5
    
    def test_agreement_detection(self):
        """Test agreement between text and LLM parsing"""
        parser = GitHubQueryParser()
        
        # Test cases where both methods should agree
        agreement_cases = [
            "get PRs from scimarketplace/externaldata",
            "show commits in microsoft/vscode",
            "clone facebook/react"
        ]
        
        for query in agreement_cases:
            result = parser.parse_query(query)
            assert result is not None
            # Agreement should be True when both methods return the same result
            if result.get('agreement'):
                assert result['confidence'] > 0.8
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        parser = GitHubQueryParser()
        
        # Test empty query
        result = parser.parse_query("")
        assert result is None or result['confidence'] == 0
        
        # Test None input
        result = parser.parse_query(None)
        assert result is None or result['confidence'] == 0
        
        # Test invalid format
        result = parser.parse_query("invalid/format/with/slashes")
        assert result is None or result['confidence'] < 0.5
    
    def test_edge_cases(self):
        """Test edge cases"""
        parser = GitHubQueryParser()
        
        edge_cases = [
            ("org/repo with spaces", "org/repo"),
            ("UPPERCASE/REPO", "UPPERCASE/REPO"),
            ("repo-with-dashes", None),  # No org
            ("org/repo-with-dashes", "org/repo-with-dashes"),
            ("org123/repo456", "org123/repo456")
        ]
        
        for query, expected in edge_cases:
            result = parser.parse_query(query)
            if expected:
                assert result is not None
                assert result['org_repo'] == expected
            else:
                assert result is None or result['confidence'] < 0.5
