"""
WebSearch tool for searching the web
"""

from typing import Dict, Any, Optional, List
from .base_tool import BaseTool


class WebSearchTool(BaseTool):
    """Tool for searching the web"""
    
    def __init__(self):
        super().__init__(
            name="WebSearch",
            description="\n- Allows Claude to search the web and use the results to inform responses\n- Provides up-to-date information for current events and recent data\n- Returns search result information formatted as search result blocks\n- Use this tool for accessing information beyond Claude's knowledge cutoff\n- Searches are performed automatically within a single API call\n\nUsage notes:\n  - Domain filtering is supported to include or block specific websites\n  - Web search is only available in the US\n  - Account for \"Today's date\" in <env>. For example, if <env> says \"Today's date: 2025-07-01\", and the user wants the latest docs, do not use 2024 in the search query. Use 2025.\n",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "minLength": 2,
                        "description": "The search query to use"
                    },
                    "allowed_domains": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Only include search results from these domains"
                    },
                    "blocked_domains": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Never include search results from these domains"
                    }
                },
                "required": [
                    "query"
                ],
                "additionalProperties": False,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        )
    
    async def execute(self, query: str, allowed_domains: Optional[List[str]] = None, 
                     blocked_domains: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute web search"""
        if not self.validate_input(query=query):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        try:
            # Mock search results - in a real implementation, this would use a search API
            mock_results = [
                {
                    "title": f"Search result 1 for: {query}",
                    "url": "https://example.com/result1",
                    "snippet": f"This is a mock search result for the query '{query}'. In a real implementation, this would contain actual search results from a search API."
                },
                {
                    "title": f"Search result 2 for: {query}",
                    "url": "https://example.com/result2", 
                    "snippet": f"Another mock search result for '{query}'. This demonstrates how the tool would work with real search results."
                }
            ]
            
            # Apply domain filtering if specified
            if allowed_domains:
                mock_results = [r for r in mock_results if any(domain in r["url"] for domain in allowed_domains)]
            
            if blocked_domains:
                mock_results = [r for r in mock_results if not any(domain in r["url"] for domain in blocked_domains)]
            
            return {
                "error": None,
                "result": mock_results,
                "query": query,
                "result_count": len(mock_results)
            }
            
        except Exception as e:
            return {
                "error": f"Error performing web search: {str(e)}",
                "result": None
            }
