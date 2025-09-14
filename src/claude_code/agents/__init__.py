"""
Agent implementations for Claude-Code-Python
"""

from .base_agent import BaseAgent
from .lead_agent import LeadAgent
from .general_purpose_agent import GeneralPurposeAgent
from .statusline_setup_agent import StatuslineSetupAgent
from .output_style_setup_agent import OutputStyleSetupAgent
from .agent_settings import (
    AgentSettings, 
    DEFAULT_LOOP_AGENT_SETTINGS, 
    DEFAULT_LEAD_AGENT_SETTINGS, 
    DEFAULT_GENERAL_PURPOSE_AGENT_SETTINGS
)

__all__ = [
    "BaseAgent",
    "LeadAgent",
    "GeneralPurposeAgent",
    "StatuslineSetupAgent", 
    "OutputStyleSetupAgent",
    "AgentSettings",
    "DEFAULT_LOOP_AGENT_SETTINGS",
    "DEFAULT_LEAD_AGENT_SETTINGS", 
    "DEFAULT_GENERAL_PURPOSE_AGENT_SETTINGS"
]
