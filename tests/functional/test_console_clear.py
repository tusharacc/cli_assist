#!/usr/bin/env python3
"""
Test console clearing functionality
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lumos_cli.ui.console import clear_console
from lumos_cli.interactive.mode import interactive_mode

class TestConsoleClear(unittest.TestCase):
    """Test console clearing functionality"""
    
    @patch('lumos_cli.ui.console.console.clear')
    def test_clear_console_uses_rich_clear(self, mock_clear):
        """Test that clear_console uses Rich's clear method"""
        clear_console()
        mock_clear.assert_called_once()
    
    @patch('lumos_cli.ui.console.console.clear')
    @patch('os.system')
    def test_clear_console_fallback_to_system_clear(self, mock_system, mock_clear):
        """Test that clear_console falls back to system clear when Rich fails"""
        # Make Rich clear raise an exception
        mock_clear.side_effect = Exception("Rich clear failed")
        
        clear_console()
        
        # Should call Rich clear first
        mock_clear.assert_called_once()
        # Should fall back to system clear
        mock_system.assert_called_once()
    
    @patch('lumos_cli.ui.console.console.clear')
    @patch('os.system')
    @patch('platform.system')
    def test_clear_console_windows_fallback(self, mock_platform, mock_system, mock_clear):
        """Test that clear_console uses 'cls' on Windows"""
        # Make Rich clear fail
        mock_clear.side_effect = Exception("Rich clear failed")
        # Mock Windows platform
        mock_platform.return_value = "Windows"
        
        clear_console()
        
        # Should call 'cls' on Windows
        mock_system.assert_called_once_with('cls')
    
    @patch('lumos_cli.ui.console.console.clear')
    @patch('os.system')
    @patch('platform.system')
    def test_clear_console_unix_fallback(self, mock_platform, mock_system, mock_clear):
        """Test that clear_console uses 'clear' on Unix-like systems"""
        # Make Rich clear fail
        mock_clear.side_effect = Exception("Rich clear failed")
        # Mock Unix-like platform
        mock_platform.return_value = "Linux"
        
        clear_console()
        
        # Should call 'clear' on Unix-like systems
        mock_system.assert_called_once_with('clear')
    
    @patch('lumos_cli.interactive.mode.clear_console')
    @patch('lumos_cli.interactive.mode.LLMRouter')
    @patch('lumos_cli.interactive.mode.EmbeddingDB')
    @patch('lumos_cli.interactive.mode.HistoryManager')
    @patch('lumos_cli.interactive.mode.PersonaManager')
    @patch('lumos_cli.ui.console.create_header')
    @patch('lumos_cli.interactive.mode.display_claude_style_prompt')
    def test_interactive_mode_clears_console_on_start(self, mock_prompt, mock_header, 
                                                     mock_persona, mock_history, 
                                                     mock_db, mock_router, mock_clear):
        """Test that interactive_mode clears console when it starts"""
        # Mock the prompt to return exit command immediately
        mock_prompt.return_value = '/exit'
        
        # Mock other dependencies
        mock_router.return_value = MagicMock()
        mock_db.return_value = MagicMock()
        mock_history.return_value = MagicMock()
        mock_persona.return_value = MagicMock()
        mock_header.return_value = None
        
        # Mock history manager methods
        mock_history_instance = mock_history.return_value
        mock_history_instance.get_or_create_session.return_value = "test-session"
        mock_history_instance.get_repository_stats.return_value = {
            'message_count': 0,
            'session_count': 1
        }
        
        # Call interactive mode
        interactive_mode()
        
        # Verify that clear_console was called
        mock_clear.assert_called_once()

if __name__ == '__main__':
    unittest.main()
