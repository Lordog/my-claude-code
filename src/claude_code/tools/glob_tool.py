"""
Glob tool for file pattern matching
"""

import glob
import os
from typing import Dict, Any, Optional
from .base_tool import BaseTool


class GlobTool(BaseTool):
    """Tool for fast file pattern matching"""
    
    def __init__(self):
        super().__init__(
            name="Glob",
            description="Fast file pattern matching tool that works with any codebase size. Supports glob patterns like '**/*.js' or 'src/**/*.ts'. Returns matching file paths sorted by modification time.",
            input_schema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The glob pattern to match files against"
                    },
                    "path": {
                        "type": "string",
                        "description": "The directory to search in. If not specified, the current working directory will be used."
                    }
                },
                "required": ["pattern"],
                "additionalProperties": False
            }
        )
    
    async def execute(self, pattern: str, path: Optional[str] = None) -> Dict[str, Any]:
        """Execute glob pattern matching"""
        if not self.validate_input(pattern=pattern):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        try:
            # Set search directory
            search_dir = path or os.getcwd()
            
            # Ensure the pattern is relative to search directory
            if not os.path.isabs(pattern):
                full_pattern = os.path.join(search_dir, pattern)
            else:
                full_pattern = pattern
            
            # Find matching files
            matches = glob.glob(full_pattern, recursive=True)
            
            # Sort by modification time (newest first)
            matches_with_time = []
            for match in matches:
                try:
                    mtime = os.path.getmtime(match)
                    matches_with_time.append((match, mtime))
                except OSError:
                    # Skip files we can't access
                    continue
            
            # Sort by modification time (newest first)
            matches_with_time.sort(key=lambda x: x[1], reverse=True)
            sorted_matches = [match[0] for match in matches_with_time]
            
            return {
                "error": None,
                "result": sorted_matches,
                "pattern": pattern,
                "search_dir": search_dir,
                "count": len(sorted_matches)
            }
            
        except Exception as e:
            return {
                "error": f"Error executing glob pattern: {str(e)}",
                "result": None
            }
