#!/usr/bin/env python3
"""Enhanced application execution detection system"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from rich.console import Console

@dataclass
class ExecutionOption:
    """Represents a possible way to execute the application"""
    command: str
    description: str
    confidence: float
    file_path: Optional[str] = None
    framework: Optional[str] = None
    is_primary: bool = False

@dataclass 
class AppExecutionContext:
    """Contains all detected execution options for an application"""
    primary_option: Optional[ExecutionOption]
    all_options: List[ExecutionOption] 
    project_type: str
    confidence: float

class EnhancedAppDetector:
    """Enhanced application execution detection with smart analysis"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.console = Console()
        
        # Patterns for detecting main entry points
        self.python_main_patterns = [
            r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
            r'def\s+main\s*\(',
            r'app\.run\s*\(',
            r'uvicorn\.run\s*\(',
            r'fastapi\.FastAPI\s*\(',
        ]
        
        # Framework-specific execution patterns
        self.framework_patterns = {
            'flask': {
                'indicators': ['Flask', 'app.run', '@app.route'],
                'command_template': 'python {file}',
                'alternative': 'flask run'
            },
            'fastapi': {
                'indicators': ['FastAPI', 'uvicorn'],
                'command_template': 'uvicorn {module}:app --reload',
                'alternative': 'python {file}'
            },
            'django': {
                'indicators': ['django', 'manage.py'],
                'command_template': 'python manage.py runserver',
                'file_required': 'manage.py'
            },
            'streamlit': {
                'indicators': ['streamlit'],
                'command_template': 'streamlit run {file}'
            },
            'gradio': {
                'indicators': ['gradio'],
                'command_template': 'python {file}'
            }
        }
    
    def detect_execution_options(self) -> AppExecutionContext:
        """Detect all possible ways to execute the application"""
        all_options = []
        
        # 1. Detect Python executables
        python_options = self._detect_python_executables()
        all_options.extend(python_options)
        
        # 2. Detect Node.js/npm executables  
        nodejs_options = self._detect_nodejs_executables()
        all_options.extend(nodejs_options)
        
        # 3. Detect other language executables
        other_options = self._detect_other_executables()
        all_options.extend(other_options)
        
        # 4. Detect Docker executables
        docker_options = self._detect_docker_executables()
        all_options.extend(docker_options)
        
        # Sort by confidence and select primary
        all_options.sort(key=lambda x: x.confidence, reverse=True)
        primary_option = all_options[0] if all_options else None
        
        if primary_option:
            primary_option.is_primary = True
        
        # Determine project type
        project_type = self._determine_project_type(all_options)
        
        # Calculate overall confidence
        confidence = primary_option.confidence if primary_option else 0.0
        
        return AppExecutionContext(
            primary_option=primary_option,
            all_options=all_options,
            project_type=project_type,
            confidence=confidence
        )
    
    def _detect_python_executables(self) -> List[ExecutionOption]:
        """Detect Python executable files with smart analysis"""
        options = []
        
        # Find all .py files
        python_files = list(self.base_path.glob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                confidence = 0.0
                description = f"Python script: {py_file.name}"
                framework = None
                
                # Check for main patterns
                for pattern in self.python_main_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        confidence += 0.3
                        description = f"Python application with main entry: {py_file.name}"
                        break
                
                # Check for framework patterns
                for fw_name, fw_info in self.framework_patterns.items():
                    for indicator in fw_info['indicators']:
                        if indicator.lower() in content.lower():
                            confidence = min(confidence + 0.4, 1.0)  # Cap at 1.0
                            framework = fw_name
                            
                            # Use framework-specific command
                            if fw_name == 'fastapi':
                                module_name = py_file.stem
                                command = fw_info['command_template'].format(module=module_name)
                                description = f"FastAPI application: {py_file.name}"
                            else:
                                command = fw_info['command_template'].format(file=py_file.name)
                                description = f"{fw_name.title()} application: {py_file.name}"
                            
                            options.append(ExecutionOption(
                                command=command,
                                description=description,
                                confidence=min(confidence, 1.0),  # Cap confidence
                                file_path=str(py_file),
                                framework=framework
                            ))
                            
                            # Add alternative if available
                            if 'alternative' in fw_info:
                                alt_command = fw_info['alternative'].format(file=py_file.name) if '{file}' in fw_info['alternative'] else fw_info['alternative']
                                options.append(ExecutionOption(
                                    command=alt_command,
                                    description=f"{fw_name.title()} alternative: {py_file.name}",
                                    confidence=min(confidence - 0.1, 0.9),  # Cap alternative confidence
                                    file_path=str(py_file),
                                    framework=framework
                                ))
                            break
                
                # Generic python execution if no framework detected
                if confidence > 0 and not framework:
                    options.append(ExecutionOption(
                        command=f"python {py_file.name}",
                        description=description,
                        confidence=confidence,
                        file_path=str(py_file)
                    ))
                elif confidence == 0:
                    # Still add as low-confidence option
                    options.append(ExecutionOption(
                        command=f"python {py_file.name}",
                        description=f"Python script: {py_file.name}",
                        confidence=0.1,
                        file_path=str(py_file)
                    ))
                    
            except Exception:
                # Add basic option even if we can't read the file
                options.append(ExecutionOption(
                    command=f"python {py_file.name}",
                    description=f"Python script: {py_file.name}",
                    confidence=0.05,
                    file_path=str(py_file)
                ))
        
        return options
    
    def _detect_nodejs_executables(self) -> List[ExecutionOption]:
        """Detect Node.js/npm executable options"""
        options = []
        
        # Check for package.json
        package_json = self.base_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                
                scripts = package_data.get('scripts', {})
                
                # Priority order for npm scripts
                script_priorities = ['dev', 'start', 'serve', 'build', 'test']
                
                for priority, script_name in enumerate(script_priorities):
                    if script_name in scripts:
                        confidence = 0.9 - (priority * 0.1)
                        options.append(ExecutionOption(
                            command=f"npm run {script_name}",
                            description=f"npm script: {script_name} ({scripts[script_name]})",
                            confidence=confidence,
                            file_path="package.json",
                            framework="nodejs"
                        ))
                
                # Add other custom scripts with lower confidence
                for script_name, script_cmd in scripts.items():
                    if script_name not in script_priorities:
                        options.append(ExecutionOption(
                            command=f"npm run {script_name}",
                            description=f"npm script: {script_name} ({script_cmd})",
                            confidence=0.3,
                            file_path="package.json", 
                            framework="nodejs"
                        ))
                        
            except Exception:
                # Basic npm options if we can't parse package.json
                options.append(ExecutionOption(
                    command="npm start",
                    description="npm start (default)",
                    confidence=0.2,
                    file_path="package.json",
                    framework="nodejs"
                ))
        
        # Check for common Node.js entry files
        node_files = ['server.js', 'app.js', 'index.js', 'main.js']
        for node_file in node_files:
            file_path = self.base_path / node_file
            if file_path.exists():
                confidence = 0.6 if node_file in ['app.js', 'server.js'] else 0.4
                options.append(ExecutionOption(
                    command=f"node {node_file}",
                    description=f"Node.js application: {node_file}",
                    confidence=confidence,
                    file_path=node_file,
                    framework="nodejs"
                ))
        
        return options
    
    def _detect_other_executables(self) -> List[ExecutionOption]:
        """Detect executables for other languages/frameworks"""
        options = []
        
        # Go
        if (self.base_path / "main.go").exists():
            options.append(ExecutionOption(
                command="go run main.go",
                description="Go application",
                confidence=0.8,
                file_path="main.go",
                framework="go"
            ))
            options.append(ExecutionOption(
                command="go build && ./main",
                description="Go build and run",
                confidence=0.6,
                file_path="main.go", 
                framework="go"
            ))
        
        # Rust
        if (self.base_path / "Cargo.toml").exists():
            options.append(ExecutionOption(
                command="cargo run",
                description="Rust application",
                confidence=0.8,
                file_path="Cargo.toml",
                framework="rust"
            ))
        
        # Java
        java_files = list(self.base_path.glob("*.java"))
        for java_file in java_files:
            if "Main" in java_file.name or "main" in java_file.name.lower():
                class_name = java_file.stem
                options.append(ExecutionOption(
                    command=f"javac {java_file.name} && java {class_name}",
                    description=f"Java application: {java_file.name}",
                    confidence=0.7,
                    file_path=str(java_file),
                    framework="java"
                ))
        
        # Maven
        if (self.base_path / "pom.xml").exists():
            options.append(ExecutionOption(
                command="mvn spring-boot:run",
                description="Maven Spring Boot application",
                confidence=0.7,
                file_path="pom.xml",
                framework="java"
            ))
        
        # Gradle  
        if (self.base_path / "build.gradle").exists():
            options.append(ExecutionOption(
                command="gradle bootRun",
                description="Gradle Spring Boot application", 
                confidence=0.7,
                file_path="build.gradle",
                framework="java"
            ))
        
        return options
    
    def _detect_docker_executables(self) -> List[ExecutionOption]:
        """Detect Docker-based execution options"""
        options = []
        
        if (self.base_path / "Dockerfile").exists():
            project_name = self.base_path.name.lower()
            options.append(ExecutionOption(
                command=f"docker build -t {project_name} . && docker run {project_name}",
                description="Docker containerized application",
                confidence=0.6,
                file_path="Dockerfile",
                framework="docker"
            ))
        
        if (self.base_path / "docker-compose.yml").exists() or (self.base_path / "docker-compose.yaml").exists():
            options.append(ExecutionOption(
                command="docker-compose up",
                description="Docker Compose application",
                confidence=0.7,
                file_path="docker-compose.yml",
                framework="docker"
            ))
        
        return options
    
    def _determine_project_type(self, options: List[ExecutionOption]) -> str:
        """Determine the overall project type based on detected options"""
        if not options:
            return "unknown"
        
        # Count frameworks
        framework_counts = {}
        for option in options:
            if option.framework:
                framework_counts[option.framework] = framework_counts.get(option.framework, 0) + 1
        
        if framework_counts:
            # Return the most common framework
            return max(framework_counts.keys(), key=lambda x: framework_counts[x])
        
        return "mixed"
    
    def suggest_execution_command(self, context: AppExecutionContext, interactive: bool = True) -> Optional[str]:
        """Suggest the best execution command, optionally with user interaction"""
        if not context.all_options:
            return None
        
        if context.confidence > 0.7 and context.primary_option:
            return context.primary_option.command
        
        if interactive and len(context.all_options) > 1:
            # In a real implementation, you'd show options to user
            # For now, just return the highest confidence option
            return context.primary_option.command if context.primary_option else None
        
        return context.primary_option.command if context.primary_option else None