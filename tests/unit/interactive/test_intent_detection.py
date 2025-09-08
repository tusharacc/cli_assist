"""
Unit tests for intent detection
"""

import pytest
from src.lumos_cli.interactive.intent_detection import detect_intent

class TestIntentDetection:
    """Test cases for intent detection"""
    
    def test_github_intent_detection(self):
        """Test GitHub intent detection"""
        # Test PR queries
        result = detect_intent("get latest PRs from scimarketplace/externaldata")
        assert result['type'] == 'github'
        assert result['confidence'] > 0
        assert 'org_repo' in result
        
        # Test commit queries
        result = detect_intent("show me commits from tusharacc/cli_assist")
        assert result['type'] == 'github'
        assert result['confidence'] > 0
        
        # Test clone queries
        result = detect_intent("clone the repository microsoft/vscode")
        assert result['type'] == 'github'
        assert result['confidence'] > 0
    
    def test_jenkins_intent_detection(self):
        """Test Jenkins intent detection"""
        # Test build status queries
        result = detect_intent("show me failed builds in jenkins")
        assert result['type'] == 'jenkins'
        assert result['confidence'] > 0
        
        # Test job queries
        result = detect_intent("get running jobs from deploy-all folder")
        assert result['type'] == 'jenkins'
        assert result['confidence'] > 0
        
        # Test build number queries
        result = detect_intent("show build parameters for build 123")
        assert result['type'] == 'jenkins'
        assert result['confidence'] > 0
    
    def test_jira_intent_detection(self):
        """Test Jira intent detection"""
        # Test ticket queries
        result = detect_intent("get details for ticket PROJ-123")
        assert result['type'] == 'jira'
        assert result['confidence'] > 0
        assert 'ticket_key' in result
        
        # Test comment queries
        result = detect_intent("extract comments for JIRA-456")
        assert result['type'] == 'jira'
        assert result['confidence'] > 0
    
    def test_neo4j_intent_detection(self):
        """Test Neo4j intent detection"""
        # Test dependency queries
        result = detect_intent("show dependencies of class UserService")
        assert result['type'] == 'neo4j'
        assert result['confidence'] > 0
        assert 'class_name' in result
        
        # Test impact analysis
        result = detect_intent("analyze impact of method validateUser")
        assert result['type'] == 'neo4j'
        assert result['confidence'] > 0
    
    def test_appdynamics_intent_detection(self):
        """Test AppDynamics intent detection"""
        # Test resource utilization
        result = detect_intent("show resource utilization for servers")
        assert result['type'] == 'appdynamics'
        assert result['confidence'] > 0
        
        # Test business transactions
        result = detect_intent("get business transaction metrics")
        assert result['type'] == 'appdynamics'
        assert result['confidence'] > 0
        
        # Test alerts
        result = detect_intent("show me active alerts")
        assert result['type'] == 'appdynamics'
        assert result['confidence'] > 0
    
    def test_code_intent_detection(self):
        """Test code intent detection"""
        # Test code generation
        result = detect_intent("generate a Python function for data processing")
        assert result['type'] == 'code'
        assert result['confidence'] > 0
        
        # Test code editing
        result = detect_intent("edit the authentication function")
        assert result['type'] == 'code'
        assert result['confidence'] > 0
        
        # Test code review
        result = detect_intent("review the API implementation")
        assert result['type'] == 'code'
        assert result['confidence'] > 0
    
    def test_legacy_intent_detection(self):
        """Test legacy intent detection for backward compatibility"""
        # Test edit intent
        result = detect_intent("edit the main function")
        assert result['type'] == 'edit'
        assert result['confidence'] > 0
        
        # Test plan intent
        result = detect_intent("plan a new feature")
        assert result['type'] == 'plan'
        assert result['confidence'] > 0
        
        # Test review intent
        result = detect_intent("review this code file")
        assert result['type'] == 'review'
        assert result['confidence'] > 0
        
        # Test fix intent
        result = detect_intent("fix the bug in the code")
        assert result['type'] == 'fix'
        assert result['confidence'] > 0
    
    def test_shell_intent_detection(self):
        """Test shell intent detection"""
        # Test shell commands
        result = detect_intent("run ls -la command")
        assert result['type'] == 'shell'
        assert result['confidence'] > 0
        
        # Test git commands
        result = detect_intent("execute git status")
        assert result['type'] == 'shell'
        assert result['confidence'] > 0
    
    def test_chat_fallback(self):
        """Test chat fallback for unrecognized intents"""
        # Test general conversation
        result = detect_intent("hello, how are you?")
        assert result['type'] == 'chat'
        assert result['confidence'] == 0.0
        
        # Test unclear intent
        result = detect_intent("what is the weather like?")
        assert result['type'] == 'chat'
        assert result['confidence'] == 0.0
    
    def test_confidence_scoring(self):
        """Test confidence scoring"""
        # High confidence GitHub query
        result = detect_intent("get pull requests from github repository")
        assert result['confidence'] > 0.5
        
        # Low confidence query
        result = detect_intent("hello world")
        assert result['confidence'] == 0.0
    
    def test_extracted_data(self):
        """Test data extraction from queries"""
        # Test GitHub org/repo extraction
        result = detect_intent("get PRs from microsoft/vscode")
        assert result['type'] == 'github'
        assert result['org_repo'] == 'microsoft/vscode'
        
        # Test Jira ticket key extraction
        result = detect_intent("show details for PROJ-123")
        assert result['type'] == 'jira'
        assert result['ticket_key'] == 'PROJ-123'
        
        # Test class name extraction
        result = detect_intent("analyze dependencies of class PaymentService")
        assert result['type'] == 'neo4j'
        assert result['class_name'] == 'PaymentService'
