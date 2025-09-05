"""Repository-aware persona and context detection system"""

import os
import json
import glob
import re
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess

@dataclass
class ProjectContext:
    """Comprehensive project context information"""
    repo_path: str
    primary_languages: List[str]
    frameworks: List[str]
    project_type: str
    dependencies: Dict[str, List[str]]  # language -> [dependencies]
    config_files: List[str]
    build_tools: List[str]
    testing_frameworks: List[str]
    package_managers: List[str]
    git_info: Dict[str, str]
    confidence_score: float  # How confident we are about the detection
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RepositoryAnalyzer:
    """Analyzes repository structure to determine project context"""
    
    # Language detection patterns
    LANGUAGE_INDICATORS = {
        "python": {
            "files": ["*.py", "requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "dirs": ["__pycache__", ".pytest_cache", "venv", ".venv"],
            "patterns": [r"\.py$", r"requirements.*\.txt$"]
        },
        "javascript": {
            "files": ["package.json", "*.js", "*.mjs", "yarn.lock", "package-lock.json"],
            "dirs": ["node_modules", ".npm"],
            "patterns": [r"\.js$", r"\.mjs$", r"package\.json$"]
        },
        "typescript": {
            "files": ["tsconfig.json", "*.ts", "*.tsx"],
            "dirs": ["dist", "build"],
            "patterns": [r"\.ts$", r"\.tsx$", r"tsconfig.*\.json$"]
        },
        "java": {
            "files": ["pom.xml", "build.gradle", "*.java", "gradle.properties"],
            "dirs": ["target", ".gradle", "build"],
            "patterns": [r"\.java$", r"pom\.xml$", r"build\.gradle$"]
        },
        "csharp": {
            "files": ["*.cs", "*.csproj", "*.sln", "packages.config"],
            "dirs": ["bin", "obj", "packages"],
            "patterns": [r"\.cs$", r"\.csproj$", r"\.sln$"]
        },
        "go": {
            "files": ["go.mod", "go.sum", "*.go"],
            "dirs": ["vendor"],
            "patterns": [r"\.go$", r"go\.mod$", r"go\.sum$"]
        },
        "rust": {
            "files": ["Cargo.toml", "Cargo.lock", "*.rs"],
            "dirs": ["target", "src"],
            "patterns": [r"\.rs$", r"Cargo\.toml$"]
        },
        "powershell": {
            "files": ["*.ps1", "*.psm1", "*.psd1"],
            "dirs": [],
            "patterns": [r"\.ps1$", r"\.psm1$", r"\.psd1$"]
        }
    }
    
    # Framework detection patterns
    FRAMEWORK_INDICATORS = {
        "python": {
            "django": ["manage.py", "settings.py", "urls.py", "wsgi.py"],
            "flask": ["app.py", "application.py", "run.py", "wsgi.py", "templates/"],
            "fastapi": ["main.py", "api.py"],
            "pytest": ["pytest.ini", "conftest.py", "test_*.py"],
            "poetry": ["pyproject.toml"],
            "pipenv": ["Pipfile"],
        },
        "javascript": {
            "react": ["src/App.js", "src/index.js", "public/index.html"],
            "vue": ["src/App.vue", "src/main.js"],
            "angular": ["angular.json", "src/app/app.module.ts"],
            "express": ["app.js", "server.js", "index.js"],
            "next": ["next.config.js", "pages/", "app/"],
            "nuxt": ["nuxt.config.js", "pages/"],
            "jest": ["jest.config.js", "*.test.js", "*.spec.js"],
            "cypress": ["cypress.json", "cypress/"],
        },
        "typescript": {
            "react": ["src/App.tsx", "src/index.tsx"],
            "vue": ["src/App.vue", "src/main.ts"],
            "angular": ["src/app/app.module.ts", "angular.json"],
            "express": ["app.ts", "server.ts", "index.ts"],
            "next": ["next.config.ts", "pages/", "app/"],
            "nest": ["src/app.module.ts", "nest-cli.json"],
            "electron": ["src/main.ts", "src/renderer/"],
        },
        "java": {
            "spring": ["pom.xml", "src/main/java", "application.properties"],
            "junit": ["src/test/java"],
            "maven": ["pom.xml"],
            "gradle": ["build.gradle", "gradle.properties"],
        },
        "csharp": {
            "aspnet": ["Startup.cs", "Program.cs", "Controllers/"],
            "blazor": ["*.razor", "wwwroot/"],
            "xamarin": ["MainActivity.cs", "App.xaml"],
            "unity": ["Assets/", "ProjectSettings/"],
        },
        "go": {
            "gin": ["main.go"],
            "echo": ["main.go"],
            "fiber": ["main.go"],
            "chi": ["main.go"],
        }
    }
    
    # Project type classification
    PROJECT_TYPES = {
        "web_application": ["app.py", "server.js", "index.html", "package.json"],
        "cli_tool": ["main.py", "cli.py", "cmd/", "bin/"],
        "library": ["setup.py", "lib/", "src/", "__init__.py"],
        "api_service": ["api.py", "routes/", "controllers/", "endpoints/"],
        "desktop_application": ["main.cpp", "main.java", "MainWindow.xaml"],
        "mobile_application": ["android/", "ios/", "flutter/", "react-native/"],
        "data_science": ["*.ipynb", "data/", "notebooks/", "models/"],
        "devops": ["Dockerfile", "docker-compose.yml", "Jenkinsfile", "terraform/"],
        "documentation": ["docs/", "README.md", "*.md", "mkdocs.yml"],
    }
    
    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self._file_cache = {}
        self._populate_file_cache()
    
    def _populate_file_cache(self):
        """Cache all files in the repository for faster analysis"""
        try:
            for root, dirs, files in os.walk(self.repo_path):
                # Skip common ignore directories
                dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.github', '.vscode']]
                
                rel_root = os.path.relpath(root, self.repo_path)
                if rel_root == '.':
                    rel_root = ''
                
                for file in files:
                    if not file.startswith('.') or file in ['package.json', '.gitignore']:
                        rel_path = os.path.join(rel_root, file) if rel_root else file
                        full_path = os.path.join(root, file)
                        self._file_cache[rel_path] = full_path
                        
                # Also cache directory names
                for dir_name in dirs:
                    rel_path = os.path.join(rel_root, dir_name) if rel_root else dir_name
                    self._file_cache[f"{rel_path}/"] = os.path.join(root, dir_name)
                    
        except Exception as e:
            print(f"Warning: Error caching repository files: {e}")
    
    def detect_languages(self) -> Dict[str, float]:
        """Detect programming languages and confidence scores"""
        language_scores = {}
        
        for lang, indicators in self.LANGUAGE_INDICATORS.items():
            score = 0.0
            matches = 0
            
            # Check for specific files
            for file_pattern in indicators["files"]:
                if "*" in file_pattern:
                    # Glob pattern
                    pattern = file_pattern.replace("*", "")
                    matching_files = [f for f in self._file_cache.keys() if pattern in f]
                    if matching_files:
                        score += len(matching_files) * 0.3
                        matches += len(matching_files)
                else:
                    # Exact match
                    if file_pattern in self._file_cache:
                        score += 1.0
                        matches += 1
            
            # Check for directories
            for dir_name in indicators["dirs"]:
                if f"{dir_name}/" in self._file_cache:
                    score += 0.5
                    matches += 1
            
            # Check patterns with regex
            for pattern in indicators["patterns"]:
                matching_files = [f for f in self._file_cache.keys() if re.search(pattern, f)]
                if matching_files:
                    score += len(matching_files) * 0.2
                    matches += len(matching_files)
            
            if matches > 0:
                # Normalize score based on repository size
                total_files = len([f for f in self._file_cache.keys() if not f.endswith("/")])
                normalized_score = min(score / max(total_files * 0.1, 1), 1.0)
                language_scores[lang] = normalized_score
        
        return language_scores
    
    def detect_frameworks(self, languages: List[str]) -> Dict[str, float]:
        """Detect frameworks for detected languages"""
        framework_scores = {}
        
        for lang in languages:
            if lang not in self.FRAMEWORK_INDICATORS:
                continue
                
            lang_frameworks = self.FRAMEWORK_INDICATORS[lang]
            
            for framework, indicators in lang_frameworks.items():
                score = 0.0
                matches = 0
                
                for indicator in indicators:
                    if "/" in indicator:
                        # Directory indicator
                        if indicator in self._file_cache or f"{indicator}/" in self._file_cache:
                            score += 1.0
                            matches += 1
                    elif "*" in indicator:
                        # Pattern indicator
                        pattern = indicator.replace("*", "")
                        matching_files = [f for f in self._file_cache.keys() if pattern in f]
                        if matching_files:
                            score += len(matching_files) * 0.5
                            matches += len(matching_files)
                    else:
                        # Exact file match
                        if indicator in self._file_cache:
                            score += 1.0
                            matches += 1
                
                # Also check dependencies for framework presence
                dependencies = self.extract_dependencies([lang])
                if lang in dependencies:
                    lang_deps = [dep.lower() for dep in dependencies[lang]]
                    if framework.lower() in lang_deps:
                        score += 2.0  # Strong indicator from dependencies
                        matches += 1
                
                if matches > 0:
                    framework_scores[f"{lang}:{framework}"] = min(score / max(len(indicators), 1), 1.0)
        
        return framework_scores
    
    def detect_project_type(self) -> str:
        """Determine the most likely project type"""
        type_scores = {}
        
        for project_type, indicators in self.PROJECT_TYPES.items():
            score = 0.0
            
            for indicator in indicators:
                if "/" in indicator:
                    # Directory indicator
                    if indicator in self._file_cache or f"{indicator}/" in self._file_cache:
                        score += 1.0
                elif "*" in indicator:
                    # Pattern indicator
                    pattern = indicator.replace("*", "")
                    matching_files = [f for f in self._file_cache.keys() if pattern in f]
                    score += len(matching_files) * 0.3
                else:
                    # Exact file match
                    if indicator in self._file_cache:
                        score += 1.0
            
            if score > 0:
                type_scores[project_type] = score / len(indicators)
        
        if type_scores:
            return max(type_scores, key=type_scores.get)
        return "general_purpose"
    
    def extract_dependencies(self, languages: List[str]) -> Dict[str, List[str]]:
        """Extract dependencies from package files"""
        dependencies = {}
        
        # Python dependencies
        if "python" in languages:
            python_deps = []
            
            # requirements.txt
            if "requirements.txt" in self._file_cache:
                python_deps.extend(self._parse_requirements_txt(self._file_cache["requirements.txt"]))
            
            # pyproject.toml
            if "pyproject.toml" in self._file_cache:
                python_deps.extend(self._parse_pyproject_toml(self._file_cache["pyproject.toml"]))
            
            # setup.py
            if "setup.py" in self._file_cache:
                python_deps.extend(self._parse_setup_py(self._file_cache["setup.py"]))
            
            if python_deps:
                dependencies["python"] = python_deps[:10]  # Limit to top 10
        
        # JavaScript/Node.js dependencies
        if "javascript" in languages or "typescript" in languages:
            if "package.json" in self._file_cache:
                js_deps = self._parse_package_json(self._file_cache["package.json"])
                if js_deps:
                    dependencies["javascript"] = js_deps[:10]
        
        # Java dependencies
        if "java" in languages:
            java_deps = []
            if "pom.xml" in self._file_cache:
                java_deps.extend(self._parse_pom_xml(self._file_cache["pom.xml"]))
            if "build.gradle" in self._file_cache:
                java_deps.extend(self._parse_build_gradle(self._file_cache["build.gradle"]))
            if java_deps:
                dependencies["java"] = java_deps[:10]
        
        # Go dependencies
        if "go" in languages and "go.mod" in self._file_cache:
            go_deps = self._parse_go_mod(self._file_cache["go.mod"])
            if go_deps:
                dependencies["go"] = go_deps[:10]
        
        return dependencies
    
    def _parse_requirements_txt(self, file_path: str) -> List[str]:
        """Parse Python requirements.txt file"""
        deps = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (before ==, >=, etc.)
                        dep = re.split(r'[>=<!]', line)[0].strip()
                        if dep:
                            deps.append(dep)
        except Exception:
            pass
        return deps
    
    def _parse_package_json(self, file_path: str) -> List[str]:
        """Parse Node.js package.json file"""
        deps = []
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                # Get dependencies
                for dep_type in ['dependencies', 'devDependencies']:
                    if dep_type in data:
                        deps.extend(data[dep_type].keys())
        except Exception:
            pass
        return deps
    
    def _parse_pyproject_toml(self, file_path: str) -> List[str]:
        """Parse Python pyproject.toml file"""
        deps = []
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Simple regex parsing (would be better with toml library)
                matches = re.findall(r'"([^"]+)"', content)
                for match in matches:
                    if '==' in match or '>=' in match:
                        dep = re.split(r'[>=<!]', match)[0].strip()
                        if dep and not dep.startswith('python'):
                            deps.append(dep)
        except Exception:
            pass
        return deps
    
    def _parse_setup_py(self, file_path: str) -> List[str]:
        """Parse Python setup.py file"""
        deps = []
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Look for install_requires
                match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
                if match:
                    requirements_str = match.group(1)
                    # Extract quoted strings
                    deps = re.findall(r'"([^"]+)"', requirements_str)
                    deps = [re.split(r'[>=<!]', dep)[0].strip() for dep in deps]
        except Exception:
            pass
        return deps
    
    def _parse_pom_xml(self, file_path: str) -> List[str]:
        """Parse Java pom.xml file"""
        deps = []
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Simple regex to find artifactId in dependencies
                matches = re.findall(r'<artifactId>([^<]+)</artifactId>', content)
                deps = matches[:10]  # Limit results
        except Exception:
            pass
        return deps
    
    def _parse_build_gradle(self, file_path: str) -> List[str]:
        """Parse Java build.gradle file"""
        deps = []
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Look for dependency declarations
                matches = re.findall(r'implementation\s+[\'"]([^:\'"]+)', content)
                deps.extend(matches)
                matches = re.findall(r'compile\s+[\'"]([^:\'"]+)', content)
                deps.extend(matches)
        except Exception:
            pass
        return deps
    
    def _parse_go_mod(self, file_path: str) -> List[str]:
        """Parse Go go.mod file"""
        deps = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('require'):
                        continue
                    if re.match(r'^[a-zA-Z]', line):
                        dep = line.split()[0]
                        if '/' in dep:  # Likely a module path
                            deps.append(dep.split('/')[-1])  # Get last part
        except Exception:
            pass
        return deps
    
    def get_git_info(self) -> Dict[str, str]:
        """Extract git repository information"""
        git_info = {}
        try:
            # Get remote URL
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                git_info["remote_url"] = result.stdout.strip()
            
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                git_info["current_branch"] = result.stdout.strip()
            
            # Get last commit info
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%H %s"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(' ', 1)
                if len(parts) == 2:
                    git_info["last_commit_hash"] = parts[0][:8]
                    git_info["last_commit_message"] = parts[1]
        except Exception:
            pass
        
        return git_info
    
    def analyze(self) -> ProjectContext:
        """Perform complete repository analysis"""
        # Detect languages
        language_scores = self.detect_languages()
        primary_languages = [lang for lang, score in language_scores.items() if score > 0.1]
        primary_languages.sort(key=lambda x: language_scores[x], reverse=True)
        
        # Detect frameworks
        framework_scores = self.detect_frameworks(primary_languages)
        frameworks = [fw.split(':', 1)[1] for fw, score in framework_scores.items() if score > 0.3]
        
        # Detect project type
        project_type = self.detect_project_type()
        
        # Extract dependencies
        dependencies = self.extract_dependencies(primary_languages)
        
        # Get build tools, testing frameworks, etc.
        build_tools = self._detect_build_tools()
        testing_frameworks = self._detect_testing_frameworks()
        package_managers = self._detect_package_managers()
        
        # Get config files
        config_files = [f for f in self._file_cache.keys() 
                       if any(f.endswith(ext) for ext in ['.json', '.yml', '.yaml', '.toml', '.ini', '.conf'])]
        
        # Get git info
        git_info = self.get_git_info()
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(language_scores, framework_scores)
        
        return ProjectContext(
            repo_path=self.repo_path,
            primary_languages=primary_languages[:3],  # Top 3 languages
            frameworks=frameworks[:5],  # Top 5 frameworks
            project_type=project_type,
            dependencies=dependencies,
            config_files=config_files[:10],  # Limit config files
            build_tools=build_tools,
            testing_frameworks=testing_frameworks,
            package_managers=package_managers,
            git_info=git_info,
            confidence_score=confidence_score
        )
    
    def _detect_build_tools(self) -> List[str]:
        """Detect build tools in the repository"""
        tools = []
        indicators = {
            "webpack": ["webpack.config.js", "webpack.config.ts"],
            "vite": ["vite.config.js", "vite.config.ts"],
            "rollup": ["rollup.config.js"],
            "gulp": ["gulpfile.js"],
            "grunt": ["Gruntfile.js"],
            "make": ["Makefile"],
            "cmake": ["CMakeLists.txt"],
            "docker": ["Dockerfile", "docker-compose.yml"],
            "terraform": ["*.tf"],
        }
        
        for tool, files in indicators.items():
            for file_pattern in files:
                if "*" in file_pattern:
                    pattern = file_pattern.replace("*", "")
                    if any(pattern in f for f in self._file_cache.keys()):
                        tools.append(tool)
                        break
                elif file_pattern in self._file_cache:
                    tools.append(tool)
                    break
        
        return tools
    
    def _detect_testing_frameworks(self) -> List[str]:
        """Detect testing frameworks"""
        frameworks = []
        indicators = {
            "pytest": ["pytest.ini", "conftest.py"],
            "unittest": ["test_*.py"],
            "jest": ["jest.config.js"],
            "mocha": ["mocha.opts", ".mocharc.json"],
            "jasmine": ["jasmine.json"],
            "junit": ["src/test/java/"],
            "nunit": ["*.Tests.csproj"],
            "go-test": ["*_test.go"],
        }
        
        for framework, files in indicators.items():
            for file_pattern in files:
                if "*" in file_pattern:
                    pattern = file_pattern.replace("*", "")
                    if any(pattern in f for f in self._file_cache.keys()):
                        frameworks.append(framework)
                        break
                elif "/" in file_pattern:
                    if f"{file_pattern}" in self._file_cache:
                        frameworks.append(framework)
                        break
                elif file_pattern in self._file_cache:
                    frameworks.append(framework)
                    break
        
        return frameworks
    
    def _detect_package_managers(self) -> List[str]:
        """Detect package managers"""
        managers = []
        indicators = {
            "npm": ["package.json", "package-lock.json"],
            "yarn": ["yarn.lock"],
            "pnpm": ["pnpm-lock.yaml"],
            "pip": ["requirements.txt"],
            "poetry": ["poetry.lock", "pyproject.toml"],
            "pipenv": ["Pipfile", "Pipfile.lock"],
            "conda": ["environment.yml"],
            "maven": ["pom.xml"],
            "gradle": ["build.gradle"],
            "go-mod": ["go.mod"],
            "cargo": ["Cargo.toml"],
            "nuget": ["packages.config"],
        }
        
        for manager, files in indicators.items():
            if any(f in self._file_cache for f in files):
                managers.append(manager)
        
        return managers
    
    def _calculate_confidence(self, language_scores: Dict[str, float], 
                            framework_scores: Dict[str, float]) -> float:
        """Calculate overall confidence in the analysis"""
        if not language_scores:
            return 0.0
        
        # Base confidence on strongest language detection
        max_lang_score = max(language_scores.values())
        
        # Boost confidence if we detected frameworks
        framework_boost = 0.1 if framework_scores else 0.0
        
        # Boost confidence if we have config files
        config_boost = 0.05 if len(self._file_cache) > 5 else 0.0
        
        return min(max_lang_score + framework_boost + config_boost, 1.0)