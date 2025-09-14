"""
LeadAgent - Main agent that has access to all tools and can call sub-agents
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from .loop_agent import LoopAgent
from ..core.output_parser import OutputParser
from ..core.tool_executor import ToolExecutor
from ..tools import (
    TaskTool, BashTool, GlobTool, GrepTool, LSTool, 
    ReadTool, EditTool, WriteTool, WebFetchTool, 
    TodoWriteTool, WebSearchTool, ExitTool
)


class LeadAgent(LoopAgent):
    """Main agent that orchestrates all tools and sub-agents"""
    
    def __init__(self, model_manager=None):
        super().__init__(
            name="LeadAgent",
            description="Main agent with access to all tools and sub-agents",
            capabilities=["code_generation", "file_operations", "web_search", "task_delegation"],
            available_tools=None,  # All tools available
            can_delegate=True  # Can delegate tasks to sub-agents
        )
        self.model_manager = model_manager
        self.sub_agents = {}
    
    def set_sub_agents(self, sub_agents: Dict[str, Any]):
        """Set the available sub-agents"""
        self.sub_agents = sub_agents
        # Update parent class with sub-agents
        super().set_sub_agents(sub_agents)
    
    def set_model_manager(self, model_manager):
        """Set the model manager for this agent"""
        self.model_manager = model_manager
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for the lead agent"""
        base_prompt = """You are the LeadAgent, the main orchestrator in the Claude Code system. You have access to all tools and can route tasks to specialized sub-agents.

Available sub-agents:
- general-purpose: For researching complex questions, searching for code, and executing multi-step tasks
- statusline-setup: For configuring Claude Code status line settings
- output-style-setup: For creating Claude Code output styles

When to use sub-agents:
- Use general-purpose for complex research or multi-step tasks
- Use statusline-setup for status line configuration
- Use output-style-setup for output style creation
- For simple file operations, use tools directly

IMPORTANT: When you have completed the task or encountered an error that cannot be resolved, you MUST call the Exit tool with either "success" or "failed" status.

Always be helpful, accurate, and efficient in your responses."""
        
        # Add project context if available
        if "project" in context and context["project"] is not None:
            project = context["project"]
            base_prompt += f"\n\nCurrent project: {project.get('path', 'Unknown')}"
            
            if project.get("files"):
                base_prompt += f"\nProject files: {', '.join(project['files'].keys())}"
        
        return base_prompt
    
    def get_available_sub_agents(self) -> List[str]:
        """Get list of available sub-agents"""
        return list(self.sub_agents.keys())
