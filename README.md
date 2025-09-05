# Lumos CLI ✨

A smart CLI-based LLM code assistant that brings the power of AI to your command line. Built for developers who want fast, context-aware code assistance without leaving the terminal.

## 🚀 Features

### Smart Model Routing
- **Automatic task detection** - Analyzes your requests to choose the best model
- **Multi-backend support** - Works with OpenAI, Enterprise LLMs, and local Ollama
- **Enterprise-ready** - Custom authentication flow for corporate environments
- **Optimized performance** - Fast local models for code tasks, powerful remote models for planning

### Safety & Preview System  
- **Diff previews** - See exactly what will change before applying
- **Automatic backups** - Timestamped backups before any modification
- **Syntax validation** - Warns about potential syntax errors
- **Easy rollback** - Restore from backups with simple commands

### Context-Aware Code Understanding
- **Semantic search** - Finds relevant code using embeddings
- **Multi-language support** - Python, JavaScript, TypeScript, Go, PowerShell
- **Repository indexing** - Understands your entire codebase

### Repository-Aware Persistent History
- **Multi-repository isolation** - Each repo has separate chat history
- **Smart summarization** - Automatically compresses long conversations
- **Session management** - Organize conversations by topics/sessions
- **Full-text search** - Find past conversations and solutions
- **Cross-session context** - Maintains context across all interactions

### Intelligent Repository Personas
- **Automatic project detection** - Analyzes languages, frameworks, dependencies
- **Dynamic system prompts** - Tailored instructions per project type
- **Framework-aware assistance** - Django vs Flask, React vs Vue, etc.
- **Dependency-aware suggestions** - Understands your tech stack
- **Caching & performance** - Fast context retrieval with smart caching

## 🛠 Installation

```bash
# Clone the repository
git clone <repository-url>
cd llm_cli_scaffold_full

# Install in development mode
pip install -e .
```

## ⚙️ Configuration

Set up your environment variables:

```bash
# For OpenAI/External API (Personal Use)
export LLM_API_URL="https://api.openai.com/v1/chat/completions"
export LLM_API_KEY="your-api-key"

# For Enterprise LLM (Corporate Environment)
export ENTERPRISE_TOKEN_URL="https://your-enterprise.com/api/auth/token"
export ENTERPRISE_CHAT_URL="https://your-enterprise.com/api/chat/completions"
export ENTERPRISE_APP_ID="your-app-id"
export ENTERPRISE_APP_KEY="your-app-key"
export ENTERPRISE_APP_RESOURCE="your-resource"

# Backend selection (auto, openai, enterprise, ollama)
export LUMOS_BACKEND="auto"

# Embedding database location (optional)
export LLM_EMBED_DB=".lumos_embeddings.db"
```

## 🎯 Usage

### 🌟 Interactive Mode (Recommended)

```bash
# Start interactive assistant (like Claude Code)
lumos-cli

# Now you can chat naturally:
🤖 You: add error handling
🤖 You: plan user authentication  
🤖 You: review api.py
🤖 You: how do I implement JWT tokens?
```

### 📝 Smart File Discovery

```bash
# No file path needed - smart discovery finds relevant files
lumos-cli edit "add error handling"
lumos-cli edit "implement authentication"
lumos-cli edit "add logging to database operations"

# Still works with specific files
lumos-cli edit "add validation" --path src/auth.py
```

### 🔧 Command Mode

```bash
# Index your codebase
lumos-cli index

# Plan a feature implementation
lumos-cli plan "add user authentication system"

# Review code for issues
lumos-cli review src/auth.py

# Debug a specific problem
lumos-cli debug src/auth.py "login function not working"

# Traditional chat mode
lumos-cli chat --session session_20240905_120000
```

### Safety Commands

```bash
# List available backups
lumos-cli backups

# List backups for specific file
lumos-cli backups src/auth.py  

# Restore from backup
lumos-cli restore .llm_backups/auth.py.20240905_120000.bak
```

### History & Session Commands

```bash
# Show repository chat history statistics  
lumos-cli history

# List all chat sessions for current repo
lumos-cli sessions

# Search chat history
lumos-cli search "authentication bug"

# List all repositories with history
lumos-cli repos

# Clean up old sessions (30+ days)
lumos-cli cleanup --days 30 --no-dry-run
```

### Project Scaffolding

```bash
# List available project templates
lumos-cli templates

# Create new Python CLI project
lumos-cli scaffold python-cli my-app

# Create Node.js Express web app
lumos-cli scaffold node-web-express my-server

# Preview without creating (dry run)
lumos-cli scaffold python-web-fastapi api --dry-run
```

### Persona & Context Commands

```bash
# Show current repository analysis
lumos-cli persona --action show

# Refresh repository context (re-analyze)
lumos-cli persona --action refresh

# Show current system prompt 
lumos-cli context

# Show persona cache statistics
lumos-cli persona --action cache
```

### Command Options

```bash
# Force changes without preview
lumos-cli edit file.py "changes" --force

# Disable preview
lumos-cli edit file.py "changes" --no-preview

# Use specific backend
lumos-cli plan "feature" --backend rest
lumos-cli plan "feature" --backend ollama

# Use specific model  
lumos-cli edit file.py "changes" --model codellama
```

## 🧠 Smart Routing

Lumos automatically chooses the best model for each task:

| Task Type | Model Choice | Reason |
|-----------|--------------|---------|
| Code Generation | Local (Devstral) | Fast, excellent at code |
| Code Review | Local (Devstral) | Quick feedback loops |
| Debugging | Local (Devstral) | Immediate assistance |
| Planning | Enterprise/OpenAI | High-level reasoning |
| Architecture | Enterprise/OpenAI | Complex explanations |

## 🏢 Enterprise LLM Support

Lumos CLI supports enterprise LLM deployments with custom authentication:

### **Enterprise Configuration**
```bash
# Required enterprise variables
ENTERPRISE_TOKEN_URL=https://your-corp.com/api/auth/token
ENTERPRISE_CHAT_URL=https://your-corp.com/api/chat/completions  
ENTERPRISE_APP_ID=your-app-identifier
ENTERPRISE_APP_KEY=your-app-secret
ENTERPRISE_APP_RESOURCE=your-resource-id

# Force enterprise backend
LUMOS_BACKEND=enterprise
```

### **Enterprise Features**
- **🔐 Token-based Authentication** - Automatic bearer token management
- **🏢 Corporate API Integration** - Works with any enterprise LLM endpoint
- **🔄 Auto Token Refresh** - Handles token expiration transparently  
- **🛡️ Secure Credential Handling** - No hardcoded secrets
- **📋 Dual Configuration** - Personal laptop + enterprise deployment

### **Testing Enterprise Setup**
```bash
# Test enterprise configuration
python test_enterprise_llm.py

# Check configuration status
lumos-cli config-show
```

## 🔒 Safety Features

- **Preview diffs** before applying any changes
- **Automatic backups** with timestamps
- **Syntax validation** for common languages
- **User confirmation** for destructive operations
- **Easy rollback** from backups

## 📁 Project Structure

```
src/lumos_cli/
├── cli.py          # Main CLI interface
├── client.py       # LLM routing and API calls
├── embeddings.py   # Code indexing and search
├── prompts.py      # Prompt templates
└── safety.py       # Preview and backup system
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python test_routing.py` and `python test_safety_preview.py`
5. Submit a pull request

## 📝 Examples

### Planning a Feature
```bash
$ lumos-cli plan "add rate limiting to API endpoints"
# Uses REST API for high-level architecture planning
```

### Quick Code Fix  
```bash
$ lumos-cli edit api.py "fix the memory leak in process_request"
# Uses local Devstral for fast code generation
```

### Safe Editing with Preview
```bash
$ lumos-cli preview auth.py "add JWT token validation"
# Shows diff, then ask if you want to apply
```

## 🎉 Why "Lumos"?

Lumos (Latin for "light") illuminates your code with AI assistance - bringing clarity to complex development tasks while keeping you in control with smart safety features.

---

*✨ Illuminate your code with AI - Fast, Safe, Smart*