"""
Base agent implementation
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from ..utils.logger import get_logger, log_function_call, log_function_result, log_error


class BaseAgent(ABC):
    """Base implementation for all agents"""
    
    def __init__(self, name: str, description: str = "", capabilities: List[str] = None, 
                 settings: Optional[Any] = None):
        self.name = name
        self.description = description
        self.capabilities = capabilities or []
        self.model_manager = None
        self.settings = settings
        self.logger = get_logger(f"claude_code.agent.{name.lower()}")
    
    def set_model_manager(self, model_manager):
        """Set the model manager for this agent"""
        self.model_manager = model_manager
    
    async def execute(self, request: str, context: Dict[str, Any]) -> str:
        """Execute the agent's task"""
        log_function_call(self.logger, f"{self.name}.execute", 
                         request=request[:100] + "..." if len(request) > 100 else request,
                         context_keys=list(context.keys()))
        
        try:
            if not self.model_manager:
                error_msg = "Error: Model manager not set"
                self.logger.error(error_msg)
                return error_msg
            
            # Prepare messages for the model
            self.logger.debug("Preparing messages for model")
            messages = self._prepare_messages(request, context)
            
            # Generate response
            self.logger.debug("Generating response from model")
            response = await self.model_manager.generate_response(messages)
            
            # Post-process response
            self.logger.debug("Post-processing response")
            result = self._post_process_response(response, request, context)
            
            log_function_result(self.logger, f"{self.name}.execute", "Success", True)
            return result
            
        except Exception as e:
            log_error(self.logger, e, f"{self.name}.execute")
            return f"Error executing {self.name}: {str(e)}"
    
    def _prepare_messages(self, request: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepare messages for the model"""
        messages = []
        
        # Add system message
        system_prompt = self._get_system_prompt(context)
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history (excluding the current request which is passed separately)
        if "messages" in context:
            # Get messages excluding the last user message (current request)
            context_messages = context["messages"]
            if context_messages and context_messages[-1]["role"] == "user":
                # Exclude the last user message since it's the current request
                context_messages = context_messages[:-1]
            
            # Get max context messages from settings, default to 5
            max_context = getattr(self.settings, 'max_context_messages', 5) if self.settings else 5
            for msg in context_messages[-max_context:]:  # Last N messages for context (excluding current request)
                message_dict = {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                # Add tool_calls if present
                if "tool_calls" in msg and msg["tool_calls"]:
                    message_dict["tool_calls"] = msg["tool_calls"]
                messages.append(message_dict)
        
        # Add the current user request
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