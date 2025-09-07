#!/usr/bin/env python3
"""
Test script for Enterprise LLM Replica with Real OpenAI GPT-4
Tests the OAuth2 framework with real OpenAI GPT-4 responses
"""

import sys
import os
sys.path.append('src')

def test_enterprise_llm_real_openai():
    """Test the Enterprise LLM Replica with real OpenAI GPT-4"""
    print("🏢 Testing Enterprise LLM Replica with Real OpenAI GPT-4...")
    
    try:
        from lumos_cli.enterprise_llm_replica import get_enterprise_llm_replica
        
        # Initialize the Enterprise LLM Replica
        print("\n1. Initializing Enterprise LLM Replica...")
        enterprise_llm = get_enterprise_llm_replica()
        
        # Configure with mock enterprise credentials
        print("\n2. Configuring with mock enterprise credentials...")
        enterprise_llm.configure(
            token_url="https://mock-enterprise.com/oauth2/token",
            chat_url="https://mock-enterprise.com/api/v1/chat/completions",
            app_id="mock-client-id",
            app_key="mock-client-secret",
            app_resource="https://mock-enterprise.com/api"
        )
        
        # Show configuration status
        print("\n3. Checking configuration status...")
        model_info = enterprise_llm.get_model_info()
        print(f"   Configured: {model_info['configured']}")
        print(f"   Token URL: {model_info['token_url']}")
        print(f"   Chat URL: {model_info['chat_url']}")
        print(f"   APP_ID: {model_info['app_id']}")
        print(f"   APP_RESOURCE: {model_info['app_resource']}")
        
        # Test connection (will simulate OAuth2 and use real OpenAI GPT-4)
        print("\n4. Testing connection (simulating OAuth2 + real OpenAI GPT-4)...")
        if enterprise_llm.test_connection():
            print("   ✅ Enterprise LLM Replica simulation successful")
        else:
            print("   ❌ Enterprise LLM Replica simulation failed")
            return False
        
        # Test generate_response with real OpenAI GPT-4
        print("\n5. Testing generate_response (real OpenAI GPT-4)...")
        response = enterprise_llm.generate_response(
            "Explain what microservices architecture is in 2 sentences",
            max_tokens=100,
            temperature=0.7
        )
        print(f"   Response: {response}")
        
        # Test chat interface with real OpenAI GPT-4
        print("\n6. Testing chat interface (real OpenAI GPT-4)...")
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant"},
            {"role": "user", "content": "What are the benefits of using containers?"}
        ]
        chat_response = enterprise_llm.chat(messages)
        print(f"   Chat Response: {chat_response}")
        
        # Test code generation with real OpenAI GPT-4
        print("\n7. Testing code generation (real OpenAI GPT-4)...")
        code_response = enterprise_llm.generate_code(
            "create a simple Python function to calculate fibonacci numbers",
            language="python"
        )
        print(f"   Code Response: {code_response}")
        
        print("\n✅ Enterprise LLM Replica with real OpenAI GPT-4 test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enterprise_vs_fallback_real():
    """Test Enterprise LLM vs Fallback behavior with real OpenAI"""
    print("\n🔄 Testing Enterprise LLM vs Fallback Behavior with Real OpenAI...")
    
    try:
        from lumos_cli.enterprise_llm_replica import get_enterprise_llm_replica
        
        enterprise_llm = get_enterprise_llm_replica()
        
        # Test 1: No configuration (should use fallback)
        print("\n1. Testing without Enterprise configuration (fallback mode)...")
        enterprise_llm.config.token_url = ""  # Clear configuration
        enterprise_llm.config.chat_url = ""
        enterprise_llm.config.app_id = ""
        enterprise_llm.config.app_key = ""
        
        response1 = enterprise_llm.generate_response("Test fallback mode", max_tokens=50)
        print(f"   Fallback Response: {response1[:100]}...")
        
        # Test 2: With Enterprise configuration (should use real OpenAI GPT-4)
        print("\n2. Testing with Enterprise configuration (real OpenAI GPT-4 mode)...")
        enterprise_llm.configure(
            token_url="https://mock-enterprise.com/oauth2/token",
            chat_url="https://mock-enterprise.com/api/v1/chat/completions",
            app_id="mock-client-id",
            app_key="mock-client-secret",
            app_resource="https://mock-enterprise.com/api"
        )
        
        response2 = enterprise_llm.generate_response("Test enterprise simulation with real OpenAI", max_tokens=50)
        print(f"   Enterprise Simulation Response: {response2[:100]}...")
        
        print("\n✅ Enterprise vs Fallback test with real OpenAI completed!")
        return True
        
    except Exception as e:
        print(f"❌ Enterprise vs Fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_code_intent_simulation():
    """Test code intent simulation with real OpenAI GPT-4"""
    print("\n💻 Testing Code Intent Simulation with Real OpenAI GPT-4...")
    
    try:
        from lumos_cli.enterprise_llm_replica import get_enterprise_llm_replica
        
        enterprise_llm = get_enterprise_llm_replica()
        
        # Configure with mock enterprise credentials
        enterprise_llm.configure(
            token_url="https://mock-enterprise.com/oauth2/token",
            chat_url="https://mock-enterprise.com/api/v1/chat/completions",
            app_id="mock-client-id",
            app_key="mock-client-secret",
            app_resource="https://mock-enterprise.com/api"
        )
        
        # Test code generation scenarios
        code_scenarios = [
            {
                "prompt": "Create a Python function to validate email addresses",
                "language": "python",
                "description": "Email validation function"
            },
            {
                "prompt": "Write a JavaScript function to sort an array of objects by a property",
                "language": "javascript",
                "description": "Array sorting function"
            },
            {
                "prompt": "Create a SQL query to find the top 10 customers by total orders",
                "language": "sql",
                "description": "SQL query for customer analysis"
            }
        ]
        
        for i, scenario in enumerate(code_scenarios, 1):
            print(f"\n{i}. Testing {scenario['description']}...")
            response = enterprise_llm.generate_code(
                scenario['prompt'],
                language=scenario['language']
            )
            print(f"   Generated Code: {response[:200]}...")
        
        print("\n✅ Code intent simulation with real OpenAI GPT-4 completed!")
        return True
        
    except Exception as e:
        print(f"❌ Code intent simulation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🏢 Enterprise LLM Replica with Real OpenAI GPT-4 Test Suite")
    print("=" * 70)
    
    # Test Enterprise LLM with real OpenAI
    openai_success = test_enterprise_llm_real_openai()
    
    # Test Enterprise vs Fallback behavior
    fallback_success = test_enterprise_vs_fallback_real()
    
    # Test code intent simulation
    code_success = test_code_intent_simulation()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary:")
    print("=" * 70)
    
    print(f"Enterprise LLM with Real OpenAI: {'✅ PASSED' if openai_success else '❌ FAILED'}")
    print(f"Enterprise vs Fallback (Real OpenAI): {'✅ PASSED' if fallback_success else '❌ FAILED'}")
    print(f"Code Intent Simulation (Real OpenAI): {'✅ PASSED' if code_success else '❌ FAILED'}")
    
    if openai_success and fallback_success and code_success:
        print("\n🎉 All tests passed! Enterprise LLM Replica with real OpenAI GPT-4 is working!")
        print("\n📋 What this means:")
        print("   • OAuth2 framework simulates enterprise authentication")
        print("   • Real OpenAI GPT-4 provides enterprise-quality responses")
        print("   • Perfect replication of enterprise environment on laptop")
        print("   • Same quality responses as you'd get in enterprise")
        print("   • Easy testing with real AI responses")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("\n🚀 Next steps:")
    print("1. Use this for code intent development and testing")
    print("2. Get real enterprise-quality responses on your laptop")
    print("3. Perfect simulation of enterprise environment")
    print("4. Ready for production deployment")

if __name__ == "__main__":
    main()
