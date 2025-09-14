"""
LeadAgent - Main agent that has access to all tools and can call sub-agents
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from ..core.output_parser import OutputParser
from ..core.tool_executor import ToolExecutor
from ..tools import (
    TaskTool, BashTool, GlobTool, GrepTool, LSTool, 
    ReadTool, EditTool, WriteTool, WebFetchTool, 
    TodoWriteTool, WebSearchTool
)


class LeadAgent(BaseAgent):
    """Main agent that orchestrates all tools and sub-agents"""
    
    def __init__(self, model_manager=None):
        super().__init__(
            name="LeadAgent",
            description="Main agent with access to all tools and sub-agents",
            capabilities=["code_generation", "file_operations", "web_search", "task_delegation"]
        )
        self.model_manager = model_manager
        self.tools = {}
        self.sub_agents = {}
        self.output_parser = OutputParser()
        self.tool_executor = ToolExecutor()
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all available tools"""
        # Core tools
        self.tools["Task"] = TaskTool()
        self.tools["Bash"] = BashTool()
        self.tools["Glob"] = GlobTool()
        self.tools["Grep"] = GrepTool()
        self.tools["LS"] = LSTool()
        self.tools["Read"] = ReadTool()
        self.tools["Edit"] = EditTool()
        self.tools["Write"] = WriteTool()
        self.tools["WebFetch"] = WebFetchTool()
        self.tools["TodoWrite"] = TodoWriteTool()
        self.tools["WebSearch"] = WebSearchTool()
    
    def set_sub_agents(self, sub_agents: Dict[str, Any]):
        """Set the available sub-agents"""
        self.sub_agents = sub_agents
        # Update Task tool with sub-agents
        if "Task" in self.tools:
            self.tools["Task"].set_sub_agents(sub_agents)
        # Update tool executor with sub-agents
        self.tool_executor.set_sub_agents(sub_agents)
    
    def set_model_manager(self, model_manager):
        """Set the model manager for this agent"""
        self.model_manager = model_manager
    
    async def execute(self, request: str, context: Dict[str, Any]) -> str:
        """Execute the lead agent's task"""
        if not self.model_manager:
            return "Error: Model manager not set"
        
        # Prepare messages for the model
        messages = self._prepare_messages(request, context)
        
        # Generate response with tool calling capability
        response = await self._generate_response_with_tools(messages, request, context)
        
        return response
    
    def _prepare_messages(self, request: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepare messages for the model"""
        messages = []
        
        # Add system message
        system_prompt = self._get_system_prompt(context or {})
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        if context and "messages" in context:
            for msg in context["messages"][-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current request
        messages.append({"role": "user", "content": request})
        
        return messages
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for the lead agent"""
        base_prompt = """You are the LeadAgent, the main orchestrator in the Claude Code system. You have access to all tools and can route tasks to specialized sub-agents.

Available tools:
- Task: Route tasks to specialized sub-agents for execution
- Bash: Execute shell commands
- Glob: Find files by pattern
- Grep: Search file contents
- LS: List directory contents
- Read: Read files
- Edit: Edit files with exact string replacements
- Write: Write/create files
- WebFetch: Fetch web content
- TodoWrite: Manage task lists
- WebSearch: Search the web

Available sub-agents:
- general-purpose: For researching complex questions, searching for code, and executing multi-step tasks
- statusline-setup: For configuring Claude Code status line settings
- output-style-setup: For creating Claude Code output styles

When to use sub-agents:
- Use general-purpose for complex research or multi-step tasks
- Use statusline-setup for status line configuration
- Use output-style-setup for output style creation
- For simple file operations, use tools directly

Tool Usage Instructions:
To use tools, format your tool calls in one of these ways:
1. <tool_name>{"param1": "value1", "param2": "value2"}</tool_name>
2. [tool_name: {"param1": "value1", "param2": "value2"}]
3. TOOL_CALL: tool_name {"param1": "value1", "param2": "value2"}

Examples:
- <Read>{"file_path": "/path/to/file.txt"}</Read>
- [Bash: {"command": "ls -la"}]
- TOOL_CALL: WebSearch {"query": "python best practices"}

You can include multiple tool calls in a single response. The content outside tool calls will be shown to the user.

Always be helpful, accurate, and efficient in your responses."""
        
        # Add project context if available
        if "project" in context and context["project"] is not None:
            project = context["project"]
            base_prompt += f"\n\nCurrent project: {project.get('path', 'Unknown')}"
            
            if project.get("files"):
                base_prompt += f"\nProject files: {', '.join(project['files'].keys())}"
        
        return base_prompt
    
    async def _generate_response_with_tools(self, messages: List[Dict[str, str]], 
                                          request: str, context: Dict[str, Any]) -> str:
        """Generate response with tool calling capability"""
        # For now, implement a simple tool calling mechanism
        # In a real implementation, this would use a model that supports function calling

        return await self._generate_default_response(messages)
    
    
    async def _generate_default_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a default response using the model"""
        if self.model_manager:
            return await self.model_manager.generate_response(messages)
        else:
            return "I'm here to help! I have access to various tools and sub-agents. What would you like me to do?"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.tools.keys())
    
    def get_available_sub_agents(self) -> List[str]:
        """Get list of available sub-agents"""
        return list(self.sub_agents.keys())
