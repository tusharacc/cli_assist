#!/usr/bin/env python3
"""
Demo of Enterprise LLM Replica with OAuth2 Authentication
Tests the actual enterprise API integration
"""

import sys
import os
sys.path.append('src')

def demo_enterprise_llm_oauth2():
    """Demonstrate the Enterprise LLM Replica with OAuth2"""
    
    print("🏢 Enterprise LLM Replica with OAuth2 Demo")
    print("=" * 60)
    
    print("\n📋 Enterprise LLM Replica Features:")
    print("-" * 50)
    
    features = [
        "OAuth2 client credentials flow authentication",
        "Bearer token management with automatic refresh",
        "Real enterprise API integration",
        "GPT-4 compatible chat interface",
        "Configuration management with secure storage",
        "Interactive setup and testing",
        "Comprehensive error handling and logging",
        "Environment variable and config file support"
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"{i:2d}. {feature}")
    
    print("\n" + "=" * 60)
    print("🔐 OAuth2 Authentication Flow:")
    print("=" * 60)
    
    oauth2_steps = [
        "1. Client sends credentials to Token URL",
        "2. Server validates APP_ID and APP_KEY",
        "3. Server returns access_token and expires_in",
        "4. Client uses Bearer token for API calls",
        "5. Token automatically refreshed when expired",
        "6. Secure storage of credentials and tokens"
    ]
    
    for step in oauth2_steps:
        print(f"   {step}")
    
    print("\n" + "=" * 60)
    print("🎯 Configuration Parameters:")
    print("=" * 60)
    
    config_params = [
        {
            "parameter": "TOKEN_URL",
            "description": "OAuth2 token endpoint URL",
            "example": "https://your-enterprise.com/oauth2/token",
            "required": "Yes"
        },
        {
            "parameter": "CHAT_URL", 
            "description": "LLM chat API endpoint URL",
            "example": "https://your-enterprise.com/api/v1/chat/completions",
            "required": "Yes"
        },
        {
            "parameter": "APP_ID",
            "description": "Client ID for OAuth2 authentication",
            "example": "your-client-id-here",
            "required": "Yes"
        },
        {
            "parameter": "APP_KEY",
            "description": "Client Secret for OAuth2 authentication",
            "example": "your-client-secret-here",
            "required": "Yes"
        },
        {
            "parameter": "APP_RESOURCE",
            "description": "Resource identifier (optional)",
            "example": "https://your-enterprise.com/api",
            "required": "No"
        }
    ]
    
    for param in config_params:
        print(f"\n🔧 {param['parameter']}:")
        print(f"   Description: {param['description']}")
        print(f"   Example: {param['example']}")
        print(f"   Required: {param['required']}")
    
    print("\n" + "=" * 60)
    print("🚀 Usage Examples:")
    print("=" * 60)
    
    examples = [
        {
            "scenario": "Interactive Configuration",
            "code": "from src.lumos_cli.config.enterprise_llm_config import get_enterprise_llm_config_manager\n\nconfig_manager = get_enterprise_llm_config_manager()\nconfig_manager.setup_interactive()"
        },
        {
            "scenario": "Programmatic Configuration",
            "code": "from lumos_cli.enterprise_llm_replica import get_enterprise_llm_replica\n\nenterprise_llm = get_enterprise_llm_replica()\nenterprise_llm.configure(\n    token_url='https://your-enterprise.com/oauth2/token',\n    chat_url='https://your-enterprise.com/api/v1/chat/completions',\n    app_id='your-client-id',\n    app_key='your-client-secret',\n    app_resource='https://your-enterprise.com/api'\n)"
        },
        {
            "scenario": "Generate Response",
            "code": "response = enterprise_llm.generate_response(\n    'Explain microservices architecture',\n    max_tokens=500,\n    temperature=0.7\n)\nprint(f'Response: {response}')"
        },
        {
            "scenario": "Chat Interface",
            "code": "messages = [\n    {'role': 'system', 'content': 'You are a helpful AI assistant'},\n    {'role': 'user', 'content': 'How do I optimize database performance?'}\n]\nresponse = enterprise_llm.chat(messages)\nprint(f'Chat response: {response}')"
        },
        {
            "scenario": "Test Connection",
            "code": "if enterprise_llm.test_connection():\n    print('✅ Enterprise LLM is working')\nelse:\n    print('❌ Enterprise LLM connection failed')"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['scenario']}:")
        print(f"   {example['code']}")
    
    print("\n" + "=" * 60)
    print("🔧 Environment Variables:")
    print("=" * 60)
    
    env_vars = [
        "ENTERPRISE_LLM_TOKEN_URL=https://your-enterprise.com/oauth2/token",
        "ENTERPRISE_LLM_CHAT_URL=https://your-enterprise.com/api/v1/chat/completions",
        "ENTERPRISE_LLM_APP_ID=your-client-id-here",
        "ENTERPRISE_LLM_APP_KEY=your-client-secret-here",
        "ENTERPRISE_LLM_APP_RESOURCE=https://your-enterprise.com/api"
    ]
    
    for env_var in env_vars:
        print(f"   {env_var}")
    
    print("\n" + "=" * 60)
    print("🏗️ Architecture:")
    print("=" * 60)
    
    architecture = """
    Enterprise LLM Replica with OAuth2
    │
    ├─ Configuration Manager
    │  ├─ Interactive Setup
    │  ├─ Config File Storage
    │  ├─ Environment Variables
    │  └─ Secure Credential Storage
    │
    ├─ OAuth2 Authentication
    │  ├─ Token URL Request
    │  ├─ Bearer Token Management
    │  ├─ Automatic Token Refresh
    │  └─ Token Expiration Handling
    │
    ├─ Enterprise API Client
    │  ├─ Chat Completions API
    │  ├─ Error Handling
    │  ├─ Request/Response Logging
    │  └─ Timeout Management
    │
    └─ Integration Points
        ├─ Lumos CLI Code Manager
        ├─ Debug Logging
        ├─ Error Handling
        └─ User Interface
    """
    
    print(architecture)
    
    print("\n🎯 Benefits of Enterprise LLM Replica:")
    print("   • Real enterprise API integration")
    print("   • OAuth2 authentication with automatic token refresh")
    print("   • GPT-4 compatible interface")
    print("   • Secure credential storage")
    print("   • Interactive configuration setup")
    print("   • Comprehensive error handling")
    print("   • Environment variable support")
    print("   • Easy testing and validation")
    
    print("\n" + "=" * 60)
    print("🔧 Setup Instructions:")
    print("=" * 60)
    
    setup_steps = [
        "1. Set environment variables or use interactive setup",
        "2. Run: python -c \"from lumos_cli.enterprise_llm_config import get_enterprise_llm_config_manager; get_enterprise_llm_config_manager().setup_interactive()\"",
        "3. Test connection: python -c \"from lumos_cli.enterprise_llm_replica import get_enterprise_llm_replica; print('Connected:', get_enterprise_llm_replica().test_connection())\"",
        "4. Start using Enterprise LLM in your applications",
        "5. Monitor logs for debugging and troubleshooting"
    ]
    
    for step in setup_steps:
        print(f"   {step}")
    
    print("\n" + "=" * 60)
    print("⚠️  Security Notes:")
    print("=" * 60)
    
    security_notes = [
        "• Credentials are stored securely with 600 file permissions",
        "• Access tokens are managed automatically",
        "• No credentials are logged in debug output",
        "• Use environment variables in production",
        "• Rotate APP_KEY regularly for security",
        "• Monitor API usage and token expiration",
        "• Use HTTPS for all API endpoints"
    ]
    
    for note in security_notes:
        print(f"   {note}")

if __name__ == "__main__":
    demo_enterprise_llm_oauth2()
