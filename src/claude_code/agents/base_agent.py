"""
Base agent implementation
"""

from typing import Dict, Any, List
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base implementation for all agents"""
    
    def __init__(self, name: str, description: str = "", capabilities: List[str] = None):
        self.name = name
        self.description = description
        self.capabilities = capabilities or []
        self.model_manager = None
    
    def set_model_manager(self, model_manager):
        """Set the model manager for this agent"""
        self.model_manager = model_manager
    
    async def execute(self, request: str, context: Dict[str, Any]) -> str:
        """Execute the agent's task"""
        if not self.model_manager:
            return "Error: Model manager not set"
        
        # Prepare messages for the model
        messages = self._prepare_messages(request, context)
        
        # Generate response
        response = await self.model_manager.generate_response(messages)
        
        # Post-process response
        return self._post_process_response(response, request, context)
    
    def _prepare_messages(self, request: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepare messages for the model"""
        messages = []
        
        # Add system message
        system_prompt = self._get_system_prompt(context)
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        if "messages" in context:
            for msg in context["messages"][-5:]:  # Last 5 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current request
        messages.append({"role": "user", "content": request})
        
        return messages
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for this agent"""
        base_prompt = f"""You are a {self.name} agent with the following capabilities:
{', '.join(self.capabilities)}

Description: {self.description}

You should focus on your specific domain and provide helpful, accurate responses.
"""
        
        # Add project context if available
        if "project" in context:
            project = context["project"]
            base_prompt += f"\nCurrent project: {project.get('path', 'Unknown')}"
            
            if project.get("files"):
                base_prompt += f"\nProject files: {', '.join(project['files'].keys())}"
        
        return base_prompt
    
    def _post_process_response(self, response: str, request: str, context: Dict[str, Any]) -> str:
        """Post-process the model response"""
        # Override in subclasses for specific processing
        return response