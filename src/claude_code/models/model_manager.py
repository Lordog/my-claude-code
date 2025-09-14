"""
Model manager for handling different AI model providers
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import asyncio


class BaseModelProvider(ABC):
    """Base class for model providers"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_available = False
    
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> str:
        """Generate a response from the model with optional tool calling"""
        pass
    
    @abstractmethod
    async def check_availability(self) -> bool:
        """Check if the model provider is available"""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """Shutdown the model provider"""
        pass


class ModelManager:
    """Manages different model providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseModelProvider] = {}
        self.default_provider = None
        self.fallback_providers: List[str] = []
    
    def register_provider(self, provider: BaseModelProvider, is_default: bool = False) -> None:
        """Register a model provider"""
        self.providers[provider.name] = provider
        if is_default:
            self.default_provider = provider.name
    
    def set_fallback_providers(self, provider_names: List[str]) -> None:
        """Set fallback providers in order of preference"""
        self.fallback_providers = provider_names
    
    async def initialize_providers(self) -> None:
        """Initialize all registered providers"""
        for name, provider in self.providers.items():
            try:
                provider.is_available = await provider.check_availability()
            except Exception as e:
                provider.is_available = False
                # Don't print error for mock provider as it's expected to work
                if name != "mock":
                    print(f"⚠️  Provider {name} initialization failed: {e}")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        provider_name: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> str:
        """Generate response using specified or default provider"""
        # Try specified provider first
        if provider_name and provider_name in self.providers:
            provider = self.providers[provider_name]
            if provider.is_available:
                try:
                    return await provider.generate_response(messages, tools=tools, **kwargs)
                except Exception as e:
                    print(f"Error with provider {provider_name}: {e}")
        
        # Try default provider
        if self.default_provider and self.default_provider in self.providers:
            provider = self.providers[self.default_provider]
            if provider.is_available:
                try:
                    return await provider.generate_response(messages, tools=tools, **kwargs)
                except Exception as e:
                    print(f"Error with default provider {self.default_provider}: {e}")
        
        # Try fallback providers
        for fallback_name in self.fallback_providers:
            if fallback_name in self.providers:
                provider = self.providers[fallback_name]
                if provider.is_available:
                    try:
                        return await provider.generate_response(messages, tools=tools, **kwargs)
                    except Exception as e:
                        print(f"Error with fallback provider {fallback_name}: {e}")
        
        available_providers = self.get_available_providers()
        if not available_providers:
            raise Exception("No available model providers. Please check your API keys or configuration.")
        else:
            raise Exception(f"No available model providers. Registered providers: {list(self.providers.keys())}, Available: {available_providers}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [
            name for name, provider in self.providers.items() 
            if provider.is_available
        ]
    
    def get_provider_info(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a provider"""
        provider = self.providers.get(provider_name)
        if not provider:
            return None
        
        return {
            "name": provider.name,
            "available": provider.is_available,
            "type": type(provider).__name__
        }
    
    async def shutdown(self) -> None:
        """Shutdown all providers"""
        for provider in self.providers.values():
            await provider.shutdown()
