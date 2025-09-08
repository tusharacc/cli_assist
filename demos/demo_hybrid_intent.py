#!/usr/bin/env python3
"""
Demo of Hybrid Intent Pattern for Lumos CLI
Shows both explicit intent prefixes and natural language detection
"""

import sys
import os
sys.path.append('src')

def demo_hybrid_intent():
    """Demonstrate the hybrid intent pattern"""
    
    print("🎯 Hybrid Intent Pattern Demo for Lumos CLI")
    print("=" * 60)
    
    # Test queries showing both approaches
    test_queries = [
        # Explicit Intent Prefixes
        "/github get me the latest PR from scimarketplace/externaldata",
        "/jenkins get me the last 5 builds from folder deploy-all",
        "/jira show me ticket ABC-123",
        "/neo4j what are the dependencies of class UserService",
        "/appdynamics show me resource utilization for SCI Market Place PROD",
        
        # Natural Language (existing approach)
        "get me the latest PR from scimarketplace/externaldata",
        "get me the last 5 builds from jenkins folder deploy-all",
        "show me ticket ABC-123",
        "what are the dependencies of class UserService from neo4j",
        "show me resource utilization for SCI Market Place PROD Azure",
        
        # Mixed approaches
        "/github check if there are any open PRs in branch RC1",
        "/jenkins analyze why build number 20 failed",
        "/jira get comments for ticket PROJ-456",
        "/neo4j find impact analysis for method validateUser",
        "/appdynamics get me critical alerts from last hour"
    ]
    
    print("\n🔍 Query Analysis:")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i:2d}. {query}")
        
        # Determine the approach
        if query.startswith('/'):
            prefix = query.split()[0]
            intent = prefix[1:]  # Remove the '/'
            remaining_query = query[len(prefix):].strip()
            
            print(f"    🎯 Approach: Explicit Intent Prefix")
            print(f"    📋 Intent: {intent}")
            print(f"    🔧 Query: {remaining_query}")
            print(f"    ⚡ Processing: Direct routing to {intent} agent")
            
        else:
            print(f"    🎯 Approach: Natural Language Detection")
            print(f"    🔍 Processing: Intent detection → Service routing")
            print(f"    🤖 Method: LLM + Regex fallback")
    
    print("\n" + "=" * 60)
    print("🎯 Benefits of Hybrid Approach:")
    print("=" * 60)
    
    benefits = [
        ("⚡ Speed", "Explicit prefixes bypass intent detection for faster routing"),
        ("🎯 Precision", "No ambiguity about which service to use"),
        ("🔧 Control", "Users have explicit control over service selection"),
        ("🤖 Intelligence", "Natural language still works for complex queries"),
        ("📚 Learning", "Users can learn patterns from explicit examples"),
        ("🔄 Flexibility", "Can mix both approaches in same session"),
        ("🚀 Performance", "Reduces LLM calls for simple operations"),
        ("💡 Discoverability", "Help shows all available prefixes")
    ]
    
    for benefit, description in benefits:
        print(f"\n{benefit}")
        print(f"   {description}")
    
    print("\n" + "=" * 60)
    print("🔧 Usage Examples:")
    print("=" * 60)
    
    examples = [
        ("Quick GitHub PR check", "/github get latest PR from scimarketplace/externaldata"),
        ("Jenkins build status", "/jenkins get last 5 builds from folder deploy-all"),
        ("Jira ticket details", "/jira show me ticket ABC-123"),
        ("Neo4j dependency analysis", "/neo4j dependencies of class UserService"),
        ("AppDynamics monitoring", "/appdynamics resource utilization for SCI Market Place"),
        ("Complex natural language", "get me the last 5 builds from jenkins, then check dependencies of changed classes in neo4j"),
        ("Mixed approach", "/github get PR details, then /neo4j check impact of changed classes")
    ]
    
    for use_case, example in examples:
        print(f"\n📋 {use_case}:")
        print(f"   {example}")
    
    print("\n" + "=" * 60)
    print("🏗️  Implementation Architecture:")
    print("=" * 60)
    
    architecture = """
    User Input
        │
        ├─ /github <query> ──→ GitHub Agent (Direct)
        ├─ /jenkins <query> ──→ Jenkins Agent (Direct)  
        ├─ /jira <query> ──→ Jira Agent (Direct)
        ├─ /neo4j <query> ──→ Neo4j Agent (Direct)
        ├─ /appdynamics <query> ──→ AppDynamics Agent (Direct)
        │
        └─ Natural Language ──→ Intent Detection Agent ──→ Service Agent
                                    │
                                    ├─ LLM Analysis
                                    └─ Regex Fallback
    """
    
    print(architecture)
    
    print("\n🎯 This hybrid approach gives users the best of both worlds:")
    print("   • Fast, explicit control when they know what they want")
    print("   • Intelligent, natural language understanding for complex queries")
    print("   • Learning path from explicit to natural language")
    print("   • Reduced ambiguity and faster processing")

if __name__ == "__main__":
    demo_hybrid_intent()
