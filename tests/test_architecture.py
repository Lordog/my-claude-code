#!/usr/bin/env python3
"""
Test script to verify the architecture works
"""

import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from claude_code import ClaudeCodeController, ClaudeCodeConfig
        print("✅ Core imports successful")
        
        from claude_code.core import AgentRegistry, ContextManager, TaskRouter
        print("✅ Core modules imported")
        
        from claude_code.models import ModelManager, OpenRouterProvider, OpenAIProvider
        print("✅ Model modules imported")
        
        from claude_code.agents import MainAgent, CodeAgent, ToolAgent, DebugAgent, TestAgent, DocAgent
        print("✅ Agent modules imported")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_agent_registry():
    """Test agent registry functionality"""
    print("\n🧪 Testing agent registry...")
    
    try:
        from claude_code.core.agent_registry import AgentRegistry
        from claude_code.agents.main_agent import MainAgent
        
        registry = AgentRegistry()
        agent = MainAgent()
        registry.register("test_agent", agent)
        
        assert registry.get_agent("test_agent") is not None
        assert "test_agent" in registry.list_agents()
        print("✅ Agent registry working")
        return True
    except Exception as e:
        print(f"❌ Agent registry error: {e}")
        return False

def test_context_manager():
    """Test context manager functionality"""
    print("\n🧪 Testing context manager...")
    
    try:
        from claude_code.core.context_manager import ContextManager
        
        manager = ContextManager()
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi there!")
        
        messages = manager.get_messages()
        assert len(messages) == 2
        assert messages[0].content == "Hello"
        assert messages[1].content == "Hi there!"
        
        print("✅ Context manager working")
        return True
    except Exception as e:
        print(f"❌ Context manager error: {e}")
        return False

def test_task_router():
    """Test task router functionality"""
    print("\n🧪 Testing task router...")
    
    try:
        from claude_code.core.task_router import TaskRouter
        from claude_code.core.agent_registry import AgentRegistry
        from claude_code.agents.main_agent import MainAgent
        from claude_code.agents.code_agent import CodeAgent
        
        registry = AgentRegistry()
        registry.register("main", MainAgent())
        registry.register("code", CodeAgent())
        
        router = TaskRouter(registry)
        
        # Test task analysis
        task_type = router._analyze_task_type("Write a Python function")
        assert task_type == "code_generation"
        
        print("✅ Task router working")
        return True
    except Exception as e:
        print(f"❌ Task router error: {e}")
        return False

async def test_controller():
    """Test controller functionality"""
    print("\n🧪 Testing controller...")
    
    try:
        from claude_code import ClaudeCodeController, ClaudeCodeConfig
        
        config = ClaudeCodeConfig(debug_mode=True)
        controller = ClaudeCodeController(config)
        
        # Test agent registration
        agents = controller.get_available_agents()
        assert len(agents) > 0
        assert "main" in agents
        
        print("✅ Controller working")
        return True
    except Exception as e:
        print(f"❌ Controller error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Claude-Code-Python Architecture Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_agent_registry,
        test_context_manager,
        test_task_router,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    # Test controller asynchronously
    try:
        if asyncio.run(test_controller()):
            passed += 1
        total += 1
    except Exception as e:
        print(f"❌ Controller test error: {e}")
        total += 1
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Architecture is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
