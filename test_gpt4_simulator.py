#!/usr/bin/env python3
"""
Test script for GPT-4 Simulator
Tests the GPT-4 simulation functionality
"""

import sys
import os
sys.path.append('src')

def test_gpt4_simulator():
    """Test the GPT-4 Simulator system"""
    print("🧪 Testing GPT-4 Simulator...")
    
    try:
        from lumos_cli.gpt4_simulator import get_gpt4_simulator
        
        # Initialize the simulator
        print("\n1. Initializing GPT-4 Simulator...")
        simulator = get_gpt4_simulator()
        
        # Test model info
        print("\n2. Testing model information...")
        model_info = simulator.get_model_info()
        print(f"   Loaded models: {model_info['loaded_models']}")
        print(f"   Total models: {model_info['total_models']}")
        print(f"   Device: {model_info['device']}")
        
        # Test connection
        print("\n3. Testing connection...")
        if simulator.test_connection():
            print("   ✅ Connection test successful")
        else:
            print("   ❌ Connection test failed")
            return False
        
        # Test general conversation
        print("\n4. Testing general conversation...")
        response = simulator.generate_response(
            "Hello, can you introduce yourself?",
            task_type="general",
            max_tokens=100
        )
        print(f"   Response: {response[:200]}...")
        
        # Test code generation
        print("\n5. Testing code generation...")
        code = simulator.generate_code(
            "create a simple hello world function",
            language="python"
        )
        print(f"   Generated code:\n{code}")
        
        # Test code analysis
        print("\n6. Testing code analysis...")
        test_code = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
        analysis = simulator.analyze_code(test_code, "performance")
        print(f"   Analysis: {analysis}")
        
        # Test chat interface
        print("\n7. Testing chat interface...")
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant"},
            {"role": "user", "content": "What is the capital of France?"}
        ]
        chat_response = simulator.chat(messages)
        print(f"   Chat response: {chat_response[:200]}...")
        
        print("\n✅ GPT-4 Simulator test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enterprise_integration():
    """Test integration with enterprise LLM replica"""
    print("\n🏢 Testing Enterprise Integration...")
    
    try:
        from lumos_cli.enterprise_llm_replica import get_enterprise_llm_replica
        
        # Initialize enterprise LLM replica
        print("\n1. Initializing Enterprise LLM Replica...")
        enterprise_llm = get_enterprise_llm_replica()
        
        # Test enterprise LLM
        print("\n2. Testing Enterprise LLM...")
        if enterprise_llm.test_connection():
            print("   ✅ Enterprise LLM connection successful")
        else:
            print("   ❌ Enterprise LLM connection failed")
            return False
        
        # Test enterprise LLM response
        print("\n3. Testing Enterprise LLM response...")
        response = enterprise_llm.generate_response(
            "Explain the benefits of microservices architecture",
            max_tokens=150
        )
        print(f"   Enterprise LLM response: {response[:200]}...")
        
        print("\n✅ Enterprise Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Enterprise integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🤖 GPT-4 Simulator Test Suite")
    print("=" * 50)
    
    # Test GPT-4 Simulator
    gpt4_success = test_gpt4_simulator()
    
    # Test Enterprise Integration
    enterprise_success = test_enterprise_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    print(f"GPT-4 Simulator: {'✅ PASSED' if gpt4_success else '❌ FAILED'}")
    print(f"Enterprise Integration: {'✅ PASSED' if enterprise_success else '❌ FAILED'}")
    
    if gpt4_success and enterprise_success:
        print("\n🎉 All tests passed! GPT-4 Simulator is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("\nNext steps:")
    print("1. Integrate with Lumos CLI")
    print("2. Test with real enterprise scenarios")
    print("3. Optimize model performance")
    print("4. Deploy to enterprise environment")

if __name__ == "__main__":
    main()
