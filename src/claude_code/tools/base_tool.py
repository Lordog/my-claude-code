"""
Base tool implementation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json


class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.input_schema = input_schema
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters against schema"""
        # Basic validation - can be enhanced with jsonschema
        required_fields = self.input_schema.get('required', [])
        
        for field in required_fields:
            if field not in kwargs:
                return False
        
        return True
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema for the model"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }
    
    def get_kimi_schema(self) -> Dict[str, Any]:
        """Get the tool schema in Kimi format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema
            }
        }