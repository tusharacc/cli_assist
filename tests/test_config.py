"""
Test Configuration for Lumos CLI

This file defines test configurations for different testing scenarios.
Modify the configurations below to customize which tests run in different modes.
"""

# Test categories and their configurations
TEST_CATEGORIES = {
    "core": {
        "description": "Core functionality tests",
        "paths": ["tests/unit/core/"],
        "critical": True,
        "timeout": 60,
        "dependencies": []
    },
    "clients": {
        "description": "External service client tests",
        "paths": ["tests/unit/clients/"],
        "critical": True,
        "timeout": 120,
        "dependencies": []
    },
    "interactive": {
        "description": "Interactive mode tests",
        "paths": ["tests/unit/interactive/"],
        "critical": True,
        "timeout": 60,
        "dependencies": ["core"]
    },
    "github": {
        "description": "GitHub integration tests",
        "paths": [
            "tests/functional/test_github_parsing.py",
            "tests/functional/test_commit_parsing_fix.py",
            "tests/functional/test_hybrid_github_parsing.py"
        ],
        "critical": False,
        "timeout": 180,
        "dependencies": ["core", "clients"],
        "requires_config": True
    },
    "jenkins": {
        "description": "Jenkins integration tests",
        "paths": ["tests/functional/test_jenkins_*.py"],
        "critical": False,
        "timeout": 180,
        "dependencies": ["core", "clients"],
        "requires_config": True
    },
    "jira": {
        "description": "Jira integration tests",
        "paths": ["tests/functional/test_jira_*.py"],
        "critical": False,
        "timeout": 120,
        "dependencies": ["core", "clients"],
        "requires_config": True
    },
    "neo4j": {
        "description": "Neo4j graph database tests",
        "paths": ["tests/functional/test_neo4j_*.py"],
        "critical": False,
        "timeout": 120,
        "dependencies": ["core", "clients"],
        "requires_config": True
    },
    "appdynamics": {
        "description": "AppDynamics monitoring tests",
        "paths": ["tests/functional/test_appdynamics_*.py"],
        "critical": False,
        "timeout": 120,
        "dependencies": ["core", "clients"],
        "requires_config": True
    },
    "shell": {
        "description": "Shell execution tests",
        "paths": [
            "tests/functional/test_shell_execution.py",
            "tests/functional/test_shell_executor.py"
        ],
        "critical": True,
        "timeout": 60,
        "dependencies": ["core"]
    },
    "config": {
        "description": "Configuration management tests",
        "paths": [
            "tests/functional/test_*config*.py",
            "tests/functional/test_*env*.py"
        ],
        "critical": True,
        "timeout": 60,
        "dependencies": ["core"]
    },
    "integration": {
        "description": "End-to-end integration tests",
        "paths": ["tests/integration/"],
        "critical": False,
        "timeout": 300,
        "dependencies": ["core", "clients", "interactive"],
        "requires_config": True
    }
}

# Test suites for different scenarios
TEST_SUITES = {
    "smoke": {
        "description": "Quick smoke test - basic functionality only",
        "categories": ["core", "clients", "interactive", "shell", "config"],
        "parallel": False
    },
    "unit": {
        "description": "Unit tests only - fast and reliable",
        "categories": ["core", "clients", "interactive"],
        "parallel": True
    },
    "integration": {
        "description": "Integration tests - requires external services",
        "categories": ["github", "jenkins", "jira", "neo4j", "appdynamics"],
        "parallel": False
    },
    "full": {
        "description": "Full test suite - everything",
        "categories": list(TEST_CATEGORIES.keys()),
        "parallel": False
    },
    "ci": {
        "description": "CI/CD pipeline tests - critical tests only",
        "categories": ["core", "clients", "interactive", "shell", "config"],
        "parallel": True
    },
    "development": {
        "description": "Development tests - fast feedback loop",
        "categories": ["core", "clients", "interactive", "shell"],
        "parallel": True
    }
}

# Test environment configurations
TEST_ENVIRONMENTS = {
    "local": {
        "description": "Local development environment",
        "requires_services": [],
        "timeout_multiplier": 1.0
    },
    "ci": {
        "description": "CI/CD environment",
        "requires_services": [],
        "timeout_multiplier": 2.0
    },
    "enterprise": {
        "description": "Enterprise environment with all services",
        "requires_services": ["github", "jenkins", "jira", "neo4j", "appdynamics"],
        "timeout_multiplier": 1.5
    }
}

# Test markers for pytest
PYTEST_MARKERS = {
    "unit": "Unit tests - fast, no external dependencies",
    "integration": "Integration tests - require external services",
    "slow": "Slow tests - may take longer to run",
    "requires_config": "Tests that require configuration setup",
    "requires_service": "Tests that require external services",
    "critical": "Critical tests - must pass for deployment",
    "optional": "Optional tests - nice to have but not critical"
}

# Default test configuration
DEFAULT_CONFIG = {
    "suite": "smoke",
    "environment": "local",
    "verbose": True,
    "parallel": False,
    "timeout": 300,
    "retries": 1,
    "stop_on_failure": True
}

def get_test_config(suite: str = "smoke", environment: str = "local") -> dict:
    """Get test configuration for a specific suite and environment"""
    config = DEFAULT_CONFIG.copy()
    
    if suite in TEST_SUITES:
        config.update(TEST_SUITES[suite])
    
    if environment in TEST_ENVIRONMENTS:
        env_config = TEST_ENVIRONMENTS[environment]
        config["timeout"] = int(config["timeout"] * env_config["timeout_multiplier"])
        config["requires_services"] = env_config["requires_services"]
    
    return config

def get_categories_for_suite(suite: str) -> list:
    """Get test categories for a specific suite"""
    if suite in TEST_SUITES:
        return TEST_SUITES[suite]["categories"]
    return []

def get_critical_categories() -> list:
    """Get all critical test categories"""
    return [name for name, config in TEST_CATEGORIES.items() if config["critical"]]

def get_categories_requiring_config() -> list:
    """Get categories that require configuration"""
    return [name for name, config in TEST_CATEGORIES.items() if config.get("requires_config", False)]

def validate_test_environment(environment: str) -> bool:
    """Validate that the test environment has required services"""
    if environment not in TEST_ENVIRONMENTS:
        return False
    
    env_config = TEST_ENVIRONMENTS[environment]
    required_services = env_config.get("requires_services", [])
    
    # Check if required services are available
    # This is a placeholder - implement actual service checks
    return True

# Export commonly used functions
__all__ = [
    "TEST_CATEGORIES",
    "TEST_SUITES", 
    "TEST_ENVIRONMENTS",
    "get_test_config",
    "get_categories_for_suite",
    "get_critical_categories",
    "get_categories_requiring_config",
    "validate_test_environment"
]
