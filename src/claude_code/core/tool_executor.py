"""
Tool Executor - Executes tool actions and returns results
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .output_parser import ToolAction, ParsedOutput
from ..tools import (
    TaskTool, BashTool, GlobTool, GrepTool, LSTool, 
    ReadTool, EditTool, WriteTool, WebFetchTool, 
    TodoWriteTool, WebSearchTool
)


@dataclass
class ToolResult:
    """Represents the result of a tool execution"""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    action_id: Optional[str] = None


@dataclass
class ExecutionResult:
    """Represents the result of executing all tool actions"""
    results: List[ToolResult]
    success_count: int
    error_count: int
    has_errors: bool = False


class ToolExecutor:
    """Executes tool actions and manages tool results"""
    
    def __init__(self):
        self.tools = {}
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
        """Set sub-agents for tools that need them"""
        if "Task" in self.tools:
            self.tools["Task"].set_sub_agents(sub_agents)
    
    async def execute_tool_actions(self, tool_actions: List[ToolAction], 
                                 context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """
        Execute a list of tool actions
        
        Args:
            tool_actions: List of tool actions to execute
            context: Optional context information
            
        Returns:
            ExecutionResult containing all tool results
        """
        if not tool_actions:
            return ExecutionResult(results=[], success_count=0, error_count=0)
        
        results = []
        success_count = 0
        error_count = 0
        
        # Execute tools sequentially to avoid conflicts
        for tool_action in tool_actions:
            result = await self._execute_single_tool(tool_action, context)
            results.append(result)
            
            if result.success:
                success_count += 1
            else:
                error_count += 1
        
        return ExecutionResult(
            results=results,
            success_count=success_count,
            error_count=error_count,
            has_errors=error_count > 0
        )
    
    async def _execute_single_tool(self, tool_action: ToolAction, 
                                 context: Optional[Dict[str, Any]]) -> ToolResult:
        """
        Execute a single tool action
        
        Args:
            tool_action: Tool action to execute
            context: Optional context information
            
        Returns:
            ToolResult containing execution result
        """
        tool_name = tool_action.tool_name
        parameters = tool_action.parameters
        action_id = tool_action.action_id
        
        if tool_name not in self.tools:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Tool '{tool_name}' not found",
                action_id=action_id
            )
        
        try:
            tool = self.tools[tool_name]
            
            # Execute the tool
            if hasattr(tool, 'execute'):
                result = await tool.execute(parameters, context)
            elif hasattr(tool, 'run'):
                result = await tool.run(parameters, context)
            else:
                # Try to call the tool directly with parameters
                result = await tool(parameters, context)
            
            return ToolResult(
                tool_name=tool_name,
                success=True,
                result=result,
                action_id=action_id
            )
            
        except Exception as e:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Error executing tool '{tool_name}': {str(e)}",
                action_id=action_id
            )
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        if tool_name not in self.tools:
            return None
        
        tool = self.tools[tool_name]
        return {
            "name": tool_name,
            "description": getattr(tool, 'description', 'No description available'),
            "parameters": getattr(tool, 'parameters', {}),
            "capabilities": getattr(tool, 'capabilities', [])
        }
    
    def format_tool_results(self, execution_result: ExecutionResult) -> str:
        """
        Format tool execution results for display
        
        Args:
            execution_result: Result of tool execution
            
        Returns:
            Formatted string of results
        """
        if not execution_result.results:
            return "No tools were executed."
        
        formatted_results = []
        
        for result in execution_result.results:
            if result.success:
                formatted_results.append(f"✅ {result.tool_name}: {result.result}")
            else:
                formatted_results.append(f"❌ {result.tool_name}: {result.error}")
        
        summary = f"\nTool execution summary: {execution_result.success_count} successful, {execution_result.error_count} failed"
        
        return "\n".join(formatted_results) + summary
