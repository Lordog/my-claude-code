"""
Task tool for routing tasks to sub-agents
"""

import asyncio
from typing import Dict, Any, Optional
from .base_tool import BaseTool


class TaskTool(BaseTool):
    """Tool for routing tasks to specialized sub-agents"""
    
    def __init__(self, sub_agents: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="Task",
            description="Route a task to a specialized sub-agent for execution.",
            input_schema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "A short (3-5 word) description of the task"
                    },
                    "prompt": {
                        "type": "string", 
                        "description": "The task for the agent to perform"
                    },
                    "subagent_type": {
                        "type": "string",
                        "description": "The type of specialized agent to use for this task"
                    }
                },
                "required": ["description", "prompt", "subagent_type"],
                "additionalProperties": False
            }
        )
        self.sub_agents = sub_agents or {}
    
    def set_sub_agents(self, sub_agents: Dict[str, Any]):
        """Set the available sub-agents"""
        self.sub_agents = sub_agents
    
    async def execute(self, description: str, prompt: str, subagent_type: str) -> Dict[str, Any]:
        """Route the task to the appropriate sub-agent for execution"""
        if not self.validate_input(description=description, prompt=prompt, subagent_type=subagent_type):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        # Check if sub-agent type is available
        if subagent_type not in self.sub_agents:
            available_types = list(self.sub_agents.keys())
            return {
                "error": f"Unknown subagent type '{subagent_type}'. Available types: {available_types}",
                "result": None
            }
        
        try:
            # Get the sub-agent
            sub_agent = self.sub_agents[subagent_type]
            
            # Route the task to the sub-agent for execution
            result = await sub_agent.execute(prompt, {"description": description})
            
            return {
                "error": None,
                "result": result,
                "subagent_type": subagent_type,
                "description": description
            }
            
        except Exception as e:
            return {
                "error": f"Error routing task to {subagent_type}: {str(e)}",
                "result": None
            }
