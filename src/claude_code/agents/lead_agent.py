"""
LeadAgent - Main agent that has access to all tools and can call sub-agents
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from .loop_agent import LoopAgent
from .agent_settings import AgentSettings, DEFAULT_LEAD_AGENT_SETTINGS
from ..core.output_parser import OutputParser
from ..core.tool_executor import ToolExecutor
from ..tools import (
    TaskTool, BashTool, GlobTool, GrepTool, LSTool, 
    ReadTool, EditTool, WriteTool, WebFetchTool, 
    TodoWriteTool, WebSearchTool, ExitTool
)
from .prompts import lead_agent_prompt
from ..utils.context_utils import get_context_variables

class LeadAgent(LoopAgent):
    """Main agent that orchestrates all tools and sub-agents"""
    
    def __init__(self, model_manager=None, settings: Optional[AgentSettings] = None):
        super().__init__(
            name="LeadAgent",
            description="Main agent with access to all tools and sub-agents",
            available_tools=None,  # All tools available
            can_delegate=True,  # Can delegate tasks to sub-agents
            settings=settings or DEFAULT_LEAD_AGENT_SETTINGS.copy()
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
        # Get context variables from utils
        context_vars = get_context_variables()
        
        # Merge with provided context, giving priority to provided context
        merged_context = {**context_vars, **context}
        
        base_prompt = lead_agent_prompt.format(
            working_directory=merged_context.get("working_directory", "Unknown"),
            is_directory_a_git_repo=merged_context.get("is_directory_a_git_repo", "Unknown"),
            platform=merged_context.get("platform", "Unknown"),
            os_version=merged_context.get("os_version", "Unknown"),
            today_date=merged_context.get("today_date", "Unknown"),
            last_5_recent_commits=merged_context.get("last_5_recent_commits", "Unknown"),
        )
        
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
