"""
Configuration validators for Lumos CLI
"""

import re
from typing import Dict, Any, List, Optional

def validate_config(config: Dict[str, Any], required_fields: List[str]) -> tuple[bool, str]:
    """
    Validate configuration data
    
    Args:
        config: Configuration dictionary
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(config, dict):
        return False, "Configuration must be a dictionary"
    
    missing_fields = []
    for field in required_fields:
        if field not in config or not config[field]:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, ""

def validate_credentials(credentials: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate credential data
    
    Args:
        credentials: Credentials dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(credentials, dict):
        return False, "Credentials must be a dictionary"
    
    # Check for common credential fields
    required_fields = ['username', 'password']
    optional_fields = ['token', 'api_key', 'client_id', 'client_secret']
    
    has_required = any(field in credentials for field in required_fields)
    has_optional = any(field in credentials for field in optional_fields)
    
    if not has_required and not has_optional:
        return False, "Must provide either username/password or token/api_key"
    
    return True, ""

def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    if not url:
        return False
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email string to validate
        
    Returns:
        True if valid email, False otherwise
    """
    if not email:
        return False
    
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(email))

def validate_github_token(token: str) -> bool:
    """
    Validate GitHub token format
    
    Args:
        token: GitHub token string
        
    Returns:
        True if valid token, False otherwise
    """
    if not token:
        return False
    
    # GitHub tokens are typically 40 characters (classic) or start with ghp_ (fine-grained)
    if len(token) == 40 and token.isalnum():
        return True
    elif token.startswith('ghp_') and len(token) > 40:
        return True
    elif token.startswith('github_pat_') and len(token) > 50:
        return True
    
    return False

def validate_jira_key(key: str) -> bool:
    """
    Validate Jira ticket key format
    
    Args:
        key: Jira ticket key (e.g., PROJECT-123)
        
    Returns:
        True if valid key, False otherwise
    """
    if not key:
        return False
    
    # Jira keys are typically PROJECT-123 format
    key_pattern = re.compile(r'^[A-Z]+-\d+$')
    return bool(key_pattern.match(key))

def validate_neo4j_uri(uri: str) -> bool:
    """
    Validate Neo4j URI format
    
    Args:
        uri: Neo4j URI string
        
    Returns:
        True if valid URI, False otherwise
    """
    if not uri:
        return False
    
    # Neo4j URIs typically start with bolt:// or neo4j://
    return uri.startswith(('bolt://', 'neo4j://', 'bolt+s://', 'neo4j+s://'))

def validate_appdynamics_url(url: str) -> bool:
    """
    Validate AppDynamics controller URL
    
    Args:
        url: AppDynamics controller URL
        
    Returns:
        True if valid URL, False otherwise
    """
    if not url:
        return False
    
    # AppDynamics URLs typically end with .saas.appdynamics.com or similar
    return validate_url(url) and ('appdynamics.com' in url or 'appdynamics.io' in url)
