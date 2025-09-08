"""
Enhanced Agentic Router for Lumos CLI
Implements a multi-agent system with specialized agents for each service
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import re

from .client import LLMRouter, TaskType
from .debug_logger import debug_logger

class AgentType(Enum):
    """Types of specialized agents"""
    MASTER_INTENT = "master_intent"
    GITHUB = "github"
    JENKINS = "jenkins"
    JIRA = "jira"
    NEO4J = "neo4j"
    APPDYNAMICS = "appdynamics"
    CODE_ANALYSIS = "code_analysis"
    WORKFLOW = "workflow"

@dataclass
class AgentResponse:
    """Standardized response from any agent"""
    agent_type: AgentType
    intent: str
    confidence: float
    parameters: Dict[str, Any]
    next_agent: Optional[AgentType] = None
    reasoning: str = ""

class MasterIntentAgent:
    """Master agent that determines intent and routes to specialized agents"""
    
    def __init__(self):
        self.llm_router = LLMRouter()
        self.service_agents = {
            AgentType.GITHUB: GitHubAgent(),
            AgentType.JENKINS: JenkinsAgent(),
            AgentType.JIRA: JiraAgent(),
            AgentType.NEO4J: Neo4jAgent(),
            AgentType.APPDYNAMICS: AppDynamicsAgent(),
            AgentType.CODE_ANALYSIS: CodeAnalysisAgent(),
            AgentType.WORKFLOW: WorkflowAgent()
        }
    
    def process_query(self, user_input: str) -> AgentResponse:
        """Process user query and determine routing"""
        debug_logger.log_function_call("MasterIntentAgent.process_query", {"user_input": user_input})
        
        # First, detect the primary intent
        intent_result = self._detect_intent(user_input)
        
        # Route to appropriate service agent
        if intent_result.agent_type in self.service_agents:
            service_agent = self.service_agents[intent_result.agent_type]
            return service_agent.process_query(user_input, intent_result)
        
        # Default to workflow agent for complex queries
        return self.service_agents[AgentType.WORKFLOW].process_query(user_input, intent_result)
    
    def _detect_intent(self, user_input: str) -> AgentResponse:
        """Detect primary intent using LLM"""
        prompt = f"""
You are a master intent detection agent. Analyze the user query and determine the primary service intent.

User Query: "{user_input}"

Available Services:
1. **github** - Git operations, repositories, PRs, commits
2. **jenkins** - Build status, job parameters, console logs, CI/CD
3. **jira** - Tickets, issues, project management
4. **neo4j** - Graph database, dependencies, impact analysis
5. **appdynamics** - Application monitoring, resources, alerts
6. **code_analysis** - Code review, analysis, debugging
7. **workflow** - Multi-service operations, complex workflows

Return ONLY a JSON object:
{{
    "agent_type": "service_name",
    "intent": "specific_functionality",
    "confidence": 0.95,
    "parameters": {{"key": "value"}},
    "reasoning": "why this service was chosen"
}}
"""
        
        try:
            response = self.llm_router.generate_response(
                messages=[{"role": "user", "content": prompt}],
                task_type=TaskType.PLANNING
            )
            
            result = json.loads(response)
            return AgentResponse(
                agent_type=AgentType(result["agent_type"]),
                intent=result["intent"],
                confidence=result["confidence"],
                parameters=result["parameters"],
                reasoning=result["reasoning"]
            )
        except Exception as e:
            debug_logger.warning(f"Intent detection failed: {e}")
            # Fallback to regex-based detection
            return self._fallback_intent_detection(user_input)
    
    def _fallback_intent_detection(self, user_input: str) -> AgentResponse:
        """Fallback intent detection using regex patterns"""
        lower_input = user_input.lower()
        
        # Simple keyword-based detection
        if any(word in lower_input for word in ["github", "git", "pr", "pull request", "commit", "repository"]):
            return AgentResponse(AgentType.GITHUB, "git_operations", 0.8, {})
        elif any(word in lower_input for word in ["jenkins", "build", "job", "ci", "cd"]):
            return AgentResponse(AgentType.JENKINS, "build_operations", 0.8, {})
        elif any(word in lower_input for word in ["jira", "ticket", "issue", "sprint"]):
            return AgentResponse(AgentType.JIRA, "ticket_operations", 0.8, {})
        elif any(word in lower_input for word in ["neo4j", "graph", "dependencies", "impact"]):
            return AgentResponse(AgentType.NEO4J, "graph_operations", 0.8, {})
        elif any(word in lower_input for word in ["appdynamics", "appd", "monitoring", "resources", "alerts"]):
            return AgentResponse(AgentType.APPDYNAMICS, "monitoring_operations", 0.8, {})
        else:
            return AgentResponse(AgentType.WORKFLOW, "general_query", 0.5, {})

class GitHubAgent:
    """Specialized agent for GitHub operations"""
    
    def process_query(self, user_input: str, intent_result: AgentResponse) -> AgentResponse:
        """Process GitHub-specific queries"""
        debug_logger.log_function_call("GitHubAgent.process_query", {"user_input": user_input})
        
        # Determine specific GitHub functionality
        functionality = self._determine_functionality(user_input)
        
        return AgentResponse(
            agent_type=AgentType.GITHUB,
            intent=functionality["intent"],
            confidence=functionality["confidence"],
            parameters=functionality["parameters"],
            reasoning=f"GitHub agent determined: {functionality['intent']}"
        )
    
    def _determine_functionality(self, user_input: str) -> Dict[str, Any]:
        """Determine specific GitHub functionality needed"""
        lower_input = user_input.lower()
        
        if "pr" in lower_input or "pull request" in lower_input:
            return {
                "intent": "pull_request_operations",
                "confidence": 0.9,
                "parameters": {"operation": "list_prs", "query": user_input}
            }
        elif "commit" in lower_input:
            return {
                "intent": "commit_operations", 
                "confidence": 0.9,
                "parameters": {"operation": "list_commits", "query": user_input}
            }
        elif "clone" in lower_input:
            return {
                "intent": "repository_operations",
                "confidence": 0.9,
                "parameters": {"operation": "clone_repo", "query": user_input}
            }
        else:
            return {
                "intent": "general_github",
                "confidence": 0.7,
                "parameters": {"operation": "general", "query": user_input}
            }

class JenkinsAgent:
    """Specialized agent for Jenkins operations"""
    
    def process_query(self, user_input: str, intent_result: AgentResponse) -> AgentResponse:
        """Process Jenkins-specific queries"""
        debug_logger.log_function_call("JenkinsAgent.process_query", {"user_input": user_input})
        
        functionality = self._determine_functionality(user_input)
        
        return AgentResponse(
            agent_type=AgentType.JENKINS,
            intent=functionality["intent"],
            confidence=functionality["confidence"],
            parameters=functionality["parameters"],
            reasoning=f"Jenkins agent determined: {functionality['intent']}"
        )
    
    def _determine_functionality(self, user_input: str) -> Dict[str, Any]:
        """Determine specific Jenkins functionality needed"""
        lower_input = user_input.lower()
        
        if "build status" in lower_input or "builds" in lower_input:
            return {
                "intent": "build_status",
                "confidence": 0.9,
                "parameters": {"operation": "get_build_status", "query": user_input}
            }
        elif "console" in lower_input or "log" in lower_input:
            return {
                "intent": "console_analysis",
                "confidence": 0.9,
                "parameters": {"operation": "analyze_console", "query": user_input}
            }
        elif "parameters" in lower_input:
            return {
                "intent": "build_parameters",
                "confidence": 0.9,
                "parameters": {"operation": "get_parameters", "query": user_input}
            }
        else:
            return {
                "intent": "general_jenkins",
                "confidence": 0.7,
                "parameters": {"operation": "general", "query": user_input}
            }

class JiraAgent:
    """Specialized agent for Jira operations"""
    
    def process_query(self, user_input: str, intent_result: AgentResponse) -> AgentResponse:
        """Process Jira-specific queries"""
        functionality = self._determine_functionality(user_input)
        
        return AgentResponse(
            agent_type=AgentType.JIRA,
            intent=functionality["intent"],
            confidence=functionality["confidence"],
            parameters=functionality["parameters"],
            reasoning=f"Jira agent determined: {functionality['intent']}"
        )
    
    def _determine_functionality(self, user_input: str) -> Dict[str, Any]:
        """Determine specific Jira functionality needed"""
        lower_input = user_input.lower()
        
        if "comment" in lower_input:
            return {
                "intent": "comment_operations",
                "confidence": 0.9,
                "parameters": {"operation": "get_comments", "query": user_input}
            }
        elif re.search(r'[A-Z]+-\d+', user_input):
            return {
                "intent": "ticket_operations",
                "confidence": 0.9,
                "parameters": {"operation": "get_ticket", "query": user_input}
            }
        else:
            return {
                "intent": "general_jira",
                "confidence": 0.7,
                "parameters": {"operation": "general", "query": user_input}
            }

class Neo4jAgent:
    """Specialized agent for Neo4j operations"""
    
    def process_query(self, user_input: str, intent_result: AgentResponse) -> AgentResponse:
        """Process Neo4j-specific queries"""
        functionality = self._determine_functionality(user_input)
        
        return AgentResponse(
            agent_type=AgentType.NEO4J,
            intent=functionality["intent"],
            confidence=functionality["confidence"],
            parameters=functionality["parameters"],
            reasoning=f"Neo4j agent determined: {functionality['intent']}"
        )
    
    def _determine_functionality(self, user_input: str) -> Dict[str, Any]:
        """Determine specific Neo4j functionality needed"""
        lower_input = user_input.lower()
        
        if "dependencies" in lower_input:
            return {
                "intent": "dependency_analysis",
                "confidence": 0.9,
                "parameters": {"operation": "find_dependencies", "query": user_input}
            }
        elif "impact" in lower_input:
            return {
                "intent": "impact_analysis",
                "confidence": 0.9,
                "parameters": {"operation": "find_impact", "query": user_input}
            }
        else:
            return {
                "intent": "general_neo4j",
                "confidence": 0.7,
                "parameters": {"operation": "general", "query": user_input}
            }

class AppDynamicsAgent:
    """Specialized agent for AppDynamics operations"""
    
    def process_query(self, user_input: str, intent_result: AgentResponse) -> AgentResponse:
        """Process AppDynamics-specific queries"""
        functionality = self._determine_functionality(user_input)
        
        return AgentResponse(
            agent_type=AgentType.APPDYNAMICS,
            intent=functionality["intent"],
            confidence=functionality["confidence"],
            parameters=functionality["parameters"],
            reasoning=f"AppDynamics agent determined: {functionality['intent']}"
        )
    
    def _determine_functionality(self, user_input: str) -> Dict[str, Any]:
        """Determine specific AppDynamics functionality needed"""
        lower_input = user_input.lower()
        
        if "resource" in lower_input and "utilization" in lower_input:
            return {
                "intent": "resource_monitoring",
                "confidence": 0.9,
                "parameters": {"operation": "get_resource_utilization", "query": user_input}
            }
        elif "alert" in lower_input:
            return {
                "intent": "alert_management",
                "confidence": 0.9,
                "parameters": {"operation": "get_alerts", "query": user_input}
            }
        elif "transaction" in lower_input:
            return {
                "intent": "transaction_monitoring",
                "confidence": 0.9,
                "parameters": {"operation": "get_transactions", "query": user_input}
            }
        else:
            return {
                "intent": "general_appdynamics",
                "confidence": 0.7,
                "parameters": {"operation": "general", "query": user_input}
            }

class CodeAnalysisAgent:
    """Specialized agent for code analysis operations"""
    
    def process_query(self, user_input: str, intent_result: AgentResponse) -> AgentResponse:
        """Process code analysis queries"""
        functionality = self._determine_functionality(user_input)
        
        return AgentResponse(
            agent_type=AgentType.CODE_ANALYSIS,
            intent=functionality["intent"],
            confidence=functionality["confidence"],
            parameters=functionality["parameters"],
            reasoning=f"Code analysis agent determined: {functionality['intent']}"
        )
    
    def _determine_functionality(self, user_input: str) -> Dict[str, Any]:
        """Determine specific code analysis functionality needed"""
        lower_input = user_input.lower()
        
        if "review" in lower_input:
            return {
                "intent": "code_review",
                "confidence": 0.9,
                "parameters": {"operation": "review_code", "query": user_input}
            }
        elif "debug" in lower_input or "fix" in lower_input:
            return {
                "intent": "debugging",
                "confidence": 0.9,
                "parameters": {"operation": "debug_code", "query": user_input}
            }
        else:
            return {
                "intent": "general_analysis",
                "confidence": 0.7,
                "parameters": {"operation": "general", "query": user_input}
            }

class WorkflowAgent:
    """Specialized agent for complex multi-service workflows"""
    
    def process_query(self, user_input: str, intent_result: AgentResponse) -> AgentResponse:
        """Process complex workflow queries"""
        functionality = self._determine_functionality(user_input)
        
        return AgentResponse(
            agent_type=AgentType.WORKFLOW,
            intent=functionality["intent"],
            confidence=functionality["confidence"],
            parameters=functionality["parameters"],
            reasoning=f"Workflow agent determined: {functionality['intent']}"
        )
    
    def _determine_functionality(self, user_input: str) -> Dict[str, Any]:
        """Determine specific workflow functionality needed"""
        return {
            "intent": "multi_service_workflow",
            "confidence": 0.8,
            "parameters": {"operation": "orchestrate", "query": user_input}
        }

# Main router class
class AgenticRouter:
    """Main router that orchestrates all agents"""
    
    def __init__(self):
        self.master_agent = MasterIntentAgent()
    
    def route_query(self, user_input: str) -> AgentResponse:
        """Route user query through the agentic system"""
        debug_logger.log_function_call("AgenticRouter.route_query", {"user_input": user_input})
        
        # Process through master intent agent
        response = self.master_agent.process_query(user_input)
        
        debug_logger.log_function_return("AgenticRouter.route_query", f"Routed to {response.agent_type.value}: {response.intent}")
        return response
