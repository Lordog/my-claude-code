"""
Kimi-k2 model provider
"""

import os
from typing import List, Dict, Any, Optional
from .model_manager import BaseModelProvider
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class OpenRouterProvider(BaseModelProvider):
    """Provider for models via OpenRouter"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "moonshotai/kimi-k2-0905"):
        super().__init__("openrouter")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
    
    async def check_availability(self) -> bool:
        """Check if OpenRouter provider is available"""
        if not self.client or not self.api_key:
            return False
        
        try:
            # Test with a simple request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception:
            return False
    
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response using OpenRouter"""
        if not self.client:
            raise Exception("OpenRouter provider not initialized")
        
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Set default parameters
        params = {
            "model": self.model,
            "messages": openai_messages,
            "max_tokens": kwargs.get("max_tokens", 2000),
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["max_tokens", "temperature"]:
                params[key] = value
        
        try:
            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating response with OpenRouter: {str(e)}")
    
    async def shutdown(self):
        """Shutdown the provider"""
        self.client = None
