
🪟 WINDOWS INSTALLATION GUIDE FOR LUMOS CLI

📦 Installation:
   1. Install Python 3.8+ from python.org
   2. Open Command Prompt or PowerShell as Administrator
   3. Run: pip install lumos-cli
   
🔧 Configuration:
   • Global config stored in: %APPDATA%\Lumos\config.json
   • Logs stored in: %LOCALAPPDATA%\Lumos\Logs
   • Cache stored in: %LOCALAPPDATA%\Lumos\Cache
   
⚡ Quick Setup:
   lumos-cli config set llm.rest_api_key sk-your-key-here
   lumos-cli config set llm.rest_api_url https://api.openai.com/v1/chat/completions
   
🤖 Optional - Install Ollama:
   • Download from: https://ollama.ai
   • Install to: C:\Program Files\Ollama
   • Add to PATH or use full path
   
🚀 Usage:
   • Open PowerShell or Command Prompt
   • Navigate to your project: cd C:\Users\YourName\Projects\MyProject
   • Run: lumos-cli
   
🔍 Troubleshooting:
   • Check platform info: lumos-cli platform
   • View debug info: lumos-cli debug
   • Check logs: lumos-cli logs
   
💡 Tips:
   • Use PowerShell for better experience
   • No need for .env files - global config works everywhere!
   • Run 'lumos-cli config list' to verify settings
