"""
Claude-Code-Python: A Python implementation of Claude Code
"""

__version__ = "0.1.0"
__author__ = "Yuantongxin"

from .core.controller import ClaudeCodeController, ClaudeCodeConfig
from .core.agent_registry import AgentRegistry
from .core.context_manager import ContextManager

__all__ = [
    "ClaudeCodeController",
    "ClaudeCodeConfig",
    "AgentRegistry", 
    "ContextManager",
]
