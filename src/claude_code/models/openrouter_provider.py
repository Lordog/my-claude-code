"""
openrouter model provider
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
        except Exception as e:
            print(e)
            return False
    
    async def generate_response(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> str:
        """Generate response using OpenRouter with optional tool calling"""
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
        
        # Add tools if provided
        if tools:
            params["tools"] = tools
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["max_tokens", "temperature", "tools"]:
                params[key] = value
        
        try:
            response = self.client.chat.completions.create(**params)
            
            # Check if the response contains tool calls
            message = response.choices[0].message
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Return the raw response for tool calling
                return {
                    "content": message.content or "",
                    "tool_calls": message.tool_calls,
                    "finish_reason": response.choices[0].finish_reason
                }
            else:
                # Return just the content for regular responses
                return message.content or ""
                
        except Exception as e:
            raise Exception(f"Error generating response with OpenRouter: {str(e)}")
    
    async def shutdown(self):
        """Shutdown the provider"""
        self.client = None
