"""Enterprise LLM Provider for corporate environments with custom authentication"""

import httpx
import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class EnterpriseToken:
    """Represents an enterprise authentication token"""
    token: str
    expires_at: datetime
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired (with 5 minute buffer)"""
        return datetime.now() >= (self.expires_at - timedelta(minutes=5))


class EnterpriseLLMProvider:
    """Enterprise LLM provider with custom authentication and API format"""
    
    def __init__(self, config: Dict[str, str]):
        """
        Initialize enterprise provider with configuration
        
        Args:
            config: Dictionary with keys:
                - token_url: URL to get bearer token
                - chat_url: URL for chat completions
                - app_id: Application ID
                - app_key: Application key  
                - app_resource: Application resource identifier
        """
        self.token_url = config.get('token_url')
        self.chat_url = config.get('chat_url')
        self.app_id = config.get('app_id')
        self.app_key = config.get('app_key')
        self.app_resource = config.get('app_resource')
        
        # Validate required configuration
        required_fields = ['token_url', 'chat_url', 'app_id', 'app_key', 'app_resource']
        missing = [field for field in required_fields if not config.get(field)]
        if missing:
            raise ValueError(f"Missing required enterprise configuration: {', '.join(missing)}")
        
        self._token: Optional[EnterpriseToken] = None
        self.timeout = 120.0
    
    def _get_bearer_token(self, debug: bool = False) -> str:
        """Get bearer token from enterprise token endpoint"""
        
        if debug:
            print(f"🔐 Requesting enterprise token from: {self.token_url}")
        
        # Prepare token request payload
        token_payload = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "app_resource": self.app_resource
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.token_url,
                    json=token_payload,
                    headers=headers
                )
                response.raise_for_status()
                
                token_data = response.json()
                
                if debug:
                    print(f"✅ Token response status: {response.status_code}")
                    print(f"✅ Token data keys: {list(token_data.keys())}")
                
                # Extract token and expiration (adjust based on your enterprise API format)
                token = token_data.get('access_token') or token_data.get('token')
                expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
                
                if not token:
                    raise ValueError(f"No token found in response: {token_data}")
                
                # Calculate expiration time
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Cache the token
                self._token = EnterpriseToken(token=token, expires_at=expires_at)
                
                if debug:
                    print(f"✅ Token cached, expires at: {expires_at}")
                
                return token
                
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to enterprise token endpoint: {e}")
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"Enterprise token request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Enterprise token error: {e}")
    
    def _ensure_valid_token(self, debug: bool = False) -> str:
        """Ensure we have a valid, non-expired token"""
        if not self._token or self._token.is_expired:
            if debug and self._token:
                print(f"🔄 Token expired, refreshing...")
            return self._get_bearer_token(debug)
        
        if debug:
            print(f"✅ Using cached token (expires: {self._token.expires_at})")
        return self._token.token
    
    def chat(self, messages: List[Dict[str, Any]], model: str = "enterprise-default", debug: bool = False) -> str:
        """
        Send chat request to enterprise LLM endpoint
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model identifier (if supported by enterprise)
            debug: Enable debug logging
            
        Returns:
            Response content string
        """
        
        if debug:
            print(f"🏢 Enterprise LLM Chat Request")
            print(f"   Chat URL: {self.chat_url}")
            print(f"   Messages: {len(messages)} messages")
            print(f"   Model: {model}")
        
        # Get valid bearer token
        token = self._ensure_valid_token(debug)
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Prepare enterprise-specific payload
        # Adjust this format based on your enterprise API specification
        payload = {
            "messages": messages,
            "model": model,
            "max_tokens": 2000,
            "temperature": 0.7,
            "app_id": self.app_id,  # Include app_id if required by enterprise API
            "app_resource": self.app_resource  # Include resource if required
        }
        
        if debug:
            print(f"📤 Payload keys: {list(payload.keys())}")
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.chat_url,
                    json=payload,
                    headers=headers
                )
                
                if debug:
                    print(f"📥 Response status: {response.status_code}")
                
                response.raise_for_status()
                response_data = response.json()
                
                if debug:
                    print(f"📥 Response data keys: {list(response_data.keys())}")
                
                # Extract content from response (adjust based on enterprise API format)
                # Common formats:
                if 'choices' in response_data and response_data['choices']:
                    # OpenAI-compatible format
                    return response_data['choices'][0]['message']['content']
                elif 'response' in response_data:
                    # Simple response format
                    return response_data['response']
                elif 'content' in response_data:
                    # Direct content format
                    return response_data['content']
                elif 'text' in response_data:
                    # Text field format
                    return response_data['text']
                else:
                    # Fallback: return full response as string
                    return str(response_data)
                    
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to enterprise chat endpoint: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                # Token might be invalid, clear cache and retry once
                if debug:
                    print(f"🔄 401 error, clearing token cache and retrying...")
                self._token = None
                return self.chat(messages, model, debug)
            raise ConnectionError(f"Enterprise chat request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Enterprise chat error: {e}")
    
    def test_connection(self, debug: bool = True) -> bool:
        """Test enterprise LLM connection"""
        try:
            if debug:
                print("🧪 Testing enterprise LLM connection...")
            
            test_messages = [{"role": "user", "content": "Hello, respond with just 'OK'"}]
            response = self.chat(test_messages, debug=debug)
            
            if debug:
                print(f"✅ Enterprise LLM test successful: {response}")
            
            return True
        except Exception as e:
            if debug:
                print(f"❌ Enterprise LLM test failed: {e}")
            return False


def create_enterprise_provider_from_env() -> Optional[EnterpriseLLMProvider]:
    """Create enterprise provider from environment variables"""
    
    config = {
        'token_url': os.getenv('ENTERPRISE_TOKEN_URL'),
        'chat_url': os.getenv('ENTERPRISE_CHAT_URL'),
        'app_id': os.getenv('ENTERPRISE_APP_ID'),
        'app_key': os.getenv('ENTERPRISE_APP_KEY'),
        'app_resource': os.getenv('ENTERPRISE_APP_RESOURCE')
    }
    
    # Check if all required variables are present
    if all(config.values()):
        return EnterpriseLLMProvider(config)
    
    return None


def is_enterprise_configured() -> bool:
    """Check if enterprise configuration is available"""
    required_vars = [
        'ENTERPRISE_TOKEN_URL',
        'ENTERPRISE_CHAT_URL', 
        'ENTERPRISE_APP_ID',
        'ENTERPRISE_APP_KEY',
        'ENTERPRISE_APP_RESOURCE'
    ]
    
    return all(os.getenv(var) for var in required_vars)