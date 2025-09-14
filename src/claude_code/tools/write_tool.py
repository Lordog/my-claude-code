"""
Write tool for creating/writing files
"""

import os
from typing import Dict, Any
from .base_tool import BaseTool


class WriteTool(BaseTool):
    """Tool for writing files to the filesystem"""
    
    def __init__(self):
        super().__init__(
            name="Write",
            description="Writes a file to the local filesystem.",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The absolute path to the file to write (must be absolute, not relative)"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file"
                    }
                },
                "required": ["file_path", "content"],
                "additionalProperties": False
            }
        )
    
    async def execute(self, file_path: str, content: str) -> Dict[str, Any]:
        """Execute file writing"""
        if not self.validate_input(file_path=file_path, content=content):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        try:
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "error": None,
                "result": f"Successfully wrote {len(content)} characters to {file_path}",
                "file_path": file_path,
                "bytes_written": len(content.encode('utf-8'))
            }
            
        except PermissionError:
            return {
                "error": f"Permission denied: {file_path}",
                "result": None
            }
        except Exception as e:
            return {
                "error": f"Error writing file: {str(e)}",
                "result": None
            }
