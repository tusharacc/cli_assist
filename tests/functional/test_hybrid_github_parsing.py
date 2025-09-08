#!/usr/bin/env python3
"""
Test hybrid GitHub query parsing (text patterns + LLM)
This file tests the new hybrid approach for GitHub natural language parsing.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lumos_cli.utils.github_query_parser import GitHubQueryParser

def test_hybrid_parsing():
    """Test the hybrid GitHub parsing approach"""
    print("🚀 Hybrid GitHub Query Parsing Test")
    print("=" * 60)
    
    parser = GitHubQueryParser()
    
    test_queries = [
        "get me the latest pull request for repository externaldata in organization scimarketplace from github",
        "check PRs for scimarketplace/externaldata",
        "github tusharacc cli_assist",
        "repository scimarketplace externaldata",
        "for repository externaldata in organization scimarketplace",
        "organization scimarketplace repository externaldata",
        "show me pull requests for externaldata in scimarketplace",
        "latest PR for externaldata repo in scimarketplace org",
        "for externaldata in scimarketplace",
        "externaldata in scimarketplace",
        "externaldata repo in scimarketplace org",
        # Complex cases that might break text parsing
        "can you show me the pull requests for the externaldata repository which is under the scimarketplace organization",
        "I need to see PRs from scimarketplace org, specifically the externaldata repo",
        "what are the recent changes in externaldata repo of scimarketplace organization"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 60)
        
        try:
            result = parser.parse_query(query)
            
            if result and result.get('org_repo'):
                print(f"✅ Organization: {result.get('organization', 'N/A')}")
                print(f"✅ Repository: {result.get('repository', 'N/A')}")
                print(f"✅ Org/Repo: {result.get('org_repo', 'N/A')}")
                print(f"✅ Method: {result.get('method', 'N/A')}")
                print(f"✅ Confidence: {result.get('confidence', 0.0):.2f}")
                print(f"✅ Agreement: {result.get('agreement', False)}")
            else:
                print("❌ Failed to parse")
                if result and 'error' in result:
                    print(f"   Error: {result['error']}")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_confidence_scoring():
    """Test confidence scoring for different query types"""
    print("\n\n🎯 Confidence Scoring Test")
    print("=" * 60)
    
    parser = GitHubQueryParser()
    
    confidence_tests = [
        ("scimarketplace/externaldata", "Direct format - should be high confidence"),
        ("repository externaldata in organization scimarketplace", "Clear pattern - should be medium-high confidence"),
        ("can you show me the pull requests for the externaldata repository which is under the scimarketplace organization", "Complex natural language - should be lower confidence"),
        ("github microsoft vscode", "Simple format - should be high confidence"),
        ("externaldata in scimarketplace", "Simple pattern - should be medium confidence")
    ]
    
    for query, description in confidence_tests:
        print(f"\n📝 {description}")
        print(f"Query: '{query}'")
        
        try:
            result = parser.parse_query(query)
            if result:
                print(f"Confidence: {result.get('confidence', 0.0):.2f}")
                print(f"Method: {result.get('method', 'N/A')}")
                print(f"Result: {result.get('org_repo', 'N/A')}")
            else:
                print("Failed to parse")
        except Exception as e:
            print(f"Exception: {e}")

def main():
    """Run all tests"""
    test_hybrid_parsing()
    test_confidence_scoring()
    
    print("\n\n✅ Hybrid parsing test completed!")
    print("Note: LLM parsing requires Ollama to be running with devstral model")

if __name__ == "__main__":
    main()
