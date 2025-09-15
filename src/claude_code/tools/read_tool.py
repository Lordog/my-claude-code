"""
Read tool for reading files
"""

import os
from typing import Dict, Any, Optional
from .base_tool import BaseTool


class ReadTool(BaseTool):
    """Tool for reading files from the filesystem"""
    
    def __init__(self):
        super().__init__(
            name="Read",
            description="Reads a file from the local filesystem. You can access any file directly by using this tool.\nAssume this tool is able to read all files on the machine. If the User provides a path to a file assume that path is valid. It is okay to read a file that does not exist; an error will be returned.\n\nUsage:\n- The file_path parameter must be an absolute path, not a relative path\n- By default, it reads up to 2000 lines starting from the beginning of the file\n- You can optionally specify a line offset and limit (especially handy for long files), but it's recommended to read the whole file by not providing these parameters\n- Any lines longer than 2000 characters will be truncated\n- Results are returned using cat -n format, with line numbers starting at 1\n- This tool allows Claude Code to read images (eg PNG, JPG, etc). When reading an image file the contents are presented visually as Claude Code is a multimodal LLM.\n- This tool can read PDF files (.pdf). PDFs are processed page by page, extracting both text and visual content for analysis.\n- This tool can read Jupyter notebooks (.ipynb files) and returns all cells with their outputs, combining code, text, and visualizations.\n- You have the capability to call multiple tools in a single response. It is always better to speculatively read multiple files as a batch that are potentially useful. \n- You will regularly be asked to read screenshots. If the user provides a path to a screenshot ALWAYS use this tool to view the file at the path. This tool will work with all temporary file paths like /var/folders/123/abc/T/TemporaryItems/NSIRD_screencaptureui_ZfB1tD/Screenshot.png\n- If you read a file that exists but has empty contents you will receive a system reminder warning in place of file contents.",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The absolute path to the file to read"
                    },
                    "offset": {
                        "type": "number",
                        "description": "The line number to start reading from. Only provide if the file is too large to read at once"
                    },
                    "limit": {
                        "type": "number",
                        "description": "The number of lines to read. Only provide if the file is too large to read at once."
                    }
                },
                "required": [
                    "file_path"
                ],
                "additionalProperties": False,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        )
    
    async def execute(self, file_path: str, offset: Optional[int] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """Execute file reading"""
        if not self.validate_input(file_path=file_path):
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
            
            if not os.path.isfile(file_path):
                return {
                    "error": f"Path is not a file: {file_path}",
                    "result": None
                }
            
            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                if offset is not None and limit is not None:
                    # Read specific lines
                    lines = []
                    for i, line in enumerate(f):
                        if i >= offset - 1:  # Convert to 0-based index
                            lines.append(f"{i + 1}\t{line.rstrip()}")
                            if len(lines) >= limit:
                                break
                    content = '\n'.join(lines)
                else:
                    # Read entire file
                    lines = f.readlines()
                    # Add line numbers
                    numbered_lines = [f"{i + 1}\t{line.rstrip()}" for i, line in enumerate(lines)]
                    content = '\n'.join(numbered_lines)
            
            # Truncate very long lines
            lines = content.split('\n')
            truncated_lines = []
            for line in lines:
                if len(line) > 2000:
                    truncated_lines.append(line[:2000] + "... (line truncated)")
                else:
                    truncated_lines.append(line)
            content = '\n'.join(truncated_lines)
            
            return {
                "error": None,
                "result": content,
                "file_path": file_path,
                "lines_read": len(content.split('\n'))
            }
            
        except PermissionError:
            return {
                "error": f"Permission denied: {file_path}",
                "result": None
            }
        except Exception as e:
            return {
                "error": f"Error reading file: {str(e)}",
                "result": None
            }
