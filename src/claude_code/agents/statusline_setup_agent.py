"""
Statusline setup agent for configuring Claude Code status line settings
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class StatuslineSetupAgent(BaseAgent):
    """Agent for configuring Claude Code status line settings"""
    
    def __init__(self, model_manager=None):
        super().__init__(
            name="statusline-setup",
            description="Use this agent to configure the user's Claude Code status line setting",
            capabilities=["statusline_configuration", "file_editing", "settings_management"]
        )
        self.model_manager = model_manager
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for the statusline setup agent"""
        base_prompt = """You are a statusline setup agent specialized in configuring Claude Code status line settings.

Your capabilities include:
- Reading and understanding status line configuration files
- Editing status line settings and preferences
- Managing Claude Code status line customization
- Providing guidance on status line configuration options

Available tools:
- Read: Read configuration files
- Edit: Edit files with exact string replacements

When working on status line setup:
1. Read the current status line configuration
2. Understand the user's requirements
3. Make appropriate modifications
4. Ensure the configuration is valid and functional
5. Provide clear instructions on how to apply changes

Focus specifically on status line configuration and avoid other tasks."""
        
        # Add project context if available
        if "project" in context:
            project = context["project"]
            base_prompt += f"\n\nCurrent project: {project.get('path', 'Unknown')}"
        
        return base_prompt