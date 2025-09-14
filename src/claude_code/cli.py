"""
Command-line interface for Claude-Code-Python
"""

import asyncio
import argparse
import sys
from typing import Optional
from .core.claude_code_system import ClaudeCodeSystem, ClaudeCodeConfig


class ClaudeCodeCLI:
    """Command-line interface for Claude-Code-Python"""
    
    def __init__(self):
        self.system: Optional[ClaudeCodeSystem] = None
    
    async def initialize(self, config: Optional[ClaudeCodeConfig] = None):
        """Initialize the system"""
        self.system = ClaudeCodeSystem(config)
        await self.system.initialize()
    
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
                
                if user_input.lower() == 'tools':
                    self._show_tools()
                    continue
                
                if user_input.lower() == 'context':
                    self._show_context()
                    continue
                
                if user_input.lower() == 'clear':
                    self.system.clear_context()
                    print("Context cleared.")
                    continue
                
                # Process the request
                print("🤔 Thinking...")
                response = await self.system.process_request(user_input)
                
                if "error" in response:
                    print(f"❌ Error: {response['error']}")
                else:
                    print(f"\n🤖 Response:\n{response['response']}")
                
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
        print(f"Processing request: {request}")
        response = await self.system.process_request(request)
        
        if "error" in response:
            print(f"Error: {response['error']}")
            sys.exit(1)
        else:
            print(f"Response: {response['response']}")
    
    def _show_help(self):
        """Show help information"""
        print("""
Available commands:
  help     - Show this help message
  agents   - List available sub-agents
  tools    - List available tools
  context  - Show current context
  clear    - Clear current context
  quit     - Exit the program

You can also ask questions or give instructions directly!
        """)
    
    def _show_agents(self):
        """Show available sub-agents"""
        agents = self.system.get_available_sub_agents()
        print(f"\nAvailable sub-agents ({len(agents)}):")
        for agent_name in agents:
            print(f"  • {agent_name}")
    
    def _show_tools(self):
        """Show available tools"""
        tools = self.system.get_available_tools()
        print(f"\nAvailable tools ({len(tools)}):")
        for tool_name in tools:
            print(f"  • {tool_name}")
    
    def _show_context(self):
        """Show current context"""
        context = self.system.get_context()
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
    if cli.system:
        await cli.system.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
