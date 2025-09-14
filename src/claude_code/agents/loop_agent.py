"""
Loop-based agent implementation that supports multiple tool calls until Exit tool is called
"""

import asyncio
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from .base_agent import BaseAgent
from ..core.output_parser import OutputParser
from ..core.tool_executor import ToolExecutor
from ..tools import (
    TaskTool, BashTool, GlobTool, GrepTool, LSTool, 
    ReadTool, EditTool, WriteTool, WebFetchTool, 
    TodoWriteTool, WebSearchTool, ExitTool
)


class LoopAgent(BaseAgent):
    """Base agent that supports loop-based execution with tool calling"""
    
    def __init__(self, name: str, description: str = "", capabilities: List[str] = None, available_tools: List[str] = None, can_delegate: bool = False):
        super().__init__(name, description, capabilities)
        self.available_tools = available_tools or []
        self.can_delegate = can_delegate
        self.tools = {}
        self.output_parser = OutputParser()
        self.tool_executor = ToolExecutor()
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize available tools based on agent capabilities"""
        # Core tools available to all agents
        core_tools = {
            "Bash": BashTool(),
            "Glob": GlobTool(),
            "Grep": GrepTool(),
            "LS": LSTool(),
            "Read": ReadTool(),
            "Edit": EditTool(),
            "Write": WriteTool(),
            "WebFetch": WebFetchTool(),
            "TodoWrite": TodoWriteTool(),
            "WebSearch": WebSearchTool(),
            "Exit": ExitTool()
        }
        
        # Add delegation tool if agent can delegate
        if self.can_delegate:
            core_tools["Task"] = TaskTool()
        
        # Filter tools based on available_tools list
        if self.available_tools:
            self.tools = {name: tool for name, tool in core_tools.items() 
                         if name in self.available_tools}
        else:
            self.tools = core_tools
    
    def set_sub_agents(self, sub_agents: Dict[str, Any]):
        """Set the available sub-agents for delegation"""
        if "Task" in self.tools:
            self.tools["Task"].set_sub_agents(sub_agents)
        self.tool_executor.set_sub_agents(sub_agents)
    
    async def execute(self, request: str, context: Dict[str, Any]) -> str:
        """Execute the agent's task with loop-based tool calling"""
        if not self.model_manager:
            return "Error: Model manager not set"
        
        # Prepare initial messages
        messages = self._prepare_messages(request, context)
        
        # Execute loop-based tool calling
        return await self._execute_with_loop(messages, request, context)
    
    async def _execute_with_loop(self, initial_messages: List[Dict[str, str]], 
                                request: str, context: Dict[str, Any]) -> str:
        """Execute with loop-based tool calling until Exit tool is called"""
        messages = initial_messages.copy()
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        # Convert tools to Kimi format
        kimi_tools = [tool.get_kimi_schema() for tool in self.tools.values()]
        
        while iteration < max_iterations:
            iteration += 1
            
            # Generate response with tools
            response = await self.model_manager.generate_response(messages, tools=kimi_tools)
            
            # Check if response contains tool calls (Kimi format)
            if isinstance(response, dict) and "tool_calls" in response:
                # Handle Kimi tool calling format
                tool_actions = self._parse_kimi_tool_calls(response["tool_calls"])
                
                # Check if Exit tool was called
                if self._check_for_exit(tool_actions):
                    return self._handle_kimi_exit(response, tool_actions)
                
                # Execute tool actions if any
                if tool_actions:
                    tool_results = await self._execute_tools(tool_actions, context)
                    
                    # Add tool results to conversation
                    if tool_results:
                        tool_summary = self.tool_executor.format_tool_results(tool_results)
                        messages.append({"role": "assistant", "content": response["content"] or ""})
                        messages.append({"role": "user", "content": f"Tool execution results:\n{tool_summary}"})
                    else:
                        # No tools to execute, return the response
                        return response["content"] or ""
                else:
                    # No tool actions, return the response
                    return response["content"] or ""
            else:
                # Regular text response, parse for tool calls in text format
                parsed_output = self.output_parser.parse(response)
                
                # Check if Exit tool was called
                if self._check_for_exit(parsed_output.tool_actions):
                    return self._handle_exit(parsed_output, response)
                
                # Execute tool actions if any
                if parsed_output.has_tool_actions:
                    tool_results = await self._execute_tools(parsed_output.tool_actions, context)
                    
                    # Add tool results to conversation
                    if tool_results:
                        tool_summary = self.tool_executor.format_tool_results(tool_results)
                        messages.append({"role": "assistant", "content": response})
                        messages.append({"role": "user", "content": f"Tool execution results:\n{tool_summary}"})
                    else:
                        # No tools to execute, return the response
                        return response
                else:
                    # No tool actions, return the response
                    return response
        
        # Max iterations reached
        return f"Maximum iterations ({max_iterations}) reached. Please use the Exit tool to terminate execution."
    
    def _parse_kimi_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List:
        """Parse Kimi tool calls into ToolAction objects"""
        from ..core.output_parser import ToolAction
        import json
        
        tool_actions = []
        for tool_call in tool_calls:
            if tool_call.get("type") == "function":
                function = tool_call.get("function", {})
                tool_name = function.get("name")
                arguments = function.get("arguments", "{}")
                action_id = tool_call.get("id")
                
                try:
                    parameters = json.loads(arguments)
                except json.JSONDecodeError:
                    parameters = {}
                
                tool_action = ToolAction(
                    tool_name=tool_name,
                    parameters=parameters,
                    action_id=action_id
                )
                tool_actions.append(tool_action)
        
        return tool_actions
    
    def _check_for_exit(self, tool_actions: List) -> bool:
        """Check if any tool action is the Exit tool"""
        for action in tool_actions:
            if hasattr(action, 'tool_name') and action.tool_name == "Exit":
                return True
        return False
    
    def _handle_exit(self, parsed_output, response: str) -> str:
        """Handle the Exit tool call"""
        # Extract the content before the Exit tool call
        content = parsed_output.content.strip()
        if content:
            return content
        else:
            return "Task completed."
    
    def _handle_kimi_exit(self, response: Dict[str, Any], tool_actions: List) -> str:
        """Handle the Exit tool call from Kimi format"""
        # Extract the content before the Exit tool call
        content = response.get("content", "").strip()
        if content:
            return content
        else:
            return "Task completed."
    
    async def _execute_tools(self, tool_actions: List, context: Dict[str, Any]):
        """Execute tool actions and return results"""
        if not tool_actions:
            return None
        
        # Update tool executor with current tools
        self.tool_executor.tools = self.tools
        
        # Execute tools
        return await self.tool_executor.execute_tool_actions(tool_actions, context)
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for this agent"""
        base_prompt = f"""You are a {self.name} agent with the following capabilities:
{', '.join(self.capabilities)}

Description: {self.description}

Available tools:
{self._format_available_tools()}

Tool Usage Instructions:
To use tools, format your tool calls in one of these ways:
1. <tool_name>{"param1": "value1", "param2": "value2"}</tool_name>
2. [tool_name: {"param1": "value1", "param2": "value2"}]
3. TOOL_CALL: tool_name {"param1": "value1", "param2": "value2"}

You can make multiple tool calls in a single response. The system will execute all tools and provide you with the results.

IMPORTANT: When you have completed the task or encountered an error that cannot be resolved, you MUST call the Exit tool with either "success" or "failed" status.

Examples:
- <Read>{"file_path": "/path/to/file.txt"}</Read>
- [Bash: {"command": "ls -la"}]
- TOOL_CALL: WebSearch {"query": "python best practices"}
- <Exit>{"status": "success", "message": "Task completed successfully"}</Exit>

Always be helpful, accurate, and efficient in your responses."""
        
        # Add project context if available
        if "project" in context and context["project"] is not None:
            project = context["project"]
            base_prompt += f"\n\nCurrent project: {project.get('path', 'Unknown')}"
            
            if project.get("files"):
                base_prompt += f"\nProject files: {', '.join(project['files'].keys())}"
        
        return base_prompt
    
    def _format_available_tools(self) -> str:
        """Format the list of available tools for the system prompt"""
        tool_descriptions = []
        for tool_name, tool in self.tools.items():
            description = getattr(tool, 'description', 'No description available')
            tool_descriptions.append(f"- {tool_name}: {description}")
        return "\n".join(tool_descriptions)
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.tools.keys())
