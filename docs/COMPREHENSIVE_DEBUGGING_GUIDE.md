# 🔧 Comprehensive Debugging Guide - Lumos CLI

This guide covers both the enhanced debugging features and debug logging capabilities in Lumos CLI.

## Table of Contents
1. [Enhanced Debugging Features](#enhanced-debugging-features)
2. [Debug Logging System](#debug-logging-system)
3. [Integration Debugging](#integration-debugging)
4. [Troubleshooting](#troubleshooting)
5. [Getting Started](#getting-started)

---

## Enhanced Debugging Features

### Problem: Manual Code Snippets Required ❌

**Before Enhancement:**
```
You: "My app has a bug in the login function"
Lumos: "Please provide the code snippet for analysis"
You: *manually copies and pastes code*
```

### Solution: Automatic File Discovery & Analysis ✅

**After Enhancement:**
```
You: "My app has a bug in the login function" 
Lumos: 🔍 Analyzing your request and searching for relevant files...
       📂 Found 3 potentially relevant files
       📖 Analyzed: src/auth.py (score: 8.5)
       📖 Analyzed: src/user.py (score: 7.2)  
       📖 Analyzed: config/auth_config.py (score: 6.8)
       
       [Provides detailed analysis and solution based on actual code]
```

### How Enhanced Debugging Works

#### 1. **Intelligent Request Detection**
Lumos CLI automatically detects when you're describing bugs or issues:

**Detected Patterns:**
- "My app has a bug"
- "There is an error in my code"
- "Why is my function not working?"
- "Help me debug this issue"  
- "Cannot connect to the database"
- "The login.py file is broken"
- "My API returns wrong data"

#### 2. **Smart File Discovery**
When debugging is detected, Lumos CLI:
- Analyzes your description using natural language processing
- Searches your codebase for relevant files
- Scores files based on relevance to your issue
- Automatically reads the top 3 most relevant files

#### 3. **Comprehensive Code Analysis**
Instead of asking for snippets, Lumos CLI:
- Reads the full file contents
- Understands the context and structure  
- Provides detailed analysis based on actual code
- Suggests specific fixes with line references

---

## Debug Logging System

### Overview

Debug logging has been added to both GitHub and Jenkins integrations to help trace function calls, URL construction, and API requests. All logs are written to disk files for detailed analysis.

### Log File Locations

#### Windows
```
%APPDATA%\Lumos\Logs\
```
**Example:** `C:\Users\YourUsername\AppData\Roaming\Lumos\Logs\`

#### macOS/Linux
```
~/.lumos/logs/
```
**Example:** `/home/username/.lumos/logs/`

### Log File Format

Log files are created with timestamps:
- `lumos-debug-YYYYMMDD_HHMMSS.log`

Example: `lumos-debug-20250906_143022.log`

### What Gets Logged

#### GitHub Client
- Function calls with parameters
- URL construction details
- HTTP request/response information
- Authentication setup
- Error details

#### Jenkins Client
- Function calls with parameters
- API path construction
- HTTP request/response information
- Authentication setup
- Error details

### Log Levels

- **DEBUG**: Detailed function call traces, URL construction, parameter details
- **INFO**: High-level operations, configuration loading
- **WARNING**: Non-critical issues
- **ERROR**: Critical errors and exceptions

### Example Log Output

```
2025-09-06 14:30:22 - lumos_debug - INFO - GitHubClient.__init__:25 - Using config file: base_url=https://api.github.com, token=***
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient.__init__:47 - Session headers set: {'Authorization': 'token ***', 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Lumos-CLI/1.0'}
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient.list_pull_requests:151 - 🔍 CALL: GitHubClient.list_pull_requests({'org': 'microsoft', 'repo': 'vscode', 'state': 'open', 'head': None, 'base': None})
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._get_api_endpoint:53 - 🔍 CALL: GitHubClient._get_api_endpoint({'operation': 'list_pull_requests', 'org': 'microsoft', 'repo': 'vscode'})
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._get_fallback_endpoint:63 - 🔍 CALL: GitHubClient._get_fallback_endpoint({'operation': 'list_pull_requests', 'org': 'microsoft', 'repo': 'vscode'})
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._get_fallback_endpoint:69 - Constructed list_pull_requests endpoint: /repos/microsoft/vscode/pulls
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._make_request:113 - 🔍 CALL: GitHubClient._make_request({'endpoint': '/repos/microsoft/vscode/pulls', 'params': {'state': 'open'}})
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._make_request:116 - 🌐 URL CONSTRUCTION:
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._make_request:117 -    Base URL: https://api.github.com
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._make_request:117 -    Endpoint: /repos/microsoft/vscode/pulls
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._make_request:117 -    Params: {'state': 'open'}
2025-09-06 14:30:22 - lumos_debug - DEBUG - GitHubClient._make_request:117 -    Full URL: https://api.github.com/repos/microsoft/vscode/pulls?state=open
```

---

## Integration Debugging

### GitHub Integration Debugging

#### Common Issues to Look For
- **Empty org/repo parameters**: Look for `org=''` or `repo=''` in logs
- **Malformed endpoints**: Check the constructed endpoint path
- **Missing parameters**: Verify all required parameters are passed
- **Authentication issues**: Check token and base URL configuration

#### Debugging URL Construction Issues
1. **Check the logs** for the exact URL being constructed
2. **Look for parameter passing** issues in function calls
3. **Verify base URL** configuration
4. **Check for missing parameters** in endpoint construction

### Jenkins Integration Debugging

#### Common Issues to Look For
- **Connection failures**: Check Jenkins URL and authentication
- **API path construction**: Verify folder path conversion
- **Authentication errors**: Check token and username configuration
- **Network issues**: Verify Jenkins server accessibility

---

## Example Debugging Scenarios

### Scenario 1: Database Connection Issue
```bash
# Your input
You: "Cannot connect to my SQLite database, getting errors"

# Lumos CLI's automatic response:
🔍 Analyzing your request and searching for relevant files...
📂 Found 4 potentially relevant files
📖 Analyzed: database.py (score: 9.1)
📖 Analyzed: models/user.py (score: 7.8)  
📖 Analyzed: config/db_config.py (score: 7.2)

# Analysis with actual code
Based on your database.py file, I found several issues:

1. Line 15: Database path missing .db extension
   ❌ self.db_path = "users" 
   ✅ self.db_path = "users.db"

2. Line 23: SQL syntax error - missing comma
   ❌ CREATE TABLE users (id INTEGER PRIMARY KEY name TEXT...)
   ✅ CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT...)
   
3. Line 45: SQL injection vulnerability
   ❌ cursor.execute(f"INSERT INTO users VALUES ('{name}')")
   ✅ cursor.execute("INSERT INTO users VALUES (?)", (name,))

[Provides complete fixed code]
```

### Scenario 2: GitHub API URL Construction Issue
```bash
# Your input
You: "GitHub PR command is giving 404 errors"

# Lumos CLI's automatic response:
🔍 Analyzing your request and searching for relevant files...
📂 Found 2 potentially relevant files
📖 Analyzed: src/lumos_cli/github_client.py (score: 9.5)
📖 Analyzed: src/lumos_cli/cli.py (score: 7.8)

# Analysis with debug logs
Based on the debug logs, I found the issue:

The URL construction is actually working correctly:
✅ Base URL: https://api.github.com
✅ Endpoint: /repos/microsoft/vscode/pulls
✅ Full URL: https://api.github.com/repos/microsoft/vscode/pulls?state=open

The 404 error might be due to:
1. Repository doesn't exist
2. Token doesn't have access
3. Branch name is incorrect

[Provides specific troubleshooting steps]
```

### Scenario 3: Jenkins Connection Issue
```bash
# Your input
You: "Jenkins integration is not connecting"

# Lumos CLI's automatic response:
🔍 Analyzing your request and searching for relevant files...
📂 Found 3 potentially relevant files
📖 Analyzed: src/lumos_cli/jenkins_client.py (score: 9.2)
📖 Analyzed: src/lumos_cli/jenkins_config_manager.py (score: 8.1)
📖 Analyzed: src/lumos_cli/cli.py (score: 6.9)

# Analysis with debug logs
Based on the debug logs, I found the issue:

❌ Jenkins connection error: JENKINS_URL environment variable is required
❌ Using Jenkins environment variables: base_url=None, username=None, token=None

Solution:
1. Configure Jenkins integration: lumos-cli jenkins-config
2. Set environment variables:
   export JENKINS_URL=https://your-jenkins.com
   export JENKINS_TOKEN=your_token_here
   export JENKINS_USERNAME=your_username

[Provides step-by-step configuration guide]
```

---

## Troubleshooting

### Debugging Keywords Detected
```
bug, error, issue, problem, broken, not working, failing,
exception, crash, traceback, fix, debug, solve, resolve,
wrong, incorrect, unexpected, doesn't work, failed,  
cannot, won't, timeout, connection, unresponsive
```

### Question Patterns Detected
```  
"why is...", "why doesn't...", "what is wrong...",
"how to fix...", "help with...", "having trouble..."
```

### Testing Debug Logging

Run the test script to see debug logging in action:

```bash
python test_debug_logging.py
```

This will:
1. Show log file locations for your platform
2. Test GitHub client with debug logging
3. Test Jenkins client with debug logging
4. Create log files you can examine

### Disabling Debug Logging

To disable debug logging, you can modify the `debug_logger.py` file and change the log level:

```python
# Change this line in debug_logger.py
self.logger.setLevel(logging.INFO)  # Instead of logging.DEBUG
```

### Log Rotation

Log files are created with timestamps, so they won't overwrite each other. For production use, consider implementing log rotation to manage disk space.

### Security Note

Debug logs may contain sensitive information like API tokens (partially masked) and URLs. Ensure log files are stored securely and not shared publicly.

---

## Getting Started

### Test the Enhanced Debugging:

1. **Start Lumos CLI interactive mode:**
   ```bash
   lumos-cli
   ```

2. **Describe your bug naturally:**
   ```
   You: "My database connection is failing"
   You: "There's a bug in my login function"  
   You: "Why isn't my API working?"
   You: "Help me debug this authentication issue"
   ```

3. **Watch Lumos CLI automatically:**
   - Detect the debugging request
   - Find relevant files in your codebase
   - Read and analyze the actual code
   - Provide specific solutions

### Test Demo App:
```bash  
# Run the demo app with intentional bugs
python demo_app.py

# Then ask Lumos CLI to help debug it:  
lumos-cli
You: "My demo_app.py has database errors"
```

### Test Integration Debugging:
```bash
# Test GitHub integration with debug logging
lumos-cli github-pr microsoft/vscode --branch main

# Test Jenkins integration with debug logging
lumos-cli jenkins-failed-jobs --folder scimarketplace/deploy-all

# Check the debug logs
ls ~/.lumos/logs/  # macOS/Linux
dir %APPDATA%\Lumos\Logs\  # Windows
```

**Your debugging workflow just became 10x faster!** 🚀

---

## Technical Implementation

### Enhanced Interactive Mode
- **Detection Algorithm**: Uses keyword matching + pattern recognition
- **File Discovery**: Leverages existing SmartFileDiscovery system  
- **Context Analysis**: Reads and analyzes up to 3 most relevant files
- **Smart Fallback**: Uses embedding search if no specific files found

### Debug Logging System
- **Centralized Logging**: Single logger instance for all integrations
- **Disk-based Storage**: Logs written to platform-specific directories
- **Function Tracing**: Complete call stack with parameters and return values
- **URL Construction**: Detailed API endpoint building process
- **Error Tracking**: Comprehensive error logging and analysis

### Benefits for Your Workflow

#### Before: Manual & Slow ❌
1. Describe issue to Lumos CLI
2. Lumos asks for code snippets  
3. You manually find and copy relevant files
4. Paste code snippets
5. Get analysis based on partial context

#### After: Automatic & Fast ✅
1. Describe issue to Lumos CLI
2. **Lumos automatically finds and reads relevant files**
3. **Get comprehensive analysis with full context**
4. **Receive specific fixes with file:line references**
5. **Debug logs provide detailed technical insights**
