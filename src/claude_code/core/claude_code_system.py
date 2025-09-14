"""
Claude Code System - New simplified architecture based on official implementation
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time

from ..agents.lead_agent import LeadAgent
from ..agents.general_purpose_agent import GeneralPurposeAgent
from ..agents.statusline_setup_agent import StatuslineSetupAgent
from ..agents.output_style_setup_agent import OutputStyleSetupAgent
from ..models.model_manager import ModelManager
from .workflow_pipeline import WorkflowPipeline
from ..utils.logger import get_logger, log_function_call, log_function_result, log_error, log_performance


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
        self.logger = get_logger("claude_code.system")
        
        log_function_call(self.logger, "ClaudeCodeSystem.__init__", config=config)
        
        try:
            # Initialize model manager
            self.logger.info("Initializing model manager")
            self.model_manager = ModelManager()
            
            # Initialize lead agent
            self.logger.info("Initializing lead agent")
            self.lead_agent = LeadAgent(self.model_manager)
            
            # Initialize workflow pipeline
            self.logger.info("Initializing workflow pipeline")
            self.workflow_pipeline = WorkflowPipeline(self.lead_agent, self.model_manager)
            
            # Initialize sub-agents
            self.logger.info("Initializing sub-agents")
            self.sub_agents = {
                "general-purpose": GeneralPurposeAgent(self.model_manager),
                "statusline-setup": StatuslineSetupAgent(self.model_manager),
                "output-style-setup": OutputStyleSetupAgent(self.model_manager)
            }
            
            # Register sub-agents with the workflow pipeline
            for name, agent in self.sub_agents.items():
                self.logger.debug(f"Registering sub-agent: {name}")
                self.workflow_pipeline.register_sub_agent(agent)
            
            # Set sub-agents for lead agent (for backward compatibility)
            self.lead_agent.set_sub_agents(self.sub_agents)
            
            self.logger.info("ClaudeCodeSystem initialized successfully")
            log_function_result(self.logger, "ClaudeCodeSystem.__init__", "Success", True)
            
        except Exception as e:
            log_error(self.logger, e, "ClaudeCodeSystem.__init__")
            raise
    
    async def initialize(self):
        """Initialize the system with model providers"""
        log_function_call(self.logger, "ClaudeCodeSystem.initialize")
        start_time = time.time()
        
        try:
            # Initialize model providers
            self.logger.info("Loading model providers")
            from ..models.openrouter_provider import OpenRouterProvider
            from ..models.mock_provider import MockProvider
            
            # Register OpenRouter as primary provider           
            self.logger.info("Registering OpenRouter provider")
            openrouter_provider = OpenRouterProvider()
            self.model_manager.register_provider(openrouter_provider, is_default=True)
            
            # Register Mock provider as final fallback
            self.logger.info("Registering Mock provider")
            mock_provider = MockProvider()
            self.model_manager.register_provider(mock_provider)
            
            self.model_manager.set_fallback_providers([openrouter_provider.name, mock_provider.name])
            
            # Initialize providers
            self.logger.info("Initializing model providers")
            await self.model_manager.initialize_providers()
            
            # Show provider status
            available_providers = self.model_manager.get_available_providers()
            self.logger.info(f"Available providers: {available_providers}")
            
            if self.config.debug_mode:
                self.logger.debug("Provider status details:")
                for provider_name in self.model_manager.providers.keys():
                    provider_info = self.model_manager.get_provider_info(provider_name)
                    status = "Available" if provider_info['available'] else "Unavailable"
                    self.logger.debug(f"  • {provider_name}: {status}")
            
            if not available_providers:
                self.logger.warning("No model providers are available. Please check your API keys.")
                self.logger.warning("Set OPENROUTER_API_KEY for OpenRouter provider.")
                self.logger.warning("Using mock provider for testing...")
            
            duration = time.time() - start_time
            log_performance(self.logger, "ClaudeCodeSystem.initialize", duration, 
                          providers_registered=len(self.model_manager.providers),
                          available_providers=len(available_providers))
            log_function_result(self.logger, "ClaudeCodeSystem.initialize", "Success", True)
            
        except Exception as e:
            log_error(self.logger, e, "ClaudeCodeSystem.initialize")
            raise
    
    async def process_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user request through the workflow pipeline
        
        Args:
            request: User's request/query
            context: Optional context information
            
        Returns:
            Response from the system
        """
        log_function_call(self.logger, "ClaudeCodeSystem.process_request", 
                         request=request[:100] + "..." if len(request) > 100 else request,
                         context_keys=list(context.keys()) if context else None)
        start_time = time.time()
        
        try:
            # Process with workflow pipeline
            self.logger.info("Processing request through workflow pipeline")
            result = await self.workflow_pipeline.process_request(request, context)
            
            duration = time.time() - start_time
            log_performance(self.logger, "ClaudeCodeSystem.process_request", duration,
                          success=result.success, agent_used=result.agent_used)
            
            if result.success:
                self.logger.info(f"Request processed successfully by {result.agent_used}")
                response = {
                    "response": result.content,
                    "context": self.workflow_pipeline.get_context(),
                    "agent_used": result.agent_used,
                    "tool_results": [tr.__dict__ for tr in result.tool_results]
                }
                log_function_result(self.logger, "ClaudeCodeSystem.process_request", "Success", True)
                return response
            else:
                self.logger.warning(f"Request processing failed: {result.error}")
                response = {
                    "error": result.error,
                    "response": result.content,
                    "context": self.workflow_pipeline.get_context()
                }
                log_function_result(self.logger, "ClaudeCodeSystem.process_request", "Failed", False)
                return response
            
        except Exception as e:
            log_error(self.logger, e, "ClaudeCodeSystem.process_request")
            import traceback
            error_msg = f"Error processing request: {str(e)}"
            if self.config.debug_mode:
                error_msg += f"\nTraceback: {traceback.format_exc()}"
                self.logger.debug(f"Full traceback: {traceback.format_exc()}")
            
            response = {
                "error": error_msg,
                "response": "I encountered an error while processing your request. Please try again.",
                "context": self.workflow_pipeline.get_context()
            }
            log_function_result(self.logger, "ClaudeCodeSystem.process_request", "Exception", False)
            return response
    
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
