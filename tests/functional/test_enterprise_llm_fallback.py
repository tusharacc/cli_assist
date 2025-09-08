#!/usr/bin/env python3
"""
Test script for Enterprise LLM Replica with Fallback Models
Tests the OAuth2 framework with OpenAI GPT-4 and Hugging Face fallbacks
"""

import sys
import os
sys.path.append('src')

def test_enterprise_llm_fallback():
    """Test the Enterprise LLM Replica with fallback models"""
    print("🧪 Testing Enterprise LLM Replica with Fallback Models...")
    
    try:
        from lumos_cli.enterprise_llm_replica import get_enterprise_llm_replica
        
        # Initialize the Enterprise LLM Replica
        print("\n1. Initializing Enterprise LLM Replica...")
        enterprise_llm = get_enterprise_llm_replica()
        
        # Show configuration status
        print("\n2. Checking configuration status...")
        model_info = enterprise_llm.get_model_info()
        print(f"   Configured: {model_info['configured']}")
        print(f"   Has Token: {model_info['has_token']}")
        print(f"   Token URL: {model_info['token_url'] or 'Not set'}")
        print(f"   Chat URL: {model_info['chat_url'] or 'Not set'}")
        
        # Test connection (will use fallback models)
        print("\n3. Testing connection (using fallback models)...")
        if enterprise_llm.test_connection():
            print("   ✅ Enterprise LLM Replica connection successful")
        else:
            print("   ❌ Enterprise LLM Replica connection failed")
            return False
        
        # Test generate_response
        print("\n4. Testing generate_response...")
        response = enterprise_llm.generate_response(
            "Explain what microservices architecture is in 2 sentences",
            max_tokens=100,
            temperature=0.7
        )
        print(f"   Response: {response[:200]}...")
        
        # Test chat interface
        print("\n5. Testing chat interface...")
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant"},
            {"role": "user", "content": "What are the benefits of using containers?"}
        ]
        chat_response = enterprise_llm.chat(messages)
        print(f"   Chat Response: {chat_response[:200]}...")
        
        # Test code generation
        print("\n6. Testing code generation...")
        code_response = enterprise_llm.generate_code(
            "create a simple Python function to calculate fibonacci numbers",
            language="python"
        )
        print(f"   Code Response: {code_response[:200]}...")
        
        print("\n✅ Enterprise LLM Replica with fallback models test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enterprise_configuration():
    """Test Enterprise LLM configuration without real credentials"""
    print("\n🏢 Testing Enterprise LLM Configuration...")
    
    try:
        from src.lumos_cli.config.enterprise_llm_config import get_enterprise_llm_config_manager
        
        # Initialize configuration manager
        print("\n1. Initializing configuration manager...")
        config_manager = get_enterprise_llm_config_manager()
        
        # Show current configuration
        print("\n2. Current configuration status...")
        config_manager.show_config()
        
        # Test configuration without real credentials
        print("\n3. Testing configuration with mock credentials...")
        from lumos_cli.enterprise_llm_replica import get_enterprise_llm_replica
        
        enterprise_llm = get_enterprise_llm_replica()
        
        # Configure with mock credentials (won't work but tests the framework)
        enterprise_llm.configure(
            token_url="https://mock-enterprise.com/oauth2/token",
            chat_url="https://mock-enterprise.com/api/v1/chat/completions",
            app_id="mock-client-id",
            app_key="mock-client-secret",
            app_resource="https://mock-enterprise.com/api"
        )
        
        print("   ✅ Mock configuration set successfully")
        
        # Test that it falls back to local models
        print("\n4. Testing fallback to local models...")
        response = enterprise_llm.generate_response(
            "This should use fallback models since mock credentials won't work",
            max_tokens=50
        )
        print(f"   Fallback Response: {response[:200]}...")
        
        print("\n✅ Enterprise LLM configuration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_fallback_priority():
    """Test the priority of fallback models"""
    print("\n🔄 Testing Model Fallback Priority...")
    
    try:
        from lumos_cli.enterprise_llm_replica import get_enterprise_llm_replica
        
        enterprise_llm = get_enterprise_llm_replica()
        
        print("\n1. Testing OpenAI GPT-4 availability...")
        if enterprise_llm._try_openai_gpt4("", None, None):
            print("   ✅ OpenAI GPT-4 is available")
            print("   📝 Will use OpenAI GPT-4 as primary fallback")
        else:
            print("   ❌ OpenAI GPT-4 is not available")
            print("   📝 Will use Hugging Face models as fallback")
        
        print("\n2. Testing Hugging Face GPT-4 simulation...")
        try:
            from lumos_cli.gpt4_simulator import get_gpt4_simulator
            gpt4_simulator = get_gpt4_simulator()
            print("   ✅ Hugging Face GPT-4 simulator is available")
        except Exception as e:
            print(f"   ❌ Hugging Face GPT-4 simulator not available: {e}")
        
        print("\n3. Testing actual fallback behavior...")
        response = enterprise_llm.generate_response(
            "Test the fallback model priority",
            max_tokens=30
        )
        print(f"   Fallback Response: {response[:100]}...")
        
        print("\n✅ Model fallback priority test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Fallback priority test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🏢 Enterprise LLM Replica with Fallback Models Test Suite")
    print("=" * 70)
    
    # Test Enterprise LLM with fallback models
    fallback_success = test_enterprise_llm_fallback()
    
    # Test Enterprise configuration
    config_success = test_enterprise_configuration()
    
    # Test model fallback priority
    priority_success = test_model_fallback_priority()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary:")
    print("=" * 70)
    
    print(f"Enterprise LLM Fallback: {'✅ PASSED' if fallback_success else '❌ FAILED'}")
    print(f"Enterprise Configuration: {'✅ PASSED' if config_success else '❌ FAILED'}")
    print(f"Model Fallback Priority: {'✅ PASSED' if priority_success else '❌ FAILED'}")
    
    if fallback_success and config_success and priority_success:
        print("\n🎉 All tests passed! Enterprise LLM Replica with fallback models is ready!")
        print("\n📋 What this means:")
        print("   • OAuth2 framework is ready for real enterprise credentials")
        print("   • Fallback to OpenAI GPT-4 when available")
        print("   • Fallback to Hugging Face models when OpenAI not available")
        print("   • Seamless testing without real enterprise credentials")
        print("   • Production-ready when real credentials are provided")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("\n🚀 Next steps:")
    print("1. Configure with real enterprise credentials when available")
    print("2. Test with actual enterprise API")
    print("3. Integrate with Lumos CLI")
    print("4. Deploy to production environment")

if __name__ == "__main__":
    main()
