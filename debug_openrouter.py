#!/usr/bin/env python3
"""
Debug script to test OpenRouter provider availability
"""

import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_code.models.openrouter_provider import OpenRouterProvider

async def test_openrouter():
    """Test OpenRouter provider availability"""
    print("Testing OpenRouter provider...")
    
    # Test 1: Without API key
    print("\n1. Testing without API key:")
    provider1 = OpenRouterProvider()
    print(f"   API Key present: {provider1.api_key is not None}")
    print(f"   Client initialized: {provider1.client is not None}")
    availability1 = await provider1.check_availability()
    print(f"   Available: {availability1}")
    
    # Test 2: With empty API key
    print("\n2. Testing with empty API key:")
    provider2 = OpenRouterProvider(api_key="")
    print(f"   API Key present: {provider2.api_key is not None}")
    print(f"   Client initialized: {provider2.client is not None}")
    availability2 = await provider2.check_availability()
    print(f"   Available: {availability2}")
    
    # Test 3: With fake API key
    print("\n3. Testing with fake API key:")
    provider3 = OpenRouterProvider(api_key="fake-key-123")
    print(f"   API Key present: {provider3.api_key is not None}")
    print(f"   Client initialized: {provider3.client is not None}")
    try:
        availability3 = await provider3.check_availability()
        print(f"   Available: {availability3}")
    except Exception as e:
        print(f"   Error during availability check: {e}")
    
    print("\nEnvironment variables:")
    print(f"   OPENROUTER_API_KEY: {os.getenv('OPENROUTER_API_KEY', 'Not set')}")

if __name__ == "__main__":
    asyncio.run(test_openrouter())
