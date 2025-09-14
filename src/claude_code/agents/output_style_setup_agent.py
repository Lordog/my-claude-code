"""
Output style setup agent for creating Claude Code output styles
"""

from typing import Dict, Any, List, Optional
from .loop_agent import LoopAgent
from .agent_settings import AgentSettings, DEFAULT_LOOP_AGENT_SETTINGS


class OutputStyleSetupAgent(LoopAgent):
    """Agent for creating Claude Code output styles"""
    
    def __init__(self, model_manager=None, settings: Optional[AgentSettings] = None):
        super().__init__(
            name="output-style-setup",
            description="Use this agent to create a Claude Code output style",
            capabilities=["output_style_creation", "file_operations", "style_configuration", "template_management"],
            available_tools=["Read", "Write", "Edit", "Glob", "LS", "Grep", "Exit"],
            can_delegate=False,  # Cannot delegate tasks
            settings=settings or DEFAULT_LOOP_AGENT_SETTINGS.copy()
        )
        self.model_manager = model_manager
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for the output style setup agent"""
        base_prompt = """You are an output style setup agent specialized in creating Claude Code output styles.

Your capabilities include:
- Reading and understanding output style configuration files
- Creating new output styles and templates
- Editing existing output style configurations
- Managing Claude Code output style customization
- Providing guidance on output style options

When working on output style setup:
1. Understand the user's style requirements
2. Read existing style configurations if any
3. Create or modify output style files
4. Ensure the style configuration is valid and functional
5. Provide clear instructions on how to apply the new style

IMPORTANT: When you have completed the task or encountered an error that cannot be resolved, you MUST call the Exit tool with either "success" or "failed" status.

Focus specifically on output style creation and avoid other tasks."""
        
        # Add project context if available
        if "project" in context:
            project = context["project"]
            base_prompt += f"\n\nCurrent project: {project.get('path', 'Unknown')}"
        
        return base_prompt