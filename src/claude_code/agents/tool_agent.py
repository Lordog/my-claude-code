"""
Tool agent - handles tool execution and management
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class ToolAgent(BaseAgent):
    """Specialized agent for tool execution and management"""
    
    def __init__(self):
        super().__init__(
            name="tool",
            description="Specialized agent for executing tools, running commands, and managing system operations",
            capabilities=[
                "command_execution",
                "file_operations",
                "git_operations", 
                "package_management",
                "system_operations",
                "web_search",
                "api_calls"
            ]
        )
    
    def can_handle(self, request: str, context: Dict[str, Any]) -> bool:
        """Check if this is a tool-related request"""
        tool_keywords = [
            "run", "execute", "command", "terminal", "shell",
            "file", "directory", "folder", "create", "delete", "move", "copy",
            "git", "commit", "push", "pull", "branch", "merge",
            "install", "package", "dependency", "pip", "npm", "yarn",
            "search", "web", "api", "http", "request"
        ]
        
        request_lower = request.lower()
        return any(keyword in request_lower for keyword in tool_keywords)
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for tool agent"""
        return """You are a specialized tool agent with expertise in:

1. Command execution and terminal operations
2. File system operations (create, read, write, delete, move, copy)
3. Git version control operations
4. Package and dependency management
5. System administration tasks
6. Web search and API interactions
7. Process management and monitoring

When executing tools:
- Always consider safety and security implications
- Provide clear explanations of what commands will do
- Suggest alternatives when appropriate
- Handle errors gracefully
- Follow best practices for each tool

For file operations:
- Check if files exist before operations
- Provide backup suggestions for destructive operations
- Use appropriate file permissions
- Consider cross-platform compatibility

For git operations:
- Explain the purpose of each command
- Suggest commit messages
- Warn about potential conflicts
- Recommend branching strategies

Always be cautious with system-level operations and explain the risks."""
