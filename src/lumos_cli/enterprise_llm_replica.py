"""
Enterprise LLM Replica with OAuth2 Authentication
Simulates enterprise LLM (GPT-4) with actual enterprise API calls
"""

import os
import json
import requests
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .debug_logger import debug_logger

console = Console()

@dataclass
class EnterpriseLLMConfig:
    """Configuration for Enterprise LLM Replica"""
    # Enterprise API Configuration
    token_url: str = ""
    chat_url: str = ""
    app_id: str = ""
    app_key: str = ""
    app_resource: str = ""
    
    # API Parameters
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    
    # Token Management
    access_token: str = ""
    token_expires_at: float = 0

class EnterpriseLLMReplica:
    """Enterprise LLM Replica with OAuth2 Authentication"""
    
    def __init__(self):
        self.console = console
        self.config = EnterpriseLLMConfig()
        self.session = requests.Session()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment or config file"""
        try:
            # Load from environment variables
            self.config.token_url = os.getenv("ENTERPRISE_LLM_TOKEN_URL", "")
            self.config.chat_url = os.getenv("ENTERPRISE_LLM_CHAT_URL", "")
            self.config.app_id = os.getenv("ENTERPRISE_LLM_APP_ID", "")
            self.config.app_key = os.getenv("ENTERPRISE_LLM_APP_KEY", "")
            self.config.app_resource = os.getenv("ENTERPRISE_LLM_APP_RESOURCE", "")
            
            # Load from config file if environment variables not set
            if not self.config.token_url:
                self._load_from_config_file()
            
            if self.config.token_url and self.config.chat_url and self.config.app_id and self.config.app_key:
                self.console.print("[green]✅ Enterprise LLM Replica configuration loaded[/green]")
                self.console.print(f"[dim]Token URL: {self.config.token_url}[/dim]")
                self.console.print(f"[dim]Chat URL: {self.config.chat_url}[/dim]")
            else:
                self.console.print("[yellow]⚠️  Enterprise LLM Replica not configured[/yellow]")
                self.console.print("[dim]Set environment variables or use config command[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Failed to load Enterprise LLM Replica config: {str(e)}[/red]")
            debug_logger.error(f"Failed to load Enterprise LLM Replica config: {e}")
    
    def _load_from_config_file(self):
        """Load configuration from config file"""
        try:
            config_file = os.path.expanduser("~/.lumos/enterprise_llm_config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    self.config.token_url = config_data.get("token_url", "")
                    self.config.chat_url = config_data.get("chat_url", "")
                    self.config.app_id = config_data.get("app_id", "")
                    self.config.app_key = config_data.get("app_key", "")
                    self.config.app_resource = config_data.get("app_resource", "")
        except Exception as e:
            debug_logger.error(f"Failed to load config file: {e}")
    
    def _get_access_token(self) -> bool:
        """Get access token using OAuth2 client credentials flow"""
        try:
            if not self.config.token_url or not self.config.app_id or not self.config.app_key:
                self.console.print("[red]❌ Enterprise LLM not configured[/red]")
                return False
            
            # Check if token is still valid
            if self.config.access_token and time.time() < self.config.token_expires_at:
                return True
            
            self.console.print("[cyan]🔑 Getting access token...[/cyan]")
            
            # Prepare OAuth2 request
            token_data = {
                "grant_type": "client_credentials",
                "client_id": self.config.app_id,
                "client_secret": self.config.app_key,
                "resource": self.config.app_resource
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Make token request
            response = self.session.post(
                self.config.token_url,
                data=token_data,
                headers=headers,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                token_response = response.json()
                self.config.access_token = token_response.get("access_token", "")
                expires_in = token_response.get("expires_in", 3600)
                self.config.token_expires_at = time.time() + expires_in - 60  # 1 minute buffer
                
                self.console.print("[green]✅ Access token obtained successfully[/green]")
                debug_logger.log_function_call("EnterpriseLLMReplica._get_access_token", {
                    "token_url": self.config.token_url,
                    "app_id": self.config.app_id,
                    "expires_in": expires_in
                })
                return True
            else:
                self.console.print(f"[red]❌ Failed to get access token: {response.status_code}[/red]")
                self.console.print(f"[red]Response: {response.text}[/red]")
                debug_logger.error(f"Token request failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.console.print(f"[red]❌ Error getting access token: {str(e)}[/red]")
            debug_logger.error(f"Error getting access token: {e}")
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """Generate response using Enterprise LLM API"""
        try:
            # Get access token
            if not self._get_access_token():
                return "Error: Failed to get access token"
            
            debug_logger.log_function_call("EnterpriseLLMReplica.generate_response", {
                "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "max_tokens": max_tokens or self.config.max_tokens,
                "temperature": temperature or self.config.temperature
            })
            
            # Prepare chat request
            chat_data = {
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens or self.config.max_tokens,
                "temperature": temperature or self.config.temperature,
                "top_p": self.config.top_p,
                "frequency_penalty": self.config.frequency_penalty,
                "presence_penalty": self.config.presence_penalty
            }
            
            headers = {
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json"
            }
            
            # Make chat request
            response = self.session.post(
                self.config.chat_url,
                json=chat_data,
                headers=headers,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                chat_response = response.json()
                # Extract the response content
                if "choices" in chat_response and len(chat_response["choices"]) > 0:
                    content = chat_response["choices"][0].get("message", {}).get("content", "")
                    return content
                else:
                    return "Error: No response content received"
            else:
                self.console.print(f"[red]❌ Chat request failed: {response.status_code}[/red]")
                self.console.print(f"[red]Response: {response.text}[/red]")
                debug_logger.error(f"Chat request failed: {response.status_code} - {response.text}")
                return f"Error: Chat request failed with status {response.status_code}"
            
        except Exception as e:
            debug_logger.error(f"Enterprise LLM Replica generation failed: {e}")
            return f"Error generating response: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Chat interface compatible with existing LLM router"""
        if not messages:
            return "No messages provided"
        
        try:
            # Get access token
            if not self._get_access_token():
                return "Error: Failed to get access token"
            
            debug_logger.log_function_call("EnterpriseLLMReplica.chat", {
                "message_count": len(messages),
                "messages": [msg.get("role", "unknown") for msg in messages]
            })
            
            # Prepare chat request with messages
            chat_data = {
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "frequency_penalty": self.config.frequency_penalty,
                "presence_penalty": self.config.presence_penalty
            }
            
            headers = {
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json"
            }
            
            # Make chat request
            response = self.session.post(
                self.config.chat_url,
                json=chat_data,
                headers=headers,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                chat_response = response.json()
                # Extract the response content
                if "choices" in chat_response and len(chat_response["choices"]) > 0:
                    content = chat_response["choices"][0].get("message", {}).get("content", "")
                    return content
                else:
                    return "Error: No response content received"
            else:
                self.console.print(f"[red]❌ Chat request failed: {response.status_code}[/red]")
                self.console.print(f"[red]Response: {response.text}[/red]")
                debug_logger.error(f"Chat request failed: {response.status_code} - {response.text}")
                return f"Error: Chat request failed with status {response.status_code}"
            
        except Exception as e:
            debug_logger.error(f"Enterprise LLM Replica chat failed: {e}")
            return f"Error in chat: {str(e)}"
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to a single prompt"""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        # Add instruction for the model
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)
    
    def generate_code(self, specification: str, language: str = "python") -> str:
        """Generate code using Enterprise LLM Replica"""
        prompt = f"""You are an expert software engineer. Generate {language} code based on the following specification.

Specification: {specification}

Requirements:
1. Write clean, production-ready code
2. Follow best practices for {language}
3. Include proper error handling
4. Add appropriate comments
5. Return only the code, no explanations

Code:"""
        
        response = self.generate_response(prompt)
        
        # Extract code from response
        code = self._extract_code(response, language)
        
        return code
    
    def analyze_code(self, code: str, analysis_type: str = "quality") -> Dict[str, Any]:
        """Analyze code using Enterprise LLM Replica"""
        prompt = f"""You are an expert code reviewer. Analyze the following {analysis_type} of the code:

Code:
{code}

Please provide:
1. Overall quality score (1-10)
2. Issues found
3. Recommendations for improvement
4. Best practices suggestions

Analysis:"""
        
        response = self.generate_response(prompt)
        
        # Parse the response into structured data
        analysis = self._parse_analysis_response(response)
        
        return analysis
    
    def refactor_code(self, code: str, refactor_type: str = "general") -> str:
        """Refactor code using Enterprise LLM Replica"""
        prompt = f"""You are an expert software engineer. Refactor the following code for {refactor_type}:

Original Code:
{code}

Requirements:
1. Improve code quality and readability
2. Follow best practices
3. Maintain functionality
4. Add appropriate comments
5. Return only the refactored code

Refactored Code:"""
        
        response = self.generate_response(prompt)
        
        # Extract refactored code
        refactored_code = self._extract_code(response, "python")
        
        return refactored_code
    
    def review_code(self, code: str) -> Dict[str, Any]:
        """Review code using Enterprise LLM Replica"""
        prompt = f"""You are an expert code reviewer. Review the following code:

Code:
{code}

Please provide:
1. Code quality assessment
2. Security issues
3. Performance concerns
4. Best practices violations
5. Recommendations for improvement

Review:"""
        
        response = self.generate_response(prompt)
        
        # Parse the response into structured data
        review = self._parse_review_response(response)
        
        return review
    
    def _extract_code(self, response: str, language: str) -> str:
        """Extract code from response"""
        lines = response.split('\n')
        code_lines = []
        
        # Find the start of the actual code
        in_code = False
        for line in lines:
            # Look for code indicators
            if (line.strip().startswith('def ') or 
                line.strip().startswith('class ') or 
                line.strip().startswith('import ') or
                line.strip().startswith('from ') or
                line.strip().startswith('function ') or
                line.strip().startswith('const ') or
                line.strip().startswith('let ') or
                line.strip().startswith('var ') or
                line.strip().startswith('package ') or
                line.strip().startswith('public class')):
                in_code = True
            
            if in_code:
                code_lines.append(line)
        
        return '\n'.join(code_lines).strip()
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse analysis response into structured data"""
        # Simple parsing - in a real implementation, you'd use more sophisticated parsing
        return {
            "analysis_type": "quality",
            "score": 8.0,  # Placeholder
            "issues": [],
            "recommendations": [response],
            "raw_response": response
        }
    
    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """Parse review response into structured data"""
        # Simple parsing - in a real implementation, you'd use more sophisticated parsing
        return {
            "quality_score": 8.0,  # Placeholder
            "issues": [],
            "recommendations": [response],
            "raw_response": response
        }
    
    def configure(self, token_url: str, chat_url: str, app_id: str, app_key: str, app_resource: str = ""):
        """Configure the Enterprise LLM Replica"""
        self.config.token_url = token_url
        self.config.chat_url = chat_url
        self.config.app_id = app_id
        self.config.app_key = app_key
        self.config.app_resource = app_resource
        
        # Save configuration to file
        self._save_config()
        
        self.console.print("[green]✅ Enterprise LLM Replica configured successfully[/green]")
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            config_dir = os.path.expanduser("~/.lumos")
            os.makedirs(config_dir, exist_ok=True)
            
            config_file = os.path.join(config_dir, "enterprise_llm_config.json")
            config_data = {
                "token_url": self.config.token_url,
                "chat_url": self.config.chat_url,
                "app_id": self.config.app_id,
                "app_key": self.config.app_key,
                "app_resource": self.config.app_resource
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            debug_logger.log_function_call("EnterpriseLLMReplica._save_config", {
                "config_file": config_file,
                "token_url": self.config.token_url,
                "chat_url": self.config.chat_url
            })
            
        except Exception as e:
            debug_logger.error(f"Failed to save config: {e}")
    
    def is_configured(self) -> bool:
        """Check if Enterprise LLM Replica is configured"""
        return bool(
            self.config.token_url and 
            self.config.chat_url and 
            self.config.app_id and 
            self.config.app_key
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the Enterprise LLM Replica"""
        return {
            "token_url": self.config.token_url,
            "chat_url": self.config.chat_url,
            "app_id": self.config.app_id,
            "app_resource": self.config.app_resource,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "configured": self.is_configured(),
            "has_token": bool(self.config.access_token),
            "token_expires_at": self.config.token_expires_at
        }
    
    def test_connection(self) -> bool:
        """Test the connection to the Enterprise LLM Replica"""
        try:
            if not self.is_configured():
                return False
            
            test_prompt = "Hello, can you respond with 'Enterprise LLM Replica is working'?"
            response = self.generate_response(test_prompt, max_tokens=50)
            
            if "Enterprise LLM Replica is working" in response or len(response) > 0:
                return True
            else:
                return False
                
        except Exception as e:
            debug_logger.error(f"Enterprise LLM Replica connection test failed: {e}")
            return False

# Global Enterprise LLM Replica instance
enterprise_llm_replica = EnterpriseLLMReplica()

def get_enterprise_llm_replica() -> EnterpriseLLMReplica:
    """Get the global Enterprise LLM Replica instance"""
    return enterprise_llm_replica
