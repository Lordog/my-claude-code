#!/usr/bin/env python3
"""
Test script for the new Claude Code system
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_code.core.claude_code_system import ClaudeCodeSystem, ClaudeCodeConfig

async def test_system():
    """Test the new system"""
    print("🧪 Testing Claude Code System...")
    
    # Create system
    config = ClaudeCodeConfig(debug_mode=True)
    system = ClaudeCodeSystem(config)
    
    # Initialize
    print("🔧 Initializing system...")
    await system.initialize()
    
    # Test request
    print("📝 Testing request...")
    response = await system.process_request("Hello, can you help me?")
    
    print(f"📤 Response: {response}")
    
    # Cleanup
    await system.shutdown()
    print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_system())
