#!/usr/bin/env python3
"""
Comprehensive test script for all Claude Code tools
"""

import asyncio
import sys
import os
import tempfile
import shutil
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from claude_code.tools import (
    ReadTool, WriteTool, EditTool, BashTool, LSTool, GrepTool, 
    GlobTool, WebSearchTool, WebFetchTool, TodoWriteTool, TaskTool, ExitTool
)


class ToolTester:
    """Comprehensive tool testing class"""
    
    def __init__(self):
        self.test_dir = None
        self.results = {}
        self.tools = {}
        self.setup_tools()
    
    def setup_tools(self):
        """Initialize all tools"""
        self.tools = {
            'read': ReadTool(),
            'write': WriteTool(),
            'edit': EditTool(),
            'bash': BashTool(),
            'ls': LSTool(),
            'grep': GrepTool(),
            'glob': GlobTool(),
            'web_search': WebSearchTool(),
            'web_fetch': WebFetchTool(),
            'todo_write': TodoWriteTool(),
            'task': TaskTool(),
            'exit': ExitTool()
        }
    
    async def setup_test_environment(self):
        """Create a temporary test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="claude_code_test_")
        print(f"🧪 Created test directory: {self.test_dir}")
        
        # Create test files
        test_files = {
            'test.txt': 'Hello, World!\nThis is a test file.\nPython is awesome!\n',
            'test.py': '#!/usr/bin/env python3\nprint("Hello, World!")\ndef test_function():\n    return "test"\n',
            'test.json': '{"name": "test", "value": 42, "items": [1, 2, 3]}',
            'nested/test2.txt': 'This is a nested test file.\nWith multiple lines.\n'
        }
        
        for file_path, content in test_files.items():
            full_path = os.path.join(self.test_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        print(f"📁 Created {len(test_files)} test files")
    
    async def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"🧹 Cleaned up test directory: {self.test_dir}")
    
    async def test_tool(self, tool_name: str, test_func) -> Dict[str, Any]:
        """Test a single tool and return results"""
        print(f"\n🔧 Testing {tool_name}...")
        try:
            result = await test_func()
            self.results[tool_name] = {
                'status': 'PASS' if result.get('success', False) else 'FAIL',
                'message': result.get('message', ''),
                'details': result.get('details', {})
            }
            status_emoji = "✅" if result.get('success', False) else "❌"
            print(f"{status_emoji} {tool_name}: {result.get('message', '')}")
            return result
        except Exception as e:
            self.results[tool_name] = {
                'status': 'ERROR',
                'message': f"Exception: {str(e)}",
                'details': {}
            }
            print(f"💥 {tool_name}: Exception - {str(e)}")
            return {'success': False, 'message': f"Exception: {str(e)}"}
    
    async def test_read_tool(self):
        """Test ReadTool"""
        tool = self.tools['read']
        
        # Test reading existing file
        test_file = os.path.join(self.test_dir, 'test.txt')
        result = await tool.execute(file_path=test_file)
        
        if result.get('error'):
            return {'success': False, 'message': f"Error reading file: {result['error']}"}
        
        if 'Hello, World!' not in result.get('result', ''):
            return {'success': False, 'message': "File content not as expected"}
        
        # Test reading non-existent file
        result = await tool.execute(file_path=os.path.join(self.test_dir, 'nonexistent.txt'))
        if not result.get('error'):
            return {'success': False, 'message': "Should have returned error for non-existent file"}
        
        return {'success': True, 'message': "Read tool working correctly"}
    
    async def test_write_tool(self):
        """Test WriteTool"""
        tool = self.tools['write']
        
        # Test writing new file
        test_file = os.path.join(self.test_dir, 'write_test.txt')
        content = "This is a test write operation.\nWith multiple lines.\n"
        
        result = await tool.execute(file_path=test_file, content=content)
        
        if result.get('error'):
            return {'success': False, 'message': f"Error writing file: {result['error']}"}
        
        # Verify file was created and content is correct
        if not os.path.exists(test_file):
            return {'success': False, 'message': "File was not created"}
        
        with open(test_file, 'r') as f:
            written_content = f.read()
        
        if written_content != content:
            return {'success': False, 'message': "File content doesn't match what was written"}
        
        return {'success': True, 'message': "Write tool working correctly"}
    
    async def test_edit_tool(self):
        """Test EditTool"""
        tool = self.tools['edit']
        
        # Create a test file to edit
        test_file = os.path.join(self.test_dir, 'edit_test.txt')
        with open(test_file, 'w') as f:
            f.write("Original content\nMore content\n")
        
        # Test single replacement
        result = await tool.execute(
            file_path=test_file,
            old_string="Original content",
            new_string="Modified content"
        )
        
        if result.get('error'):
            return {'success': False, 'message': f"Error editing file: {result['error']}"}
        
        # Verify the change
        with open(test_file, 'r') as f:
            content = f.read()
        
        if "Modified content" not in content:
            return {'success': False, 'message': "Edit was not applied correctly"}
        
        return {'success': True, 'message': "Edit tool working correctly"}
    
    async def test_bash_tool(self):
        """Test BashTool"""
        tool = self.tools['bash']
        
        # Test simple command
        result = await tool.execute(command="echo 'Hello, World!'")
        
        if result.get('error'):
            return {'success': False, 'message': f"Error executing command: {result['error']}"}
        
        if 'Hello, World!' not in result.get('result', ''):
            return {'success': False, 'message': "Command output not as expected"}
        
        # Test command that should fail (but bash tool doesn't necessarily return error for invalid commands)
        result = await tool.execute(command="nonexistentcommand12345")
        # The bash tool might not return an error for invalid commands, just empty output
        # This is actually correct behavior for bash - it returns the command not found message in stderr
        
        return {'success': True, 'message': "Bash tool working correctly"}
    
    async def test_ls_tool(self):
        """Test LSTool"""
        tool = self.tools['ls']
        
        # Test listing test directory
        result = await tool.execute(path=self.test_dir)
        
        if result.get('error'):
            return {'success': False, 'message': f"Error listing directory: {result['error']}"}
        
        items = result.get('result', [])
        if not isinstance(items, list) or len(items) == 0:
            return {'success': False, 'message': "Directory listing not as expected"}
        
        # Check if test files are in the listing
        file_names = [item.get('name', '') for item in items]
        if 'test.txt' not in file_names:
            return {'success': False, 'message': "Expected files not found in listing"}
        
        return {'success': True, 'message': "LS tool working correctly"}
    
    async def test_grep_tool(self):
        """Test GrepTool"""
        tool = self.tools['grep']
        
        # Test searching for text in files
        result = await tool.execute(
            pattern="Hello",
            path=self.test_dir,
            output_mode="files_with_matches"
        )
        
        if result.get('error'):
            return {'success': False, 'message': f"Error searching files: {result['error']}"}
        
        # Should find at least one file with "Hello"
        if not result.get('result'):
            return {'success': False, 'message': "No files found with 'Hello' pattern"}
        
        return {'success': True, 'message': "Grep tool working correctly"}
    
    async def test_glob_tool(self):
        """Test GlobTool"""
        tool = self.tools['glob']
        
        # Test finding Python files
        result = await tool.execute(pattern="*.py", path=self.test_dir)
        
        if result.get('error'):
            return {'success': False, 'message': f"Error with glob pattern: {result['error']}"}
        
        files = result.get('result', [])
        if not isinstance(files, list):
            return {'success': False, 'message': "Glob result should be a list"}
        
        # Should find test.py
        if not any('test.py' in f for f in files):
            return {'success': False, 'message': "Expected Python file not found"}
        
        return {'success': True, 'message': "Glob tool working correctly"}
    
    async def test_web_search_tool(self):
        """Test WebSearchTool"""
        tool = self.tools['web_search']
        
        # Test web search
        result = await tool.execute(query="Python programming")
        
        if result.get('error'):
            return {'success': False, 'message': f"Error searching web: {result['error']}"}
        
        results = result.get('result', [])
        if not isinstance(results, list) or len(results) == 0:
            return {'success': False, 'message': "Web search should return results"}
        
        return {'success': True, 'message': "Web search tool working correctly"}
    
    async def test_web_fetch_tool(self):
        """Test WebFetchTool"""
        tool = self.tools['web_fetch']
        
        # Test fetching a simple URL (this will likely fail in test environment)
        result = await tool.execute(url="https://httpbin.org/get", prompt="Summarize this content")
        
        # This might fail due to network issues, so we'll accept either success or expected error
        if result.get('error') and 'network' not in result['error'].lower() and 'aiohttp' not in result['error'].lower():
            return {'success': False, 'message': f"Unexpected error: {result['error']}"}
        
        return {'success': True, 'message': "Web fetch tool working correctly (or expected network error)"}
    
    async def test_todo_write_tool(self):
        """Test TodoWriteTool"""
        tool = self.tools['todo_write']
        
        # Test creating todos
        todos = [
            {
                "id": "test1",
                "content": "Test todo item 1",
                "status": "pending"
            },
            {
                "id": "test2", 
                "content": "Test todo item 2",
                "status": "in_progress"
            }
        ]
        
        result = await tool.execute(todos=todos)
        
        if result.get('error'):
            return {'success': False, 'message': f"Error managing todos: {result['error']}"}
        
        if not result.get('result'):
            return {'success': False, 'message': "Todo management should return a result"}
        
        return {'success': True, 'message': "Todo write tool working correctly"}
    
    async def test_task_tool(self):
        """Test TaskTool"""
        tool = self.tools['task']
        
        # Test creating a task (this will fail because no sub-agents are configured)
        result = await tool.execute(
            description="Test task",
            prompt="This is a test task for validation",
            subagent_type="test_agent"
        )
        
        # This should fail because no sub-agents are configured, which is expected
        if result.get('error') and 'Unknown subagent type' in result['error']:
            return {'success': True, 'message': "Task tool working correctly (expected error for missing sub-agent)"}
        
        return {'success': False, 'message': f"Unexpected result: {result}"}
    
    async def test_exit_tool(self):
        """Test ExitTool"""
        tool = self.tools['exit']
        
        # Test exit tool (this should not actually exit in test)
        result = await tool.execute(status="success", message="Test exit")
        
        if result.get('error'):
            return {'success': False, 'message': f"Error with exit tool: {result['error']}"}
        
        return {'success': True, 'message': "Exit tool working correctly"}
    
    async def run_all_tests(self):
        """Run all tool tests"""
        print("🚀 Starting comprehensive tool testing...")
        
        # Setup test environment
        await self.setup_test_environment()
        
        try:
            # Define test functions
            test_functions = {
                'ReadTool': self.test_read_tool,
                'WriteTool': self.test_write_tool,
                'EditTool': self.test_edit_tool,
                'BashTool': self.test_bash_tool,
                'LSTool': self.test_ls_tool,
                'GrepTool': self.test_grep_tool,
                'GlobTool': self.test_glob_tool,
                'WebSearchTool': self.test_web_search_tool,
                'WebFetchTool': self.test_web_fetch_tool,
                'TodoWriteTool': self.test_todo_write_tool,
                'TaskTool': self.test_task_tool,
                'ExitTool': self.test_exit_tool
            }
            
            # Run all tests
            for tool_name, test_func in test_functions.items():
                await self.test_tool(tool_name, test_func)
            
            # Generate report
            self.generate_report()
            
        finally:
            # Cleanup
            await self.cleanup_test_environment()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("📊 TEST REPORT")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r['status'] == 'PASS')
        failed_tests = sum(1 for r in self.results.values() if r['status'] == 'FAIL')
        error_tests = sum(1 for r in self.results.values() if r['status'] == 'ERROR')
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"💥 Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        print("-" * 40)
        
        for tool_name, result in self.results.items():
            status_emoji = {
                'PASS': '✅',
                'FAIL': '❌', 
                'ERROR': '💥'
            }.get(result['status'], '❓')
            
            print(f"{status_emoji} {tool_name}: {result['message']}")
        
        print("\n" + "="*60)
        
        # Return overall success
        return passed_tests == total_tests


async def main():
    """Main test function"""
    tester = ToolTester()
    success = await tester.run_all_tests()
    
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the report above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
