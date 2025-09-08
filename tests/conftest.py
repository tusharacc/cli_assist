"""
Pytest configuration and fixtures for Lumos CLI tests
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_config():
    """Mock configuration for tests"""
    return {
        'github': {
            'token': 'test_token',
            'base_url': 'https://api.github.com'
        },
        'jenkins': {
            'url': 'http://localhost:8080',
            'token': 'test_token'
        },
        'jira': {
            'url': 'https://test.atlassian.net',
            'username': 'test@example.com',
            'token': 'test_token'
        },
        'neo4j': {
            'uri': 'bolt://localhost:7687',
            'username': 'neo4j',
            'password': 'password'
        },
        'appdynamics': {
            'controller_url': 'https://test.saas.appdynamics.com',
            'client_id': 'test_client',
            'client_secret': 'test_secret'
        }
    }

@pytest.fixture
def mock_enterprise_llm_config():
    """Mock enterprise LLM configuration for tests"""
    return {
        'token_url': 'https://test-enterprise.com/oauth2/token',
        'chat_url': 'https://test-enterprise.com/api/v1/chat/completions',
        'app_id': 'test_client_id',
        'app_key': 'test_client_secret',
        'app_resource': 'https://test-enterprise.com/api'
    }

@pytest.fixture
def sample_code_files(temp_dir):
    """Create sample code files for testing"""
    files = {
        'test.py': '''
def hello_world():
    """A simple hello world function"""
    return "Hello, World!"

def add_numbers(a, b):
    """Add two numbers"""
    return a + b
''',
        'test.js': '''
function greet(name) {
    return `Hello, ${name}!`;
}

const add = (a, b) => a + b;
''',
        'test.java': '''
public class TestClass {
    public String hello() {
        return "Hello, World!";
    }
    
    public int add(int a, int b) {
        return a + b;
    }
}
'''
    }
    
    for filename, content in files.items():
        file_path = Path(temp_dir) / filename
        file_path.write_text(content)
    
    return temp_dir

@pytest.fixture
def mock_github_response():
    """Mock GitHub API response"""
    return {
        'id': 12345,
        'name': 'test-repo',
        'full_name': 'test-org/test-repo',
        'description': 'A test repository',
        'html_url': 'https://github.com/test-org/test-repo',
        'clone_url': 'https://github.com/test-org/test-repo.git',
        'stargazers_count': 100,
        'forks_count': 25,
        'updated_at': '2024-01-01T00:00:00Z'
    }

@pytest.fixture
def mock_jenkins_response():
    """Mock Jenkins API response"""
    return {
        'jobs': [
            {
                'name': 'test-job',
                'url': 'http://localhost:8080/job/test-job/',
                'color': 'blue',
                'lastBuild': {
                    'number': 123,
                    'url': 'http://localhost:8080/job/test-job/123/',
                    'result': 'SUCCESS'
                }
            }
        ]
    }

@pytest.fixture
def mock_jira_response():
    """Mock Jira API response"""
    return {
        'id': '12345',
        'key': 'TEST-123',
        'fields': {
            'summary': 'Test Issue',
            'description': 'This is a test issue',
            'status': {'name': 'To Do'},
            'assignee': {'displayName': 'Test User'},
            'reporter': {'displayName': 'Test Reporter'}
        }
    }

@pytest.fixture
def mock_neo4j_response():
    """Mock Neo4j query response"""
    return [
        {
            'class_name': 'TestClass',
            'repository': 'test-repo',
            'dependency_type': 'inherits'
        }
    ]

@pytest.fixture
def mock_appdynamics_response():
    """Mock AppDynamics API response"""
    return {
        'access_token': 'test_access_token',
        'token_type': 'Bearer',
        'expires_in': 3600
    }
