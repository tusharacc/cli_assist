"""
Command modules for Lumos CLI
"""

from .github import github_clone, github_pr, github_config
from .jenkins import jenkins_failed_jobs, jenkins_running_jobs, jenkins_repository_jobs, jenkins_build_parameters, jenkins_analyze_failure, jenkins_config

# TODO: Implement remaining command modules
# from .edit import edit
# from .review import review
# from .plan import plan
# from .debug import debug
# from .chat import chat
# from .scaffold import scaffold
# from .backups import backups, restore
# from .config import config_show, config_setup
# from .utils import platform, logs, detect, start, fix, preview, index, cleanup, sessions, repos, context, search, history, persona, shell, templates, welcome

__all__ = [
    # GitHub commands
    'github_clone', 'github_pr', 'github_config',
    
    # Jenkins commands
    'jenkins_failed_jobs', 'jenkins_running_jobs', 'jenkins_repository_jobs', 
    'jenkins_build_parameters', 'jenkins_analyze_failure', 'jenkins_config',
    
    # TODO: Add other commands when implemented
]
