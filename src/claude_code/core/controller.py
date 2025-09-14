"""
Main controller for Claude-Code-Python
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .agent_registry import AgentRegistry
from .context_manager import ContextManager
from .task_router import TaskRouter
from ..models.model_manager import ModelManager

# TODO: only debug_mode is used now
@dataclass
class ClaudeCodeConfig:
    """Configuration for Claude-Code-Python"""
    model: str = "moonshotai/kimi-k2-0905"
    max_agents: int = 10
    enable_tools: bool = True
    debug_mode: bool = False


class ClaudeCodeController:
    """
    Main controller that orchestrates the entire Claude-Code-Python system
    """
    
    def __init__(self, config: Optional[ClaudeCodeConfig] = None):
        self.config = config or ClaudeCodeConfig()
        
        # Initialize core components
        self.agent_registry = AgentRegistry()
        self.context_manager = ContextManager()
        self.task_router = TaskRouter(self.agent_registry)
        self.model_manager = ModelManager()
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents"""
        from ..agents.main_agent import MainAgent
        from ..agents.code_agent import CodeAgent
        from ..agents.tool_agent import ToolAgent
        from ..agents.debug_agent import DebugAgent
        from ..agents.test_agent import TestAgent
        from ..agents.doc_agent import DocAgent
        
        # Register core agents
        self.agent_registry.register("main", MainAgent())
        self.agent_registry.register("code", CodeAgent())
        self.agent_registry.register("tool", ToolAgent())
        self.agent_registry.register("debug", DebugAgent())
        self.agent_registry.register("test", TestAgent())
        self.agent_registry.register("doc", DocAgent())
    
    async def process_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user request through the agent system
        
        Args:
            request: User's request/query
            context: Optional context information
            
        Returns:
            Response from the system
        """
        try:
            # Update context
            if context:
                self.context_manager.update_context(context)
            
            # Add request to context
            self.context_manager.add_message("user", request)
            
            # Route task to appropriate agent(s)
            selected_agents = await self.task_router.route_task(request, self.context_manager.get_context())
            
            # Execute task with selected agents
            results = []
            for agent_name, agent in selected_agents.items():
                result = await agent.execute(request, self.context_manager.get_context())
                results.append({
                    "agent": agent_name,
                    "result": result
                })
            
            # Combine results
            final_response = await self._combine_results(results)
            
            # Update context with response
            self.context_manager.add_message("assistant", final_response)
            
            return {
                "response": final_response,
                "agents_used": list(selected_agents.keys()),
                "context": self.context_manager.get_context()
            }
            
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            if self.config.debug_mode:
                error_msg += f"\nTraceback: {e.__traceback__}"
            
            return {
                "error": error_msg,
                "response": "I encountered an error while processing your request. Please try again.",
                "agents_used": [],
                "context": self.context_manager.get_context()
            }
    
    async def _combine_results(self, results: List[Dict[str, Any]]) -> str:
        """Combine results from multiple agents into a coherent response"""
        if not results:
            return "No agents were able to process this request."
        
        if len(results) == 1:
            return results[0]["result"]
        
        # For multiple agents, combine their outputs intelligently
        combined = "Based on the analysis from multiple agents:\n\n"
        for i, result in enumerate(results, 1):
            combined += f"**{result['agent'].title()} Agent:**\n{result['result']}\n\n"
        
        return combined.strip()
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agents"""
        return self.agent_registry.list_agents()
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context"""
        return self.context_manager.get_context()
    
    def clear_context(self):
        """Clear current context"""
        self.context_manager.clear_context()
    
    async def shutdown(self):
        """Shutdown the controller and cleanup resources"""
        await self.model_manager.shutdown()
        self.context_manager.clear_context()
