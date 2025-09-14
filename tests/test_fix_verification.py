#!/usr/bin/env python3
"""
Test script to verify the fixes for LS tool and tool result formatting
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_code.tools.ls_tool import LSTool
from claude_code.core.tool_executor import ToolExecutor, ToolResult, ExecutionResult

async def test_ls_tool_path_expansion():
    """Test that LS tool properly expands ~ paths"""
    print("Testing LS tool path expansion...")
    
    ls_tool = LSTool()
    
    # Test with ~ path (should expand to current user's home)
    result = await ls_tool.execute("~")
    print(f"Result for '~': {result}")
    
    # Test with ~/ytx-code path
    result = await ls_tool.execute("~/ytx-code")
    print(f"Result for '~/ytx-code': {result}")
    
    # Test with current directory
    result = await ls_tool.execute(".")
    print(f"Result for '.': {result}")

async def test_tool_result_formatting():
    """Test that tool result formatting works correctly"""
    print("\nTesting tool result formatting...")
    
    executor = ToolExecutor()
    
    # Create mock results
    results = [
        ToolResult(
            tool_name="LS",
            success=True,
            result={"error": None, "result": ["file1.txt", "file2.txt"], "count": 2}
        ),
        ToolResult(
            tool_name="LS", 
            success=True,
            result={"error": "Path does not exist: /nonexistent", "result": None}
        ),
        ToolResult(
            tool_name="Bash",
            success=True,
            result="Command executed successfully"
        )
    ]
    
    execution_result = ExecutionResult(
        results=results,
        success_count=3,
        error_count=0
    )
    
    formatted = executor.format_tool_results(execution_result)
    print("Formatted results:")
    print(formatted)

async def main():
    """Run all tests"""
    print("Running fix verification tests...\n")
    
    await test_ls_tool_path_expansion()
    await test_tool_result_formatting()
    
    print("\nTests completed!")

if __name__ == "__main__":
    asyncio.run(main())
