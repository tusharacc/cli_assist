#!/usr/bin/env python3
"""
Test GitHub query parsing to ensure correct org/repo extraction
"""

import re

def test_github_parsing(query: str):
    """Test the GitHub parsing logic"""
    print(f"\n🔍 Testing query: '{query}'")
    print("=" * 60)
    
    lower_query = query.lower()
    org_repo = None
    
    # Pattern 1: "tusharacc/cli_assist" or "scimarketplace/externaldata" (exact format)
    org_repo_pattern = r'([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)'
    match = re.search(org_repo_pattern, query)
    if match:
        org_repo = f"{match.group(1)}/{match.group(2)}"
        print(f"✅ Pattern 1 matched: {org_repo}")
    
    # Pattern 2: "repository externaldata in organization scimarketplace" (most specific)
    if not org_repo:
        repo_org_pattern = r'repository\s+([a-zA-Z0-9_-]+)\s+in\s+organization\s+([a-zA-Z0-9_-]+)'
        match = re.search(repo_org_pattern, lower_query)
        if match:
            repo_name = match.group(1)
            org_name = match.group(2)
            org_repo = f"{org_name}/{repo_name}"
            print(f"✅ Pattern 2 matched: {org_repo}")
    
    # Pattern 3: "for repository externaldata in organization scimarketplace"
    if not org_repo:
        for_repo_org_pattern = r'for\s+repository\s+([a-zA-Z0-9_-]+)\s+in\s+organization\s+([a-zA-Z0-9_-]+)'
        match = re.search(for_repo_org_pattern, lower_query)
        if match:
            repo_name = match.group(1)
            org_name = match.group(2)
            org_repo = f"{org_name}/{repo_name}"
            print(f"✅ Pattern 3 matched: {org_repo}")
    
    # Pattern 4: "organization scimarketplace repository externaldata"
    if not org_repo:
        org_repo_pattern2 = r'organization\s+([a-zA-Z0-9_-]+)\s+repository\s+([a-zA-Z0-9_-]+)'
        match = re.search(org_repo_pattern2, lower_query)
        if match:
            org_name = match.group(1)
            repo_name = match.group(2)
            org_repo = f"{org_name}/{repo_name}"
            print(f"✅ Pattern 4 matched: {org_repo}")
    
    # Pattern 5: "github tusharacc cli_assist" or "repository scimarketplace externaldata" (simple format)
    if not org_repo:
        words = query.split()
        if len(words) >= 3:
            for i, word in enumerate(words):
                if word.lower() in ['github', 'repository', 'repo'] and i + 2 < len(words):
                    # Make sure the next two words don't contain "in" or "organization"
                    next_words = words[i+1:i+3]
                    if not any(w.lower() in ['in', 'organization', 'org'] for w in next_words):
                        org_repo = f"{words[i+1]}/{words[i+2]}"
                        print(f"✅ Pattern 5 matched: {org_repo}")
                        break
    
    # Pattern 6: "for externaldata in scimarketplace" or "externaldata in scimarketplace"
    if not org_repo:
        simple_pattern = r'for\s+([a-zA-Z0-9_-]+)\s+in\s+([a-zA-Z0-9_-]+)'
        match = re.search(simple_pattern, lower_query)
        if match:
            repo_name = match.group(1)
            org_name = match.group(2)
            org_repo = f"{org_name}/{repo_name}"
            print(f"✅ Pattern 6 matched: {org_repo}")
    
    # Pattern 7: "externaldata repo in scimarketplace org"
    if not org_repo:
        repo_org_simple = r'([a-zA-Z0-9_-]+)\s+repo\s+in\s+([a-zA-Z0-9_-]+)\s+org'
        match = re.search(repo_org_simple, lower_query)
        if match:
            repo_name = match.group(1)
            org_name = match.group(2)
            org_repo = f"{org_name}/{repo_name}"
            print(f"✅ Pattern 7 matched: {org_repo}")
    
    if org_repo:
        print(f"🎯 Final result: {org_repo}")
        return org_repo
    else:
        print("❌ No pattern matched")
        return None

def main():
    """Test various GitHub query patterns"""
    print("🚀 GitHub Query Parsing Test")
    print("=" * 60)
    
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
        "externaldata repo in scimarketplace org"
    ]
    
    for query in test_queries:
        result = test_github_parsing(query)
        print()

if __name__ == "__main__":
    main()
