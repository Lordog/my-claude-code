"""
Command-line interface for Claude-Code-Python
"""

import asyncio
import argparse
import sys
from typing import Optional
from .core.controller import ClaudeCodeController, ClaudeCodeConfig


class ClaudeCodeCLI:
    """Command-line interface for Claude-Code-Python"""
    
    def __init__(self):
        self.controller: Optional[ClaudeCodeController] = None
    
    async def initialize(self, config: Optional[ClaudeCodeConfig] = None):
        """Initialize the controller"""
        self.controller = ClaudeCodeController(config)
        
        # Initialize model providers
        from .models.openrouter_provider import OpenRouterProvider
        from .models.mock_provider import MockProvider
        
        # Register OpenRouter as primary provider           
        openrouter_provider = OpenRouterProvider()
        self.controller.model_manager.register_provider(openrouter_provider, is_default=True)
        
        # Register Mock provider as final fallback
        mock_provider = MockProvider()
        self.controller.model_manager.register_provider(mock_provider)
        
        self.controller.model_manager.set_fallback_providers([openrouter_provider.name, mock_provider.name])
        
        # Initialize providers
        await self.controller.model_manager.initialize_providers()
        
        # Show provider status
        available_providers = self.controller.model_manager.get_available_providers()
        if config and config.debug_mode:
            print(f"🔧 Debug: Available providers: {available_providers}")
            for provider_name in self.controller.model_manager.providers.keys():
                provider_info = self.controller.model_manager.get_provider_info(provider_name)
                status = "✅ Available" if provider_info['available'] else "❌ Unavailable"
                print(f"  • {provider_name}: {status}")
        
        if not available_providers:
            print("⚠️  Warning: No model providers are available. Please check your API keys.")
            print("   Set OPENROUTER_API_KEY for OpenRouter provider.")
            print("   Using mock provider for testing...")
        
        # Set model manager for all agents
        for agent_name in self.controller.get_available_agents():
            agent = self.controller.agent_registry.get_agent(agent_name)
            if agent:
                agent.set_model_manager(self.controller.model_manager)
    
    async def run_interactive(self):
        """Run interactive mode"""
        print("🤖 Claude-Code-Python - Interactive Mode")
        print("Type 'help' for commands, 'quit' to exit")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'agents':
                    self._show_agents()
                    continue
                
                if user_input.lower() == 'context':
                    self._show_context()
                    continue
                
                if user_input.lower() == 'clear':
                    self.controller.clear_context()
                    print("Context cleared.")
                    continue
                
                # Process the request
                print("🤔 Thinking...")
                response = await self.controller.process_request(user_input)
                
                if "error" in response:
                    print(f"❌ Error: {response['error']}")
                else:
                    print(f"\n🤖 Response:\n{response['response']}")
                    
                    if response.get('agents_used'):
                        print(f"\n🔧 Agents used: {', '.join(response['agents_used'])}")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except EOFError:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                break
    
    async def run_single(self, request: str):
        """Run single request mode"""
        response = await self.controller.process_request(request)
        
        if "error" in response:
            print(f"Error: {response['error']}")
            sys.exit(1)
        else:
            print(response['response'])
    
    def _show_help(self):
        """Show help information"""
        print("""
Available commands:
  help     - Show this help message
  agents   - List available agents
  context  - Show current context
  clear    - Clear current context
  quit     - Exit the program

You can also ask questions or give instructions directly!
        """)
    
    def _show_agents(self):
        """Show available agents"""
        agents = self.controller.get_available_agents()
        print(f"\nAvailable agents ({len(agents)}):")
        for agent_name in agents:
            agent_info = self.controller.agent_registry.get_agent_info(agent_name)
            if agent_info:
                print(f"  • {agent_name}: {agent_info['description']}")
                print(f"    Capabilities: {', '.join(agent_info['capabilities'])}")
    
    def _show_context(self):
        """Show current context"""
        context = self.controller.get_context()
        print(f"\nCurrent context:")
        print(f"  Messages: {len(context.get('messages', []))}")
        if 'project' in context:
            project = context['project']
            print(f"  Project: {project.get('path', 'None')}")
            print(f"  Files: {len(project.get('files', {}))}")
        else:
            print("  Project: None")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Claude-Code-Python CLI")
    parser.add_argument("--request", "-r", help="Single request to process")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--model", default="moonshotai/kimi-k2-0905", help="Default model provider")
    
    args = parser.parse_args()
    
    # Create configuration
    config = ClaudeCodeConfig(
        model=args.model,
        debug_mode=args.debug
    )
    
    # Initialize CLI
    cli = ClaudeCodeCLI()
    await cli.initialize(config)
    
    if args.request:
        # Single request mode
        await cli.run_single(args.request)
    else:
        # Interactive mode
        await cli.run_interactive()
    
    # Cleanup
    if cli.controller:
        await cli.controller.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
