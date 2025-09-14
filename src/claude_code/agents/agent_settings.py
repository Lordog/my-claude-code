"""
Agent settings and configuration parameters
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class AgentSettings:
    """Configuration settings for agents"""
    
    # Loop execution settings
    max_iterations: int = 100
    """Maximum number of iterations for loop-based agents to prevent infinite loops"""
    
    # Conversation history settings
    max_context_messages: int = 5
    """Maximum number of previous messages to include in context"""
    
    # Tool execution settings
    tool_timeout: Optional[float] = None
    """Timeout for tool execution in seconds (None for no timeout)"""
    
    # Response settings
    max_response_length: Optional[int] = None
    """Maximum length of agent responses (None for no limit)"""
    
    # Error handling settings
    max_retries: int = 3
    """Maximum number of retries for failed operations"""
    
    # Logging settings
    log_level: str = "DEBUG"
    """Logging level for agent operations"""
    
    # Tool calling settings
    enable_tool_calling: bool = True
    """Whether to enable tool calling for this agent"""
    
    # Delegation settings
    enable_delegation: bool = False
    """Whether this agent can delegate tasks to sub-agents"""
    
    def __post_init__(self):
        """Validate settings after initialization"""
        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        if self.max_context_messages < 0:
            raise ValueError("max_context_messages must be non-negative")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.tool_timeout is not None and self.tool_timeout <= 0:
            raise ValueError("tool_timeout must be positive if specified")
        if self.max_response_length is not None and self.max_response_length <= 0:
            raise ValueError("max_response_length must be positive if specified")
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("log_level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary"""
        return {
            "max_iterations": self.max_iterations,
            "max_context_messages": self.max_context_messages,
            "tool_timeout": self.tool_timeout,
            "max_response_length": self.max_response_length,
            "max_retries": self.max_retries,
            "log_level": self.log_level,
            "enable_tool_calling": self.enable_tool_calling,
            "enable_delegation": self.enable_delegation,
        }
    
    @classmethod
    def from_dict(cls, settings_dict: dict) -> "AgentSettings":
        """Create AgentSettings from dictionary"""
        return cls(**settings_dict)
    
    def copy(self) -> "AgentSettings":
        """Create a copy of the settings"""
        return AgentSettings(
            max_iterations=self.max_iterations,
            max_context_messages=self.max_context_messages,
            tool_timeout=self.tool_timeout,
            max_response_length=self.max_response_length,
            max_retries=self.max_retries,
            log_level=self.log_level,
            enable_tool_calling=self.enable_tool_calling,
            enable_delegation=self.enable_delegation,
        )
    
    def update(self, **kwargs) -> "AgentSettings":
        """Create a new instance with updated settings"""
        current_dict = self.to_dict()
        current_dict.update(kwargs)
        return AgentSettings.from_dict(current_dict)


# Default settings for different agent types
DEFAULT_LOOP_AGENT_SETTINGS = AgentSettings(
    max_iterations=100,
    max_context_messages=5,
    enable_tool_calling=True,
    enable_delegation=False,
)

DEFAULT_LEAD_AGENT_SETTINGS = AgentSettings(
    max_iterations=100,  # Lead agents might need more iterations
    max_context_messages=5,
    enable_tool_calling=True,
    enable_delegation=True,
)

DEFAULT_GENERAL_PURPOSE_AGENT_SETTINGS = AgentSettings(
    max_iterations=50,  # General purpose agents might need more iterations
    max_context_messages=5,
    enable_tool_calling=True,
    enable_delegation=False,
)
