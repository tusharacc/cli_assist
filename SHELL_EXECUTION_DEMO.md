# 🖥️ Shell Command Execution - Lumos CLI

## ✅ **Feature Complete!**

Lumos CLI now supports **safe shell command execution with user confirmation**! Users can run shell/cmd commands through multiple intuitive methods while maintaining security through intelligent safety checks.

## 🚀 **How to Use**

### 1. **Direct Shell Command**
```bash
# Execute with confirmation
lumos-cli shell --command "git status"
lumos-cli shell --command "npm install"  
lumos-cli shell --command "ls -la"

# Interactive command input
lumos-cli shell
# Then enter your command when prompted
```

### 2. **Interactive Mode - Natural Language**
```bash
lumos-cli chat  # Start interactive mode

# Then use natural language:
You: "git status"
You: "execute ls -la" 
You: "run npm install"
You: "shell docker ps"
```

### 3. **Interactive Mode - Slash Commands**
```bash
lumos-cli chat  # Start interactive mode

# Direct slash commands:
You: "/shell git status"
You: "/shell ls -la"  
You: "/shell docker ps"
```

## 🔒 **Safety Features**

### **Dangerous Command Detection**
The system automatically detects and warns about potentially dangerous commands:

- ✅ **Very Dangerous**: `rm -rf`, `format c:`, `dd if=`, etc.
- ⚠️ **Potentially Dangerous**: `sudo`, `pip install`, `curl`, etc.
- 🆘 **Extra Confirmation**: Dangerous commands require typing the full command to confirm

### **Safety Warnings Example**
```
🔧 Command to Execute: sudo apt update

🚨 Safety Warning
⚠️  WARNING: Potentially dangerous: 'sudo' command  
This command may modify your system or files!

Are you sure you want to run this potentially dangerous command? [y/N]
```

### **Command Preview**
Every command shows a preview before execution:
```
Context: User requested shell command execution via Lumos CLI

🔧 Command to Execute
git status

Working directory: /Users/username/project
Execute this command? [y/n] (y):
```

## 🎯 **Supported Commands**

### **Automatically Detected Shell Commands**
- **File Operations**: `ls`, `cd`, `pwd`, `mkdir`, `cp`, `mv`
- **Git Commands**: `git status`, `git add`, `git commit`, etc.
- **Package Managers**: `npm`, `pip`, `yarn` (with safety warnings)
- **System Tools**: `ps`, `top`, `grep`, `cat`, `tail`
- **Development**: `python`, `node`, `java`, `docker`, `kubectl`
- **Network**: `curl`, `wget`, `ssh` (with safety warnings)

### **Command Pattern Matching**
The system recognizes these patterns:
- Direct commands: `ls -la`
- Prefixed commands: `run ls -la`, `execute git status`, `shell docker ps`
- Natural expressions: "can you run git status" → `git status`

## 🛡️ **Security Features**

### **1. Dangerous Pattern Detection**
```python
# These patterns trigger extra security:
'rm -rf', 'sudo', 'del /s', 'format c:', 'dd if=', 
'--force', 'curl | sh', 'chmod 777', etc.
```

### **2. Safe Alternative Suggestions**
For dangerous commands, the system suggests safer alternatives:
```
Suggestions for 'rm -rf tmp/':
• Use 'ls' first to see what will be deleted
• Consider using a trash/recycle bin instead  
• Use 'rm' without -rf to delete files individually
```

### **3. Working Directory Display**
Always shows the working directory where commands will execute:
```
Working directory: /Users/username/my-project
```

### **4. Real-time Output**
Commands show output in real-time as they execute, with clear success/failure indicators.

## 📋 **Example Usage Scenarios**

### **Scenario 1: Git Workflow**
```bash
lumos-cli chat
You: "git status"
🔧 Command Preview: git status  
Execute this command? [y/n] (y): y
✅ Command executed successfully!

You: "git add ."  
🔧 Command Preview: git add .
Execute this command? [y/n] (y): y  
✅ Command executed successfully!
```

### **Scenario 2: Development Setup**
```bash  
You: "npm install"
⚠️  WARNING: Potentially dangerous: 'npm' command
This command may modify your system or files!
Execute this command? [y/n] (y): y
✅ Command executed successfully!
```

### **Scenario 3: System Information**
```bash
You: "ls -la"
🔧 Command Preview: ls -la
Execute this command? [y/n] (y): y
[Output shows file listing]
✅ Command executed successfully!

You: "pwd"  
🔧 Command Preview: pwd
Execute this command? [y/n] (y): y
/Users/username/my-project
✅ Command executed successfully!
```

## 🔧 **Technical Implementation**

### **Components Added**:
1. **`shell_executor.py`** - Core execution engine with safety checks
2. **Shell command detection** in `_detect_command_intent()`  
3. **Interactive shell handler** `_interactive_shell()`
4. **CLI shell command** via typer
5. **`/shell` slash command** for direct access

### **Safety Architecture**:
- **Pre-execution analysis** of command patterns
- **User confirmation prompts** with context
- **Real-time output streaming** 
- **Exit code handling** and error reporting
- **Command history tracking** for context

## 🎉 **Benefits**

✅ **Seamless Integration**: Works naturally within Lumos CLI workflow  
✅ **Multiple Access Methods**: Natural language, slash commands, direct CLI  
✅ **Enhanced Security**: Intelligent dangerous command detection  
✅ **User-Friendly**: Clear previews and confirmations  
✅ **Real-time Feedback**: Live command output and status  
✅ **Cross-Platform**: Works on Windows (cmd) and Unix-like systems (bash)

## 🚀 **Ready to Use!**

The shell command execution feature is **fully implemented and tested**. Users can now safely run shell commands through Lumos CLI with intelligent confirmation and safety checks!

**Try it now:**
```bash
lumos-cli chat
You: "ls -la"
# Watch the magic happen! 🪄
```