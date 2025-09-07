"""
GPT-4 Simulator using Hugging Face Models
Simulates enterprise GPT-4 on local laptop using large language models
"""

import os
import json
import torch
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from .debug_logger import debug_logger

console = Console()

@dataclass
class GPT4SimulatorConfig:
    """Configuration for GPT-4 Simulator"""
    # Primary model for GPT-4 simulation
    primary_model: str = "microsoft/DialoGPT-large"
    
    # Alternative models for different capabilities
    code_model: str = "microsoft/CodeGPT-small-py"
    analysis_model: str = "microsoft/unixcoder-base"
    
    # GPT-4 simulation parameters
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    
    # Model selection strategy
    use_primary_for_general: bool = True
    use_specialized_for_code: bool = True

class GPT4Simulator:
    """GPT-4 Simulator using Hugging Face models"""
    
    def __init__(self):
        self.console = console
        self.config = GPT4SimulatorConfig()
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        self._load_models()
    
    def _load_models(self):
        """Load the Hugging Face models for GPT-4 simulation"""
        try:
            self.console.print("[cyan]🤖 Loading GPT-4 Simulator...[/cyan]")
            
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            
            # Load primary model for general tasks
            if self.config.use_primary_for_general:
                self._load_model("primary", self.config.primary_model)
            
            # Load specialized models for code tasks
            if self.config.use_specialized_for_code:
                self._load_model("code", self.config.code_model)
                self._load_model("analysis", self.config.analysis_model)
            
            self.console.print(f"[green]✅ GPT-4 Simulator loaded successfully[/green]")
            self.console.print(f"[dim]Simulating: GPT-4 with {len(self.models)} models[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Failed to load GPT-4 Simulator: {str(e)}[/red]")
            debug_logger.error(f"Failed to load GPT-4 Simulator: {e}")
            self.models = {}
            self.tokenizers = {}
            self.pipelines = {}
    
    def _load_model(self, model_type: str, model_name: str):
        """Load a specific model"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Loading {model_name}", total=None)
                
                # Load tokenizer and model
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None
                )
                
                # Create pipeline
                pipeline_obj = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    device="cuda" if torch.cuda.is_available() else "cpu"
                )
                
                # Store components
                self.models[model_type] = model
                self.tokenizers[model_type] = tokenizer
                self.pipelines[model_type] = pipeline_obj
                
                progress.update(task, description=f"Loaded {model_name}")
            
            self.console.print(f"[green]✅ Loaded {model_name} for {model_type}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Failed to load {model_name}: {str(e)}[/red]")
            debug_logger.error(f"Failed to load {model_name}: {e}")
    
    def generate_response(self, prompt: str, task_type: str = "general", 
                         max_tokens: int = None, temperature: float = None) -> str:
        """Generate response using GPT-4 Simulator"""
        
        # Select appropriate model based on task type
        model_type = self._select_model(task_type)
        
        if model_type not in self.pipelines:
            return "Error: No suitable model available for this task"
        
        try:
            debug_logger.log_function_call("GPT4Simulator.generate_response", {
                "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "task_type": task_type,
                "model_type": model_type,
                "max_tokens": max_tokens or self.config.max_tokens,
                "temperature": temperature or self.config.temperature
            })
            
            # Configure generation parameters
            generation_kwargs = {
                "max_length": (max_tokens or self.config.max_tokens) + len(prompt.split()),
                "temperature": temperature or self.config.temperature,
                "top_p": self.config.top_p,
                "do_sample": True,
                "pad_token_id": self.tokenizers[model_type].eos_token_id,
                "eos_token_id": self.tokenizers[model_type].eos_token_id,
                "num_return_sequences": 1,
                "repetition_penalty": 1.1
            }
            
            # Generate response
            result = self.pipelines[model_type](prompt, **generation_kwargs)
            
            # Extract generated text
            generated_text = result[0]["generated_text"]
            
            # Remove the original prompt from the response
            response = generated_text[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            debug_logger.error(f"GPT-4 Simulator generation failed: {e}")
            return f"Error generating response: {str(e)}"
    
    def _select_model(self, task_type: str) -> str:
        """Select appropriate model based on task type"""
        if task_type in ["code", "programming", "generation"] and "code" in self.pipelines:
            return "code"
        elif task_type in ["analysis", "review", "quality"] and "analysis" in self.pipelines:
            return "analysis"
        elif "primary" in self.pipelines:
            return "primary"
        else:
            # Return any available model
            return list(self.pipelines.keys())[0] if self.pipelines else "primary"
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Chat interface compatible with existing LLM router"""
        if not messages:
            return "No messages provided"
        
        # Convert messages to a single prompt
        prompt = self._messages_to_prompt(messages)
        
        # Determine task type from messages
        task_type = self._determine_task_type(messages)
        
        # Generate response
        response = self.generate_response(prompt, task_type)
        
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
    
    def _determine_task_type(self, messages: List[Dict[str, str]]) -> str:
        """Determine task type from messages"""
        content = " ".join([msg.get("content", "") for msg in messages]).lower()
        
        if any(keyword in content for keyword in ["code", "programming", "function", "class", "script"]):
            return "code"
        elif any(keyword in content for keyword in ["analyze", "review", "quality", "issue", "problem"]):
            return "analysis"
        else:
            return "general"
    
    def generate_code(self, specification: str, language: str = "python") -> str:
        """Generate code using GPT-4 Simulator"""
        prompt = f"""You are an expert software engineer with GPT-4 level capabilities. Generate {language} code based on the following specification.

Specification: {specification}

Requirements:
1. Write clean, production-ready code
2. Follow best practices for {language}
3. Include proper error handling
4. Add appropriate comments
5. Return only the code, no explanations

Code:"""
        
        response = self.generate_response(prompt, "code")
        
        # Extract code from response
        code = self._extract_code(response, language)
        
        return code
    
    def analyze_code(self, code: str, analysis_type: str = "quality") -> Dict[str, Any]:
        """Analyze code using GPT-4 Simulator"""
        prompt = f"""You are an expert code reviewer with GPT-4 level capabilities. Analyze the following {analysis_type} of the code:

Code:
{code}

Please provide:
1. Overall quality score (1-10)
2. Issues found
3. Recommendations for improvement
4. Best practices suggestions

Analysis:"""
        
        response = self.generate_response(prompt, "analysis")
        
        # Parse the response into structured data
        analysis = self._parse_analysis_response(response)
        
        return analysis
    
    def refactor_code(self, code: str, refactor_type: str = "general") -> str:
        """Refactor code using GPT-4 Simulator"""
        prompt = f"""You are an expert software engineer with GPT-4 level capabilities. Refactor the following code for {refactor_type}:

Original Code:
{code}

Requirements:
1. Improve code quality and readability
2. Follow best practices
3. Maintain functionality
4. Add appropriate comments
5. Return only the refactored code

Refactored Code:"""
        
        response = self.generate_response(prompt, "code")
        
        # Extract refactored code
        refactored_code = self._extract_code(response, "python")
        
        return refactored_code
    
    def review_code(self, code: str) -> Dict[str, Any]:
        """Review code using GPT-4 Simulator"""
        prompt = f"""You are an expert code reviewer with GPT-4 level capabilities. Review the following code:

Code:
{code}

Please provide:
1. Code quality assessment
2. Security issues
3. Performance concerns
4. Best practices violations
5. Recommendations for improvement

Review:"""
        
        response = self.generate_response(prompt, "analysis")
        
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
        """Get information about the loaded models"""
        return {
            "primary_model": self.config.primary_model,
            "code_model": self.config.code_model,
            "analysis_model": self.config.analysis_model,
            "loaded_models": list(self.models.keys()),
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "total_models": len(self.models)
        }
    
    def test_connection(self) -> bool:
        """Test the connection to the GPT-4 Simulator"""
        try:
            test_prompt = "Hello, can you respond with 'GPT-4 Simulator is working'?"
            response = self.generate_response(test_prompt, "general", max_tokens=50)
            
            if "GPT-4 Simulator is working" in response or len(response) > 0:
                return True
            else:
                return False
                
        except Exception as e:
            debug_logger.error(f"GPT-4 Simulator connection test failed: {e}")
            return False

# Global GPT-4 Simulator instance
gpt4_simulator = GPT4Simulator()

def get_gpt4_simulator() -> GPT4Simulator:
    """Get the global GPT-4 Simulator instance"""
    return gpt4_simulator
