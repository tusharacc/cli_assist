#!/usr/bin/env python3
"""
Test the specific commit parsing issue fix
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lumos_cli.utils.github_query_parser import GitHubQueryParser

def test_specific_query():
    """Test the specific query that was failing"""
    print("🔍 Testing Specific Commit Query Parsing Fix")
    print("=" * 60)
    
    parser = GitHubQueryParser()
    
    # The specific query that was failing
    test_query = "give me the 5 latest commits in branch RC1 in the repository quote under org scimarketplace"
    
    print(f"📝 Testing query: '{test_query}'")
    print("-" * 60)
    
    try:
        result = parser.parse_query(test_query)
        
        if result and result.get('org_repo'):
            print(f"✅ Parsed successfully!")
            print(f"   Organization: {result.get('organization', 'N/A')}")
            print(f"   Repository: {result.get('repository', 'N/A')}")
            print(f"   Org/Repo: {result.get('org_repo', 'N/A')}")
            print(f"   Method: {result.get('method', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 0.0):.2f}")
            print(f"   Agreement: {result.get('agreement', False)}")
            
            # Check if it's correct
            if result.get('org_repo') == 'scimarketplace/quote':
                print("🎯 CORRECT! Parsed as scimarketplace/quote")
            else:
                print(f"❌ INCORRECT! Expected 'scimarketplace/quote', got '{result.get('org_repo')}'")
        else:
            print("❌ Failed to parse")
            if result and 'error' in result:
                print(f"   Error: {result['error']}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_other_commit_queries():
    """Test other commit query patterns"""
    print("\n\n🔍 Testing Other Commit Query Patterns")
    print("=" * 60)
    
    parser = GitHubQueryParser()
    
    test_queries = [
        "get me the details for last 5 commits from repository externaldata under org scimarketplace",
        "get me latest commit in repo externaldata in org scimarketplace",
        "show me commits for scimarketplace/externaldata",
        "latest commit from microsoft/vscode",
        "last 10 commits in repository vscode under organization microsoft",
        "commits in repository quote under org scimarketplace"
    ]
    
    for query in test_queries:
        print(f"\n📝 Testing: '{query}'")
        try:
            result = parser.parse_query(query)
            if result and result.get('org_repo'):
                print(f"✅ Parsed: {result['org_repo']} (method: {result.get('method', 'unknown')})")
            else:
                print("❌ Failed to parse")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    test_specific_query()
    test_other_commit_queries()
    
    print("\n\n✅ Commit parsing fix test completed!")

if __name__ == "__main__":
    main()
