#!/usr/bin/env python3
"""Test Enterprise LLM integration"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.config import config
from lumos_cli.client import LLMRouter
from lumos_cli.enterprise_llm import EnterpriseLLMProvider, is_enterprise_configured
from lumos_cli.ui import create_header
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def test_enterprise_configuration():
    """Test enterprise configuration detection"""
    console = Console()
    create_header(console, "Enterprise LLM Configuration Test")
    
    # Check if enterprise is configured
    is_configured = is_enterprise_configured()
    console.print(f"🏢 Enterprise configured from env vars: {'✅ Yes' if is_configured else '❌ No'}")
    
    # Check config detection
    config_configured = config.is_enterprise_configured(debug=True)
    console.print(f"🏢 Enterprise configured in config: {'✅ Yes' if config_configured else '❌ No'}")
    
    # Show what's needed for enterprise configuration
    if not is_configured:
        console.print("\n📋 Required Environment Variables for Enterprise LLM:")
        required_vars = [
            'ENTERPRISE_TOKEN_URL',
            'ENTERPRISE_CHAT_URL',
            'ENTERPRISE_APP_ID',
            'ENTERPRISE_APP_KEY',
            'ENTERPRISE_APP_RESOURCE'
        ]
        
        table = Table(title="Enterprise Configuration Requirements")
        table.add_column("Variable", style="cyan")
        table.add_column("Purpose", style="yellow")
        table.add_column("Status", style="bold")
        
        purposes = [
            "URL to get authentication token",
            "URL for chat completions",
            "Your application identifier",
            "Your application key/secret",
            "Resource identifier for your app"
        ]
        
        for var, purpose in zip(required_vars, purposes):
            status = "✅ Set" if os.getenv(var) else "❌ Not Set"
            table.add_row(var, purpose, status)
        
        console.print(table)
    
    return is_configured

def test_enterprise_provider_direct():
    """Test enterprise provider directly (if configured)"""
    console = Console()
    
    if not is_enterprise_configured():
        console.print("\n🏢 Enterprise not configured - skipping direct provider test")
        return False
    
    console.print("\n🏢 Testing Enterprise LLM Provider directly...")
    
    try:
        # Create enterprise provider
        enterprise_config = {
            'token_url': os.getenv('ENTERPRISE_TOKEN_URL'),
            'chat_url': os.getenv('ENTERPRISE_CHAT_URL'),
            'app_id': os.getenv('ENTERPRISE_APP_ID'),
            'app_key': os.getenv('ENTERPRISE_APP_KEY'),
            'app_resource': os.getenv('ENTERPRISE_APP_RESOURCE')
        }
        
        provider = EnterpriseLLMProvider(enterprise_config)
        
        # Test connection
        console.print("🔐 Testing enterprise authentication and chat...")
        test_messages = [{"role": "user", "content": "Hello, respond with just 'Enterprise OK'"}]
        
        response = provider.chat(test_messages, debug=True)
        console.print(f"✅ Enterprise LLM test successful: {response}")
        return True
        
    except Exception as e:
        console.print(f"❌ Enterprise LLM test failed: {e}")
        return False

def test_llm_router_with_enterprise():
    """Test LLM router with enterprise backend"""
    console = Console()
    
    if not config.is_enterprise_configured():
        console.print("\n🏢 Enterprise not configured - skipping router test")
        return False
    
    console.print("\n🚀 Testing LLM Router with Enterprise backend...")
    
    try:
        # Force enterprise backend
        router = LLMRouter(backend="enterprise")
        
        # Test simple chat
        test_messages = [{"role": "user", "content": "Say 'Router Enterprise OK'"}]
        response = router.chat(test_messages)
        
        console.print(f"✅ LLM Router enterprise test successful: {response}")
        return True
        
    except Exception as e:
        console.print(f"❌ LLM Router enterprise test failed: {e}")
        return False

def test_backend_selection():
    """Test automatic backend selection with enterprise"""
    console = Console()
    
    console.print("\n🎯 Testing Backend Selection...")
    
    available_backends = config.get_available_backends()
    console.print(f"Available backends: {available_backends}")
    
    # Test auto backend selection
    router = LLMRouter(backend="auto")
    
    if available_backends:
        try:
            test_messages = [{"role": "user", "content": "Hello from auto-selection"}]
            response = router.chat(test_messages)
            console.print(f"✅ Auto backend selection successful: {response[:50]}...")
            return True
        except Exception as e:
            console.print(f"❌ Auto backend selection failed: {e}")
            return False
    else:
        console.print("❌ No backends available for testing")
        return False

def create_enterprise_env_example():
    """Create enterprise .env file example"""
    console = Console()
    
    console.print("\n📝 Creating enterprise .env file example...")
    
    enterprise_env_content = """# Enterprise LLM Configuration Example
# Copy this to .env and fill in your enterprise details

# Enterprise Authentication & Chat URLs
ENTERPRISE_TOKEN_URL=https://your-enterprise-domain.com/api/auth/token
ENTERPRISE_CHAT_URL=https://your-enterprise-domain.com/api/chat/completions

# Enterprise Application Credentials
ENTERPRISE_APP_ID=your-application-id
ENTERPRISE_APP_KEY=your-application-key-or-secret
ENTERPRISE_APP_RESOURCE=your-resource-identifier

# Optional: Enterprise Model Name
ENTERPRISE_MODEL=your-enterprise-model-name

# Force enterprise backend (optional)
# LUMOS_BACKEND=enterprise

# Keep OpenAI config for personal laptop use
# LLM_API_URL=https://api.openai.com/v1/chat/completions
# LLM_API_KEY=sk-your-openai-key

# Ollama for local development
# OLLAMA_URL=http://localhost:11434
"""
    
    with open(".env.enterprise.example", "w") as f:
        f.write(enterprise_env_content)
    
    console.print("✅ Created .env.enterprise.example file")
    console.print("📋 Copy to .env and configure for your enterprise environment")

def main():
    """Run all enterprise tests"""
    console = Console()
    
    console.print(Panel("🏢 Enterprise LLM Integration Test Suite", style="bold blue"))
    
    results = {}
    
    # Test 1: Configuration
    results['config'] = test_enterprise_configuration()
    
    # Test 2: Direct provider (if configured)  
    results['provider'] = test_enterprise_provider_direct()
    
    # Test 3: Router integration (if configured)
    results['router'] = test_llm_router_with_enterprise()
    
    # Test 4: Backend selection
    results['selection'] = test_backend_selection()
    
    # Create enterprise example
    create_enterprise_env_example()
    
    # Summary
    console.print("\n📊 Test Results Summary:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL" 
        console.print(f"  {test_name.title()}: {status}")
    
    if any(results.values()):
        console.print("\n🎉 Some enterprise features are working!")
    else:
        console.print("\n⚠️  Enterprise not configured - see .env.enterprise.example")
    
    return results

if __name__ == "__main__":
    main()