"""
Hugging Face Model Manager for Enterprise LLM Replica
Provides local model inference for code operations
"""

import os
import torch
from typing import Dict, List, Optional, Any
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    AutoModelForSeq2SeqLM,
    pipeline,
    set_seed
)
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .debug_logger import debug_logger

console = Console()

class HuggingFaceModelManager:
    """Manages Hugging Face models for code operations"""
    
    def __init__(self):
        self.models = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.console = console
        
        # Model configurations for different code tasks
        self.model_configs = {
            "code_generation": {
                "model_name": "microsoft/CodeGPT-small-py",
                "task": "text-generation",
                "max_length": 512,
                "temperature": 0.7,
                "description": "Python code generation"
            },
            "code_analysis": {
                "model_name": "microsoft/unixcoder-base",
                "task": "text-classification",
                "max_length": 256,
                "temperature": 0.3,
                "description": "Code analysis and understanding"
            },
            "code_review": {
                "model_name": "microsoft/codebert-base",
                "task": "text-classification",
                "max_length": 512,
                "temperature": 0.5,
                "description": "Code review and quality assessment"
            },
            "code_refactoring": {
                "model_name": "Salesforce/codet5-base",
                "task": "text2text-generation",
                "max_length": 512,
                "temperature": 0.6,
                "description": "Code refactoring and improvement"
            },
            "general_code": {
                "model_name": "Salesforce/codegen-350M-mono",
                "task": "text-generation",
                "max_length": 1024,
                "temperature": 0.8,
                "description": "General purpose code generation"
            }
        }
        
        # Initialize with default model
        self.current_model = "general_code"
        self._load_model(self.current_model)
    
    def _load_model(self, model_type: str) -> bool:
        """Load a specific model"""
        try:
            if model_type not in self.model_configs:
                console.print(f"[red]Unknown model type: {model_type}[/red]")
                return False
            
            config = self.model_configs[model_type]
            model_name = config["model_name"]
            
            console.print(f"[cyan]Loading {model_name}...[/cyan]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Loading {model_name}", total=None)
                
                if config["task"] == "text-generation":
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    model = AutoModelForCausalLM.from_pretrained(model_name)
                    pipeline_obj = pipeline(
                        "text-generation",
                        model=model,
                        tokenizer=tokenizer,
                        device=self.device
                    )
                elif config["task"] == "text2text-generation":
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                    pipeline_obj = pipeline(
                        "text2text-generation",
                        model=model,
                        tokenizer=tokenizer,
                        device=self.device
                    )
                else:
                    pipeline_obj = pipeline(
                        config["task"],
                        model=model_name,
                        device=self.device
                    )
                
                progress.update(task, description=f"Loaded {model_name}")
            
            self.models[model_type] = {
                "pipeline": pipeline_obj,
                "config": config,
                "loaded": True
            }
            
            console.print(f"[green]✅ Loaded {model_name} successfully[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Failed to load {model_name}: {str(e)}[/red]")
            debug_logger.error(f"Failed to load model {model_name}: {e}")
            return False
    
    def generate_code(self, prompt: str, language: str = "python", max_length: int = 512) -> str:
        """Generate code using the current model"""
        try:
            if self.current_model not in self.models:
                self._load_model(self.current_model)
            
            model_info = self.models[self.current_model]
            pipeline_obj = model_info["pipeline"]
            config = model_info["config"]
            
            # Create a code-specific prompt
            code_prompt = self._create_code_prompt(prompt, language)
            
            # Generate code
            result = pipeline_obj(
                code_prompt,
                max_length=min(max_length, config["max_length"]),
                temperature=config["temperature"],
                do_sample=True,
                pad_token_id=pipeline_obj.tokenizer.eos_token_id,
                num_return_sequences=1
            )
            
            # Extract generated code
            generated_text = result[0]["generated_text"]
            code = self._extract_code(generated_text, language)
            
            debug_logger.log_function_call("HuggingFaceModelManager.generate_code", {
                "prompt": prompt,
                "language": language,
                "model": self.current_model,
                "generated_length": len(code)
            })
            
            return code
            
        except Exception as e:
            console.print(f"[red]❌ Code generation failed: {str(e)}[/red]")
            debug_logger.error(f"Code generation failed: {e}")
            return ""
    
    def analyze_code(self, code: str, analysis_type: str = "quality") -> Dict[str, Any]:
        """Analyze code using the analysis model"""
        try:
            if "code_analysis" not in self.models:
                self._load_model("code_analysis")
            
            model_info = self.models["code_analysis"]
            pipeline_obj = model_info["pipeline"]
            
            # Create analysis prompt
            analysis_prompt = self._create_analysis_prompt(code, analysis_type)
            
            # Analyze code
            result = pipeline_obj(analysis_prompt)
            
            # Process results
            analysis = self._process_analysis_result(result, analysis_type)
            
            debug_logger.log_function_call("HuggingFaceModelManager.analyze_code", {
                "code_length": len(code),
                "analysis_type": analysis_type,
                "result": analysis
            })
            
            return analysis
            
        except Exception as e:
            console.print(f"[red]❌ Code analysis failed: {str(e)}[/red]")
            debug_logger.error(f"Code analysis failed: {e}")
            return {"error": str(e)}
    
    def refactor_code(self, code: str, refactor_type: str = "general") -> str:
        """Refactor code using the refactoring model"""
        try:
            if "code_refactoring" not in self.models:
                self._load_model("code_refactoring")
            
            model_info = self.models["code_refactoring"]
            pipeline_obj = model_info["pipeline"]
            
            # Create refactoring prompt
            refactor_prompt = self._create_refactor_prompt(code, refactor_type)
            
            # Refactor code
            result = pipeline_obj(
                refactor_prompt,
                max_length=512,
                temperature=0.6,
                do_sample=True
            )
            
            # Extract refactored code
            refactored_code = self._extract_code(result[0]["generated_text"], "python")
            
            debug_logger.log_function_call("HuggingFaceModelManager.refactor_code", {
                "code_length": len(code),
                "refactor_type": refactor_type,
                "refactored_length": len(refactored_code)
            })
            
            return refactored_code
            
        except Exception as e:
            console.print(f"[red]❌ Code refactoring failed: {str(e)}[/red]")
            debug_logger.error(f"Code refactoring failed: {e}")
            return code
    
    def review_code(self, code: str) -> Dict[str, Any]:
        """Review code using the review model"""
        try:
            if "code_review" not in self.models:
                self._load_model("code_review")
            
            model_info = self.models["code_review"]
            pipeline_obj = model_info["pipeline"]
            
            # Create review prompt
            review_prompt = self._create_review_prompt(code)
            
            # Review code
            result = pipeline_obj(review_prompt)
            
            # Process review results
            review = self._process_review_result(result)
            
            debug_logger.log_function_call("HuggingFaceModelManager.review_code", {
                "code_length": len(code),
                "review": review
            })
            
            return review
            
        except Exception as e:
            console.print(f"[red]❌ Code review failed: {str(e)}[/red]")
            debug_logger.error(f"Code review failed: {e}")
            return {"error": str(e)}
    
    def switch_model(self, model_type: str) -> bool:
        """Switch to a different model"""
        if model_type not in self.model_configs:
            console.print(f"[red]Unknown model type: {model_type}[/red]")
            return False
        
        if model_type not in self.models:
            success = self._load_model(model_type)
            if not success:
                return False
        
        self.current_model = model_type
        console.print(f"[green]✅ Switched to {model_type} model[/green]")
        return True
    
    def list_models(self) -> None:
        """List available models and their status"""
        console.print("\n[bold]Available Models:[/bold]")
        console.print("=" * 50)
        
        for model_type, config in self.model_configs.items():
            status = "✅ Loaded" if model_type in self.models else "⏳ Not loaded"
            current = " (Current)" if model_type == self.current_model else ""
            
            console.print(f"\n[bold]{model_type}[/bold]{current}:")
            console.print(f"  Model: {config['model_name']}")
            console.print(f"  Description: {config['description']}")
            console.print(f"  Status: {status}")
    
    def _create_code_prompt(self, prompt: str, language: str) -> str:
        """Create a code generation prompt"""
        language_comments = {
            "python": "#",
            "javascript": "//",
            "typescript": "//",
            "go": "//",
            "java": "//",
            "cpp": "//",
            "c": "//"
        }
        
        comment = language_comments.get(language, "//")
        
        return f"""{comment} Generate {language} code for: {prompt}
{comment} Requirements:
{comment} 1. Write clean, production-ready code
{comment} 2. Follow best practices for {language}
{comment} 3. Include proper error handling
{comment} 4. Add appropriate comments
{comment} 5. Return only the code, no explanations

{comment} Code:"""
    
    def _create_analysis_prompt(self, code: str, analysis_type: str) -> str:
        """Create a code analysis prompt"""
        return f"""Analyze the following code for {analysis_type}:

Code:
{code}

Analysis:"""
    
    def _create_refactor_prompt(self, code: str, refactor_type: str) -> str:
        """Create a code refactoring prompt"""
        return f"""Refactor the following code for {refactor_type}:

Original Code:
{code}

Refactored Code:"""
    
    def _create_review_prompt(self, code: str) -> str:
        """Create a code review prompt"""
        return f"""Review the following code for quality, best practices, and potential issues:

Code:
{code}

Review:"""
    
    def _extract_code(self, generated_text: str, language: str) -> str:
        """Extract code from generated text"""
        # Remove the prompt part
        lines = generated_text.split('\n')
        code_lines = []
        
        # Find the start of the actual code
        in_code = False
        for line in lines:
            if line.strip().startswith('def ') or line.strip().startswith('class ') or line.strip().startswith('import '):
                in_code = True
            
            if in_code:
                code_lines.append(line)
        
        return '\n'.join(code_lines).strip()
    
    def _process_analysis_result(self, result: Any, analysis_type: str) -> Dict[str, Any]:
        """Process analysis results"""
        # This would be model-specific processing
        return {
            "analysis_type": analysis_type,
            "result": result,
            "confidence": 0.8,
            "recommendations": []
        }
    
    def _process_review_result(self, result: Any) -> Dict[str, Any]:
        """Process review results"""
        # This would be model-specific processing
        return {
            "quality_score": 0.8,
            "issues": [],
            "recommendations": [],
            "result": result
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        if self.current_model not in self.models:
            return {"error": "No model loaded"}
        
        model_info = self.models[self.current_model]
        config = model_info["config"]
        
        return {
            "current_model": self.current_model,
            "model_name": config["model_name"],
            "description": config["description"],
            "device": self.device,
            "max_length": config["max_length"],
            "temperature": config["temperature"]
        }

# Global model manager instance
hf_manager = HuggingFaceModelManager()

def get_huggingface_manager() -> HuggingFaceModelManager:
    """Get the global Hugging Face model manager"""
    return hf_manager
