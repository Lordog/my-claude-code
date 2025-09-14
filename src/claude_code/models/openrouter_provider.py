"""
openrouter model provider
"""

import os
import json
from typing import List, Dict, Any, Optional
from .model_manager import BaseModelProvider
from openai import OpenAI
from dotenv import load_dotenv
from ..utils.logger import get_logger
load_dotenv()

class OpenRouterProvider(BaseModelProvider):
    """Provider for models via OpenRouter"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "moonshotai/kimi-k2-0905"):
        super().__init__("openrouter")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.client = None
        self.logger = get_logger("claude_code.openrouter")
        
        if self.api_key:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
    
    async def check_availability(self) -> bool:
        """Check if OpenRouter provider is available"""
        if not self.client or not self.api_key:
            self.logger.warning("OpenRouter provider not available - no client or API key")
            return False
        
        try:
            # Test with a simple request
            self.logger.info("Testing OpenRouter API availability")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            self.logger.info(f"OpenRouter API availability test successful - Response: {response.choices[0].message.content}")
            return True
        except Exception as e:
            self.logger.error(f"OpenRouter API availability test failed: {e}")
            return False
    
    async def generate_response(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> str:
        """Generate response using OpenRouter with optional tool calling"""
        if not self.client:
            raise Exception("OpenRouter provider not initialized")
        
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            message_dict = {
                "role": msg["role"],
                "content": msg["content"]
            }
            # Add tool_calls if present (for assistant messages)
            if "tool_calls" in msg and msg["tool_calls"]:
                message_dict["tool_calls"] = msg["tool_calls"]
            openai_messages.append(message_dict)
        
        # Set default parameters
        params = {
            "model": self.model,
            "messages": openai_messages,
            "max_tokens": kwargs.get("max_tokens", 10000),
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        # Add tools if provided
        if tools:
            params["tools"] = tools
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["max_tokens", "temperature", "tools"]:
                params[key] = value
        
        # Log the request details
        self.logger.info(f"OpenRouter API Request - Model: {self.model}")
        self.logger.info(f"OpenRouter API Request - Messages: {json.dumps(openai_messages, indent=2, ensure_ascii=False)}")
        self.logger.info(f"OpenRouter API Request - Parameters: {json.dumps({k: v for k, v in params.items() if k not in ['messages', 'tools']}, indent=2, ensure_ascii=False)}")
        
        try:
            response = self.client.chat.completions.create(**params)
            
            # Log the response details
            message = response.choices[0].message
            self.logger.info(f"OpenRouter API Response - Content: {message.content or ''}")
            self.logger.info(f"OpenRouter API Response - Finish Reason: {response.choices[0].finish_reason}")
            
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls_data = [{
                    'id': tc.id,
                    'type': tc.type,
                    'function': {
                        'name': tc.function.name,
                        'arguments': tc.function.arguments
                    }
                } for tc in message.tool_calls]
                self.logger.info(f"OpenRouter API Response - Tool Calls: {json.dumps(tool_calls_data, indent=2, ensure_ascii=False)}")
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
            self.logger.error(f"OpenRouter API Error: {str(e)}")
            raise Exception(f"Error generating response with OpenRouter: {str(e)}")
    
    async def shutdown(self):
        """Shutdown the provider"""
        self.client = None
