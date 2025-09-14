"""
Workflow Pipeline - Main pipeline that orchestrates the agent framework
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time

from .output_parser import OutputParser, ParsedOutput
from .tool_executor import ToolExecutor, ExecutionResult
from .agent_registry import AgentRegistry, TaskRouter
from .context_manager import ContextManager
from ..agents.base_agent import BaseAgent
from ..utils.logger import get_logger, log_function_call, log_function_result, log_error, log_performance


@dataclass
class WorkflowResult:
    """Result of a workflow execution"""
    content: str
    tool_results: List[ExecutionResult]
    agent_used: Optional[str] = None
    success: bool = True
    error: Optional[str] = None


class WorkflowPipeline:
    """
    Main workflow pipeline that orchestrates the agent framework
    
    The workflow is:
    1. User inputs a request
    2. Lead Agent receives the request and executes the specified task
    3. Lead agent can call tools itself, or delegate tasks to sub-agents
    4. Every time the lead agent outputs, the parser parses the outputs as content and/or tool actions
    5. The project module executes the tool actions and provides the execution results to the agent
    """
    
    def __init__(self, lead_agent: BaseAgent, model_manager=None):
        self.lead_agent = lead_agent
        self.model_manager = model_manager
        self.logger = get_logger("claude_code.workflow")
        
        log_function_call(self.logger, "WorkflowPipeline.__init__", 
                         lead_agent=lead_agent.name, model_manager=model_manager is not None)
        
        try:
            # Initialize components
            self.logger.info("Initializing workflow components")
            self.output_parser = OutputParser()
            self.tool_executor = ToolExecutor()
            self.agent_registry = AgentRegistry()
            self.task_router = TaskRouter(self.agent_registry)
            self.context_manager = ContextManager()
            
            # Set up lead agent
            if self.model_manager:
                self.logger.debug("Setting model manager for lead agent")
                self.lead_agent.set_model_manager(self.model_manager)
            
            # Set up tool executor with sub-agents
            self.tool_executor.set_sub_agents({})
            
            self.logger.info("WorkflowPipeline initialized successfully")
            log_function_result(self.logger, "WorkflowPipeline.__init__", "Success", True)
            
        except Exception as e:
            log_error(self.logger, e, "WorkflowPipeline.__init__")
            raise
    
    def register_sub_agent(self, agent: BaseAgent, priority: int = 0):
        """Register a sub-agent"""
        log_function_call(self.logger, "WorkflowPipeline.register_sub_agent", 
                         agent_name=agent.name, priority=priority)
        
        try:
            self.agent_registry.register_agent(agent, priority)
            self.logger.info(f"Registered sub-agent: {agent.name}")
            
            # Update tool executor with new sub-agents
            sub_agents = {name: info.agent for name, info in self.agent_registry.agents.items()}
            self.tool_executor.set_sub_agents(sub_agents)
            self.logger.debug(f"Updated tool executor with {len(sub_agents)} sub-agents")
            
            log_function_result(self.logger, "WorkflowPipeline.register_sub_agent", "Success", True)
            
        except Exception as e:
            log_error(self.logger, e, "WorkflowPipeline.register_sub_agent")
            raise
    
    def set_model_manager(self, model_manager):
        """Set the model manager for all agents"""
        self.model_manager = model_manager
        self.lead_agent.set_model_manager(model_manager)
        
        # Set model manager for all sub-agents
        for agent_info in self.agent_registry.agents.values():
            agent_info.agent.set_model_manager(model_manager)
    
    async def process_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """
        Process a user request through the workflow pipeline with loop-based execution
        
        Args:
            request: User's request/query
            context: Optional context information
            
        Returns:
            WorkflowResult containing the response and execution details
        """
        log_function_call(self.logger, "WorkflowPipeline.process_request", 
                         request=request[:100] + "..." if len(request) > 100 else request,
                         context_keys=list(context.keys()) if context else None)
        start_time = time.time()
        
        try:
            # Update context manager
            if context:
                self.logger.debug("Updating context with provided data")
                self.context_manager.session_data.update(context)
            
            # Add user message to context
            self.logger.debug("Adding user message to context")
            self.context_manager.add_message("user", request)
            
            # Get current context for agents
            current_context = self.context_manager.get_context()
            self.logger.debug(f"Context contains {len(current_context.get('messages', []))} messages")
            
            # Process with lead agent (now supports loop-based execution)
            self.logger.info("Processing request with lead agent")
            agent_response = await self.lead_agent.execute(request, current_context)
            
            # Add agent response to context
            self.logger.debug("Adding agent response to context")
            self.context_manager.add_message("assistant", agent_response.content, tool_calls=agent_response.tool_calls)
            
            duration = time.time() - start_time
            log_performance(self.logger, "WorkflowPipeline.process_request", duration,
                          agent_used=self.lead_agent.name, success=True)
            
            result = WorkflowResult(
                content=agent_response.content,
                tool_results=[],  # Tool results are now handled within the agent loop
                agent_used=self.lead_agent.name,
                success=True
            )
            
            log_function_result(self.logger, "WorkflowPipeline.process_request", "Success", True)
            return result
            
        except Exception as e:
            log_error(self.logger, e, "WorkflowPipeline.process_request")
            error_msg = f"Error processing request: {str(e)}"
            
            '''
            # Remove the last user message that caused the error and add error message
            if self.context_manager.messages and self.context_manager.messages[-1].role == "user":
                self.context_manager.messages.pop()
            '''
            self.context_manager.add_message("user", f"Error: {error_msg}")
            
            result = WorkflowResult(
                content="I encountered an error while processing your request. Please try again.",
                tool_results=[],
                success=False,
                error=error_msg
            )
            
            log_function_result(self.logger, "WorkflowPipeline.process_request", "Failed", False)
            return result
    
    async def process_with_sub_agent(self, request: str, agent_name: str, 
                                   context: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """
        Process a request with a specific sub-agent with loop-based execution
        
        Args:
            request: User's request/query
            agent_name: Name of the sub-agent to use
            context: Optional context information
            
        Returns:
            WorkflowResult containing the response and execution details
        """
        try:
            # Get the sub-agent
            sub_agent = self.agent_registry.get_agent(agent_name)
            if not sub_agent:
                return WorkflowResult(
                    content=f"Sub-agent '{agent_name}' not found.",
                    tool_results=[],
                    success=False,
                    error=f"Sub-agent '{agent_name}' not found"
                )
            
            # Update context manager
            if context:
                self.context_manager.session_data.update(context)
            
            # Add user message to context
            self.context_manager.add_message("user", request)
            
            # Get current context for agents
            current_context = self.context_manager.get_context()
            
            # Process with sub-agent (now supports loop-based execution)
            agent_response = await sub_agent.execute(request, current_context)
            
            # Add agent response to context
            self.context_manager.add_message("assistant", agent_response.content, 
                                           metadata={"agent": agent_name}, tool_calls=agent_response.tool_calls)
            
            return WorkflowResult(
                content=agent_response.content,
                tool_results=[],  # Tool results are now handled within the agent loop
                agent_used=agent_name,
                success=True
            )
            
        except Exception as e:
            error_msg = f"Error processing request with sub-agent: {str(e)}"
            
            '''
            # Remove the last user message that caused the error and add error message
            if self.context_manager.messages and self.context_manager.messages[-1].role == "user":
                self.context_manager.messages.pop()
            '''
            self.context_manager.add_message("user", f"Error: {error_msg}")
            
            return WorkflowResult(
                content="I encountered an error while processing your request. Please try again.",
                tool_results=[],
                success=False,
                error=error_msg
            )
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context"""
        return self.context_manager.get_context()
    
    def clear_context(self):
        """Clear current context"""
        self.context_manager.clear_context()
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agents"""
        return self.agent_registry.get_agent_names()
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return self.tool_executor.get_available_tools()
    
    def get_context_summary(self) -> str:
        """Get a summary of the current context"""
        return self.context_manager.get_context_summary()
    
    def set_project(self, project_path: str, project_name: str = None):
        """Set the current project"""
        self.context_manager.set_project(project_path, project_name)
    
    def get_project(self):
        """Get current project information"""
        return self.context_manager.get_project()
