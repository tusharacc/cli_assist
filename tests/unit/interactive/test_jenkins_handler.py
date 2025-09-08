"""
Unit tests for Jenkins handler LLM-based folder extraction
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

class TestJenkinsHandler:
    """Test cases for Jenkins handler LLM functionality"""
    
    @patch('lumos_cli.interactive.handlers.jenkins_handler.LLMRouter')
    def test_extract_folder_path_with_llm_success(self, mock_router_class):
        """Test successful folder path extraction with LLM"""
        # Mock the router instance
        mock_router = Mock()
        mock_router.chat.return_value = "scimarketplace/quote_multi/RC1"
        mock_router_class.return_value = mock_router
        
        from lumos_cli.interactive.handlers.jenkins_handler import _extract_folder_path_with_llm
        
        query = "get me the last 5 builds for scimarketplace and folder quote and sub folder RC1"
        result = _extract_folder_path_with_llm(query)
        
        assert result == "scimarketplace/quote_multi/RC1"
        mock_router.chat.assert_called_once()
        
        # Verify the prompt contains the query
        call_args = mock_router.chat.call_args[0][0]
        assert query in call_args[0]["content"]
    
    @patch('lumos_cli.interactive.handlers.jenkins_handler.LLMRouter')
    def test_extract_folder_path_with_llm_deploy_all(self, mock_router_class):
        """Test folder path extraction for deploy-all"""
        mock_router = Mock()
        mock_router.chat.return_value = "scimarketplace/deploy-all"
        mock_router_class.return_value = mock_router
        
        from lumos_cli.interactive.handlers.jenkins_handler import _extract_folder_path_with_llm
        
        query = "folder deploy-all"
        result = _extract_folder_path_with_llm(query)
        
        assert result == "scimarketplace/deploy-all"
    
    @patch('lumos_cli.interactive.handlers.jenkins_handler.LLMRouter')
    def test_extract_folder_path_with_llm_invalid_response(self, mock_router_class):
        """Test handling of invalid LLM response"""
        mock_router = Mock()
        mock_router.chat.return_value = "invalid response without scimarketplace prefix"
        mock_router_class.return_value = mock_router
        
        from lumos_cli.interactive.handlers.jenkins_handler import _extract_folder_path_with_llm
        
        query = "folder quote and sub folder RC1"
        result = _extract_folder_path_with_llm(query)
        
        # Should fallback to regex extraction (which works for this query)
        assert result == "scimarketplace/quote_multi/RC1"
    
    @patch('lumos_cli.interactive.handlers.jenkins_handler.LLMRouter')
    def test_extract_folder_path_with_llm_exception(self, mock_router_class):
        """Test handling of LLM exceptions"""
        mock_router = Mock()
        mock_router.chat.side_effect = Exception("LLM connection failed")
        mock_router_class.return_value = mock_router
        
        from lumos_cli.interactive.handlers.jenkins_handler import _extract_folder_path_with_llm
        
        query = "folder quote and sub folder RC1"
        result = _extract_folder_path_with_llm(query)
        
        # Should fallback to regex extraction (which works for this query)
        assert result == "scimarketplace/quote_multi/RC1"
    
    @patch('lumos_cli.interactive.handlers.jenkins_handler.LLMRouter')
    def test_extract_folder_path_with_llm_quotes_removal(self, mock_router_class):
        """Test removal of quotes from LLM response"""
        mock_router = Mock()
        mock_router.chat.return_value = '"scimarketplace/externaldata_multi/RC2"'
        mock_router_class.return_value = mock_router
        
        from lumos_cli.interactive.handlers.jenkins_handler import _extract_folder_path_with_llm
        
        query = "folder externaldata and sub folder RC2"
        result = _extract_folder_path_with_llm(query)
        
        assert result == "scimarketplace/externaldata_multi/RC2"
        assert '"' not in result
    
    @patch('lumos_cli.interactive.handlers.jenkins_handler.LLMRouter')
    def test_extract_folder_path_with_llm_different_repositories(self, mock_router_class):
        """Test extraction for different repository names"""
        test_cases = [
            ("folder addresssearch and sub folder RC3", "scimarketplace/addresssearch_multi/RC3"),
            ("folder payment and sub folder RC4", "scimarketplace/payment_multi/RC4"),
            ("folder user and sub folder RC1", "scimarketplace/user_multi/RC1")
        ]
        
        from lumos_cli.interactive.handlers.jenkins_handler import _extract_folder_path_with_llm
        
        for query, expected in test_cases:
            mock_router = Mock()
            mock_router.chat.return_value = expected
            mock_router_class.return_value = mock_router
            
            result = _extract_folder_path_with_llm(query)
            assert result == expected
    
    def test_extract_folder_path_with_llm_prompt_structure(self):
        """Test that the LLM prompt is properly structured"""
        with patch('lumos_cli.interactive.handlers.jenkins_handler.LLMRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.chat.return_value = "scimarketplace/quote_multi/RC1"
            mock_router_class.return_value = mock_router
            
            from lumos_cli.interactive.handlers.jenkins_handler import _extract_folder_path_with_llm
            
            query = "test query"
            _extract_folder_path_with_llm(query)
            
            # Verify the prompt structure
            call_args = mock_router.chat.call_args[0][0]
            prompt = call_args[0]["content"]
            
            assert "Jenkins folder path extractor" in prompt
            assert f'User Query: "{query}"' in prompt
            assert "scimarketplace/deploy-all" in prompt
            assert "scimarketplace/quote_multi/RC1" in prompt
            assert "Return ONLY the folder path" in prompt
    
    def test_extract_folder_path_with_regex_fallback_to_default(self):
        """Test regex fallback returns default when query can't be parsed"""
        from lumos_cli.interactive.handlers.jenkins_handler import _extract_folder_path_with_regex
        
        # Test query that doesn't match the regex pattern (no "folder" keyword)
        query = "random text with no matching keywords"
        result = _extract_folder_path_with_regex(query)
        
        # Should fallback to default
        assert result == "scimarketplace/deploy-all"

if __name__ == "__main__":
    pytest.main([__file__])
