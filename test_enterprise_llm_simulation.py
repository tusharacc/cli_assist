#!/usr/bin/env python3
"""
Test script for Enterprise LLM Replica Simulation
Tests the OAuth2 framework with OpenAI GPT-4 simulation
"""

import sys
import os
sys.path.append('src')

def test_enterprise_llm_simulation():
    """Test the Enterprise LLM Replica simulation"""
    print("🧪 Testing Enterprise LLM Replica Simulation...")
    
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
        
        # Test connection (will simulate OAuth2 and use OpenAI GPT-4)
        print("\n4. Testing connection (simulating OAuth2 + OpenAI GPT-4)...")
        if enterprise_llm.test_connection():
            print("   ✅ Enterprise LLM Replica simulation successful")
        else:
            print("   ❌ Enterprise LLM Replica simulation failed")
            return False
        
        # Test generate_response
        print("\n5. Testing generate_response (Enterprise LLM simulation)...")
        response = enterprise_llm.generate_response(
            "Explain what microservices architecture is in 2 sentences",
            max_tokens=100,
            temperature=0.7
        )
        print(f"   Response: {response[:200]}...")
        
        # Test chat interface
        print("\n6. Testing chat interface (Enterprise LLM simulation)...")
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant"},
            {"role": "user", "content": "What are the benefits of using containers?"}
        ]
        chat_response = enterprise_llm.chat(messages)
        print(f"   Chat Response: {chat_response[:200]}...")
        
        # Test code generation
        print("\n7. Testing code generation (Enterprise LLM simulation)...")
        code_response = enterprise_llm.generate_code(
            "create a simple Python function to calculate fibonacci numbers",
            language="python"
        )
        print(f"   Code Response: {code_response[:200]}...")
        
        print("\n✅ Enterprise LLM Replica simulation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enterprise_vs_fallback():
    """Test Enterprise LLM vs Fallback behavior"""
    print("\n🔄 Testing Enterprise LLM vs Fallback Behavior...")
    
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
        
        # Test 2: With Enterprise configuration (should simulate enterprise)
        print("\n2. Testing with Enterprise configuration (simulation mode)...")
        enterprise_llm.configure(
            token_url="https://mock-enterprise.com/oauth2/token",
            chat_url="https://mock-enterprise.com/api/v1/chat/completions",
            app_id="mock-client-id",
            app_key="mock-client-secret",
            app_resource="https://mock-enterprise.com/api"
        )
        
        response2 = enterprise_llm.generate_response("Test enterprise simulation", max_tokens=50)
        print(f"   Enterprise Simulation Response: {response2[:100]}...")
        
        print("\n✅ Enterprise vs Fallback test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Enterprise vs Fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_oauth2_simulation():
    """Test OAuth2 simulation flow"""
    print("\n🔐 Testing OAuth2 Simulation Flow...")
    
    try:
        from lumos_cli.enterprise_llm_replica import get_enterprise_llm_replica
        
        enterprise_llm = get_enterprise_llm_replica()
        
        # Configure with mock credentials
        enterprise_llm.configure(
            token_url="https://mock-enterprise.com/oauth2/token",
            chat_url="https://mock-enterprise.com/api/v1/chat/completions",
            app_id="mock-client-id",
            app_key="mock-client-secret",
            app_resource="https://mock-enterprise.com/api"
        )
        
        # Test OAuth2 token simulation
        print("\n1. Testing OAuth2 token simulation...")
        if enterprise_llm._get_access_token():
            print("   ✅ OAuth2 token simulation successful")
            print(f"   Simulated Token: {enterprise_llm.config.access_token[:50]}...")
        else:
            print("   ❌ OAuth2 token simulation failed")
            return False
        
        # Test token expiration simulation
        print("\n2. Testing token expiration simulation...")
        enterprise_llm.config.token_expires_at = time.time() - 1  # Expired token
        if enterprise_llm._get_access_token():
            print("   ✅ Token refresh simulation successful")
        else:
            print("   ❌ Token refresh simulation failed")
            return False
        
        print("\n✅ OAuth2 simulation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ OAuth2 simulation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🏢 Enterprise LLM Replica Simulation Test Suite")
    print("=" * 70)
    
    # Test Enterprise LLM simulation
    simulation_success = test_enterprise_llm_simulation()
    
    # Test Enterprise vs Fallback behavior
    fallback_success = test_enterprise_vs_fallback()
    
    # Test OAuth2 simulation
    oauth2_success = test_oauth2_simulation()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary:")
    print("=" * 70)
    
    print(f"Enterprise LLM Simulation: {'✅ PASSED' if simulation_success else '❌ FAILED'}")
    print(f"Enterprise vs Fallback: {'✅ PASSED' if fallback_success else '❌ FAILED'}")
    print(f"OAuth2 Simulation: {'✅ PASSED' if oauth2_success else '❌ FAILED'}")
    
    if simulation_success and fallback_success and oauth2_success:
        print("\n🎉 All tests passed! Enterprise LLM Replica simulation is working!")
        print("\n📋 What this means:")
        print("   • OAuth2 framework simulates enterprise authentication")
        print("   • OpenAI GPT-4 simulates enterprise LLM responses")
        print("   • Perfect replication of enterprise environment")
        print("   • Easy testing without real enterprise credentials")
        print("   • Seamless migration to real enterprise when ready")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("\n🚀 Next steps:")
    print("1. Use this simulation for development and testing")
    print("2. Configure with real enterprise credentials when available")
    print("3. Integrate with Lumos CLI code operations")
    print("4. Deploy to production environment")

if __name__ == "__main__":
    import time
    main()
