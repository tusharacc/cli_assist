#!/usr/bin/env python3
"""
Advanced intent detection using LLM with fallback to regex patterns
"""

import re
import json
from typing import Dict, List, Optional
from .client import LLMRouter
from .debug_logger import debug_logger

class IntentDetector:
    """Advanced intent detection using LLM with regex fallback"""
    
    def __init__(self):
        self.llm_router = LLMRouter()
        self.regex_patterns = self._load_regex_patterns()
        
    def _load_regex_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for fast fallback detection"""
        return {
            'github': [
                r'(github|git hub)\s+(.+)',
                r'(clone|pull|fetch)\s+(.+)',
                r'(pr|pull request|pullrequest)\s+(.+)',
                r'(repository|repo)\s+(.+)',
                r'(branch|commit|push|merge)\s+(.+)',
                r'(tusharacc|microsoft|github\.com)\s+(.+)',
                r'(.+)/(.+)\s+(pr|pull request|clone|branch)',
                r'(check|show|list|get)\s+(pr|pull request|repository|repo)\s+(.+)',
                r'(is there|are there|any)\s+(pr|pull request)\s+(.+)',
                r'(latest|recent)\s+(commit|pr|pull request)\s+(.+)',
                r'(give me|get me|show me)\s+(\d+)\s+(latest|last|recent)\s+commits\s+(.+)',
                r'(give me|get me|show me)\s+(latest|last|recent)\s+commits\s+(.+)',
                r'(latest|last|recent)\s+commits?\s+(.+)',
                r'(.+)/(.+)\s+(commits?|commit)',
                r'(commits?)\s+(.+)',
                r'(from|in)\s+(.+/.*)\s+(commits?|commit)',
                r'(scimarketplace)\s+(pr|pull request|repository|repo|commits?)\s+(.+)'
            ],
            'jira': [
                r'\b([A-Z]+-\d+)\b',
                r'(jira|ticket|sprint|issue|board|project)\s+(.+)',
                r'(show|get|find|search)\s+(ticket|issue|jira)\s+(.+)'
            ],
            'jenkins': [
                r'(jenkins|build|ci|cd|pipeline)\s+(.+)',
                r'(failed|running|builds?|jobs?)\s+(.+)',
                r'(last|recent|latest)\s+(\d+)?\s*(builds?|jobs?)\s+(.+)',
                r'(get|show|fetch|can you get)\s+(me\s+)?(the\s+)?(last|recent|latest)\s+(\d+)?\s*(builds?|jobs?)\s+(.+)',
                r'(builds?|jobs?)\s+(from|for)\s+(jenkins|scimarketplace)\s+(.+)',
                r'(jenkins|scimarketplace)\s+(folder|builds?|jobs?)\s+(.+)',
                r'(deploy-all|scimarketplace)\s+(.+)',
                r'(build|job)\s+(status|parameters?|console)\s+(.+)',
                r'(folder|folder)\s+(.+)',
                r'(rc1|rc2|rc3|rc4)\s+(.+)',
                r'(.+)_multi\s+(.+)',
                r'(addresssearch|externaldata|quote|billing)\s+(.+)',
                r'(scimarketplace)\s+(folder|builds?|jobs?)\s+(addresssearch|externaldata|quote|billing)\s+(.+)'
            ],
            'neo4j': [
                r'(graph|neo4j|database|impact|dependencies?)\s+(.+)',
                r'(which|what)\s+(repositories?|classes?|functions?)\s+(.+)',
                r'(impact|affected|dependencies?)\s+(.+)',
                r'(query|search)\s+(graph|neo4j)\s+(.+)',
                r'(identify|find|show|get)\s+(dependencies?|impact|affected)\s+(of|for)\s+(class|method|function)\s+(.+)',
                r'(dependencies?|impact|affected)\s+(of|for)\s+(class|method|function)\s+(.+)\s+(from|in)\s+(neo4j|graph)',
                r'(class|method|function)\s+(.+)\s+(dependencies?|impact|affected)',
                r'(can you|please)\s+(identify|find|show|get)\s+(dependencies?|impact)\s+(.+)',
                r'(dependencies?|impact)\s+(of|for)\s+(.+)',
                r'(which|what)\s+(classes?|methods?|functions?)\s+(depend|call|use)\s+(.+)',
                r'(analyze|check)\s+(dependencies?|impact)\s+(.+)',
                r'(graph|neo4j)\s+(query|search|analysis)\s+(.+)',
                r'(relationship|connections?)\s+(between|of)\s+(.+)',
                r'(upstream|downstream)\s+(dependencies?|impact)\s+(.+)'
            ],
            'appdynamics': [
                r'(appdynamics|app dynamics|appd)\s+(.+)',
                r'(resource|resources)\s+(utilization|usage|monitoring)\s+(.+)',
                r'(show|get|display)\s+(me\s+)?(resource|resources)\s+(utilization|usage)\s+(.+)',
                r'(server|servers)\s+(resource|resources|utilization|usage)\s+(.+)',
                r'(business\s+)?(transaction|transactions)\s+(.+)',
                r'(alert|alerts|alarming)\s+(.+)',
                r'(health|status|monitoring)\s+(.+)',
                r'(cpu|memory|disk|network)\s+(usage|utilization|monitoring)\s+(.+)',
                r'(performance|metrics|monitoring)\s+(.+)',
                r'(sci\s+market\s+place|sci\s+markpet\s+place)\s+(.+)',
                r'(production|prod|staging|uat)\s+(.+)',
                r'(critical|warning|error)\s+(alert|alerts)\s+(.+)',
                r'(slow|fast|response\s+time)\s+(transaction|transactions)\s+(.+)',
                r'(web-server|app-server|database-server)\s+(.+)',
                r'(payment|user|order|inventory)\s+(service|services)\s+(.+)',
                r'(show|get|display)\s+(me\s+)?(the\s+)?(last|recent|latest)\s+(\d+)?\s*(alert|alerts)\s+(.+)',
                r'(show|get|display)\s+(me\s+)?(the\s+)?(last|recent|latest)\s+(\d+)?\s*(transaction|transactions)\s+(.+)',
                r'(show|get|display)\s+(me\s+)?(the\s+)?(last|recent|latest)\s+(\d+)?\s*(server|servers)\s+(.+)',
                r'(monitor|monitoring|watch)\s+(.+)',
                r'(dashboard|overview|summary)\s+(.+)'
            ],
            'code': [
                r'(code|coding|programming|development)\s+(.+)',
                r'(generate|create|write|build)\s+(code|function|class|module|script)\s+(.+)',
                r'(edit|modify|update|change)\s+(code|file|function|class)\s+(.+)',
                r'(test|testing|unit test|integration test)\s+(.+)',
                r'(refactor|refactoring|improve|optimize)\s+(code|function|class)\s+(.+)',
                r'(analyze|analysis|review|inspect)\s+(code|file|function|class)\s+(.+)',
                r'(documentation|docs|document)\s+(.+)',
                r'(format|lint|style|clean)\s+(code|file)\s+(.+)',
                r'(validate|check|verify)\s+(code|syntax|style)\s+(.+)',
                r'(debug|fix|error|bug)\s+(code|function|class)\s+(.+)',
                r'(implement|add|remove)\s+(feature|function|method|class)\s+(.+)',
                r'(python|javascript|typescript|go|java|cpp)\s+(code|function|class|script)\s+(.+)',
                r'(api|endpoint|service|microservice)\s+(.+)',
                r'(database|db|sql|query)\s+(.+)',
                r'(frontend|backend|fullstack|web|mobile)\s+(.+)',
                r'(algorithm|data structure|pattern|design)\s+(.+)',
                r'(security|performance|optimization|scalability)\s+(.+)',
                r'(framework|library|package|dependency)\s+(.+)',
                r'(deployment|devops|ci|cd|pipeline)\s+(.+)',
                r'(architecture|design|pattern|principle)\s+(.+)'
            ],
            'edit': [
                r'^(edit|modify|update|change|fix)\s+(.+)',
                r'^add\s+(.+)\s+to\s+(.+)',
                r'^(.+)\s+(add|implement|improve)\s+(.+)'
            ],
            'review': [
                r'^(review|check|analyze|examine)\s+(.+)',
                r'^(code review|review code)\s+(.+)'
            ],
            'plan': [
                r'^(plan|design|architecture)\s+(.+)',
                r'^(create|build|develop)\s+(.+)'
            ]
        }
    
    def detect_intent(self, user_input: str) -> Dict:
        """Detect intent using LLM with regex fallback"""
        debug_logger.log_function_call("IntentDetector.detect_intent", kwargs={"user_input": user_input})
        
        # First try regex patterns for fast detection
        regex_result = self._detect_with_regex(user_input)
        if regex_result and regex_result.get('confidence', 0) > 0.8:
            debug_logger.log_function_return("IntentDetector.detect_intent", f"Regex detected: {regex_result['type']}")
            return regex_result
        
        # Use LLM for complex intent detection
        llm_result = self._detect_with_llm(user_input)
        if llm_result:
            debug_logger.log_function_return("IntentDetector.detect_intent", f"LLM detected: {llm_result['type']}")
            return llm_result
        
        # Fallback to regex with lower confidence
        if regex_result:
            debug_logger.log_function_return("IntentDetector.detect_intent", f"Regex fallback: {regex_result['type']}")
            return regex_result
        
        # Default to chat
        result = {
            'type': 'chat',
            'query': user_input,
            'confidence': 0.5,
            'method': 'default'
        }
        debug_logger.log_function_return("IntentDetector.detect_intent", f"Default: {result['type']}")
        return result
    
    def _detect_with_regex(self, user_input: str) -> Optional[Dict]:
        """Detect intent using regex patterns"""
        lower_input = user_input.lower()
        
        # Check Jenkins first (highest priority for build-related queries)
        if 'jenkins' in lower_input or 'builds' in lower_input or 'jobs' in lower_input:
            for pattern in self.regex_patterns.get('jenkins', []):
                match = re.search(pattern, lower_input)
                if match:
                    return {
                        'type': 'jenkins',
                        'query': user_input,
                        'confidence': 0.9,
                        'method': 'regex',
                        'match': match.groups()
                    }
        
        # Check other intents
        for intent_type, patterns in self.regex_patterns.items():
            if intent_type == 'jenkins':  # Skip Jenkins as it's already checked
                continue
            for pattern in patterns:
                match = re.search(pattern, lower_input)
                if match:
                    confidence = 0.9 if intent_type in ['github', 'jira'] else 0.7
                    return {
                        'type': intent_type,
                        'query': user_input,
                        'confidence': confidence,
                        'method': 'regex',
                        'match': match.groups()
                    }
        return None
    
    def _detect_with_llm(self, user_input: str) -> Optional[Dict]:
        """Detect intent using LLM for complex queries"""
        try:
            prompt = f"""
You are an intelligent intent detector for a developer CLI tool. Analyze this user query and determine the most likely intent.

User Query: "{user_input}"

Available intents:
1. **github** - GitHub operations (commits, PRs, cloning, repository management)
2. **jira** - Jira ticket operations (view tickets, sprints, issues)
3. **jenkins** - Jenkins CI/CD operations (build status, failed jobs, running jobs, build parameters)
4. **neo4j** - Graph database queries (impact analysis, dependencies, relationships)
5. **appdynamics** - AppDynamics monitoring (resource utilization, alerts, business transactions, health)
6. **code** - Code operations (generate, edit, test, analyze, refactor, docs, format, validate)
7. **edit** - Code editing operations (modify files, add features)
8. **review** - Code review operations (analyze code, check quality)
9. **plan** - Planning operations (design, architecture, project planning)
10. **chat** - General conversation or unclear intent

Consider these scenarios:
- "Get 5 commits from repo X" → github
- "Show me ticket ABC-123" → jira  
- "Get me the last 5 build status from jenkins in folder deploy-all" → jenkins
- "Can you get me the last 5 builds from jenkins for scimarketplace and folder addresssearch and branch RC1" → jenkins
- "Show me builds from jenkins for scimarketplace" → jenkins
- "What repositories are affected by changes to class Y?" → neo4j
- "Can you identify the dependencies of class CreateCyberRiskReportResponse from neo4j" → neo4j
- "Find impact analysis for method ValidateUser" → neo4j
- "Which classes depend on UserService" → neo4j
- "Show dependencies for PaymentController" → neo4j
- "Show me resource utilization for SCI Market Place PROD Azure" → appdynamics
- "What are the critical alerts in the last hour?" → appdynamics
- "Show me slow transactions for PaymentService" → appdynamics
- "Get me server resources for web-server-01" → appdynamics
- "Generate a REST API endpoint for user management" → code
- "Create unit tests for the authentication module" → code
- "Refactor the payment processing code for better performance" → code
- "Analyze the code complexity of the main application" → code
- "Generate documentation for the API endpoints" → code
- "Edit the login function to add validation" → edit
- "Review the authentication module" → review
- "Plan the microservices architecture" → plan
- "Hello, how are you?" → chat

Return ONLY a JSON object with this exact format:
{{
    "type": "intent_name",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this intent was chosen",
    "extracted_entities": {{
        "repositories": ["repo1", "repo2"],
        "tickets": ["ABC-123", "DEF-456"],
        "classes": ["ClassName1", "ClassName2"],
        "numbers": [5, 10]
    }}
}}

Rules:
- Choose the most specific intent that matches the query
- Confidence should be 0.0 to 1.0
- Extract relevant entities for context
- If unclear, choose 'chat' with lower confidence
- Return only the JSON, no other text
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_router.chat(messages)
            
            if response:
                # Clean response - remove backticks, markdown, and extract JSON
                cleaned_response = response.strip()
                
                # Remove markdown code blocks
                if '```json' in cleaned_response:
                    cleaned_response = cleaned_response.split('```json')[1].split('```')[0].strip()
                elif '```' in cleaned_response:
                    cleaned_response = cleaned_response.split('```')[1].split('```')[0].strip()
                
                # Remove any remaining backticks
                cleaned_response = cleaned_response.replace('`', '').strip()
                
                # Parse JSON response
                try:
                    result = json.loads(cleaned_response)
                    result['method'] = 'llm'
                    result['query'] = user_input
                    return result
                except json.JSONDecodeError:
                    debug_logger.warning(f"Failed to parse LLM intent response: {cleaned_response}")
                    return None
                    
        except Exception as e:
            debug_logger.warning(f"LLM intent detection failed: {e}")
            return None
        
        return None
    
    def detect_workflow_intent(self, user_input: str) -> Dict:
        """Detect complex workflow intents that span multiple systems"""
        debug_logger.log_function_call("IntentDetector.detect_workflow_intent", kwargs={"user_input": user_input})
        
        # Check for multi-step workflows
        workflow_patterns = [
            r'(get|show|fetch).*(commits?|prs?|pull requests?).*jira.*ticket',
            r'(analyze|check).*(impact|dependencies?).*(graph|neo4j)',
            r'(jira|ticket).*(description|details).*(graph|neo4j|impact)',
            r'(commits?|prs?).*(changed|modified).*(classes?|methods?).*(graph|neo4j)'
        ]
        
        lower_input = user_input.lower()
        for pattern in workflow_patterns:
            if re.search(pattern, lower_input):
                result = {
                    'type': 'workflow',
                    'query': user_input,
                    'confidence': 0.9,
                    'method': 'workflow_pattern',
                    'workflow_type': 'multi_system',
                    'systems': self._extract_systems(user_input)
                }
                debug_logger.log_function_return("IntentDetector.detect_workflow_intent", f"Workflow detected: {result['systems']}")
                return result
        
        # Fall back to regular intent detection
        return self.detect_intent(user_input)
    
    def _extract_systems(self, user_input: str) -> List[str]:
        """Extract which systems are involved in the workflow"""
        systems = []
        lower_input = user_input.lower()
        
        if any(keyword in lower_input for keyword in ['github', 'commit', 'pr', 'pull request', 'repository']):
            systems.append('github')
        if any(keyword in lower_input for keyword in ['jira', 'ticket', 'sprint', 'issue']):
            systems.append('jira')
        if any(keyword in lower_input for keyword in ['neo4j', 'graph', 'database', 'impact', 'dependencies']):
            systems.append('neo4j')
        
        return systems
