#!/usr/bin/env python3
"""
Setup script for Enterprise LLM Replica
Installs dependencies and tests the system
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Install basic requirements
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install Hugging Face requirements
    if not run_command("pip install -r requirements_huggingface.txt", "Installing Hugging Face dependencies"):
        return False
    
    # Install additional requirements
    additional_packages = [
        "rich",
        "typer",
        "requests",
        "python-dotenv"
    ]
    
    for package in additional_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: Failed to install {package}")
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    
    test_modules = [
        "transformers",
        "torch",
        "tokenizers",
        "datasets",
        "rich",
        "typer"
    ]
    
    failed_imports = []
    
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All imports successful")
    return True

def test_huggingface_models():
    """Test Hugging Face model loading"""
    print("\n🤖 Testing Hugging Face models...")
    
    try:
        from transformers import pipeline
        
        # Test a simple model
        print("🔄 Loading sentiment analysis model...")
        classifier = pipeline("sentiment-analysis")
        
        # Test the model
        result = classifier("I love this new system!")
        print(f"✅ Model test successful: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hugging Face model test failed: {e}")
        return False

def test_environment_detection():
    """Test environment detection"""
    print("\n🌍 Testing environment detection...")
    
    try:
        sys.path.append('src')
        from lumos_cli.environment_manager import get_environment_manager
        
        env_manager = get_environment_manager()
        env_manager.list_environments()
        
        print("✅ Environment detection successful")
        return True
        
    except Exception as e:
        print(f"❌ Environment detection failed: {e}")
        return False

def create_test_script():
    """Create a test script for the enterprise LLM replica"""
    test_script = """#!/usr/bin/env python3
\"\"\"
Test script for Enterprise LLM Replica
\"\"\"

import sys
sys.path.append('src')

def test_enterprise_llm_replica():
    \"\"\"Test the enterprise LLM replica system\"\"\"
    print("🧪 Testing Enterprise LLM Replica...")
    
    try:
        from lumos_cli.gpt4_simulator import get_gpt4_simulator
        from lumos_cli.enterprise_llm_replica import get_enterprise_llm_replica
        from lumos_cli.environment_manager import get_environment_manager
        
        # Test GPT-4 Simulator
        print("\\n1. Testing GPT-4 Simulator...")
        gpt4_simulator = get_gpt4_simulator()
        
        if gpt4_simulator.test_connection():
            print("✅ GPT-4 Simulator connection successful")
        else:
            print("❌ GPT-4 Simulator connection failed")
            return False
        
        # Test Enterprise LLM Replica
        print("\\n2. Testing Enterprise LLM Replica...")
        enterprise_llm = get_enterprise_llm_replica()
        
        if enterprise_llm.test_connection():
            print("✅ Enterprise LLM Replica connection successful")
        else:
            print("❌ Enterprise LLM Replica connection failed")
            return False
        
        # Test Environment Manager
        print("\\n3. Testing Environment Manager...")
        env_manager = get_environment_manager()
        env_manager.list_environments()
        
        # Test GPT-4 Simulator response
        print("\\n4. Testing GPT-4 Simulator response...")
        response = gpt4_simulator.generate_response(
            "Hello, can you introduce yourself?",
            task_type="general",
            max_tokens=100
        )
        print(f"GPT-4 Simulator response: {response[:200]}...")
        
        # Test Enterprise LLM response
        print("\\n5. Testing Enterprise LLM response...")
        enterprise_response = enterprise_llm.generate_response(
            "Explain the benefits of microservices architecture",
            max_tokens=100
        )
        print(f"Enterprise LLM response: {enterprise_response[:200]}...")
        
        print("\\n✅ Enterprise LLM Replica test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enterprise_llm_replica()
"""
    
    with open("test_enterprise_llm_replica.py", "w") as f:
        f.write(test_script)
    
    print("✅ Test script created: test_enterprise_llm_replica.py")

def main():
    """Main setup function"""
    print("🏢 Enterprise LLM Replica Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("❌ Import test failed")
        sys.exit(1)
    
    # Test Hugging Face models
    if not test_huggingface_models():
        print("⚠️  Hugging Face model test failed, but continuing...")
    
    # Test environment detection
    if not test_environment_detection():
        print("⚠️  Environment detection failed, but continuing...")
    
    # Create test script
    create_test_script()
    
    print("\n🎉 Enterprise LLM Replica setup completed!")
    print("\nNext steps:")
    print("1. Run: python test_enterprise_llm_replica.py")
    print("2. Test code generation and execution")
    print("3. Integrate with Lumos CLI")
    
    print("\n📚 Available models:")
    print("- microsoft/CodeGPT-small-py (Python code generation)")
    print("- microsoft/unixcoder-base (Code analysis)")
    print("- microsoft/codebert-base (Code review)")
    print("- Salesforce/codet5-base (Code refactoring)")
    print("- Salesforce/codegen-350M-mono (General code generation)")

if __name__ == "__main__":
    main()
