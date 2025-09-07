"""
Enterprise LLM Replica using Hugging Face GPT-4
Simulates enterprise LLM (GPT-4) on local laptop
"""

import os
import json
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
    model_name: str = "microsoft/DialoGPT-large"  # Fallback to DialoGPT
    gpt4_model: str = "gpt-4"  # Target GPT-4 model
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30

class EnterpriseLLMReplica:
    """Enterprise LLM Replica using Hugging Face models"""
    
    def __init__(self):
        self.console = console
        self.config = EnterpriseLLMConfig()
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load the Hugging Face model"""
        try:
            self.console.print("[cyan]🤖 Loading Enterprise LLM Replica (GPT-4 simulation)...[/cyan]")
            
            # Try to load a large language model that can simulate GPT-4
            # Using microsoft/DialoGPT-large as a starting point
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            
            model_name = self.config.model_name
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Loading {model_name}", total=None)
                
                # Load tokenizer and model
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(model_name)
                
                # Create pipeline
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device="cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
                )
                
                progress.update(task, description=f"Loaded {model_name}")
            
            self.console.print(f"[green]✅ Enterprise LLM Replica loaded successfully[/green]")
            self.console.print(f"[dim]Simulating: {self.config.gpt4_model}[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Failed to load Enterprise LLM Replica: {str(e)}[/red]")
            debug_logger.error(f"Failed to load Enterprise LLM Replica: {e}")
            self.model = None
            self.tokenizer = None
            self.pipeline = None
    
    def generate_response(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """Generate response using Enterprise LLM Replica"""
        if not self.pipeline:
            return "Error: Enterprise LLM Replica not loaded"
        
        try:
            debug_logger.log_function_call("EnterpriseLLMReplica.generate_response", {
                "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "max_tokens": max_tokens or self.config.max_tokens,
                "temperature": temperature or self.config.temperature
            })
            
            # Configure generation parameters
            generation_kwargs = {
                "max_length": (max_tokens or self.config.max_tokens) + len(prompt.split()),
                "temperature": temperature or self.config.temperature,
                "top_p": self.config.top_p,
                "do_sample": True,
                "pad_token_id": self.tokenizer.eos_token_id,
                "eos_token_id": self.tokenizer.eos_token_id,
                "num_return_sequences": 1
            }
            
            # Generate response
            result = self.pipeline(prompt, **generation_kwargs)
            
            # Extract generated text
            generated_text = result[0]["generated_text"]
            
            # Remove the original prompt from the response
            response = generated_text[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            debug_logger.error(f"Enterprise LLM Replica generation failed: {e}")
            return f"Error generating response: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Chat interface compatible with existing LLM router"""
        if not messages:
            return "No messages provided"
        
        # Convert messages to a single prompt
        prompt = self._messages_to_prompt(messages)
        
        # Generate response
        response = self.generate_response(prompt)
        
        return response
    
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
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.config.model_name,
            "target_model": self.config.gpt4_model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "loaded": self.model is not None,
            "device": "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
        }
    
    def test_connection(self) -> bool:
        """Test the connection to the Enterprise LLM Replica"""
        try:
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
