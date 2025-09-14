"""
Workflow Pipeline - Main pipeline that orchestrates the agent framework
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .output_parser import OutputParser, ParsedOutput
from .tool_executor import ToolExecutor, ExecutionResult
from .agent_registry import AgentRegistry, TaskRouter
from .context_manager import ContextManager
from ..agents.base_agent import BaseAgent


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
        
        # Initialize components
        self.output_parser = OutputParser()
        self.tool_executor = ToolExecutor()
        self.agent_registry = AgentRegistry()
        self.task_router = TaskRouter(self.agent_registry)
        self.context_manager = ContextManager()
        
        # Set up lead agent
        if self.model_manager:
            self.lead_agent.set_model_manager(self.model_manager)
        
        # Set up tool executor with sub-agents
        self.tool_executor.set_sub_agents({})
    
    def register_sub_agent(self, agent: BaseAgent, priority: int = 0):
        """Register a sub-agent"""
        self.agent_registry.register_agent(agent, priority)
        
        # Update tool executor with new sub-agents
        sub_agents = {name: info.agent for name, info in self.agent_registry.agents.items()}
        self.tool_executor.set_sub_agents(sub_agents)
    
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
        try:
            # Update context manager
            if context:
                self.context_manager.session_data.update(context)
            
            # Add user message to context
            self.context_manager.add_message("user", request)
            
            # Get current context for agents
            current_context = self.context_manager.get_context()
            
            # Process with lead agent (now supports loop-based execution)
            agent_response = await self.lead_agent.execute(request, current_context)
            
            # Add agent response to context
            self.context_manager.add_message("assistant", agent_response)
            
            return WorkflowResult(
                content=agent_response,
                tool_results=[],  # Tool results are now handled within the agent loop
                agent_used=self.lead_agent.name,
                success=True
            )
            
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            self.context_manager.add_message("system", f"Error: {error_msg}")
            
            return WorkflowResult(
                content="I encountered an error while processing your request. Please try again.",
                tool_results=[],
                success=False,
                error=error_msg
            )
    
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
            self.context_manager.add_message("assistant", agent_response, 
                                           metadata={"agent": agent_name})
            
            return WorkflowResult(
                content=agent_response,
                tool_results=[],  # Tool results are now handled within the agent loop
                agent_used=agent_name,
                success=True
            )
            
        except Exception as e:
            error_msg = f"Error processing request with sub-agent: {str(e)}"
            self.context_manager.add_message("system", f"Error: {error_msg}")
            
            return WorkflowResult(
                content="I encountered an error while processing your request. Please try again.",
                tool_results=[],
                success=False,
                error=error_msg
            )
    
    async def auto_route_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """
        Automatically route a request to the best available agent
        
        Args:
            request: User's request/query
            context: Optional context information
            
        Returns:
            WorkflowResult containing the response and execution details
        """
        try:
            # Get current context
            current_context = self.context_manager.get_context()
            if context:
                current_context.update(context)
            
            # Route the task
            selected_agent, reasoning = self.task_router.route_task(request, current_context)
            
            if not selected_agent:
                return WorkflowResult(
                    content="I couldn't find a suitable agent to handle your request.",
                    tool_results=[],
                    success=False,
                    error="No suitable agent found"
                )
            
            # Add routing decision to context
            self.context_manager.add_message("system", f"Routing decision: {reasoning}")
            
            # Process with selected agent
            if selected_agent.name == self.lead_agent.name:
                return await self.process_request(request, context)
            else:
                return await self.process_with_sub_agent(request, selected_agent.name, context)
                
        except Exception as e:
            error_msg = f"Error in auto-routing: {str(e)}"
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
