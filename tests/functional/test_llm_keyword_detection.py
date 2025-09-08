#!/usr/bin/env python3
"""
Test LLM-based keyword detection system
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lumos_cli.core.keyword_detector import (
    UnifiedKeywordDetector, KeywordDetectionResult, 
    GitHubKeywordDetector, JenkinsKeywordDetector, 
    JiraKeywordDetector, AppDynamicsKeywordDetector, 
    Neo4jKeywordDetector
)

class TestLLMKeywordDetection(unittest.TestCase):
    """Test LLM-based keyword detection system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = UnifiedKeywordDetector()
    
    def test_github_commits_detection(self):
        """Test GitHub commits keyword detection"""
        # Mock the LLM response
        mock_router = MagicMock()
        mock_router.chat.return_value = '''{
            "action": "commits",
            "confidence": 0.9,
            "extracted_values": {
                "org": "scimarketplace",
                "repo": "quote",
                "count": 5
            },
            "reasoning": "Detected commit-related query with org/repo and count"
        }'''
        
        # Create detector with mocked router
        detector = UnifiedKeywordDetector(router=mock_router)
        result = detector.detect_keywords('github', 'get last 5 commits from scimarketplace/quote')
        
        self.assertEqual(result.action, 'commits')
        self.assertEqual(result.confidence, 0.9)
        self.assertEqual(result.extracted_values['org'], 'scimarketplace')
        self.assertEqual(result.extracted_values['repo'], 'quote')
        self.assertEqual(result.extracted_values['count'], 5)
        self.assertEqual(result.integration, 'github')
    
    def test_github_pr_detection(self):
        """Test GitHub PR keyword detection"""
        # Mock the LLM response
        mock_router = MagicMock()
        mock_router.chat.return_value = '''{
            "action": "pr",
            "confidence": 0.8,
            "extracted_values": {
                "org": "tusharacc",
                "repo": "cli_assist",
                "branch": "main"
            },
            "reasoning": "Detected PR-related query with org/repo and branch"
        }'''
        
        # Create detector with mocked router
        detector = UnifiedKeywordDetector(router=mock_router)
        result = detector.detect_keywords('github', 'show PRs for tusharacc/cli_assist main branch')
        
        self.assertEqual(result.action, 'pr')
        self.assertEqual(result.confidence, 0.8)
        self.assertEqual(result.extracted_values['org'], 'tusharacc')
        self.assertEqual(result.extracted_values['repo'], 'cli_assist')
        self.assertEqual(result.extracted_values['branch'], 'main')
    
    def test_jenkins_builds_detection(self):
        """Test Jenkins builds keyword detection"""
        # Mock the LLM response
        mock_router = MagicMock()
        mock_router.chat.return_value = '''{
            "action": "builds",
            "confidence": 0.9,
            "extracted_values": {
                "folder_path": "scimarketplace/quote_multi/RC1",
                "count": 5
            },
            "reasoning": "Detected build status query with folder path and count"
        }'''
        
        # Create detector with mocked router
        detector = UnifiedKeywordDetector(router=mock_router)
        result = detector.detect_keywords('jenkins', 'get last 5 builds for scimarketplace and folder quote and sub folder RC1')
        
        self.assertEqual(result.action, 'builds')
        self.assertEqual(result.confidence, 0.9)
        self.assertEqual(result.extracted_values['folder_path'], 'scimarketplace/quote_multi/RC1')
        self.assertEqual(result.extracted_values['count'], 5)
        self.assertEqual(result.integration, 'jenkins')
    
    def test_jenkins_failed_jobs_detection(self):
        """Test Jenkins failed jobs keyword detection"""
        # Mock the LLM response
        mock_router = MagicMock()
        mock_router.chat.return_value = '''{
            "action": "failed_jobs",
            "confidence": 0.8,
            "extracted_values": {
                "folder_path": "scimarketplace/deploy-all",
                "hours": 4
            },
            "reasoning": "Detected failed jobs query with folder path and time range"
        }'''
        
        # Create detector with mocked router
        detector = UnifiedKeywordDetector(router=mock_router)
        result = detector.detect_keywords('jenkins', 'show failed jobs in scimarketplace/deploy-all last 4 hours')
        
        self.assertEqual(result.action, 'failed_jobs')
        self.assertEqual(result.confidence, 0.8)
        self.assertEqual(result.extracted_values['folder_path'], 'scimarketplace/deploy-all')
        self.assertEqual(result.extracted_values['hours'], 4)
    
    def test_jira_ticket_detection(self):
        """Test Jira ticket keyword detection"""
        # Mock the LLM response
        mock_router = MagicMock()
        mock_router.chat.return_value = '''{
            "action": "ticket",
            "confidence": 0.9,
            "extracted_values": {
                "ticket_key": "PROJECT-123"
            },
            "reasoning": "Detected specific ticket query with ticket key"
        }'''
        
        # Create detector with mocked router
        detector = UnifiedKeywordDetector(router=mock_router)
        result = detector.detect_keywords('jira', 'show me PROJECT-123')
        
        self.assertEqual(result.action, 'ticket')
        self.assertEqual(result.confidence, 0.9)
        self.assertEqual(result.extracted_values['ticket_key'], 'PROJECT-123')
        self.assertEqual(result.integration, 'jira')
    
    def test_appdynamics_resources_detection(self):
        """Test AppDynamics resources keyword detection"""
        # Mock the LLM response
        mock_router = MagicMock()
        mock_router.chat.return_value = '''{
            "action": "resources",
            "confidence": 0.8,
            "extracted_values": {
                "metric_type": "cpu",
                "time_range": "1h"
            },
            "reasoning": "Detected resource utilization query with metric type and time range"
        }'''
        
        # Create detector with mocked router
        detector = UnifiedKeywordDetector(router=mock_router)
        result = detector.detect_keywords('appdynamics', 'show resource utilization for CPU last hour')
        
        self.assertEqual(result.action, 'resources')
        self.assertEqual(result.confidence, 0.8)
        self.assertEqual(result.extracted_values['metric_type'], 'cpu')
        self.assertEqual(result.extracted_values['time_range'], '1h')
        self.assertEqual(result.integration, 'appdynamics')
    
    def test_neo4j_dependencies_detection(self):
        """Test Neo4j dependencies keyword detection"""
        # Mock the LLM response
        mock_router = MagicMock()
        mock_router.chat.return_value = '''{
            "action": "dependencies",
            "confidence": 0.9,
            "extracted_values": {
                "class_name": "UserService",
                "depth": 2
            },
            "reasoning": "Detected dependencies query with class name and depth"
        }'''
        
        # Create detector with mocked router
        detector = UnifiedKeywordDetector(router=mock_router)
        result = detector.detect_keywords('neo4j', 'show dependencies of class UserService depth 2')
        
        self.assertEqual(result.action, 'dependencies')
        self.assertEqual(result.confidence, 0.9)
        self.assertEqual(result.extracted_values['class_name'], 'UserService')
        self.assertEqual(result.extracted_values['depth'], 2)
        self.assertEqual(result.integration, 'neo4j')
    
    def test_json_parse_error_fallback(self):
        """Test fallback when LLM returns invalid JSON"""
        # Mock the LLM response with invalid JSON
        mock_router = MagicMock()
        mock_router.chat.return_value = 'Invalid JSON response'
        
        # Create detector with mocked router
        detector = UnifiedKeywordDetector(router=mock_router)
        result = detector.detect_keywords('github', 'get commits')
        
        # Should fall back to simple parsing
        self.assertIn(result.action, ['commits', 'pr', 'clone', 'unknown'])
        self.assertEqual(result.integration, 'github')
    
    def test_llm_exception_handling(self):
        """Test exception handling when LLM fails"""
        # Mock the LLM to raise an exception
        mock_router = MagicMock()
        mock_router.chat.side_effect = Exception("LLM connection failed")
        
        # Create detector with mocked router
        detector = UnifiedKeywordDetector(router=mock_router)
        result = detector.detect_keywords('github', 'get commits')
        
        self.assertEqual(result.action, 'error')
        self.assertEqual(result.confidence, 0.0)
        self.assertIn('Detection failed', result.reasoning)
        self.assertEqual(result.integration, 'github')
    
    def test_unknown_integration(self):
        """Test handling of unknown integration"""
        result = self.detector.detect_keywords('unknown', 'some query')
        
        self.assertEqual(result.action, 'error')
        self.assertEqual(result.confidence, 0.0)
        self.assertIn('Unknown integration', result.reasoning)
        self.assertEqual(result.integration, 'unknown')
    
    def test_supported_integrations(self):
        """Test getting supported integrations"""
        integrations = self.detector.get_supported_integrations()
        
        expected = ['github', 'jenkins', 'jira', 'appdynamics', 'neo4j']
        self.assertEqual(set(integrations), set(expected))

if __name__ == '__main__':
    unittest.main()
