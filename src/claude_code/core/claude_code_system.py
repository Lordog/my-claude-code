"""
Claude Code System - New simplified architecture based on official implementation
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ..agents.lead_agent import LeadAgent
from ..agents.general_purpose_agent import GeneralPurposeAgent
from ..agents.statusline_setup_agent import StatuslineSetupAgent
from ..agents.output_style_setup_agent import OutputStyleSetupAgent
from ..models.model_manager import ModelManager
from .workflow_pipeline import WorkflowPipeline


@dataclass
class ClaudeCodeConfig:
    """Configuration for Claude-Code-Python"""
    model: str = "moonshotai/kimi-k2-0905"
    debug_mode: bool = False


class ClaudeCodeSystem:
    """
    Main system that orchestrates the LeadAgent and sub-agents using the workflow pipeline
    """
    
    def __init__(self, config: Optional[ClaudeCodeConfig] = None):
        self.config = config or ClaudeCodeConfig()
        
        # Initialize model manager
        self.model_manager = ModelManager()
        
        # Initialize lead agent
        self.lead_agent = LeadAgent(self.model_manager)
        
        # Initialize workflow pipeline
        self.workflow_pipeline = WorkflowPipeline(self.lead_agent, self.model_manager)
        
        # Initialize sub-agents
        self.sub_agents = {
            "general-purpose": GeneralPurposeAgent(self.model_manager),
            "statusline-setup": StatuslineSetupAgent(self.model_manager),
            "output-style-setup": OutputStyleSetupAgent(self.model_manager)
        }
        
        # Register sub-agents with the workflow pipeline
        for name, agent in self.sub_agents.items():
            self.workflow_pipeline.register_sub_agent(agent)
        
        # Set sub-agents for lead agent (for backward compatibility)
        self.lead_agent.set_sub_agents(self.sub_agents)
    
    async def initialize(self):
        """Initialize the system with model providers"""
        # Initialize model providers
        from ..models.openrouter_provider import OpenRouterProvider
        from ..models.mock_provider import MockProvider
        
        # Register OpenRouter as primary provider           
        openrouter_provider = OpenRouterProvider()
        self.model_manager.register_provider(openrouter_provider, is_default=True)
        
        # Register Mock provider as final fallback
        mock_provider = MockProvider()
        self.model_manager.register_provider(mock_provider)
        
        self.model_manager.set_fallback_providers([openrouter_provider.name, mock_provider.name])
        
        # Initialize providers
        await self.model_manager.initialize_providers()
        
        # Show provider status
        available_providers = self.model_manager.get_available_providers()
        if self.config.debug_mode:
            print(f"🔧 Debug: Available providers: {available_providers}")
            for provider_name in self.model_manager.providers.keys():
                provider_info = self.model_manager.get_provider_info(provider_name)
                status = "✅ Available" if provider_info['available'] else "❌ Unavailable"
                print(f"  • {provider_name}: {status}")
        
        if not available_providers:
            print("⚠️  Warning: No model providers are available. Please check your API keys.")
            print("   Set OPENROUTER_API_KEY for OpenRouter provider.")
            print("   Using mock provider for testing...")
    
    async def process_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user request through the workflow pipeline
        
        Args:
            request: User's request/query
            context: Optional context information
            
        Returns:
            Response from the system
        """
        try:
            # Process with workflow pipeline
            result = await self.workflow_pipeline.process_request(request, context)
            
            if result.success:
                return {
                    "response": result.content,
                    "context": self.workflow_pipeline.get_context(),
                    "agent_used": result.agent_used,
                    "tool_results": [tr.__dict__ for tr in result.tool_results]
                }
            else:
                return {
                    "error": result.error,
                    "response": result.content,
                    "context": self.workflow_pipeline.get_context()
                }
            
        except Exception as e:
            import traceback
            error_msg = f"Error processing request: {str(e)}"
            if self.config.debug_mode:
                error_msg += f"\nTraceback: {traceback.format_exc()}"
            
            return {
                "error": error_msg,
                "response": "I encountered an error while processing your request. Please try again.",
                "context": self.workflow_pipeline.get_context()
            }
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context"""
        return self.workflow_pipeline.get_context()
    
    def clear_context(self):
        """Clear current context"""
        self.workflow_pipeline.clear_context()
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return self.workflow_pipeline.get_available_tools()
    
    def get_available_sub_agents(self) -> List[str]:
        """Get list of available sub-agents"""
        return self.workflow_pipeline.get_available_agents()
    
    def set_project(self, project_path: str, project_name: str = None):
        """Set the current project"""
        self.workflow_pipeline.set_project(project_path, project_name)
    
    def get_project(self):
        """Get current project information"""
        return self.workflow_pipeline.get_project()
    
    async def shutdown(self):
        """Shutdown the system and cleanup resources"""
        await self.model_manager.shutdown()
        self.clear_context()
