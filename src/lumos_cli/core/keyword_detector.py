"""
Unified LLM-based keyword detection system for all integrations
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from .router import LLMRouter
from ..utils.debug_logger import get_debug_logger

debug_logger = get_debug_logger()

@dataclass
class KeywordDetectionResult:
    """Result of keyword detection analysis"""
    action: str
    confidence: float
    extracted_values: Dict[str, Any]
    reasoning: str
    integration: str

class IntegrationKeywordDetector:
    """Base class for integration-specific keyword detection"""
    
    def __init__(self, integration_name: str, prompt_template: str, router: LLMRouter = None):
        self.integration_name = integration_name
        self.prompt_template = prompt_template
        self.router = router or LLMRouter(backend="ollama")
    
    def detect_keywords(self, query: str) -> KeywordDetectionResult:
        """Detect keywords and extract values from query"""
        try:
            prompt = self.prompt_template.format(query=query)
            messages = [{"role": "user", "content": prompt}]
            
            debug_logger.info(f"Detecting keywords for {self.integration_name}: {query}")
            response = self.router.chat(messages)
            
            # Parse JSON response
            try:
                result_data = json.loads(response.strip())
            except json.JSONDecodeError:
                # Fallback if response is not valid JSON
                result_data = self._parse_fallback_response(response)
            
            return KeywordDetectionResult(
                action=result_data.get('action', 'unknown'),
                confidence=result_data.get('confidence', 0.0),
                extracted_values=result_data.get('extracted_values', {}),
                reasoning=result_data.get('reasoning', ''),
                integration=self.integration_name
            )
            
        except Exception as e:
            debug_logger.error(f"Keyword detection failed for {self.integration_name}: {e}")
            return KeywordDetectionResult(
                action='error',
                confidence=0.0,
                extracted_values={},
                reasoning=f"Detection failed: {str(e)}",
                integration=self.integration_name
            )
    
    def _parse_fallback_response(self, response: str) -> Dict[str, Any]:
        """Fallback parser for non-JSON responses"""
        # Simple fallback - extract action from response
        response_lower = response.lower()
        
        if 'commit' in response_lower:
            return {
                'action': 'commits',
                'confidence': 0.7,
                'extracted_values': {},
                'reasoning': 'Detected commit-related query'
            }
        elif 'pr' in response_lower or 'pull' in response_lower:
            return {
                'action': 'pr',
                'confidence': 0.7,
                'extracted_values': {},
                'reasoning': 'Detected PR-related query'
            }
        elif 'clone' in response_lower or 'fetch' in response_lower:
            return {
                'action': 'clone',
                'confidence': 0.7,
                'extracted_values': {},
                'reasoning': 'Detected clone-related query'
            }
        else:
            return {
                'action': 'unknown',
                'confidence': 0.3,
                'extracted_values': {},
                'reasoning': 'Could not determine action'
            }

class GitHubKeywordDetector(IntegrationKeywordDetector):
    """GitHub-specific keyword detection"""
    
    def __init__(self, router: LLMRouter = None):
        prompt_template = """You are a GitHub command analyzer. Analyze the user query and extract GitHub-specific information.

User Query: "{query}"

Return a JSON response with the following structure:
{{
    "action": "commits|pr|clone|unknown",
    "confidence": 0.0-1.0,
    "extracted_values": {{
        "org": "organization_name",
        "repo": "repository_name", 
        "branch": "branch_name",
        "count": number,
        "commit_sha": "commit_hash"
    }},
    "reasoning": "Brief explanation of the analysis"
}}

Rules:
1. For commits: action="commits", extract org/repo, count (default 5), branch if specified
2. For PRs: action="pr", extract org/repo, branch if specified
3. For cloning: action="clone", extract org/repo, branch if specified
4. Extract org/repo from patterns like "scimarketplace/quote", "org/repo", etc.
5. Extract count from "last 5 commits", "5 commits", etc.
6. Extract branch from "rc1", "main", "develop", etc.
7. Extract commit SHA from 7+ character hex strings
8. Set confidence based on clarity of the query

Examples:
- "get last 5 commits from scimarketplace/quote" → {{"action": "commits", "confidence": 0.9, "extracted_values": {{"org": "scimarketplace", "repo": "quote", "count": 5}}}}
- "show PRs for tusharacc/cli_assist" → {{"action": "pr", "confidence": 0.9, "extracted_values": {{"org": "tusharacc", "repo": "cli_assist"}}}}
- "clone scimarketplace/externaldata" → {{"action": "clone", "confidence": 0.9, "extracted_values": {{"org": "scimarketplace", "repo": "externaldata"}}}}

Return ONLY the JSON response, no other text."""
        
        super().__init__("github", prompt_template, router)

class JenkinsKeywordDetector(IntegrationKeywordDetector):
    """Jenkins-specific keyword detection"""
    
    def __init__(self, router: LLMRouter = None):
        prompt_template = """You are a Jenkins command analyzer. Analyze the user query and extract Jenkins-specific information.

User Query: "{query}"

Return a JSON response with the following structure:
{{
    "action": "builds|failed_jobs|running_jobs|analyze_failure|unknown",
    "confidence": 0.0-1.0,
    "extracted_values": {{
        "folder_path": "scimarketplace/repo/branch",
        "count": number,
        "job_name": "job_name",
        "build_number": number
    }},
    "reasoning": "Brief explanation of the analysis"
}}

Rules:
1. For builds: action="builds", extract folder_path, count (default 5)
2. For failed jobs: action="failed_jobs", extract folder_path
3. For running jobs: action="running_jobs", extract folder_path
4. For failure analysis: action="analyze_failure", extract job_name, build_number
5. Extract folder_path from patterns like "scimarketplace/quote/RC1", "folder quote and sub folder RC1"
6. Convert repo names to "_multi" suffix (quote → quote_multi)
7. Extract count from "last 5 builds", "5 builds", etc.
8. Set confidence based on clarity of the query

Examples:
- "get last 5 builds for scimarketplace and folder quote and sub folder RC1" → {{"action": "builds", "confidence": 0.9, "extracted_values": {{"folder_path": "scimarketplace/quote_multi/RC1", "count": 5}}}}
- "show failed jobs for scimarketplace/deploy-all" → {{"action": "failed_jobs", "confidence": 0.9, "extracted_values": {{"folder_path": "scimarketplace/deploy-all"}}}}
- "analyze failure for job build-123" → {{"action": "analyze_failure", "confidence": 0.9, "extracted_values": {{"job_name": "build-123"}}}}

Return ONLY the JSON response, no other text."""
        
        super().__init__("jenkins", prompt_template, router)

class JiraKeywordDetector(IntegrationKeywordDetector):
    """Jira-specific keyword detection"""
    
    def __init__(self, router: LLMRouter = None):
        prompt_template = """You are a Jira command analyzer. Analyze the user query and extract Jira-specific information.

User Query: "{query}"

Return a JSON response with the following structure:
{{
    "action": "ticket|search|create|update|unknown",
    "confidence": 0.0-1.0,
    "extracted_values": {{
        "ticket_key": "PROJECT-123",
        "query": "search_query",
        "project": "PROJECT",
        "assignee": "username",
        "status": "status_name"
    }},
    "reasoning": "Brief explanation of the analysis"
}}

Rules:
1. For specific ticket: action="ticket", extract ticket_key (PROJECT-123 format)
2. For search: action="search", extract query, project, assignee, status
3. For create: action="create", extract project, assignee, status
4. For update: action="update", extract ticket_key, status
5. Extract ticket_key from patterns like "PROJECT-123", "jira PROJECT-123"
6. Extract project from ticket key or explicit mention
7. Set confidence based on clarity of the query

Examples:
- "show me PROJECT-123" → {{"action": "ticket", "confidence": 0.9, "extracted_values": {{"ticket_key": "PROJECT-123"}}}}
- "search for bugs in PROJECT" → {{"action": "search", "confidence": 0.8, "extracted_values": {{"project": "PROJECT", "query": "bugs"}}}}
- "create ticket in PROJECT" → {{"action": "create", "confidence": 0.7, "extracted_values": {{"project": "PROJECT"}}}}

Return ONLY the JSON response, no other text."""
        
        super().__init__("jira", prompt_template, router)

class AppDynamicsKeywordDetector(IntegrationKeywordDetector):
    """AppDynamics-specific keyword detection"""
    
    def __init__(self, router: LLMRouter = None):
        prompt_template = """You are an AppDynamics command analyzer. Analyze the user query and extract AppDynamics-specific information.

User Query: "{query}"

Return a JSON response with the following structure:
{{
    "action": "resources|applications|health|performance|alerts|unknown",
    "confidence": 0.0-1.0,
    "extracted_values": {{
        "application_name": "app_name",
        "metric_type": "cpu|memory|response_time",
        "time_range": "1h|24h|7d",
        "threshold": number
    }},
    "reasoning": "Brief explanation of the analysis"
}}

Rules:
1. For resources: action="resources", extract metric_type, time_range
2. For applications: action="applications", extract application_name
3. For health: action="health", extract application_name
4. For performance: action="performance", extract application_name, metric_type
5. For alerts: action="alerts", extract application_name, threshold
6. Extract application names from the query
7. Extract metric types from "cpu", "memory", "response time", etc.
8. Set confidence based on clarity of the query

Examples:
- "show resource utilization" → {{"action": "resources", "confidence": 0.9, "extracted_values": {{"metric_type": "cpu"}}}}
- "check health of myapp" → {{"action": "health", "confidence": 0.9, "extracted_values": {{"application_name": "myapp"}}}}
- "performance metrics for myapp" → {{"action": "performance", "confidence": 0.8, "extracted_values": {{"application_name": "myapp"}}}}

Return ONLY the JSON response, no other text."""
        
        super().__init__("appdynamics", prompt_template, router)

class Neo4jKeywordDetector(IntegrationKeywordDetector):
    """Neo4j-specific keyword detection"""
    
    def __init__(self, router: LLMRouter = None):
        prompt_template = """You are a Neo4j command analyzer. Analyze the user query and extract Neo4j-specific information.

User Query: "{query}"

Return a JSON response with the following structure:
{{
    "action": "dependencies|impact|relationships|query|unknown",
    "confidence": 0.0-1.0,
    "extracted_values": {{
        "class_name": "ClassName",
        "method_name": "methodName",
        "query_type": "dependencies|impact|relationships",
        "depth": number
    }},
    "reasoning": "Brief explanation of the analysis"
}}

Rules:
1. For dependencies: action="dependencies", extract class_name, method_name, depth
2. For impact: action="impact", extract class_name, method_name, depth
3. For relationships: action="relationships", extract class_name, method_name
4. For query: action="query", extract class_name, method_name
5. Extract class names (PascalCase) and method names (camelCase/snake_case)
6. Extract depth from "2 levels", "depth 3", etc.
7. Set confidence based on clarity of the query

Examples:
- "dependencies of class UserService" → {{"action": "dependencies", "confidence": 0.9, "extracted_values": {{"class_name": "UserService"}}}}
- "impact analysis for method validateUser" → {{"action": "impact", "confidence": 0.9, "extracted_values": {{"method_name": "validateUser"}}}}
- "relationships for PaymentController" → {{"action": "relationships", "confidence": 0.8, "extracted_values": {{"class_name": "PaymentController"}}}}

Return ONLY the JSON response, no other text."""
        
        super().__init__("neo4j", prompt_template, router)

class UnifiedKeywordDetector:
    """Unified keyword detection system for all integrations"""
    
    def __init__(self, router: LLMRouter = None):
        self.router = router or LLMRouter(backend="ollama")
        self.detectors = {
            'github': GitHubKeywordDetector(router=self.router),
            'jenkins': JenkinsKeywordDetector(router=self.router),
            'jira': JiraKeywordDetector(router=self.router),
            'appdynamics': AppDynamicsKeywordDetector(router=self.router),
            'neo4j': Neo4jKeywordDetector(router=self.router)
        }
    
    def detect_keywords(self, integration: str, query: str) -> KeywordDetectionResult:
        """Detect keywords for a specific integration"""
        if integration not in self.detectors:
            return KeywordDetectionResult(
                action='error',
                confidence=0.0,
                extracted_values={},
                reasoning=f"Unknown integration: {integration}",
                integration=integration
            )
        
        return self.detectors[integration].detect_keywords(query)
    
    def get_supported_integrations(self) -> List[str]:
        """Get list of supported integrations"""
        return list(self.detectors.keys())

# Global instance
keyword_detector = UnifiedKeywordDetector()
