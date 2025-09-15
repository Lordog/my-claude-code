"""
Edit tool for modifying files
"""

import os
from typing import Dict, Any, Optional
from .base_tool import BaseTool


class EditTool(BaseTool):
    """Tool for editing files with exact string replacements"""
    
    def __init__(self):
        super().__init__(
            name="Edit",
            description="Performs exact string replacements in files. \n\nUsage:\n- You must use your `Read` tool at least once in the conversation before editing. This tool will error if you attempt an edit without reading the file. \n- When editing text from Read tool output, ensure you preserve the exact indentation (tabs/spaces) as it appears AFTER the line number prefix. The line number prefix format is: spaces + line number + tab. Everything after that tab is the actual file content to match. Never include any part of the line number prefix in the old_string or new_string.\n- ALWAYS prefer editing existing files in the codebase. NEVER write new files unless explicitly required.\n- Only use emojis if the user explicitly requests it. Avoid adding emojis to files unless asked.\n- The edit will FAIL if `old_string` is not unique in the file. Either provide a larger string with more surrounding context to make it unique or use `replace_all` to change every instance of `old_string`. \n- Use `replace_all` for replacing and renaming strings across the file. This parameter is useful if you want to rename a variable for instance.",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The absolute path to the file to modify"
                    },
                    "old_string": {
                        "type": "string",
                        "description": "The text to replace"
                    },
                    "new_string": {
                        "type": "string",
                        "description": "The text to replace it with (must be different from old_string)"
                    },
                    "replace_all": {
                        "type": "boolean",
                        "default": False,
                        "description": "Replace all occurences of old_string (default false)"
                    }
                },
                "required": [
                    "file_path",
                    "old_string",
                    "new_string"
                ],
                "additionalProperties": False,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        )
    
    async def execute(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> Dict[str, Any]:
        """Execute file editing"""
        if not self.validate_input(file_path=file_path, old_string=old_string, new_string=new_string):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        if old_string == new_string:
            return {
                "error": "old_string and new_string must be different",
                "result": None
            }
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "error": f"File does not exist: {file_path}",
                    "result": None
                }
            
            # Read current file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if old_string exists in content
            if old_string not in content:
                return {
                    "error": f"old_string not found in file: {file_path}",
                    "result": None
                }
            
            # Perform replacement
            if replace_all:
                new_content = content.replace(old_string, new_string)
                replacements_made = content.count(old_string)
            else:
                # Replace only first occurrence
                new_content = content.replace(old_string, new_string, 1)
                replacements_made = 1
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {
                "error": None,
                "result": f"Successfully made {replacements_made} replacement(s) in {file_path}",
                "file_path": file_path,
                "replacements_made": replacements_made
            }
            
        except PermissionError:
            return {
                "error": f"Permission denied: {file_path}",
                "result": None
            }
        except Exception as e:
            return {
                "error": f"Error editing file: {str(e)}",
                "result": None
            }
