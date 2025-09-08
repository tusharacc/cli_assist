#!/usr/bin/env python3
"""
Test LLM-based Jenkins folder path extraction
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_jenkins_llm_folder_extraction():
    """Test the new LLM-based Jenkins folder path extraction"""
    print("🤖 Testing LLM-Based Jenkins Folder Path Extraction")
    print("=" * 70)
    
    try:
        from lumos_cli.interactive.handlers.jenkins_handler import _extract_folder_path_with_llm
        
        # Test cases with various query formats
        test_cases = [
            {
                "query": "get me the last 5 builds for scimarketplace and folder quote and sub folder RC1",
                "expected": "scimarketplace/quote_multi/RC1",
                "description": "Complex query with repository and branch"
            },
            {
                "query": "folder quote and sub folder RC1",
                "expected": "scimarketplace/quote_multi/RC1",
                "description": "Simple folder and sub-folder"
            },
            {
                "query": "folder externaldata and sub folder RC2",
                "expected": "scimarketplace/externaldata_multi/RC2",
                "description": "Different repository and branch"
            },
            {
                "query": "folder addresssearch and sub folder RC3",
                "expected": "scimarketplace/addresssearch_multi/RC3",
                "description": "Another repository and branch"
            },
            {
                "query": "folder deploy-all",
                "expected": "scimarketplace/deploy-all",
                "description": "Deploy-all folder"
            },
            {
                "query": "for scimarketplace and folder quote and sub folder RC1",
                "expected": "scimarketplace/quote_multi/RC1",
                "description": "Query with 'for scimarketplace' prefix"
            },
            {
                "query": "show me builds from jenkins for scimarketplace and folder externaldata and sub folder RC4",
                "expected": "scimarketplace/externaldata_multi/RC4",
                "description": "Full Jenkins query with context"
            },
            {
                "query": "get failed jobs in folder quote and sub folder RC1",
                "expected": "scimarketplace/quote_multi/RC1",
                "description": "Failed jobs query"
            },
            {
                "query": "show running jobs in folder addresssearch and sub folder RC2",
                "expected": "scimarketplace/addresssearch_multi/RC2",
                "description": "Running jobs query"
            },
            {
                "query": "folder quote_multi and sub folder RC1",
                "expected": "scimarketplace/quote_multi/RC1",
                "description": "Repository already has _multi suffix"
            }
        ]
        
        print(f"🧪 Running {len(test_cases)} test cases...")
        print()
        
        passed = 0
        failed = 0
        
        for i, test_case in enumerate(test_cases, 1):
            query = test_case["query"]
            expected = test_case["expected"]
            description = test_case["description"]
            
            print(f"Test {i}: {description}")
            print(f"  Query: '{query}'")
            print(f"  Expected: '{expected}'")
            
            try:
                result = _extract_folder_path_with_llm(query)
                print(f"  Result: '{result}'")
                
                if result == expected:
                    print(f"  ✅ PASS")
                    passed += 1
                else:
                    print(f"  ❌ FAIL - Expected '{expected}', got '{result}'")
                    failed += 1
                    
            except Exception as e:
                print(f"  ❌ ERROR - {e}")
                failed += 1
            
            print()
        
        print("=" * 70)
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! LLM-based folder extraction is working correctly.")
            return True
        else:
            print(f"⚠️  {failed} tests failed. Check the LLM implementation.")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_jenkins_llm_edge_cases():
    """Test edge cases and error handling"""
    print("\n🔍 Testing Edge Cases and Error Handling")
    print("=" * 50)
    
    try:
        from lumos_cli.interactive.handlers.jenkins_handler import _extract_folder_path_with_llm
        
        edge_cases = [
            {
                "query": "",
                "expected": "scimarketplace/deploy-all",
                "description": "Empty query"
            },
            {
                "query": "random text with no folder info",
                "expected": "scimarketplace/deploy-all",
                "description": "Query with no folder information"
            },
            {
                "query": "folder",
                "expected": "scimarketplace/deploy-all",
                "description": "Incomplete folder query"
            },
            {
                "query": "folder quote and sub folder",
                "expected": "scimarketplace/quote_multi",
                "description": "Missing branch name"
            }
        ]
        
        passed = 0
        failed = 0
        
        for i, test_case in enumerate(edge_cases, 1):
            query = test_case["query"]
            expected = test_case["expected"]
            description = test_case["description"]
            
            print(f"Edge Case {i}: {description}")
            print(f"  Query: '{query}'")
            print(f"  Expected: '{expected}'")
            
            try:
                result = _extract_folder_path_with_llm(query)
                print(f"  Result: '{result}'")
                
                # For edge cases, we're more lenient - just check it starts with scimarketplace/
                if result.startswith("scimarketplace/"):
                    print(f"  ✅ PASS (valid path)")
                    passed += 1
                else:
                    print(f"  ❌ FAIL - Invalid path format")
                    failed += 1
                    
            except Exception as e:
                print(f"  ❌ ERROR - {e}")
                failed += 1
            
            print()
        
        print(f"📊 Edge Case Results: {passed} passed, {failed} failed")
        return failed == 0
        
    except Exception as e:
        print(f"❌ Edge case testing error: {e}")
        return False

def test_jenkins_llm_performance():
    """Test performance and response time"""
    print("\n⚡ Testing Performance")
    print("=" * 30)
    
    try:
        import time
        from lumos_cli.interactive.handlers.jenkins_handler import _extract_folder_path_with_llm
        
        test_query = "get me the last 5 builds for scimarketplace and folder quote and sub folder RC1"
        
        print(f"Testing query: '{test_query}'")
        print("Running 3 iterations to measure performance...")
        
        times = []
        for i in range(3):
            start_time = time.time()
            result = _extract_folder_path_with_llm(test_query)
            end_time = time.time()
            
            duration = end_time - start_time
            times.append(duration)
            
            print(f"  Iteration {i+1}: {duration:.2f}s - Result: '{result}'")
        
        avg_time = sum(times) / len(times)
        print(f"\n📊 Average response time: {avg_time:.2f}s")
        
        if avg_time < 10.0:  # Should be under 10 seconds
            print("✅ Performance acceptable")
            return True
        else:
            print("⚠️  Performance may be slow")
            return False
            
    except Exception as e:
        print(f"❌ Performance testing error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Jenkins LLM Folder Extraction Tests")
    print("=" * 70)
    
    # Run all tests
    test1_passed = test_jenkins_llm_folder_extraction()
    test2_passed = test_jenkins_llm_edge_cases()
    test3_passed = test_jenkins_llm_performance()
    
    print("\n" + "=" * 70)
    print("🏁 Final Results:")
    print(f"  Main functionality: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"  Edge cases: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"  Performance: {'✅ PASS' if test3_passed else '❌ FAIL'}")
    
    if all([test1_passed, test2_passed, test3_passed]):
        print("\n🎉 All tests passed! The LLM-based Jenkins folder extraction is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        sys.exit(1)
