"""Generic project scaffolding system with safety features"""

import os
import json
import shutil
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.table import Table

console = Console()

class ProjectType(Enum):
    # Python
    PYTHON_CLI = "python-cli"
    PYTHON_WEB_FLASK = "python-web-flask"
    PYTHON_WEB_FASTAPI = "python-web-fastapi"
    PYTHON_LIB = "python-lib"
    
    # Node.js
    NODE_CLI = "node-cli"
    NODE_WEB_EXPRESS = "node-web-express"
    NODE_WEB_NEXT = "node-web-next"
    NODE_DESKTOP_ELECTRON = "node-desktop-electron"
    
    # Java
    JAVA_CLI = "java-cli"
    JAVA_WEB_SPRING = "java-web-spring"
    JAVA_LIB = "java-lib"
    
    # .NET Core
    DOTNET_CLI = "dotnet-cli"
    DOTNET_WEB_API = "dotnet-web-api"
    DOTNET_WEB_MVC = "dotnet-web-mvc"
    
    # PowerShell
    POWERSHELL_MODULE = "powershell-module"
    POWERSHELL_SCRIPT = "powershell-script"

@dataclass
class CommandStep:
    """Represents a single command to execute"""
    command: str
    args: List[str]
    description: str
    working_dir: Optional[str] = None
    required: bool = True
    
    def __str__(self):
        cmd = f"{self.command} {' '.join(self.args)}"
        if self.working_dir:
            cmd = f"cd {self.working_dir} && {cmd}"
        return cmd

@dataclass
class FileTemplate:
    """Represents a file to create"""
    path: str
    content: str
    description: str
    executable: bool = False

@dataclass
class ProjectTemplate:
    """Complete project template definition"""
    name: str
    description: str
    language: str
    project_type: ProjectType
    commands: List[CommandStep]
    files: List[FileTemplate]
    dependencies: List[str]
    post_setup_message: Optional[str] = None

class SafeCommandExecutor:
    """Safely execute commands with validation and sandboxing"""
    
    # Whitelist of allowed commands per language
    ALLOWED_COMMANDS = {
        "python": ["python", "pip", "poetry", "conda", "virtualenv", "mkdir", "touch"],
        "node": ["npm", "yarn", "pnpm", "node", "npx", "mkdir", "touch"],
        "java": ["java", "javac", "maven", "mvn", "gradle", "mkdir", "touch"],
        "dotnet": ["dotnet", "mkdir", "touch"],
        "powershell": ["powershell", "pwsh", "mkdir", "New-Item"],
        "git": ["git"],
        "system": ["mkdir", "touch", "cp", "mv"]
    }
    
    # Commands that require extra confirmation
    DANGEROUS_COMMANDS = ["rm", "del", "Remove-Item", "rmdir"]
    
    def __init__(self, working_dir: str, dry_run: bool = False):
        self.working_dir = os.path.abspath(working_dir)
        self.dry_run = dry_run
        self.executed_commands = []
    
    def is_command_allowed(self, command: str, language: str) -> bool:
        """Check if command is allowed for the given language"""
        allowed = self.ALLOWED_COMMANDS.get(language, [])
        system_allowed = self.ALLOWED_COMMANDS.get("system", [])
        git_allowed = self.ALLOWED_COMMANDS.get("git", [])
        
        return (command in allowed or 
                command in system_allowed or 
                command in git_allowed)
    
    def is_command_dangerous(self, command: str) -> bool:
        """Check if command is potentially dangerous"""
        return command in self.DANGEROUS_COMMANDS
    
    def execute_step(self, step: CommandStep, language: str) -> bool:
        """Execute a single command step safely"""
        if not self.is_command_allowed(step.command, language):
            console.print(f"[red]❌ Command not allowed: {step.command}[/red]")
            return False
        
        if self.is_command_dangerous(step.command):
            if not Confirm.ask(f"⚠️  Execute potentially dangerous command: {step}?"):
                console.print("[yellow]Skipped dangerous command[/yellow]")
                return True
        
        work_dir = step.working_dir or self.working_dir
        
        if self.dry_run:
            console.print(f"[dim]DRY RUN: {step}[/dim]")
            return True
        
        try:
            console.print(f"[blue]▶ {step.description}[/blue]")
            console.print(f"[dim]  {step}[/dim]")
            
            result = subprocess.run(
                [step.command] + step.args,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                console.print(f"[green]✅ {step.description}[/green]")
                if result.stdout.strip():
                    console.print(f"[dim]{result.stdout.strip()}[/dim]")
            else:
                console.print(f"[red]❌ {step.description} failed[/red]")
                if result.stderr:
                    console.print(f"[red]{result.stderr.strip()}[/red]")
                return False
            
            self.executed_commands.append(step)
            return True
            
        except subprocess.TimeoutExpired:
            console.print(f"[red]❌ Command timed out: {step}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]❌ Error executing {step}: {e}[/red]")
            return False

class ProjectScaffolder:
    """Main scaffolding system"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[ProjectType, ProjectTemplate]:
        """Load all project templates"""
        templates = {}
        
        # Python templates
        templates[ProjectType.PYTHON_CLI] = self._python_cli_template()
        templates[ProjectType.PYTHON_WEB_FLASK] = self._python_flask_template()
        templates[ProjectType.PYTHON_WEB_FASTAPI] = self._python_fastapi_template()
        templates[ProjectType.PYTHON_LIB] = self._python_lib_template()
        
        # Node.js templates
        templates[ProjectType.NODE_CLI] = self._node_cli_template()
        templates[ProjectType.NODE_WEB_EXPRESS] = self._node_express_template()
        templates[ProjectType.NODE_DESKTOP_ELECTRON] = self._node_electron_template()
        
        # Java templates
        templates[ProjectType.JAVA_CLI] = self._java_cli_template()
        
        # .NET templates
        templates[ProjectType.DOTNET_CLI] = self._dotnet_cli_template()
        templates[ProjectType.DOTNET_WEB_API] = self._dotnet_webapi_template()
        
        # PowerShell templates
        templates[ProjectType.POWERSHELL_MODULE] = self._powershell_module_template()
        
        return templates
    
    def list_available_templates(self):
        """Display available project templates"""
        table = Table(title="Available Project Templates")
        table.add_column("Type", style="cyan")
        table.add_column("Language", style="green")
        table.add_column("Description", style="white")
        
        for project_type, template in self.templates.items():
            table.add_row(
                project_type.value,
                template.language,
                template.description
            )
        
        console.print(table)
    
    def preview_scaffold(self, project_type: ProjectType, project_name: str, target_dir: str):
        """Preview what the scaffold operation will do"""
        if project_type not in self.templates:
            console.print(f"[red]Unknown project type: {project_type.value}[/red]")
            return
        
        template = self.templates[project_type]
        
        console.print(Panel(
            f"[bold]{template.name}[/bold]\n{template.description}",
            title="Project Template",
            border_style="blue"
        ))
        
        # Show commands that will be executed
        console.print("\n[bold]Commands to Execute:[/bold]")
        for i, step in enumerate(template.commands, 1):
            console.print(f"  {i}. {step.description}")
            console.print(f"     [dim]{step}[/dim]")
        
        # Show files that will be created
        console.print(f"\n[bold]Files to Create in {target_dir}:[/bold]")
        for file_template in template.files:
            console.print(f"  📄 {file_template.path} - {file_template.description}")
        
        # Show dependencies
        if template.dependencies:
            console.print(f"\n[bold]Dependencies:[/bold]")
            for dep in template.dependencies:
                console.print(f"  • {dep}")
    
    def scaffold_project(self, project_type: ProjectType, project_name: str, 
                        target_dir: str = ".", dry_run: bool = False, 
                        skip_confirm: bool = False) -> bool:
        """Create a new project from template"""
        
        if project_type not in self.templates:
            console.print(f"[red]Unknown project type: {project_type.value}[/red]")
            return False
        
        template = self.templates[project_type]
        full_path = os.path.join(target_dir, project_name)
        
        # Show preview
        self.preview_scaffold(project_type, project_name, full_path)
        
        # Get confirmation
        if not skip_confirm and not dry_run:
            if not Confirm.ask(f"\nProceed with creating {template.name} project?"):
                console.print("[yellow]Scaffold cancelled[/yellow]")
                return False
        
        # Create project directory
        if not dry_run:
            os.makedirs(full_path, exist_ok=True)
            console.print(f"[green]📁 Created project directory: {full_path}[/green]")
        
        # Create files
        for file_template in template.files:
            file_path = os.path.join(full_path, file_template.path)
            file_dir = os.path.dirname(file_path)
            
            if not dry_run:
                os.makedirs(file_dir, exist_ok=True)
                with open(file_path, 'w') as f:
                    # Replace template variables
                    content = file_template.content.replace("{{PROJECT_NAME}}", project_name)
                    f.write(content)
                
                if file_template.executable:
                    os.chmod(file_path, 0o755)
                
                console.print(f"[green]📄 Created {file_template.path}[/green]")
            else:
                console.print(f"[dim]DRY RUN: Would create {file_template.path}[/dim]")
        
        # Execute commands
        executor = SafeCommandExecutor(full_path, dry_run)
        
        for step in template.commands:
            if not executor.execute_step(step, template.language):
                if step.required:
                    console.print("[red]❌ Required step failed, aborting scaffold[/red]")
                    return False
                else:
                    console.print("[yellow]⚠️  Optional step failed, continuing[/yellow]")
        
        # Show completion message
        if template.post_setup_message:
            console.print(Panel(
                template.post_setup_message.replace("{{PROJECT_NAME}}", project_name),
                title="[green]✅ Setup Complete![/green]",
                border_style="green"
            ))
        
        return True
    
    # Template definitions start here - I'll implement a few key ones
    def _python_cli_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name="Python CLI Application",
            description="Command-line application with Click framework and modern Python structure",
            language="python",
            project_type=ProjectType.PYTHON_CLI,
            commands=[
                CommandStep("python", ["-m", "venv", "venv"], "Create virtual environment"),
                CommandStep("pip", ["install", "click", "rich"], "Install dependencies", working_dir="{{PROJECT_NAME}}"),
            ],
            files=[
                FileTemplate(
                    "main.py",
                    '''#!/usr/bin/env python3
"""{{PROJECT_NAME}} - A Python CLI application"""

import click
from rich.console import Console

console = Console()

@click.command()
@click.option('--name', default='World', help='Name to greet')
def hello(name):
    """Simple CLI application that greets NAME."""
    console.print(f"Hello {name}!", style="bold green")

if __name__ == '__main__':
    hello()
''',
                    "Main CLI entry point",
                    executable=True
                ),
                FileTemplate(
                    "requirements.txt",
                    "click>=8.0.0\nrich>=13.0.0\n",
                    "Python dependencies"
                ),
                FileTemplate(
                    "README.md",
                    "# {{PROJECT_NAME}}\n\nA Python CLI application.\n\n## Usage\n\n```bash\npython main.py --name YourName\n```\n",
                    "Project documentation"
                )
            ],
            dependencies=["click", "rich"],
            post_setup_message="Your Python CLI is ready!\n\nNext steps:\n1. cd {{PROJECT_NAME}}\n2. source venv/bin/activate\n3. python main.py --help"
        )
    
    def _node_cli_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name="Node.js CLI Application", 
            description="Command-line application with modern Node.js and TypeScript",
            language="node",
            project_type=ProjectType.NODE_CLI,
            commands=[
                CommandStep("npm", ["init", "-y"], "Initialize package.json"),
                CommandStep("npm", ["install", "commander", "chalk"], "Install dependencies"),
                CommandStep("npm", ["install", "-D", "typescript", "@types/node"], "Install dev dependencies"),
            ],
            files=[
                FileTemplate(
                    "src/index.ts",
                    '''#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';

const program = new Command();

program
  .name('{{PROJECT_NAME}}')
  .description('CLI application built with Node.js and TypeScript')
  .version('1.0.0');

program
  .option('-n, --name <name>', 'name to greet', 'World')
  .action((options) => {
    console.log(chalk.green(`Hello ${options.name}!`));
  });

program.parse();
''',
                    "Main CLI entry point",
                    executable=True
                ),
                FileTemplate(
                    "tsconfig.json",
                    '''{\n  "compilerOptions": {\n    "target": "ES2020",\n    "module": "commonjs",\n    "outDir": "./dist",\n    "strict": true,\n    "esModuleInterop": true\n  },\n  "include": ["src/**/*"]\n}''',
                    "TypeScript configuration"
                )
            ],
            dependencies=["commander", "chalk", "typescript"],
            post_setup_message="Your Node.js CLI is ready!\n\nNext steps:\n1. cd {{PROJECT_NAME}}\n2. npm run build\n3. node dist/index.js --help"
        )

    def _python_flask_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name="Python Flask Web Application",
            description="Web application with Flask framework and modern Python structure",
            language="python",
            project_type=ProjectType.PYTHON_WEB_FLASK,
            commands=[
                CommandStep("python", ["-m", "venv", "venv"], "Create virtual environment"),
                CommandStep("pip", ["install", "flask", "python-dotenv"], "Install dependencies"),
            ],
            files=[
                FileTemplate(
                    "app.py",
                    '''from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', title='{{PROJECT_NAME}}')

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'service': '{{PROJECT_NAME}}'})

if __name__ == '__main__':
    app.run(debug=True)
''',
                    "Flask application entry point"
                ),
                FileTemplate(
                    "templates/index.html",
                    '''<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>Welcome to {{ title }}!</h1>
    <p>Your Flask application is running.</p>
</body>
</html>
''',
                    "HTML template"
                ),
                FileTemplate(
                    "requirements.txt",
                    "flask>=2.0.0\npython-dotenv>=0.19.0\n",
                    "Python dependencies"
                )
            ],
            dependencies=["flask", "python-dotenv"],
            post_setup_message="Flask app ready!\n\nNext steps:\n1. cd {{PROJECT_NAME}}\n2. source venv/bin/activate\n3. python app.py"
        )

    def _python_fastapi_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name="Python FastAPI Web Application",
            description="Modern async web API with FastAPI",
            language="python", 
            project_type=ProjectType.PYTHON_WEB_FASTAPI,
            commands=[
                CommandStep("python", ["-m", "venv", "venv"], "Create virtual environment"),
                CommandStep("pip", ["install", "fastapi", "uvicorn[standard]"], "Install dependencies"),
            ],
            files=[
                FileTemplate(
                    "main.py",
                    '''from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="{{PROJECT_NAME}}", version="1.0.0")

class Item(BaseModel):
    name: str
    description: str = None

@app.get("/")
def read_root():
    return {"message": "Welcome to {{PROJECT_NAME}}!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/items/")
def create_item(item: Item):
    return {"item": item, "message": "Item created successfully"}
''',
                    "FastAPI application"
                ),
                FileTemplate(
                    "requirements.txt",
                    "fastapi>=0.68.0\nuvicorn[standard]>=0.15.0\n",
                    "Python dependencies"
                )
            ],
            dependencies=["fastapi", "uvicorn"],
            post_setup_message="FastAPI ready!\n\nNext steps:\n1. cd {{PROJECT_NAME}}\n2. source venv/bin/activate\n3. uvicorn main:app --reload"
        )

    def _python_lib_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name="Python Library",
            description="Reusable Python library with modern packaging",
            language="python",
            project_type=ProjectType.PYTHON_LIB,
            commands=[
                CommandStep("python", ["-m", "venv", "venv"], "Create virtual environment"),
                CommandStep("pip", ["install", "build", "pytest"], "Install build tools"),
            ],
            files=[
                FileTemplate(
                    "src/{{PROJECT_NAME}}/__init__.py",
                    '''"""{{PROJECT_NAME}} - A Python library"""

__version__ = "0.1.0"

def hello(name: str = "World") -> str:
    """Simple hello function"""
    return f"Hello, {name}!"
''',
                    "Library main module"
                ),
                FileTemplate(
                    "pyproject.toml",
                    '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{{PROJECT_NAME}}"
version = "0.1.0"
description = "A Python library"
authors = [{name = "Your Name", email = "you@example.com"}]
license = {text = "MIT"}
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=6.0", "black", "flake8"]
''',
                    "Modern Python packaging configuration"
                ),
                FileTemplate(
                    "tests/test_main.py",
                    '''import pytest
from {{PROJECT_NAME}} import hello

def test_hello_default():
    assert hello() == "Hello, World!"

def test_hello_custom():
    assert hello("Python") == "Hello, Python!"
''',
                    "Unit tests"
                )
            ],
            dependencies=["build", "pytest"],
            post_setup_message="Python library ready!\n\nNext steps:\n1. cd {{PROJECT_NAME}}\n2. source venv/bin/activate\n3. python -m pytest"
        )

    def _node_express_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name="Node.js Express Web Application",
            description="Web server with Express.js and TypeScript",
            language="node",
            project_type=ProjectType.NODE_WEB_EXPRESS,
            commands=[
                CommandStep("npm", ["init", "-y"], "Initialize package.json"),
                CommandStep("npm", ["install", "express", "cors", "helmet"], "Install dependencies"),
                CommandStep("npm", ["install", "-D", "typescript", "@types/node", "@types/express", "nodemon"], "Install dev dependencies"),
            ],
            files=[
                FileTemplate(
                    "src/app.ts",
                    '''import express from 'express';
import cors from 'cors';
import helmet from 'helmet';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Welcome to {{PROJECT_NAME}}!' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`{{PROJECT_NAME}} server running on port ${PORT}`);
});
''',
                    "Express.js application"
                ),
                FileTemplate(
                    "package.json",
                    '''{\n  "name": "{{PROJECT_NAME}}",\n  "version": "1.0.0",\n  "scripts": {\n    "dev": "nodemon src/app.ts",\n    "build": "tsc",\n    "start": "node dist/app.js"\n  }\n}''',
                    "Package configuration"
                )
            ],
            dependencies=["express", "cors", "helmet", "typescript"],
            post_setup_message="Express app ready!\n\nNext steps:\n1. cd {{PROJECT_NAME}}\n2. npm run dev"
        )

    def _node_electron_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name="Electron Desktop Application",
            description="Cross-platform desktop app with Electron and TypeScript",
            language="node",
            project_type=ProjectType.NODE_DESKTOP_ELECTRON,
            commands=[
                CommandStep("npm", ["init", "-y"], "Initialize package.json"),
                CommandStep("npm", ["install", "electron"], "Install Electron"),
                CommandStep("npm", ["install", "-D", "typescript", "@types/node"], "Install dev dependencies"),
            ],
            files=[
                FileTemplate(
                    "src/main.ts",
                    '''import { app, BrowserWindow } from 'electron';
import * as path from 'path';

function createWindow(): void {
  const mainWindow = new BrowserWindow({
    height: 600,
    width: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile(path.join(__dirname, '../index.html'));
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
''',
                    "Electron main process"
                ),
                FileTemplate(
                    "index.html",
                    '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{PROJECT_NAME}}</title>
</head>
<body>
    <h1>{{PROJECT_NAME}}</h1>
    <p>Welcome to your Electron application!</p>
</body>
</html>
''',
                    "HTML interface"
                )
            ],
            dependencies=["electron", "typescript"],
            post_setup_message="Electron app ready!\n\nNext steps:\n1. cd {{PROJECT_NAME}}\n2. npm run electron"
        )

    def _java_cli_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name="Java CLI Application",
            description="Command-line application with modern Java",
            language="java",
            project_type=ProjectType.JAVA_CLI,
            commands=[
                CommandStep("mkdir", ["-p", "src/main/java"], "Create source directories"),
            ],
            files=[
                FileTemplate(
                    "src/main/java/Main.java",
                    '''public class Main {
    public static void main(String[] args) {
        String name = args.length > 0 ? args[0] : "World";
        System.out.println("Hello, " + name + "!");
    }
}
''',
                    "Java main class"
                ),
                FileTemplate(
                    "compile.sh",
                    '''#!/bin/bash
javac -d build src/main/java/*.java
java -cp build Main "$@"
''',
                    "Build and run script",
                    executable=True
                )
            ],
            dependencies=[],
            post_setup_message="Java CLI ready!\n\nNext steps:\n1. cd {{PROJECT_NAME}}\n2. ./compile.sh\n3. java -cp build Main YourName"
        )

    def _dotnet_cli_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name=".NET CLI Application",
            description="Command-line application with .NET Core",
            language="dotnet",
            project_type=ProjectType.DOTNET_CLI,
            commands=[
                CommandStep("dotnet", ["new", "console", "-n", "{{PROJECT_NAME}}"], "Create .NET console app"),
            ],
            files=[],  # dotnet new creates the files
            dependencies=[],
            post_setup_message=".NET CLI ready!\n\nNext steps:\n1. cd {{PROJECT_NAME}}\n2. dotnet run"
        )

    def _dotnet_webapi_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name=".NET Web API",
            description="REST API with ASP.NET Core",
            language="dotnet",
            project_type=ProjectType.DOTNET_WEB_API,
            commands=[
                CommandStep("dotnet", ["new", "webapi", "-n", "{{PROJECT_NAME}}"], "Create .NET Web API"),
            ],
            files=[],  # dotnet new creates the files
            dependencies=[],
            post_setup_message=".NET Web API ready!\n\nNext steps:\n1. cd {{PROJECT_NAME}}\n2. dotnet run"
        )

    def _powershell_module_template(self) -> ProjectTemplate:
        return ProjectTemplate(
            name="PowerShell Module",
            description="Reusable PowerShell module",
            language="powershell",
            project_type=ProjectType.POWERSHELL_MODULE,
            commands=[],  # No commands needed, just files
            files=[
                FileTemplate(
                    "{{PROJECT_NAME}}.psm1",
                    '''# {{PROJECT_NAME}} PowerShell Module

function Get-{{PROJECT_NAME}}Info {
    [CmdletBinding()]
    param()
    
    Write-Output "{{PROJECT_NAME}} Module v1.0.0"
}

function Invoke-{{PROJECT_NAME}}Action {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Action
    )
    
    Write-Output "Executing action: $Action"
}

Export-ModuleMember -Function Get-{{PROJECT_NAME}}Info, Invoke-{{PROJECT_NAME}}Action
''',
                    "PowerShell module file"
                ),
                FileTemplate(
                    "{{PROJECT_NAME}}.psd1",
                    '''@{
    ModuleVersion = '1.0.0'
    GUID = '{0}' -f (New-Guid)
    Author = 'Your Name'
    Description = '{{PROJECT_NAME}} PowerShell Module'
    RootModule = '{{PROJECT_NAME}}.psm1'
    FunctionsToExport = @('Get-{{PROJECT_NAME}}Info', 'Invoke-{{PROJECT_NAME}}Action')
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
''',
                    "PowerShell module manifest"
                )
            ],
            dependencies=[],
            post_setup_message="PowerShell module ready!\n\nNext steps:\n1. cd {{PROJECT_NAME}}\n2. Import-Module .\\{{PROJECT_NAME}}.psm1\n3. Get-{{PROJECT_NAME}}Info"
        )