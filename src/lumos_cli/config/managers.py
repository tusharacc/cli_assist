"""
Configuration managers for Lumos CLI
"""

from .github_config_manager import GitHubConfigManager
from .jenkins_config_manager import JenkinsConfigManager
from .neo4j_config import Neo4jConfigManager
from .appdynamics_config import AppDynamicsConfigManager
from .enterprise_llm_config import EnterpriseLLMConfigManager

# Jira config manager needs to be created
class JiraConfigManager:
    """Jira configuration manager"""
    def __init__(self):
        self.config_file = "jira_config.json"
    
    def is_configured(self) -> bool:
        """Check if Jira is configured"""
        import os
        return os.path.exists(self.config_file)
    
    def load_config(self):
        """Load Jira configuration"""
        if not self.is_configured():
            return None
        
        import json
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def save_config(self, config: dict) -> bool:
        """Save Jira configuration"""
        import json
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception:
            return False

__all__ = [
    'GitHubConfigManager',
    'JenkinsConfigManager', 
    'JiraConfigManager',
    'Neo4jConfigManager',
    'AppDynamicsConfigManager',
    'EnterpriseLLMConfigManager'
]
