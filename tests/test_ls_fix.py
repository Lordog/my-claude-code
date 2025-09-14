#!/usr/bin/env python3
"""
Test script to verify LS tool fix
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_code.core.tool_executor import ToolExecutor
from claude_code.core.output_parser import ToolAction

async def test_ls_tool():
    """Test LS tool with the fixed parameter passing"""
    print("🧪 Testing LS tool with fixed parameter passing...")
    
    # Create tool executor
    executor = ToolExecutor()
    
    # Create a test tool action for LS
    tool_action = ToolAction(
        tool_name="LS",
        parameters={"path": "/tmp"},  # Use /tmp as a safe test directory
        action_id="test_1"
    )
    
    # Execute the tool
    result = await executor._execute_single_tool(tool_action, None)
    
    print(f"Tool name: {result.tool_name}")
    print(f"Success: {result.success}")
    if result.success:
        print(f"Result: {result.result}")
    else:
        print(f"Error: {result.error}")
    
    return result.success

if __name__ == "__main__":
    success = asyncio.run(test_ls_tool())
    if success:
        print("✅ LS tool fix successful!")
        sys.exit(0)
    else:
        print("❌ LS tool fix failed!")
        sys.exit(1)
