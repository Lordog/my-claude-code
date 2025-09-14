"""
Agent registry for managing all available agents
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.capabilities = []
        self.description = ""
    
    @abstractmethod
    async def execute(self, request: str, context: Dict[str, Any]) -> str:
        """Execute the agent's task"""
        pass
    
    def can_handle(self, request: str, context: Dict[str, Any]) -> bool:
        """Check if this agent can handle the given request"""
        return True  # Override in subclasses for specific logic
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.capabilities
    
    def get_description(self) -> str:
        """Get agent description"""
        return self.description


class AgentRegistry:
    """Registry for managing all available agents"""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._capabilities_index: Dict[str, List[str]] = {}
    
    def register(self, name: str, agent: BaseAgent) -> None:
        """Register an agent"""
        agent.name = name
        self._agents[name] = agent
        
        # Index capabilities
        for capability in agent.get_capabilities():
            if capability not in self._capabilities_index:
                self._capabilities_index[capability] = []
            self._capabilities_index[capability].append(name)
    
    def unregister(self, name: str) -> None:
        """Unregister an agent"""
        if name in self._agents:
            agent = self._agents[name]
            # Remove from capabilities index
            for capability in agent.get_capabilities():
                if capability in self._capabilities_index:
                    if name in self._capabilities_index[capability]:
                        self._capabilities_index[capability].remove(name)
            del self._agents[name]
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self._agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agent names"""
        return list(self._agents.keys())
    
    def get_agents_by_capability(self, capability: str) -> List[str]:
        """Get agents that have a specific capability"""
        return self._capabilities_index.get(capability, [])
    
    def find_best_agent(self, request: str, context: Dict[str, Any]) -> Optional[str]:
        """Find the best agent for a given request"""
        # Simple implementation - can be enhanced with ML-based selection
        for name, agent in self._agents.items():
            if agent.can_handle(request, context):
                return name
        return None
    
    def get_agent_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an agent"""
        agent = self.get_agent(name)
        if not agent:
            return None
        
        return {
            "name": agent.name,
            "description": agent.get_description(),
            "capabilities": agent.get_capabilities()
        }
    
    def list_all_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all agents"""
        return {
            name: self.get_agent_info(name)
            for name in self.list_agents()
        }
