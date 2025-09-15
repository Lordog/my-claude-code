"""
MultiEdit tool for making multiple edits to a single file
"""

import os
from typing import Dict, Any, List
from .base_tool import BaseTool


class MultiEditTool(BaseTool):
    """Tool for making multiple edits to a single file in one operation"""
    
    def __init__(self):
        super().__init__(
            name="MultiEdit",
            description="This is a tool for making multiple edits to a single file in one operation. It is built on top of the Edit tool and allows you to perform multiple find-and-replace operations efficiently. Prefer this tool over the Edit tool when you need to make multiple edits to the same file.\n\nBefore using this tool:\n\n1. Use the Read tool to understand the file's contents and context\n2. Verify the directory path is correct\n\nTo make multiple file edits, provide the following:\n1. file_path: The absolute path to the file to modify (must be absolute, not relative)\n2. edits: An array of edit operations to perform, where each edit contains:\n   - old_string: The text to replace (must match the file contents exactly, including all whitespace and indentation)\n   - new_string: The edited text to replace the old_string\n   - replace_all: Replace all occurences of old_string. This parameter is optional and defaults to false.\n\nIMPORTANT:\n- All edits are applied in sequence, in the order they are provided\n- Each edit operates on the result of the previous edit\n- All edits must be valid for the operation to succeed - if any edit fails, none will be applied\n- This tool is ideal when you need to make several changes to different parts of the same file\n- For Jupyter notebooks (.ipynb files), use the NotebookEdit instead\n\nCRITICAL REQUIREMENTS:\n1. All edits follow the same requirements as the single Edit tool\n2. The edits are atomic - either all succeed or none are applied\n3. Plan your edits carefully to avoid conflicts between sequential operations\n\nWARNING:\n- The tool will fail if edits.old_string doesn't match the file contents exactly (including whitespace)\n- The tool will fail if edits.old_string and edits.new_string are the same\n- Since edits are applied in sequence, ensure that earlier edits don't affect the text that later edits are trying to find\n\nWhen making edits:\n- Ensure all edits result in idiomatic, correct code\n- Do not leave the code in a broken state\n- Always use absolute file paths (starting with /)\n- Only use emojis if the user explicitly requests it. Avoid adding emojis to files unless asked.\n- Use replace_all for replacing and renaming strings across the file. This parameter is useful if you want to rename a variable for instance.\n\nIf you want to create a new file, use:\n- A new file path, including dir name if needed\n- First edit: empty old_string and the new file's contents as new_string\n- Subsequent edits: normal edit operations on the created content",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The absolute path to the file to modify"
                    },
                    "edits": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "old_string": {
                                    "type": "string",
                                    "description": "The text to replace"
                                },
                                "new_string": {
                                    "type": "string",
                                    "description": "The text to replace it with"
                                },
                                "replace_all": {
                                    "type": "boolean",
                                    "default": False,
                                    "description": "Replace all occurences of old_string (default false)."
                                }
                            },
                            "required": [
                                "old_string",
                                "new_string"
                            ],
                            "additionalProperties": False
                        },
                        "minItems": 1,
                        "description": "Array of edit operations to perform sequentially on the file"
                    }
                },
                "required": [
                    "file_path",
                    "edits"
                ],
                "additionalProperties": False,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        )
    
    async def execute(self, file_path: str, edits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple edits to a file"""
        if not self.validate_input(file_path=file_path, edits=edits):
            return {
                "error": "Invalid input parameters",
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
            
            # Apply edits sequentially
            total_replacements = 0
            for i, edit in enumerate(edits):
                old_string = edit["old_string"]
                new_string = edit["new_string"]
                replace_all = edit.get("replace_all", False)
                
                if old_string == new_string:
                    return {
                        "error": f"Edit {i+1}: old_string and new_string must be different",
                        "result": None
                    }
                
                if old_string not in content:
                    return {
                        "error": f"Edit {i+1}: old_string not found in file: {file_path}",
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
                
                content = new_content
                total_replacements += replacements_made
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "error": None,
                "result": f"Successfully made {total_replacements} replacement(s) across {len(edits)} edit(s) in {file_path}",
                "file_path": file_path,
                "edits_applied": len(edits),
                "total_replacements": total_replacements
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

