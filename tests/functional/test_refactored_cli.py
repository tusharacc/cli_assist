"""
Functional tests for the refactored CLI
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import Mock, patch
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class TestRefactoredCLI:
    """Test cases for the refactored CLI"""
    
    def test_import_structure(self):
        """Test that all modules can be imported correctly"""
        # Test core imports
        from src.lumos_cli.core import LLMRouter, TaskType, EmbeddingDB, SafeFileEditor, HistoryManager
        assert LLMRouter is not None
        assert TaskType is not None
        assert EmbeddingDB is not None
        assert SafeFileEditor is not None
        assert HistoryManager is not None
        
        # Test client imports
        from src.lumos_cli.clients import GitHubClient, JenkinsClient, JiraClient, Neo4jClient, AppDynamicsClient
        assert GitHubClient is not None
        assert JenkinsClient is not None
        assert JiraClient is not None
        assert Neo4jClient is not None
        assert AppDynamicsClient is not None
        
        # Test config imports
        from src.lumos_cli.config import GitHubConfigManager, JenkinsConfigManager, JiraConfigManager
        assert GitHubConfigManager is not None
        assert JenkinsConfigManager is not None
        assert JiraConfigManager is not None
        
        # Test UI imports
        from src.lumos_cli.ui import console, create_header, show_footer
        assert console is not None
        assert create_header is not None
        assert show_footer is not None
        
        # Test interactive imports
        from src.lumos_cli.interactive import interactive_mode, detect_intent
        assert interactive_mode is not None
        assert detect_intent is not None
    
    def test_cli_initialization(self):
        """Test CLI initialization"""
        from src.lumos_cli.cli_refactored_v2 import app, get_history_manager, get_persona_manager
        
        assert app is not None
        assert callable(get_history_manager)
        assert callable(get_persona_manager)
        
        # Test manager initialization
        history_manager = get_history_manager()
        persona_manager = get_persona_manager()
        
        assert history_manager is not None
        assert persona_manager is not None
    
    def test_command_registration(self):
        """Test that all commands are properly registered"""
        from src.lumos_cli.cli_refactored_v2 import app
        
        # Get all registered commands
        commands = list(app.commands.keys())
        
        # Check that key commands are registered
        expected_commands = [
            'plan', 'edit', 'review', 'debug', 'chat',
            'github-clone', 'github-pr', 'github-config',
            'jenkins-failed-jobs', 'jenkins-running-jobs', 'jenkins-config',
            'platform', 'logs', 'detect', 'start', 'fix', 'preview',
            'index', 'cleanup', 'sessions', 'repos', 'context',
            'search', 'history', 'persona', 'shell', 'templates', 'welcome',
            'scaffold', 'backups', 'restore'
        ]
        
        for command in expected_commands:
            assert command in commands, f"Command '{command}' not found in registered commands"
    
    def test_interactive_mode_structure(self):
        """Test interactive mode structure"""
        from src.lumos_cli.interactive.mode import interactive_mode
        from src.lumos_cli.interactive.intent_detection import detect_intent
        from src.lumos_cli.interactive.handlers import (
            interactive_github, interactive_jenkins, interactive_jira,
            interactive_neo4j, interactive_appdynamics, interactive_code
        )
        
        assert callable(interactive_mode)
        assert callable(detect_intent)
        assert callable(interactive_github)
        assert callable(interactive_jenkins)
        assert callable(interactive_jira)
        assert callable(interactive_neo4j)
        assert callable(interactive_appdynamics)
        assert callable(interactive_code)
    
    def test_intent_detection_functionality(self):
        """Test intent detection functionality"""
        from src.lumos_cli.interactive.intent_detection import detect_intent
        
        # Test GitHub intent
        result = detect_intent("get PRs from microsoft/vscode")
        assert result['type'] == 'github'
        assert result['confidence'] > 0
        assert result['org_repo'] == 'microsoft/vscode'
        
        # Test Jenkins intent
        result = detect_intent("show failed builds in jenkins")
        assert result['type'] == 'jenkins'
        assert result['confidence'] > 0
        
        # Test Jira intent
        result = detect_intent("get details for ticket PROJ-123")
        assert result['type'] == 'jira'
        assert result['confidence'] > 0
        assert result['ticket_key'] == 'PROJ-123'
        
        # Test Neo4j intent
        result = detect_intent("analyze dependencies of class UserService")
        assert result['type'] == 'neo4j'
        assert result['confidence'] > 0
        assert result['class_name'] == 'UserService'
        
        # Test AppDynamics intent
        result = detect_intent("show resource utilization")
        assert result['type'] == 'appdynamics'
        assert result['confidence'] > 0
        
        # Test Code intent
        result = detect_intent("generate a Python function")
        assert result['type'] == 'code'
        assert result['confidence'] > 0
    
    def test_ui_components(self):
        """Test UI components"""
        from src.lumos_cli.ui.console import console, create_header, create_welcome_panel
        from src.lumos_cli.ui.footer import show_footer, show_status_footer
        from src.lumos_cli.ui.panels import create_command_help_panel, create_status_panel
        
        assert console is not None
        assert callable(create_header)
        assert callable(create_welcome_panel)
        assert callable(show_footer)
        assert callable(show_status_footer)
        assert callable(create_command_help_panel)
        assert callable(create_status_panel)
    
    def test_config_managers(self):
        """Test configuration managers"""
        from src.lumos_cli.config.managers import (
            GitHubConfigManager, JenkinsConfigManager, JiraConfigManager,
            Neo4jConfigManager, AppDynamicsConfigManager, EnterpriseLLMConfigManager
        )
        
        # Test that all managers can be instantiated
        github_manager = GitHubConfigManager()
        jenkins_manager = JenkinsConfigManager()
        jira_manager = JiraConfigManager()
        neo4j_manager = Neo4jConfigManager()
        appdynamics_manager = AppDynamicsConfigManager()
        enterprise_manager = EnterpriseLLMConfigManager()
        
        assert github_manager is not None
        assert jenkins_manager is not None
        assert jira_manager is not None
        assert neo4j_manager is not None
        assert appdynamics_manager is not None
        assert enterprise_manager is not None
    
    def test_validators(self):
        """Test configuration validators"""
        from src.lumos_cli.config.validators import (
            validate_config, validate_credentials, validate_url,
            validate_email, validate_github_token, validate_jira_key,
            validate_neo4j_uri, validate_appdynamics_url
        )
        
        # Test URL validation
        assert validate_url("https://api.github.com") is True
        assert validate_url("http://localhost:8080") is True
        assert validate_url("invalid-url") is False
        
        # Test email validation
        assert validate_email("test@example.com") is True
        assert validate_email("invalid-email") is False
        
        # Test GitHub token validation
        assert validate_github_token("ghp_1234567890abcdef1234567890abcdef12345678") is True
        assert validate_github_token("invalid-token") is False
        
        # Test Jira key validation
        assert validate_jira_key("PROJ-123") is True
        assert validate_jira_key("invalid-key") is False
        
        # Test Neo4j URI validation
        assert validate_neo4j_uri("bolt://localhost:7687") is True
        assert validate_neo4j_uri("neo4j://localhost:7687") is True
        assert validate_neo4j_uri("invalid-uri") is False
        
        # Test AppDynamics URL validation
        assert validate_appdynamics_url("https://test.saas.appdynamics.com") is True
        assert validate_appdynamics_url("https://test.appdynamics.io") is True
        assert validate_appdynamics_url("https://invalid.com") is False
    
    def test_core_functionality(self):
        """Test core functionality"""
        from src.lumos_cli.core.router import LLMRouter, TaskType
        from src.lumos_cli.core.embeddings import EmbeddingDB
        from src.lumos_cli.core.safety import SafeFileEditor
        from src.lumos_cli.core.history import HistoryManager
        
        # Test TaskType enum
        assert TaskType.CODE_GENERATION == "code_generation"
        assert TaskType.CODE_REVIEW == "code_review"
        assert TaskType.PLANNING == "planning"
        assert TaskType.CHAT == "chat"
        assert TaskType.DEBUGGING == "debugging"
        
        # Test router initialization
        router = LLMRouter()
        assert router is not None
        
        # Test embeddings initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            db = EmbeddingDB(db_path=os.path.join(temp_dir, "test.db"))
            assert db is not None
        
        # Test safety editor initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            editor = SafeFileEditor(backup_dir=temp_dir)
            assert editor is not None
        
        # Test history manager initialization
        history = HistoryManager()
        assert history is not None
    
    def test_module_imports(self):
        """Test that all modules can be imported without errors"""
        try:
            # Test core modules
            from src.lumos_cli.core import router, embeddings, safety, history
            
            # Test client modules
            from src.lumos_cli.clients import github_client, jenkins_client, jira_client, neo4j_client, appdynamics_client
            
            # Test config modules
            from src.lumos_cli.config import managers, validators
            
            # Test UI modules
            from src.lumos_cli.ui import console, footer, panels
            
            # Test interactive modules
            from src.lumos_cli.interactive import mode, intent_detection
            from src.lumos_cli.interactive.handlers import (
                github_handler, jenkins_handler, jira_handler,
                neo4j_handler, appdynamics_handler, code_handler
            )
            
            # Test utility modules
            from src.lumos_cli.utils import platform_utils, debug_logger, file_discovery
            
            # All imports successful
            assert True
            
        except ImportError as e:
            pytest.fail(f"Failed to import module: {e}")
    
    def test_directory_structure(self):
        """Test that the directory structure is correct"""
        base_path = Path(__file__).parent.parent.parent / "src" / "lumos_cli"
        
        # Check core directory
        assert (base_path / "core").exists()
        assert (base_path / "core" / "__init__.py").exists()
        assert (base_path / "core" / "router.py").exists()
        assert (base_path / "core" / "embeddings.py").exists()
        assert (base_path / "core" / "safety.py").exists()
        assert (base_path / "core" / "history.py").exists()
        
        # Check clients directory
        assert (base_path / "clients").exists()
        assert (base_path / "clients" / "__init__.py").exists()
        assert (base_path / "clients" / "github_client.py").exists()
        assert (base_path / "clients" / "jenkins_client.py").exists()
        assert (base_path / "clients" / "jira_client.py").exists()
        assert (base_path / "clients" / "neo4j_client.py").exists()
        assert (base_path / "clients" / "appdynamics_client.py").exists()
        
        # Check config directory
        assert (base_path / "config").exists()
        assert (base_path / "config" / "__init__.py").exists()
        assert (base_path / "config" / "managers.py").exists()
        assert (base_path / "config" / "validators.py").exists()
        
        # Check UI directory
        assert (base_path / "ui").exists()
        assert (base_path / "ui" / "__init__.py").exists()
        assert (base_path / "ui" / "console.py").exists()
        assert (base_path / "ui" / "footer.py").exists()
        assert (base_path / "ui" / "panels.py").exists()
        
        # Check interactive directory
        assert (base_path / "interactive").exists()
        assert (base_path / "interactive" / "__init__.py").exists()
        assert (base_path / "interactive" / "mode.py").exists()
        assert (base_path / "interactive" / "intent_detection.py").exists()
        assert (base_path / "interactive" / "handlers").exists()
        assert (base_path / "interactive" / "handlers" / "__init__.py").exists()
        
        # Check utils directory
        assert (base_path / "utils").exists()
        assert (base_path / "utils" / "__init__.py").exists()
        assert (base_path / "utils" / "platform_utils.py").exists()
        assert (base_path / "utils" / "debug_logger.py").exists()
        assert (base_path / "utils" / "file_discovery.py").exists()
