"""
General-purpose agent for researching complex questions and executing multi-step tasks
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class GeneralPurposeAgent(BaseAgent):
    """General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks"""
    
    def __init__(self, model_manager=None):
        super().__init__(
            name="general-purpose",
            description="General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks",
            capabilities=["research", "code_search", "multi_step_execution", "analysis", "problem_solving"]
        )
        self.model_manager = model_manager
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for the general-purpose agent"""
        base_prompt = """You are a general-purpose agent specialized in researching complex questions, searching for code, and executing multi-step tasks.

Your capabilities include:
- Researching complex technical questions
- Searching for code patterns and implementations
- Executing multi-step tasks autonomously
- Analyzing codebases and providing insights
- Problem-solving and debugging assistance

Available tools:
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

You have access to all tools and should use them proactively to:
- Search for files and code patterns
- Read and analyze code
- Execute commands and scripts
- Research information online
- Break down complex tasks into manageable steps

When working on a task:
1. Understand the full scope of the request
2. Break it down into logical steps
3. Use appropriate tools to gather information
4. Execute the necessary actions
5. Provide a comprehensive summary of your work

Be thorough, accurate, and methodical in your approach."""
        
        # Add project context if available
        if "project" in context:
            project = context["project"]
            base_prompt += f"\n\nCurrent project: {project.get('path', 'Unknown')}"
            
            if project.get("files"):
                base_prompt += f"\nProject files: {', '.join(project['files'].keys())}"
        
        return base_prompt
