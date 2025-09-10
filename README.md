# 🌟 Lumos CLI - Interactive AI Code Assistant

A powerful, modular AI-powered command-line interface that integrates with enterprise tools like GitHub, Jenkins, Jira, Neo4j, and AppDynamics. Built with a clean, maintainable architecture and designed for developers and Site Reliability Engineers.

## 🚀 Quick Start

```bash
# Install
pip install -e .

# Start interactive mode
lumos-cli

# Get help
lumos-cli --help
```

## ✨ Key Features

- **🤖 Multi-LLM Support**: OpenAI GPT-3.5/4, Ollama (devstral, llama3.2), Hugging Face, Enterprise LLM
- **🔗 Enterprise Integrations**: GitHub, Jenkins, Jira, Neo4j, AppDynamics
- **🧠 Unified LLM-Based Keyword Detection**: Intelligent natural language processing for all integrations
- **💬 Interactive Mode**: Natural language command processing with console clearing
- **🛠️ Code Management**: Generation, editing, testing, analysis with detailed commit analysis
- **🔒 Safety Features**: File validation, backup, rollback
- **📊 Debug Logging**: Centralized logging with platform-specific paths
- **⚙️ Configuration Management**: Secure credential storage
- **🔍 Neo4j Graph Analysis**: LLM-generated Cypher queries for complex graph operations
- **📈 Rich Data Visualization**: Beautiful tables, charts, and formatted output

## 🏗️ Architecture

Lumos CLI follows a clean, modular architecture:

```
src/lumos_cli/
├── core/                    # Core functionality (router, embeddings, safety, history)
├── clients/                 # External service clients (GitHub, Jenkins, Jira, Neo4j, AppDynamics)
├── config/                  # Configuration management
├── utils/                   # Shared utilities
├── ui/                      # User interface components
├── interactive/             # Interactive mode with handlers
├── commands/                # Command modules (GitHub, Jenkins)
└── cli_refactored_v2.py     # Main CLI entry point
```

## 📚 Documentation

### 🚀 Getting Started
- [Essential Features](docs/ESSENTIAL_FEATURES.md) - Core functionality overview
- [Windows Install Guide](docs/WINDOWS_INSTALL_GUIDE.md) - Windows-specific installation
- [Shell Execution Demo](docs/SHELL_EXECUTION_DEMO.md) - Command execution examples

### 🏗️ Technical Documentation
- [Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md) - System architecture and design
- [Module Functionality](docs/MODULE_FUNCTIONALITY.md) - Detailed module reference
- [System Flow Diagrams](docs/SYSTEM_FLOW_DIAGRAMS.md) - Data flow and process diagrams
- [Testing Guide](docs/TESTING_GUIDE.md) - Comprehensive testing documentation

### 🔧 Integrations
- [GitHub Integration](docs/GITHUB_INTEGRATION.md) - GitHub API integration and PR/commit management
- [Jenkins Integration](docs/JENKINS_INTEGRATION.md) - Jenkins build monitoring and failure analysis
- [Neo4j Integration](docs/NEO4J_INTEGRATION.md) - Graph database analysis with LLM-generated queries
- [AppDynamics Integration](docs/APPDYNAMICS_TEST_README.md) - Application performance monitoring

### 🧠 AI & Intelligence
- [Agentic Architecture](docs/AGENTIC_ARCHITECTURE.md) - AI agent design patterns
- [Intent Consolidation Plan](docs/INTENT_CONSOLIDATION_PLAN.md) - Command intent system
- [Enterprise LLM Replica Setup](docs/ENTERPRISE_LLM_REPLICA_SETUP.md) - Local LLM simulation

### 🛠️ Development & Debugging
- [Comprehensive Debugging Guide](docs/COMPREHENSIVE_DEBUGGING_GUIDE.md) - Debug logging and troubleshooting
- [Enhanced App Detection](docs/ENHANCED_APP_DETECTION.md) - Project type detection
- [Code Editing Analysis](docs/CODE_EDITING_ANALYSIS.md) - Code modification capabilities
- [Refactoring Plan](docs/REFACTORING_PLAN.md) - Architecture refactoring details

## 🎯 Usage Examples

### Interactive Mode
```bash
lumos-cli
# Then use natural language:
# "get me the latest PR from microsoft/vscode"
# "show failed Jenkins builds in the last 4 hours"
# "analyze commit abc123def from scimarketplace/externaldata"
# "find all classes that depend on UserService through 2 levels"
# "list all repositories in Neo4j"
# "what classes are most connected in the graph"
```

### Command Line
```bash
# GitHub operations
lumos-cli github-pr microsoft vscode
lumos-cli github-clone microsoft vscode

# Jenkins operations
lumos-cli jenkins-failed-jobs 4
lumos-cli jenkins-running-jobs

# Configuration
lumos-cli github-config
lumos-cli jenkins-config
```

## 🔧 Configuration

Lumos CLI supports multiple configuration methods:

1. **Environment Variables**: Set API keys and URLs
2. **Interactive Setup**: Use `lumos-cli <service>-config` commands
3. **Configuration Files**: Stored securely in platform-specific locations

### Supported Services
- **GitHub**: Personal Access Tokens, Enterprise instances
- **Jenkins**: Access tokens, custom job folders
- **Jira**: Personal Access Tokens, Bearer authentication
- **Neo4j**: Local and remote graph databases
- **AppDynamics**: OAuth2 authentication, multiple instances
- **Enterprise LLM**: OAuth2 with custom endpoints

## 🧪 Testing

### Quick Testing (Recommended)
```bash
# Quick functionality test (fastest)
make test-quick

# Or using Python directly
python test_lumos.py --quick
```

### Comprehensive Testing
```bash
# Run all tests
make test-all

# Test specific features
make test-feature FEATURE=github
make test-feature FEATURE=jenkins

# Test categories
make test-unit              # Unit tests only
make test-integration       # Integration tests
make test-smoke            # Smoke test
```

### Available Test Commands
```bash
make help                   # Show all test commands
make test-quick            # Quick functionality test
make test-all              # Comprehensive test suite
make cli-test              # Test CLI basic functionality
make cli-help              # Show CLI help
```

For detailed testing information, see the [Testing Guide](docs/TESTING_GUIDE.md).

## 📁 Project Structure

```
├── src/lumos_cli/          # Main source code
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── functional/        # Functional tests
├── docs/                  # Documentation
├── demos/                 # Demo scripts
├── scripts/               # Utility scripts
└── README.md              # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues, questions, or contributions:
- Check the [Comprehensive Debugging Guide](docs/COMPREHENSIVE_DEBUGGING_GUIDE.md)
- Review the [Essential Features](docs/ESSENTIAL_FEATURES.md)
- Open an issue on GitHub

---

**Built with ❤️ for developers and SREs who want AI-powered productivity tools.**