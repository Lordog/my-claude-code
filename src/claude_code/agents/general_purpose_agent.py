"""
General-purpose agent for researching complex questions and executing multi-step tasks
"""

from typing import Dict, Any, List, Optional
from .loop_agent import LoopAgent
from .agent_settings import AgentSettings, DEFAULT_GENERAL_PURPOSE_AGENT_SETTINGS
from .prompts import general_purpose_agent_prompt
from ..utils.context_utils import get_context_variables


class GeneralPurposeAgent(LoopAgent):
    """General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks"""
    
    def __init__(self, model_manager=None, settings: Optional[AgentSettings] = None):
        super().__init__(
            name="general-purpose",
            description="General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks",
            capabilities=["research", "code_search", "multi_step_execution", "analysis", "problem_solving"],
            available_tools=None,  # All tools available
            can_delegate=False,  # Cannot delegate tasks
            settings=settings or DEFAULT_GENERAL_PURPOSE_AGENT_SETTINGS.copy()
        )
        self.model_manager = model_manager
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for the general-purpose agent"""
        # Get context variables from utils
        context_vars = get_context_variables()
        
        # Merge with provided context, giving priority to provided context
        merged_context = {**context_vars, **context}
        
        base_prompt = general_purpose_agent_prompt.format(
            working_directory=merged_context.get("working_directory", "Unknown"),
            is_directory_a_git_repo=merged_context.get("is_directory_a_git_repo", "Unknown"),
            platform=merged_context.get("platform", "Unknown"),
            os_version=merged_context.get("os_version", "Unknown"),
            today_date=merged_context.get("today_date", "Unknown"),
            last_5_recent_commits=merged_context.get("last_5_recent_commits", "Unknown"),
        )
        # Add project context if available
        if "project" in context:
            project = context["project"]
            base_prompt += f"\n\nCurrent project: {project.get('path', 'Unknown')}"
            
            if project.get("files"):
                base_prompt += f"\nProject files: {', '.join(project['files'].keys())}"
        
        return base_prompt
