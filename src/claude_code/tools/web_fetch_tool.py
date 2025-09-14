"""
WebFetch tool for fetching web content
"""

import asyncio
from typing import Dict, Any
from .base_tool import BaseTool

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


class WebFetchTool(BaseTool):
    """Tool for fetching content from URLs"""
    
    def __init__(self):
        super().__init__(
            name="WebFetch",
            description="Fetches content from a specified URL and processes it using an AI model.",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "format": "uri",
                        "description": "The URL to fetch content from"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "The prompt to run on the fetched content"
                    }
                },
                "required": ["url", "prompt"],
                "additionalProperties": False
            }
        )
    
    async def execute(self, url: str, prompt: str) -> Dict[str, Any]:
        """Execute web fetch"""
        if not self.validate_input(url=url, prompt=prompt):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        if not AIOHTTP_AVAILABLE:
            return {
                "error": "aiohttp is required for web fetching. Please install it with: pip install aiohttp",
                "result": None
            }
        
        try:
            # Upgrade HTTP to HTTPS
            if url.startswith('http://'):
                url = url.replace('http://', 'https://', 1)
            
            # Fetch content
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Simple processing - in a real implementation, this would use an AI model
                        # For now, just return a summary
                        summary = f"Fetched content from {url}:\n\n"
                        summary += f"Content length: {len(content)} characters\n"
                        summary += f"Prompt: {prompt}\n\n"
                        summary += f"First 500 characters:\n{content[:500]}..."
                        
                        return {
                            "error": None,
                            "result": summary,
                            "url": url,
                            "content_length": len(content)
                        }
                    else:
                        return {
                            "error": f"HTTP {response.status}: Failed to fetch {url}",
                            "result": None
                        }
                        
        except asyncio.TimeoutError:
            return {
                "error": f"Timeout fetching {url}",
                "result": None
            }
        except Exception as e:
            return {
                "error": f"Error fetching URL: {str(e)}",
                "result": None
            }
