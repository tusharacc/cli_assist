"""Dynamic persona management and system prompt generation"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .persona import RepositoryAnalyzer, ProjectContext
from .history import HistoryManager

class PersonaManager:
    """Manages repository-aware personas and system prompts"""
    
    def __init__(self, cache_duration_hours: int = 24):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.cache_file = ".lumos_persona_cache.json"
        self._context_cache = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load cached project contexts from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    
                    # Convert timestamps back to datetime objects
                    for repo_path, data in cache_data.items():
                        if 'timestamp' in data:
                            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                    
                    self._context_cache = cache_data
        except Exception as e:
            print(f"Warning: Could not load persona cache: {e}")
            self._context_cache = {}
    
    def _save_cache(self):
        """Save project contexts to disk cache"""
        try:
            # Convert datetime objects to ISO strings for JSON serialization
            cache_data = {}
            for repo_path, data in self._context_cache.items():
                cache_data[repo_path] = data.copy()
                if 'timestamp' in cache_data[repo_path]:
                    cache_data[repo_path]['timestamp'] = cache_data[repo_path]['timestamp'].isoformat()
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save persona cache: {e}")
    
    def get_project_context(self, repo_path: str, force_refresh: bool = False) -> ProjectContext:
        """Get project context with caching"""
        repo_path = os.path.abspath(repo_path)
        
        # Check cache first
        if not force_refresh and repo_path in self._context_cache:
            cached_data = self._context_cache[repo_path]
            
            # Check if cache is still valid
            if 'timestamp' in cached_data:
                cache_age = datetime.now() - cached_data['timestamp']
                if cache_age < self.cache_duration:
                    # Reconstruct ProjectContext from cached data
                    context_dict = cached_data['context']
                    return ProjectContext(**context_dict)
        
        # Analyze repository
        print(f"[dim]Analyzing repository structure...[/dim]")
        analyzer = RepositoryAnalyzer(repo_path)
        context = analyzer.analyze()
        
        # Cache the result
        self._context_cache[repo_path] = {
            'timestamp': datetime.now(),
            'context': context.to_dict()
        }
        self._save_cache()
        
        return context
    
    def generate_system_prompt(self, context: ProjectContext, command: str = "general") -> str:
        """Generate a dynamic system prompt based on project context and command"""
        
        # Base persona
        base_prompt = "You are Lumos, an expert AI coding assistant."
        
        # Repository-specific context
        if context.primary_languages:
            languages_str = ", ".join(context.primary_languages)
            base_prompt += f" You are working in a {languages_str} repository."
        
        if context.project_type != "general_purpose":
            project_type_readable = context.project_type.replace("_", " ").title()
            base_prompt += f" This is a {project_type_readable} project."
        
        if context.frameworks:
            frameworks_str = ", ".join(context.frameworks)
            base_prompt += f" The project uses: {frameworks_str}."
        
        # Command-specific instructions
        command_instructions = self._get_command_instructions(command, context)
        if command_instructions:
            base_prompt += f"\n\n{command_instructions}"
        
        # Language-specific guidelines
        language_guidelines = self._get_language_guidelines(context.primary_languages)
        if language_guidelines:
            base_prompt += f"\n\nLanguage Guidelines:\n{language_guidelines}"
        
        # Framework-specific guidelines
        framework_guidelines = self._get_framework_guidelines(context.frameworks)
        if framework_guidelines:
            base_prompt += f"\n\nFramework Guidelines:\n{framework_guidelines}"
        
        # Project context information
        context_info = self._get_context_info(context)
        if context_info:
            base_prompt += f"\n\nProject Context:\n{context_info}"
        
        # General best practices
        base_prompt += self._get_general_guidelines(command)
        
        return base_prompt
    
    def _get_command_instructions(self, command: str, context: ProjectContext) -> str:
        """Get command-specific instructions"""
        instructions = {
            "plan": "Break down goals into step-by-step actionable tasks. Consider the project's architecture and existing patterns. Provide specific file paths and implementation details.",
            
            "edit": "Modify the provided code according to the user's instructions. Return ONLY the complete updated file content as raw code - no markdown blocks, no explanations, no comments about changes. The response must be directly writable to a file. Maintain existing code style and patterns.",
            
            "review": "Analyze the code for bugs, security issues, performance problems, and adherence to best practices. Provide specific, actionable feedback with line numbers when possible.",
            
            "debug": "Identify the root cause of the issue and provide a clear solution. Consider the project's dependencies and common patterns. Explain why the issue occurs.",
            
            "chat": "Provide helpful, context-aware responses. Reference the project's structure, dependencies, and patterns when relevant. Ask clarifying questions if needed.",
            
            "scaffold": "Help create well-structured project templates following best practices for the detected technology stack.",
            
            "general": "Provide helpful assistance tailored to this project's technology stack and structure."
        }
        
        return instructions.get(command, instructions["general"])
    
    def _get_language_guidelines(self, languages: List[str]) -> str:
        """Get language-specific guidelines"""
        guidelines = []
        
        language_rules = {
            "python": [
                "Follow PEP 8 style guidelines",
                "Use type hints for function parameters and return values",
                "Write clear docstrings (Google or NumPy style)",
                "Use f-strings for string formatting",
                "Handle exceptions appropriately with specific exception types"
            ],
            "javascript": [
                "Use modern ES6+ syntax (const/let, arrow functions, destructuring)",
                "Use async/await instead of promise chains where appropriate",
                "Add JSDoc comments for functions and classes",
                "Use strict equality (===) comparisons",
                "Handle errors with try-catch blocks"
            ],
            "typescript": [
                "Use explicit type annotations where beneficial",
                "Define interfaces for object shapes",
                "Use generics for reusable components",
                "Enable strict mode in tsconfig.json",
                "Use utility types (Partial, Pick, Omit) appropriately"
            ],
            "java": [
                "Follow Java naming conventions (camelCase, PascalCase)",
                "Use appropriate access modifiers (private, protected, public)",
                "Handle exceptions with try-catch-finally",
                "Use generics for type safety",
                "Follow SOLID principles"
            ],
            "csharp": [
                "Follow C# naming conventions (PascalCase for public members)",
                "Use properties instead of public fields",
                "Implement IDisposable for resource management",
                "Use LINQ for data operations",
                "Add XML documentation comments"
            ],
            "go": [
                "Follow Go naming conventions (exported vs unexported)",
                "Handle errors explicitly",
                "Use gofmt for code formatting",
                "Keep functions small and focused",
                "Use interfaces effectively"
            ]
        }
        
        for lang in languages:
            if lang in language_rules:
                guidelines.append(f"• {lang.title()}:")
                for rule in language_rules[lang]:
                    guidelines.append(f"  - {rule}")
                guidelines.append("")
        
        return "\n".join(guidelines).strip()
    
    def _get_framework_guidelines(self, frameworks: List[str]) -> str:
        """Get framework-specific guidelines"""
        guidelines = []
        
        framework_rules = {
            "django": [
                "Follow Django's MVT (Model-View-Template) pattern",
                "Use Django's built-in authentication and permissions",
                "Implement proper URL routing in urls.py",
                "Use Django ORM for database operations",
                "Follow Django's security best practices"
            ],
            "flask": [
                "Use blueprints for organizing larger applications",
                "Implement proper error handling with error handlers",
                "Use Flask-SQLAlchemy for database operations",
                "Follow RESTful API design principles",
                "Use environment variables for configuration"
            ],
            "fastapi": [
                "Use Pydantic models for request/response validation",
                "Implement async/await for I/O operations",
                "Use dependency injection for shared logic",
                "Add comprehensive OpenAPI documentation",
                "Implement proper error handling with HTTPException"
            ],
            "react": [
                "Use functional components with hooks",
                "Implement proper state management (useState, useContext, Redux)",
                "Follow component composition patterns",
                "Use React.memo for performance optimization",
                "Implement proper error boundaries"
            ],
            "express": [
                "Use middleware for cross-cutting concerns",
                "Implement proper error handling middleware",
                "Use routers to organize routes",
                "Implement proper request validation",
                "Follow RESTful API design principles"
            ],
            "spring": [
                "Use dependency injection with @Autowired",
                "Follow Spring Boot conventions",
                "Use proper annotations (@Service, @Repository, @Controller)",
                "Implement proper exception handling",
                "Use Spring Security for authentication"
            ]
        }
        
        for framework in frameworks:
            if framework in framework_rules:
                guidelines.append(f"• {framework.title()}:")
                for rule in framework_rules[framework]:
                    guidelines.append(f"  - {rule}")
                guidelines.append("")
        
        return "\n".join(guidelines).strip()
    
    def _get_context_info(self, context: ProjectContext) -> str:
        """Get formatted project context information"""
        info = []
        
        if context.dependencies:
            info.append("Key Dependencies:")
            for lang, deps in context.dependencies.items():
                if deps:
                    deps_str = ", ".join(deps[:5])  # Show first 5 dependencies
                    info.append(f"• {lang.title()}: {deps_str}")
        
        if context.build_tools:
            info.append(f"Build Tools: {', '.join(context.build_tools)}")
        
        if context.testing_frameworks:
            info.append(f"Testing: {', '.join(context.testing_frameworks)}")
        
        if context.package_managers:
            info.append(f"Package Managers: {', '.join(context.package_managers)}")
        
        if context.git_info:
            git_parts = []
            if 'current_branch' in context.git_info:
                git_parts.append(f"branch: {context.git_info['current_branch']}")
            if 'last_commit_message' in context.git_info:
                git_parts.append(f"last commit: {context.git_info['last_commit_message'][:50]}")
            if git_parts:
                info.append(f"Git Info: {', '.join(git_parts)}")
        
        return "\n".join(info)
    
    def _get_general_guidelines(self, command: str) -> str:
        """Get general coding guidelines"""
        return """

General Guidelines:
• Write clean, readable, and maintainable code
• Follow established patterns and conventions in the codebase
• Consider security implications and follow best practices
• Add appropriate comments and documentation
• Write tests when applicable
• Consider performance implications
• Handle edge cases and error conditions
• Use meaningful variable and function names
• Keep functions small and focused on single responsibilities
• Avoid code duplication (DRY principle)"""
    
    def get_enhanced_messages(self, messages: List[Dict[str, str]], 
                            context: ProjectContext, command: str = "general") -> List[Dict[str, str]]:
        """Add system prompt to message list if not present"""
        if not messages:
            return messages
        
        # Check if system message already exists
        has_system = any(msg.get("role") == "system" for msg in messages)
        
        if not has_system:
            # Generate and prepend system prompt
            system_prompt = self.generate_system_prompt(context, command)
            enhanced_messages = [{"role": "system", "content": system_prompt}]
            enhanced_messages.extend(messages)
            return enhanced_messages
        
        return messages
    
    def invalidate_cache(self, repo_path: str = None):
        """Invalidate persona cache for a repository or all repositories"""
        if repo_path:
            repo_path = os.path.abspath(repo_path)
            if repo_path in self._context_cache:
                del self._context_cache[repo_path]
        else:
            self._context_cache.clear()
        
        self._save_cache()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "cached_repositories": len(self._context_cache),
            "cache_file_exists": os.path.exists(self.cache_file),
            "cache_duration_hours": self.cache_duration.total_seconds() / 3600
        }
        
        if self._context_cache:
            # Find oldest and newest cache entries
            timestamps = [data.get('timestamp') for data in self._context_cache.values() 
                         if data.get('timestamp')]
            if timestamps:
                stats["oldest_cache_entry"] = min(timestamps).isoformat()
                stats["newest_cache_entry"] = max(timestamps).isoformat()
        
        return stats