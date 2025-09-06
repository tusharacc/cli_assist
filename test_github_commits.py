#!/usr/bin/env python3
"""
Test GitHub commit functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lumos_cli.github_client import GitHubClient

def test_github_commits():
    """Test GitHub commit functionality"""
    print("🚀 GitHub Commits Test")
    print("=" * 60)
    
    # Initialize GitHub client
    client = GitHubClient()
    
    if not client.test_connection():
        print("❌ GitHub connection failed. Please check your configuration.")
        return
    
    # Test repository (using a public repository)
    org = "microsoft"
    repo = "vscode"
    
    print(f"\n📋 Testing commits for {org}/{repo}")
    print("-" * 40)
    
    # Test 1: List commits
    print("\n1. Testing list_commits...")
    try:
        commits = client.list_commits(org, repo, per_page=5)
        print(f"✅ Found {len(commits)} commits")
        if commits:
            print(f"   Latest commit: {commits[0].get('sha', 'unknown')[:7]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get latest commit
    print("\n2. Testing get_latest_commit...")
    try:
        latest = client.get_latest_commit(org, repo)
        if latest:
            print(f"✅ Latest commit: {latest.get('sha', 'unknown')[:7]}")
            print(f"   Message: {latest.get('commit', {}).get('message', 'No message')[:50]}...")
        else:
            print("❌ No latest commit found")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get specific commit (using first commit from list)
    print("\n3. Testing get_commit...")
    try:
        if commits and len(commits) > 0:
            commit_sha = commits[0]['sha']
            commit = client.get_commit(org, repo, commit_sha)
            if commit:
                print(f"✅ Retrieved commit: {commit.get('sha', 'unknown')[:7]}")
                print(f"   Author: {commit.get('commit', {}).get('author', {}).get('name', 'Unknown')}")
            else:
                print("❌ Commit not found")
        else:
            print("❌ No commits available for testing")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Display commits table
    print("\n4. Testing display_commits_table...")
    try:
        commits = client.list_commits(org, repo, per_page=3)
        if commits:
            print("✅ Commits table:")
            client.display_commits_table(commits)
        else:
            print("❌ No commits to display")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Format commit summary
    print("\n5. Testing format_commit_summary...")
    try:
        if commits and len(commits) > 0:
            commit = commits[0]
            summary = client.format_commit_summary(commit)
            print("✅ Commit summary:")
            print(summary)
        else:
            print("❌ No commits available for testing")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_commit_parsing():
    """Test commit query parsing"""
    print("\n\n🔍 Commit Query Parsing Test")
    print("=" * 60)
    
    from lumos_cli.github_query_parser import GitHubQueryParser
    parser = GitHubQueryParser()
    
    test_queries = [
        "get me the details for last 5 commits from repository externaldata under org scimarketplace",
        "get me latest commit in repo externaldata in org scimarketplace",
        "show me commits for scimarketplace/externaldata",
        "latest commit from microsoft/vscode",
        "last 10 commits in repository vscode under organization microsoft"
    ]
    
    for query in test_queries:
        print(f"\n📝 Testing: '{query}'")
        try:
            result = parser.parse_query(query)
            if result and result.get('org_repo'):
                print(f"✅ Parsed: {result['org_repo']}")
                print(f"   Method: {result.get('method', 'unknown')}")
                print(f"   Confidence: {result.get('confidence', 0.0):.2f}")
            else:
                print("❌ Failed to parse")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    test_github_commits()
    test_commit_parsing()
    
    print("\n\n✅ GitHub commits test completed!")

if __name__ == "__main__":
    main()
