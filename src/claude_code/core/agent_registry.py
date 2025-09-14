"""
Agent Registry and Task Router - Manages sub-agents and routes tasks
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from ..agents.base_agent import BaseAgent


@dataclass
class AgentInfo:
    """Information about a registered agent"""
    name: str
    agent: BaseAgent
    capabilities: List[str]
    description: str
    priority: int = 0  # Higher priority agents are preferred


class AgentRegistry:
    """Registry for managing sub-agents"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.capability_index: Dict[str, List[str]] = {}  # capability -> agent_names
    
    def register_agent(self, agent: BaseAgent, priority: int = 0):
        """
        Register an agent in the registry
        
        Args:
            agent: Agent instance to register
            priority: Priority level (higher = more preferred)
        """
        agent_info = AgentInfo(
            name=agent.name,
            agent=agent,
            capabilities=agent.capabilities,
            description=agent.description,
            priority=priority
        )
        
        self.agents[agent.name] = agent_info
        
        # Update capability index
        for capability in agent.capabilities:
            if capability not in self.capability_index:
                self.capability_index[capability] = []
            self.capability_index[capability].append(agent.name)
    
    def unregister_agent(self, agent_name: str) -> bool:
        """
        Unregister an agent from the registry
        
        Args:
            agent_name: Name of agent to unregister
            
        Returns:
            True if agent was found and removed, False otherwise
        """
        if agent_name not in self.agents:
            return False
        
        agent_info = self.agents[agent_name]
        
        # Remove from capability index
        for capability in agent_info.capabilities:
            if capability in self.capability_index:
                if agent_name in self.capability_index[capability]:
                    self.capability_index[capability].remove(agent_name)
                if not self.capability_index[capability]:
                    del self.capability_index[capability]
        
        del self.agents[agent_name]
        return True
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """
        Get an agent by name
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent instance or None if not found
        """
        if agent_name in self.agents:
            return self.agents[agent_name].agent
        return None
    
    def get_agents_by_capability(self, capability: str) -> List[BaseAgent]:
        """
        Get agents that have a specific capability
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of agents with the capability, sorted by priority
        """
        if capability not in self.capability_index:
            return []
        
        agent_names = self.capability_index[capability]
        agents = []
        
        for agent_name in agent_names:
            if agent_name in self.agents:
                agents.append(self.agents[agent_name])
        
        # Sort by priority (higher priority first)
        agents.sort(key=lambda x: x.priority, reverse=True)
        
        return [agent.agent for agent in agents]
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        return [agent_info.agent for agent_info in self.agents.values()]
    
    def get_agent_names(self) -> List[str]:
        """Get names of all registered agents"""
        return list(self.agents.keys())
    
    def get_agent_info(self, agent_name: str) -> Optional[AgentInfo]:
        """Get detailed information about an agent"""
        return self.agents.get(agent_name)


class TaskRouter:
    """Routes tasks to appropriate agents based on capabilities and context"""
    
    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry
    
    def find_best_agent(self, request: str, context: Dict[str, Any], 
                       required_capabilities: List[str] = None) -> Optional[BaseAgent]:
        """
        Find the best agent for a given request
        
        Args:
            request: User request
            context: Current context
            required_capabilities: Required capabilities for the task
            
        Returns:
            Best matching agent or None
        """
        if required_capabilities:
            # Find agents with all required capabilities
            candidates = []
            for capability in required_capabilities:
                capability_agents = self.agent_registry.get_agents_by_capability(capability)
                if not candidates:
                    candidates = capability_agents
                else:
                    # Keep only agents that have all capabilities
                    candidates = [agent for agent in candidates if agent in capability_agents]
            
            if candidates:
                return candidates[0]  # Return highest priority agent
        
        # Fallback: find agents that can handle the request
        all_agents = self.agent_registry.get_all_agents()
        
        for agent in all_agents:
            if hasattr(agent, 'can_handle') and agent.can_handle(request, context):
                return agent
        
        return None
    
    def route_task(self, request: str, context: Dict[str, Any], 
                  task_type: str = None) -> Tuple[Optional[BaseAgent], str]:
        """
        Route a task to an appropriate agent
        
        Args:
            request: User request
            context: Current context
            task_type: Optional task type hint
            
        Returns:
            Tuple of (selected_agent, reasoning)
        """
        # Determine required capabilities based on request analysis
        required_capabilities = self._analyze_required_capabilities(request, task_type)
        
        # Find best agent
        agent = self.find_best_agent(request, context, required_capabilities)
        
        if agent:
            reasoning = f"Selected {agent.name} based on capabilities: {', '.join(required_capabilities)}"
            return agent, reasoning
        else:
            # Fallback to general purpose agent if available
            general_agent = self.agent_registry.get_agent("general-purpose")
            if general_agent:
                reasoning = "No specific agent found, using general-purpose agent"
                return general_agent, reasoning
            else:
                reasoning = "No suitable agent found for this task"
                return None, reasoning
    
    def _analyze_required_capabilities(self, request: str, task_type: str = None) -> List[str]:
        """
        Analyze request to determine required capabilities
        
        Args:
            request: User request
            task_type: Optional task type hint
            
        Returns:
            List of required capabilities
        """
        capabilities = []
        request_lower = request.lower()
        
        # Code-related capabilities
        if any(keyword in request_lower for keyword in ['code', 'program', 'function', 'class', 'method']):
            capabilities.append('code_generation')
        
        if any(keyword in request_lower for keyword in ['debug', 'error', 'fix', 'bug']):
            capabilities.append('debugging')
        
        if any(keyword in request_lower for keyword in ['test', 'testing', 'unit test']):
            capabilities.append('testing')
        
        if any(keyword in request_lower for keyword in ['document', 'doc', 'readme', 'comment']):
            capabilities.append('documentation')
        
        # File operations
        if any(keyword in request_lower for keyword in ['file', 'read', 'write', 'create', 'edit']):
            capabilities.append('file_operations')
        
        # Web operations
        if any(keyword in request_lower for keyword in ['search', 'web', 'url', 'fetch']):
            capabilities.append('web_search')
        
        # Task management
        if any(keyword in request_lower for keyword in ['task', 'todo', 'plan', 'organize']):
            capabilities.append('task_management')
        
        # Configuration
        if any(keyword in request_lower for keyword in ['config', 'setup', 'configure', 'settings']):
            capabilities.append('configuration')
        
        # If no specific capabilities detected, use general purpose
        if not capabilities:
            capabilities.append('general_purpose')
        
        return capabilities
    
    def get_available_capabilities(self) -> List[str]:
        """Get all available capabilities across all agents"""
        return list(self.agent_registry.capability_index.keys())
    
    def get_agents_for_capability(self, capability: str) -> List[BaseAgent]:
        """Get all agents that have a specific capability"""
        return self.agent_registry.get_agents_by_capability(capability)
