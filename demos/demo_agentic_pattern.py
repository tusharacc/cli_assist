#!/usr/bin/env python3
"""
Demo of Enhanced Agentic Pattern for Lumos CLI
Shows how the multi-agent system would work
"""

import sys
import os
sys.path.append('src')

from lumos_cli.agentic_router import AgenticRouter, AgentType

def demo_agentic_pattern():
    """Demonstrate the enhanced agentic pattern"""
    
    print("🤖 Enhanced Agentic Pattern Demo for Lumos CLI")
    print("=" * 60)
    
    # Initialize the agentic router
    router = AgenticRouter()
    
    # Test queries demonstrating different agent routing
    test_queries = [
        "can you get me the last 5 builds from jenkins for scimarketplace and folder addresssearch and branch RC1",
        "show me resource utilization for SCI Market Place PROD Azure",
        "get me the last 5 commits from scimarketplace/addresssearch",
        "show me ticket ABC-123",
        "what are the dependencies of class UserService from neo4j",
        "analyze the authentication module for security issues",
        "get me the last 5 builds from jenkins, then check the dependencies of the changed classes in neo4j"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 50)
        
        try:
            # Route the query through the agentic system
            response = router.route_query(query)
            
            print(f"🎯 Master Intent Agent → {response.agent_type.value}")
            print(f"📋 Intent: {response.intent}")
            print(f"🎯 Confidence: {response.confidence}")
            print(f"🔧 Parameters: {response.parameters}")
            print(f"💭 Reasoning: {response.reasoning}")
            
            if response.next_agent:
                print(f"➡️  Next Agent: {response.next_agent.value}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Agentic Pattern Benefits:")
    print("1. 🧠 Master Intent Agent: Understands user intent at high level")
    print("2. 🔧 Specialized Agents: Each service has its own expert agent")
    print("3. 🎯 Sub-Agent Routing: Agents can determine specific functionality")
    print("4. 🔄 Workflow Support: Complex multi-service operations")
    print("5. 📊 Confidence Scoring: Each agent provides confidence levels")
    print("6. 💭 Reasoning: Agents explain their decisions")
    print("7. 🔧 Parameter Extraction: Structured data for downstream processing")

def demo_agent_hierarchy():
    """Demonstrate the agent hierarchy"""
    
    print("\n🏗️  Agent Hierarchy:")
    print("=" * 40)
    
    hierarchy = {
        "Master Intent Agent": {
            "purpose": "High-level intent classification",
            "input": "Natural language query",
            "output": "Service routing decision",
            "sub_agents": [
                "GitHub Agent",
                "Jenkins Agent", 
                "Jira Agent",
                "Neo4j Agent",
                "AppDynamics Agent",
                "Code Analysis Agent",
                "Workflow Agent"
            ]
        },
        "GitHub Agent": {
            "purpose": "Git and repository operations",
            "sub_functions": [
                "Pull Request Operations",
                "Commit Analysis", 
                "Repository Management",
                "Branch Operations"
            ]
        },
        "Jenkins Agent": {
            "purpose": "CI/CD and build operations",
            "sub_functions": [
                "Build Status Monitoring",
                "Console Log Analysis",
                "Job Parameter Management",
                "Pipeline Operations"
            ]
        },
        "Jira Agent": {
            "purpose": "Project management and ticketing",
            "sub_functions": [
                "Ticket Operations",
                "Comment Management",
                "Sprint Planning",
                "Issue Tracking"
            ]
        },
        "Neo4j Agent": {
            "purpose": "Graph database and dependency analysis",
            "sub_functions": [
                "Dependency Analysis",
                "Impact Assessment",
                "Graph Queries",
                "Relationship Mapping"
            ]
        },
        "AppDynamics Agent": {
            "purpose": "Application performance monitoring",
            "sub_functions": [
                "Resource Utilization",
                "Alert Management",
                "Transaction Monitoring",
                "Health Assessment"
            ]
        }
    }
    
    for agent, details in hierarchy.items():
        print(f"\n🤖 {agent}")
        print(f"   Purpose: {details['purpose']}")
        if 'sub_agents' in details:
            print(f"   Sub-agents: {', '.join(details['sub_agents'])}")
        if 'sub_functions' in details:
            print(f"   Functions: {', '.join(details['sub_functions'])}")

if __name__ == "__main__":
    demo_agentic_pattern()
    demo_agent_hierarchy()
