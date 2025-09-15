"""
LS tool for listing directory contents
"""

import os
from typing import Dict, Any, Optional, List
from .base_tool import BaseTool


class LSTool(BaseTool):
    """Tool for listing files and directories"""
    
    def __init__(self):
        super().__init__(
            name="LS",
            description="Lists files and directories in a given path. The path parameter must be an absolute path, not a relative path. You can optionally provide an array of glob patterns to ignore with the ignore parameter. You should generally prefer the Glob and Grep tools, if you know which directories to search.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The absolute path to the directory to list (must be absolute, not relative)"
                    },
                    "ignore": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of glob patterns to ignore"
                    }
                },
                "required": [
                    "path"
                ],
                "additionalProperties": False,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        )
    
    async def execute(self, path: str, ignore: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute directory listing"""
        if not self.validate_input(path=path):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        try:
            # Check if path exists and is a directory
            if not os.path.exists(path):
                return {
                    "error": f"Path does not exist: {path}",
                    "result": None
                }
            
            if not os.path.isdir(path):
                return {
                    "error": f"Path is not a directory: {path}",
                    "result": None
                }
            
            # List directory contents
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                
                # Check if item should be ignored
                if ignore:
                    should_ignore = False
                    for pattern in ignore:
                        if self._matches_pattern(item, pattern):
                            should_ignore = True
                            break
                    if should_ignore:
                        continue
                
                # Get item info
                try:
                    stat = os.stat(item_path)
                    is_dir = os.path.isdir(item_path)
                    
                    items.append({
                        "name": item,
                        "path": item_path,
                        "is_directory": is_dir,
                        "size": stat.st_size if not is_dir else None,
                        "modified": stat.st_mtime
                    })
                except OSError:
                    # Skip items we can't access
                    continue
            
            # Sort items: directories first, then files, both alphabetically
            items.sort(key=lambda x: (not x["is_directory"], x["name"].lower()))
            
            return {
                "error": None,
                "result": items,
                "path": path,
                "count": len(items)
            }
            
        except Exception as e:
            return {
                "error": f"Error listing directory: {str(e)}",
                "result": None
            }
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches glob pattern"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
