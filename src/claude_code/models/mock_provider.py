"""
Mock model provider for testing and development
"""

import asyncio
from typing import List, Dict, Any, Optional
from .model_manager import BaseModelProvider


class MockProvider(BaseModelProvider):
    """Mock provider for testing and development when no API keys are available"""
    
    def __init__(self, name: str = "mock"):
        super().__init__(name)
        self.responses = [
            "Hello! I'm a mock AI assistant. I can help you with various tasks.",
            "I understand you're looking for assistance. How can I help you today?",
            "That's an interesting question! Let me think about that...",
            "I'm here to help! What would you like to know?",
            "Great question! Here's what I think about that topic...",
        ]
        self.response_index = 0
    
    async def check_availability(self) -> bool:
        """Mock provider is always available"""
        return True
    
    async def generate_response(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> str:
        """Generate a mock response"""
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Generate a contextual response
        if "hello" in user_message.lower() or "hi" in user_message.lower():
            return "Hello! I'm a mock AI assistant. I'm here to help you with your questions and tasks. How can I assist you today?"
        elif "help" in user_message.lower():
            return "I'm a mock AI assistant designed for testing and development. I can simulate responses to various queries. What would you like to know?"
        elif "who are you" in user_message.lower():
            return "I'm a mock AI assistant created for testing the Claude-Code-Python system. I simulate responses when no real API providers are available."
        elif "error" in user_message.lower() or "bug" in user_message.lower():
            return "I can help you debug issues! As a mock assistant, I can simulate various debugging scenarios. What specific error are you encountering?"
        elif "code" in user_message.lower() or "programming" in user_message.lower():
            return "I can help with programming questions! I can simulate code generation, debugging, and programming advice. What programming topic interests you?"
        else:
            # Use rotating responses for other queries
            response = self.responses[self.response_index % len(self.responses)]
            self.response_index += 1
            return f"{response}\n\n(Note: This is a mock response. In a real setup, you would need to configure API keys for actual AI providers.)"
    
    async def shutdown(self):
        """Shutdown the mock provider"""
        pass
