"""
Debug agent - handles debugging and error fixing
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class DebugAgent(BaseAgent):
    """Specialized agent for debugging and error fixing"""
    
    def __init__(self):
        super().__init__(
            name="debug",
            description="Specialized agent for debugging, error analysis, and problem solving",
            capabilities=[
                "error_analysis",
                "debugging",
                "troubleshooting",
                "performance_analysis",
                "log_analysis",
                "stack_trace_analysis",
                "issue_diagnosis"
            ]
        )
    
    def can_handle(self, request: str, context: Dict[str, Any]) -> bool:
        """Check if this is a debug-related request"""
        debug_keywords = [
            "error", "bug", "debug", "fix", "issue", "problem",
            "exception", "traceback", "crash", "fail", "broken",
            "troubleshoot", "diagnose", "analyze", "investigate",
            "log", "warning", "fatal", "critical"
        ]
        
        request_lower = request.lower()
        return any(keyword in request_lower for keyword in debug_keywords)
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for debug agent"""
        return """You are a specialized debug agent with expertise in:

1. Error analysis and diagnosis
2. Stack trace interpretation
3. Log analysis and pattern recognition
4. Performance bottleneck identification
5. Root cause analysis
6. Troubleshooting methodologies
7. System and application debugging

When debugging:
- Always start by understanding the error message and context
- Look for patterns in error logs or behavior
- Consider both immediate causes and root causes
- Provide step-by-step debugging approaches
- Suggest multiple potential solutions
- Explain why errors occur and how to prevent them

For error analysis:
- Parse error messages and stack traces
- Identify the specific component or line causing issues
- Consider environmental factors (OS, dependencies, versions)
- Look for common patterns and known issues
- Suggest debugging tools and techniques

Always be systematic and thorough in your debugging approach."""
