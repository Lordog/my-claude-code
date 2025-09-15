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
            description="Writes a file to the local filesystem.\n\nUsage:\n- This tool will overwrite the existing file if there is one at the provided path.\n- If this is an existing file, you MUST use the Read tool first to read the file's contents. This tool will fail if you did not read the file first.\n- ALWAYS prefer editing existing files in the codebase. NEVER write new files unless explicitly required.\n- NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.\n- Only use emojis if the user explicitly requests it. Avoid writing emojis to files unless asked.",
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
                "required": [
                    "file_path",
                    "content"
                ],
                "additionalProperties": False,
                "$schema": "http://json-schema.org/draft-07/schema#"
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
