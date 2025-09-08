import httpx, os
from typing import List, Dict, Any, Optional
from enum import Enum
from ..utils.platform_utils import check_ollama_installed

try:
    from ..config import config
except ImportError:
    # Fallback if config not available
    class FallbackConfig:
        def get(self, key, default=None): return os.getenv(key.replace('.', '_').upper(), default)
        def get_available_backends(self): return ['ollama'] if check_ollama_installed() else []
        def is_enterprise_configured(self): return False
    config = FallbackConfig()

REST_API_URL = config.get('llm.rest_api_url') or os.getenv("LLM_API_URL")
REST_API_KEY = config.get('llm.rest_api_key') or os.getenv("LLM_API_KEY")
OLLAMA_URL = config.get('llm.ollama_url') or "http://localhost:11434/api/chat"

class TaskType(Enum):
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    CODE_REVIEW = "code_review"
    PLANNING = "planning"
    REFACTORING = "refactoring"
    DEBUGGING = "debugging"
    EXPLANATION = "explanation"

class LLMRouter:
    def __init__(self, backend: str = "auto", devstral_model: str = None, rest_model: str = None, enterprise_model: str = None):
        self.backend = backend
        self.devstral_model = devstral_model or config.get('llm.ollama_model', 'devstral')
        self.rest_model = rest_model or config.get('llm.rest_model', 'gpt-3.5-turbo')
        self.enterprise_model = enterprise_model or config.get('llm.enterprise_model', 'enterprise-default')
        
        # Initialize enterprise provider if configured
        self.enterprise_provider = None
        if config.is_enterprise_configured():
            try:
                from ..enterprise_llm import EnterpriseLLMProvider
                enterprise_config = {
                    'token_url': config.get('llm.enterprise_token_url'),
                    'chat_url': config.get('llm.enterprise_chat_url'),
                    'app_id': config.get('llm.enterprise_app_id'),
                    'app_key': config.get('llm.enterprise_app_key'),
                    'app_resource': config.get('llm.enterprise_app_resource')
                }
                self.enterprise_provider = EnterpriseLLMProvider(enterprise_config)
            except Exception as e:
                print(f"⚠️ Enterprise LLM provider initialization failed: {e}")
        
        # Define which tasks work best with which model
        # Priority: enterprise (if available) > ollama > openai
        available_backends = config.get_available_backends()
        
        # Smart routing based on available backends
        primary_backend = "ollama" if "ollama" in available_backends else (
            "enterprise" if "enterprise" in available_backends else "openai"
        )
        secondary_backend = "enterprise" if "enterprise" in available_backends else "openai"
        
        self.task_routing = {
            TaskType.CODE_GENERATION: primary_backend,     # Fast, good at code
            TaskType.CODE_ANALYSIS: primary_backend,       # Local analysis
            TaskType.CODE_REVIEW: primary_backend,         # Fast feedback
            TaskType.REFACTORING: primary_backend,         # Code transformation
            TaskType.DEBUGGING: primary_backend,           # Quick fixes
            TaskType.PLANNING: secondary_backend,          # High-level reasoning
            TaskType.EXPLANATION: secondary_backend,       # Complex explanations
        }

    def _detect_task_type(self, messages: List[Dict[str, Any]]) -> TaskType:
        """Automatically detect task type from message content"""
        if not messages:
            return TaskType.EXPLANATION
            
        last_message = messages[-1].get("content", "").lower()
        
        # Keywords that indicate task types
        if any(word in last_message for word in ["plan", "strategy", "approach", "architecture"]):
            return TaskType.PLANNING
        elif any(word in last_message for word in ["fix", "bug", "error", "debug"]):
            return TaskType.DEBUGGING
        elif any(word in last_message for word in ["refactor", "rename", "restructure", "clean up"]):
            return TaskType.REFACTORING
        elif any(word in last_message for word in ["review", "check", "analyze", "examine"]):
            return TaskType.CODE_REVIEW
        elif any(word in last_message for word in ["write", "create", "implement", "generate"]):
            return TaskType.CODE_GENERATION
        elif any(word in last_message for word in ["explain", "what", "how", "why"]):
            return TaskType.EXPLANATION
        else:
            return TaskType.CODE_ANALYSIS

    def _choose_backend(self, task_type: TaskType) -> str:
        """Choose the best backend for the task type"""
        if self.backend != "auto":
            # Map 'rest' to 'openai' for backward compatibility
            return "openai" if self.backend == "rest" else self.backend
        return self.task_routing.get(task_type, "openai")

    def chat(self, messages: List[Dict[str, Any]], task_type: TaskType = None):
        if task_type is None:
            task_type = self._detect_task_type(messages)
        
        chosen_backend = self._choose_backend(task_type)
        
        from rich.console import Console
        console = Console()
        console.print(f"🧠 [bold cyan]Task:[/bold cyan] {task_type.value} | [bold magenta]Backend:[/bold magenta] {chosen_backend}")
        
        # Try chosen backend first, fallback if it fails
        available_backends = config.get_available_backends()
        
        try:
            if chosen_backend == "openai":
                return self._chat_rest(messages)
            elif chosen_backend == "ollama":
                return self._chat_ollama(messages)
            elif chosen_backend == "enterprise":
                return self._chat_enterprise(messages)
        except Exception as e:
            # Fallback to other available backend
            for fallback in available_backends:
                if fallback != chosen_backend:
                    try:
                        if fallback == "openai":
                            return self._chat_rest(messages)
                        elif fallback == "ollama":
                            return self._chat_ollama(messages)
                        elif fallback == "enterprise":
                            return self._chat_enterprise(messages)
                    except Exception:
                        continue  # Try next backend
            
            # If all backends failed, return helpful error message
            ollama_status = '✅' if 'ollama' in available_backends else '❌ Not available'
            openai_status = '✅' if 'openai' in available_backends else '❌ Not configured'
            enterprise_status = '✅' if 'enterprise' in available_backends else '❌ Not configured'
            
            return f"Unable to connect to any LLM backend. Please check your configuration:\n" \
                   f"- Ollama: {ollama_status}\n" \
                   f"- OpenAI/REST API: {openai_status}\n" \
                   f"- Enterprise LLM: {enterprise_status}\n\n" \
                   f"Run 'lumos-cli setup' to configure backends.\n" \
                   f"Original error: {str(e)}"
        
        raise ValueError(f"Unknown backend: {chosen_backend}")

    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            with httpx.Client(timeout=2.0) as client:
                r = client.get(OLLAMA_URL.replace('/api/chat', '/api/tags'))
                return r.status_code == 200
        except Exception:
            return False

    def _chat_rest(self, messages: List[Dict[str, Any]], debug: bool = False) -> str:
        """Chat with REST API"""
        if not REST_API_URL or not REST_API_KEY:
            if debug:
                print(f"❌ OpenAI API Configuration Error:")
                print(f"   URL: {REST_API_URL or 'Not set'}")
                print(f"   Key: {'sk-...' + REST_API_KEY[-10:] if REST_API_KEY and len(REST_API_KEY) > 10 else 'Not set'}")
            raise ValueError("OpenAI API URL and key must be configured")
            
        headers = {
            "Authorization": f"Bearer {REST_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Prepare payload with required model parameter
        payload = {
            "model": self.rest_model,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        if debug:
            print(f"🚀 Making REST API call:")
            print(f"   URL: {REST_API_URL}")
            print(f"   Model: {self.rest_model}")
            print(f"   Messages: {len(messages)} messages")
        
        try:
            with httpx.Client(timeout=120.0) as client:
                r = client.post(REST_API_URL, headers=headers, json=payload)
                
                if debug:
                    print(f"   Response Status: {r.status_code}")
                
                if r.status_code != 200:
                    error_detail = "Unknown error"
                    try:
                        error_data = r.json()
                        error_detail = error_data.get("error", {}).get("message", str(error_data))
                    except:
                        error_detail = r.text[:200] + "..." if len(r.text) > 200 else r.text
                    
                    if debug:
                        print(f"   ❌ API Error: {error_detail}")
                    
                    raise ValueError(f"REST API error ({r.status_code}): {error_detail}")
                
                r.raise_for_status()
                response_data = r.json()
                
                if debug:
                    print(f"   ✅ Success!")
                
                return response_data["choices"][0]["message"]["content"]
                
        except httpx.TimeoutException as e:
            if debug:
                print(f"   ❌ Timeout Error: {e}")
            raise ValueError(f"REST API timeout: {e}")
        except httpx.RequestError as e:
            if debug:
                print(f"   ❌ Request Error: {e}")
            raise ValueError(f"REST API request error: {e}")
        except Exception as e:
            if debug:
                print(f"   ❌ Unexpected Error: {e}")
            raise ValueError(f"REST API unexpected error: {e}")

    def _chat_enterprise(self, messages: List[Dict[str, Any]], debug: bool = False) -> str:
        """Chat with Enterprise LLM"""
        if not self.enterprise_provider:
            raise ValueError("Enterprise LLM provider not initialized")
        
        return self.enterprise_provider.chat(messages, self.enterprise_model, debug=debug)
    
    def _chat_ollama(self, messages: List[Dict[str, Any]]) -> str:
        """Chat with Ollama (Devstral)"""
        with httpx.Client(timeout=120.0) as client:
            r = client.post(OLLAMA_URL, json={
                "model": self.devstral_model, 
                "messages": messages,
                "stream": False
            })
            r.raise_for_status()
            return r.json()["message"]["content"]
