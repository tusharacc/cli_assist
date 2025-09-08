#!/usr/bin/env python3
"""Test utilities for Lumos CLI tests"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.config import config
from lumos_cli.enterprise_llm import is_enterprise_configured

def is_github_configured():
    """Check if GitHub is configured"""
    try:
        from lumos_cli.github_client import GitHubClient
        client = GitHubClient()
        return client.test_connection()
    except:
        return False

def is_jenkins_configured():
    """Check if Jenkins is configured"""
    try:
        from lumos_cli.jenkins_client import JenkinsClient
        client = JenkinsClient()
        return client.test_connection()
    except:
        return False

def is_jira_configured():
    """Check if Jira is configured"""
    try:
        from lumos_cli.jira_client import JiraClient, JiraConfigManager
        config_manager = JiraConfigManager()
        return config_manager.load_config() is not None
    except:
        return False

def is_enterprise_llm_configured():
    """Check if Enterprise LLM is configured"""
    return is_enterprise_configured() or config.is_enterprise_configured()

def skip_if_not_configured(service_name, check_function, test_name=""):
    """Decorator to skip test if service is not configured"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not check_function():
                print(f"⏭️  Skipping {test_name or func.__name__} - {service_name} not configured")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_configuration_status():
    """Get status of all configurations"""
    return {
        'github': is_github_configured(),
        'jenkins': is_jenkins_configured(),
        'jira': is_jira_configured(),
        'enterprise_llm': is_enterprise_llm_configured()
    }

def print_configuration_status():
    """Print configuration status for all services"""
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    status = get_configuration_status()
    
    table = Table(title="Configuration Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="bold")
    
    for service, configured in status.items():
        status_text = "✅ Configured" if configured else "❌ Not Configured"
        table.add_row(service.replace('_', ' ').title(), status_text)
    
    console.print(table)
    return status
