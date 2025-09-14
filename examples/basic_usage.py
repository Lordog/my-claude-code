"""
Basic usage example for Claude-Code-Python
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from claude_code import ClaudeCodeController, ClaudeCodeConfig


async def main():
    """Basic usage example"""
    print("🚀 Claude-Code-Python Basic Usage Example")
    print("=" * 50)
    
    # Create configuration
    config = ClaudeCodeConfig(
        model_provider="kimi-k2",
        debug_mode=True
    )
    
    # Initialize controller
    controller = ClaudeCodeController(config)
    
    # Initialize model providers
    from claude_code.models.openrouter_provider import OpenRouterProvider
    # Register providers
    openrouter_provider = OpenRouterProvider()
    controller.model_manager.register_provider(openrouter_provider, is_default=True)
    
    controller.model_manager.set_fallback_providers(["openrouter"])
    
    # Initialize providers
    await controller.model_manager.initialize_providers()
    
    # Set model manager for all agents
    for agent_name in controller.get_available_agents():
        agent = controller.agent_registry.get_agent(agent_name)
        if agent:
            agent.set_model_manager(controller.model_manager)
    
    print(f"✅ Initialized with {len(controller.get_available_agents())} agents")
    print(f"✅ Available model providers: {controller.model_manager.get_available_providers()}")
    
    # Example requests
    requests = [
        "Hello! Can you help me understand what you can do?",
        "Write a simple Python function to calculate fibonacci numbers",
        "What are the best practices for writing clean code?",
        "Help me debug this error: 'NameError: name 'x' is not defined'"
    ]
    
    for i, request in enumerate(requests, 1):
        print(f"\n📝 Request {i}: {request}")
        print("-" * 40)
        
        try:
            response = await controller.process_request(request)
            
            if "error" in response:
                print(f"❌ Error: {response['error']}")
            else:
                print(f"🤖 Response: {response['response']}")
                if response.get('agents_used'):
                    print(f"🔧 Agents used: {', '.join(response['agents_used'])}")
        
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()
    
    # Cleanup
    await controller.shutdown()
    print("✅ Example completed!")


if __name__ == "__main__":
    asyncio.run(main())
