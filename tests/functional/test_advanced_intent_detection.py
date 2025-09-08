#!/usr/bin/env python3
"""
Test advanced LLM-based intent detection
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_advanced_intent_detection():
    """Test the new LLM-based intent detection system"""
    print("🧠 Testing Advanced LLM-Based Intent Detection")
    print("=" * 60)
    
    try:
        from lumos_cli.intent_detector import IntentDetector
        
        detector = IntentDetector()
        
        # Test complex queries that would be difficult with regex
        test_queries = [
            # Simple GitHub queries
            "get me 5 latest commits from microsoft/vscode",
            "show me pull requests for scimarketplace/externaldata",
            
            # Complex multi-system workflows
            "get me the 5 latest commits from scimarketplace/quoteapp and show me the Jira tickets in them",
            "analyze the impact of changes in microsoft/vscode using the graph database",
            "get commits from github, extract Jira tickets, and check which repositories are affected",
            "show me PRs from github, get Jira descriptions, and analyze dependencies in Neo4j",
            
            # Jira queries
            "show me ticket ABC-123 details",
            "get description for Jira ticket DEF-456",
            
            # Neo4j queries
            "which repositories are affected by changes to class UserService?",
            "what functions depend on the authentication module?",
            "analyze the impact of modifying the database layer",
            
            # Edit queries
            "edit the login function to add validation",
            "modify the UserService class to include error handling",
            
            # Review queries
            "review the authentication module for security issues",
            "check the database connection code for potential problems",
            
            # Plan queries
            "plan the microservices architecture for the new project",
            "design the API structure for the user management system"
        ]
        
        for query in test_queries:
            print(f"\n📝 Query: '{query}'")
            print("-" * 50)
            
            # Test regular intent detection
            result = detector.detect_intent(query)
            print(f"   Type: {result['type']}")
            print(f"   Confidence: {result.get('confidence', 0.0):.2f}")
            print(f"   Method: {result.get('method', 'unknown')}")
            
            if 'reasoning' in result:
                print(f"   Reasoning: {result['reasoning']}")
            
            if 'extracted_entities' in result:
                entities = result['extracted_entities']
                if entities:
                    print(f"   Entities: {entities}")
            
            # Test workflow detection
            workflow_result = detector.detect_workflow_intent(query)
            if workflow_result.get('type') == 'workflow':
                print(f"   🔄 Workflow detected!")
                print(f"   Systems: {workflow_result.get('systems', [])}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_workflow_handler():
    """Test the workflow handler"""
    print("\n\n🔄 Testing Workflow Handler")
    print("=" * 60)
    
    try:
        from lumos_cli.workflow_handler import WorkflowHandler
        
        handler = WorkflowHandler()
        
        # Test workflow execution
        test_workflows = [
            {
                'query': 'get me 5 commits from microsoft/vscode and analyze their impact',
                'systems': ['github', 'neo4j']
            },
            {
                'query': 'show me PRs from scimarketplace/externaldata and get Jira ticket details',
                'systems': ['github', 'jira']
            }
        ]
        
        for workflow in test_workflows:
            print(f"\n🔄 Testing workflow: {workflow['query']}")
            print(f"   Systems: {workflow['systems']}")
            
            result = handler.execute_workflow('multi_system', workflow['query'], workflow['systems'])
            
            print(f"   Success: {result['success']}")
            print(f"   Steps: {result['steps']}")
            
            if result['success'] and 'report' in result:
                print(f"   Report preview: {result['report'][:100]}...")
            elif not result['success']:
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    test_advanced_intent_detection()
    test_workflow_handler()
    
    print("\n\n✅ Advanced intent detection test completed!")

if __name__ == "__main__":
    main()
