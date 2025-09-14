"""
Task router for directing requests to appropriate agents
"""

from typing import Dict, Any, List, Optional
import re
from ..core.agent_registry import AgentRegistry, BaseAgent


class TaskRouter:
    """Routes tasks to appropriate agents based on content analysis"""
    
    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry
        self.routing_rules = self._bug_rild_routinules()
    
    def _build_routing_rules(self) -> Dict[str, Dict[str, Any]]:
        """Build routing rules for different types of tasks"""
        return {
            "code_generation": {
                "keywords": ["write", "create", "generate", "implement", "code", "function", "class"],
                "agents": ["code", "main"],
                "priority": 1
            },
            "code_analysis": {
                "keywords": ["analyze", "review", "explain", "understand", "debug", "trace"],
                "agents": ["code", "debug"],
                "priority": 1
            },
            "testing": {
                "keywords": ["test", "unit test", "integration test", "coverage", "pytest"],
                "agents": ["test", "code"],
                "priority": 1
            },
            "documentation": {
                "keywords": ["document", "docstring", "readme", "comment", "explain"],
                "agents": ["doc", "code"],
                "priority": 1
            },
            "debugging": {
                "keywords": ["error", "bug", "fix", "debug", "issue", "problem"],
                "agents": ["debug", "code"],
                "priority": 1
            },
            "tool_usage": {
                "keywords": ["run", "execute", "command", "tool", "script", "file"],
                "agents": ["tool", "main"],
                "priority": 1
            },
            "general": {
                "keywords": [],
                "agents": ["main"],
                "priority": 0
            }
        }
    
    async def route_task(self, request: str, context: Dict[str, Any]) -> Dict[str, BaseAgent]:
        """
        Route a task to appropriate agents
        
        Args:
            request: The user request
            context: Current context
            
        Returns:
            Dictionary of agent_name -> agent_instance
        """
        # Analyze the request to determine task type
        task_type = self._analyze_task_type(request)
        
        # Get recommended agents for this task type
        recommended_agents = self.routing_rules.get(task_type, {}).get("agents", ["main"])
        
        # Filter agents that are available and can handle the request
        selected_agents = {}
        for agent_name in recommended_agents:
            agent = self.agent_registry.get_agent(agent_name)
            if agent and agent.can_handle(request, context):
                selected_agents[agent_name] = agent
        
        # If no specific agents were selected, fall back to main agent
        if not selected_agents:
            main_agent = self.agent_registry.get_agent("main")
            if main_agent:
                selected_agents["main"] = main_agent
        
        return selected_agents
    
    def _analyze_task_type(self, request: str) -> str:
        """Analyze request to determine task type"""
        request_lower = request.lower()
        
        # Score each task type based on keyword matches
        scores = {}
        for task_type, rules in self.routing_rules.items():
            score = 0
            for keyword in rules["keywords"]:
                if keyword in request_lower:
                    score += 1
            scores[task_type] = score
        
        # Return the task type with highest score
        if scores:
            best_task = max(scores.items(), key=lambda x: x[1])
            if best_task[1] > 0:  # Only return if there's at least one keyword match
                return best_task[0]
        
        return "general"
    
    def get_routing_suggestions(self, request: str) -> List[Dict[str, Any]]:
        """Get routing suggestions for a request"""
        task_type = self._analyze_task_type(request)
        rules = self.routing_rules.get(task_type, {})
        
        suggestions = []
        for agent_name in rules.get("agents", []):
            agent = self.agent_registry.get_agent(agent_name)
            if agent:
                suggestions.append({
                    "agent": agent_name,
                    "description": agent.get_description(),
                    "capabilities": agent.get_capabilities(),
                    "confidence": self._calculate_confidence(request, agent_name)
                })
        
        return sorted(suggestions, key=lambda x: x["confidence"], reverse=True)
    
    def _calculate_confidence(self, request: str, agent_name: str) -> float:
        """Calculate confidence score for agent selection"""
        agent = self.agent_registry.get_agent(agent_name)
        if not agent:
            return 0.0
        
        # Simple confidence calculation based on keyword matching
        request_lower = request.lower()
        capabilities = agent.get_capabilities()
        
        matches = 0
        for capability in capabilities:
            if capability.lower() in request_lower:
                matches += 1
        
        return min(matches / len(capabilities) if capabilities else 0, 1.0)
    
    def add_routing_rule(self, task_type: str, keywords: List[str], agents: List[str], priority: int = 1) -> None:
        """Add a custom routing rule"""
        self.routing_rules[task_type] = {
            "keywords": keywords,
            "agents": agents,
            "priority": priority
        }
    
    def remove_routing_rule(self, task_type: str) -> None:
        """Remove a routing rule"""
        if task_type in self.routing_rules:
            del self.routing_rules[task_type]
