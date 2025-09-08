#!/usr/bin/env python3
"""
Test the enhanced commit functionality with detailed analysis
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lumos_cli.github_client import GitHubClient

def test_detailed_commit_analysis():
    """Test detailed commit analysis functionality"""
    print("🚀 Testing Detailed Commit Analysis")
    print("=" * 60)
    
    client = GitHubClient()
    
    if not client.test_connection():
        print("❌ GitHub connection failed. Please check your configuration.")
        return
    
    # Test with a real commit from a public repository
    print("\n📋 Testing detailed commit analysis for microsoft/vscode")
    print("-" * 60)
    
    try:
        # Get a recent commit
        commits = client.list_commits("microsoft", "vscode", per_page=1)
        if commits:
            commit = commits[0]
            commit_sha = commit.get('sha', '')[:7]
            
            print(f"🔍 Testing commit: {commit_sha}")
            print("\n" + "="*60)
            
            # Test detailed analysis
            detailed_analysis = client.format_detailed_commit_analysis(commit)
            print(detailed_analysis)
            
            print("\n" + "="*60)
            print("✅ Detailed commit analysis test completed!")
            
        else:
            print("❌ No commits found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_commit_sha_detection():
    """Test commit SHA detection in interactive mode"""
    print("\n\n🔍 Testing Commit SHA Detection")
    print("=" * 60)
    
    import re
    
    test_queries = [
        "get the commit details of SHA abc1234 from scimarketplace/quote",
        "show me commit abcdef123456 from microsoft/vscode",
        "get details for commit 1234567 in scimarketplace/externaldata",
        "commit analysis for 9876543 from tusharacc/cli_assist",
        "show me the latest commits from scimarketplace/quote",  # Should not match
        "get me 5 commits from microsoft/vscode"  # Should not match
    ]
    
    sha_pattern = r'\b([a-f0-9]{7,40})\b'
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        sha_match = re.search(sha_pattern, query)
        if sha_match:
            commit_sha = sha_match.group(1)
            print(f"✅ Detected SHA: {commit_sha}")
        else:
            print("❌ No SHA detected")

def test_file_analysis():
    """Test file change analysis"""
    print("\n\n📁 Testing File Change Analysis")
    print("=" * 60)
    
    # Mock file data for testing
    mock_files = [
        {
            'filename': 'src/main.py',
            'status': 'modified',
            'additions': 25,
            'deletions': 10
        },
        {
            'filename': 'tests/test_main.py',
            'status': 'added',
            'additions': 50,
            'deletions': 0
        },
        {
            'filename': 'config.json',
            'status': 'modified',
            'additions': 5,
            'deletions': 2
        },
        {
            'filename': 'README.md',
            'status': 'modified',
            'additions': 15,
            'deletions': 3
        },
        {
            'filename': 'old_file.py',
            'status': 'removed',
            'additions': 0,
            'deletions': 100
        }
    ]
    
    client = GitHubClient()
    analysis = client._analyze_file_changes(mock_files)
    
    print("📊 File Analysis Results:")
    print(analysis['file_summary'])
    print(f"\n🔍 Code Analysis:")
    print(analysis['code_analysis'])
    print(f"\n📈 Impact Summary:")
    print(analysis['impact_summary'])

def main():
    """Run all tests"""
    test_detailed_commit_analysis()
    test_commit_sha_detection()
    test_file_analysis()
    
    print("\n\n✅ All tests completed!")

if __name__ == "__main__":
    main()
