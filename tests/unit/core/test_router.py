"""
Unit tests for LLM Router
"""

import pytest
from unittest.mock import Mock, patch
from src.lumos_cli.core.router import LLMRouter, TaskType

class TestLLMRouter:
    """Test cases for LLMRouter"""
    
    def test_router_initialization(self):
        """Test router initialization"""
        router = LLMRouter()
        assert router is not None
    
    def test_task_type_enum(self):
        """Test TaskType enum values"""
        assert TaskType.CODE_GENERATION == "code_generation"
        assert TaskType.CODE_REVIEW == "code_review"
        assert TaskType.PLANNING == "planning"
        assert TaskType.CHAT == "chat"
        assert TaskType.DEBUGGING == "debugging"
    
    @patch('src.lumos_cli.core.router.openai')
    def test_openai_chat(self, mock_openai):
        """Test OpenAI chat functionality"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        router = LLMRouter()
        messages = [{"role": "user", "content": "Test message"}]
        
        result = router.chat(messages)
        
        assert result == "Test response"
        mock_openai.ChatCompletion.create.assert_called_once()
    
    @patch('src.lumos_cli.core.router.requests')
    def test_ollama_chat(self, mock_requests):
        """Test Ollama chat functionality"""
        # Mock Ollama response
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Test response"}
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response
        
        router = LLMRouter()
        messages = [{"role": "user", "content": "Test message"}]
        
        result = router.chat(messages)
        
        assert result == "Test response"
        mock_requests.post.assert_called_once()
    
    def test_detect_task_type(self):
        """Test task type detection"""
        router = LLMRouter()
        
        # Test code generation
        assert router.detect_task_type("create a function") == TaskType.CODE_GENERATION
        
        # Test code review
        assert router.detect_task_type("review this code") == TaskType.CODE_REVIEW
        
        # Test planning
        assert router.detect_task_type("plan a feature") == TaskType.PLANNING
        
        # Test debugging
        assert router.detect_task_type("debug this error") == TaskType.DEBUGGING
        
        # Test chat (default)
        assert router.detect_task_type("hello world") == TaskType.CHAT
