#!/usr/bin/env python3
"""
Main entry point for Claude-Code-Python
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_code.cli import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())