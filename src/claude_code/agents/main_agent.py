"""
Main agent - orchestrates other agents and handles general tasks
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class MainAgent(BaseAgent):
    """Main orchestrating agent"""
    
    def __init__(self):
        super().__init__(
            name="main",
            description="Main orchestrating agent that coordinates other agents and handles general tasks",
            capabilities=[
                "coordination",
                "task_planning", 
                "general_assistance",
                "agent_management",
                "project_overview"
            ]
        )
    
    def can_handle(self, request: str, context: Dict[str, Any]) -> bool:
        """Main agent can handle any request as a fallback"""
        return True
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for main agent"""
        base_prompt = """You are the main orchestrating agent for Claude-Code-Python. Your role is to:

1. Understand user requests and determine the best approach
2. Coordinate with specialized agents when needed
3. Provide general assistance and project guidance
4. Manage overall project context and state

You have access to specialized agents for:
- Code generation and analysis (Code Agent)
- Tool execution and management (Tool Agent) 
- Debugging and error fixing (Debug Agent)
- Testing and quality assurance (Test Agent)
- Documentation and explanations (Doc Agent)

When a request requires specialized knowledge, you should:
1. Acknowledge the request
2. Explain which specialized agent would be best suited
3. Provide general guidance or coordinate the response

Always be helpful, clear, and professional in your responses."""
        
        # Add project context
        if "project" in context:
            project = context["project"]
            base_prompt += f"\n\nCurrent project context:\n"
            base_prompt += f"- Project path: {project.get('path', 'Unknown')}\n"
            
            if project.get("files"):
                base_prompt += f"- Available files: {', '.join(project['files'].keys())}\n"
            
            if project.get("dependencies"):
                base_prompt += f"- Dependencies: {', '.join(project['dependencies'])}\n"
        
        return base_prompt
