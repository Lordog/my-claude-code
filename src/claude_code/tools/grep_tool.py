"""
Grep tool for searching file contents
"""

import subprocess
import os
from typing import Dict, Any, Optional, List
from .base_tool import BaseTool


class GrepTool(BaseTool):
    """Tool for searching file contents using ripgrep"""
    
    def __init__(self):
        super().__init__(
            name="Grep",
            description="A powerful search tool built on ripgrep. Supports full regex syntax, file filtering, and multiple output modes.",
            input_schema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The regular expression pattern to search for in file contents"
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory to search in. Defaults to current working directory."
                    },
                    "glob": {
                        "type": "string",
                        "description": "Glob pattern to filter files (e.g. '*.js', '*.{ts,tsx}')"
                    },
                    "output_mode": {
                        "type": "string",
                        "enum": ["content", "files_with_matches", "count"],
                        "description": "Output mode: 'content' shows matching lines, 'files_with_matches' shows file paths, 'count' shows match counts. Defaults to 'files_with_matches'."
                    },
                    "-B": {
                        "type": "number",
                        "description": "Number of lines to show before each match"
                    },
                    "-A": {
                        "type": "number", 
                        "description": "Number of lines to show after each match"
                    },
                    "-C": {
                        "type": "number",
                        "description": "Number of lines to show before and after each match"
                    },
                    "-n": {
                        "type": "boolean",
                        "description": "Show line numbers in output"
                    },
                    "-i": {
                        "type": "boolean",
                        "description": "Case insensitive search"
                    },
                    "type": {
                        "type": "string",
                        "description": "File type to search (e.g. js, py, rust, go, java)"
                    },
                    "head_limit": {
                        "type": "number",
                        "description": "Limit output to first N lines/entries"
                    },
                    "multiline": {
                        "type": "boolean",
                        "description": "Enable multiline mode where . matches newlines"
                    }
                },
                "required": ["pattern"],
                "additionalProperties": False
            }
        )
    
    async def execute(self, pattern: str, path: Optional[str] = None, glob: Optional[str] = None,
                     output_mode: str = "files_with_matches", **kwargs) -> Dict[str, Any]:
        """Execute grep search"""
        if not self.validate_input(pattern=pattern):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        try:
            # Build ripgrep command
            cmd = ["rg"]
            
            # Add pattern
            cmd.append(pattern)
            
            # Add search path
            search_path = path or os.getcwd()
            cmd.append(search_path)
            
            # Add output mode
            if output_mode == "content":
                cmd.append("--no-heading")
                cmd.append("--with-filename")
            elif output_mode == "count":
                cmd.append("--count")
            
            # Add context lines
            if "-B" in kwargs and kwargs["-B"]:
                cmd.extend(["-B", str(kwargs["-B"])])
            if "-A" in kwargs and kwargs["-A"]:
                cmd.extend(["-A", str(kwargs["-A"])])
            if "-C" in kwargs and kwargs["-C"]:
                cmd.extend(["-C", str(kwargs["-C"])])
            
            # Add other options
            if kwargs.get("-n", False):
                cmd.append("-n")
            if kwargs.get("-i", False):
                cmd.append("-i")
            if kwargs.get("multiline", False):
                cmd.append("-U")
            
            # Add file type filter
            if "type" in kwargs and kwargs["type"]:
                cmd.extend(["-t", kwargs["type"]])
            
            # Add glob filter
            if glob:
                cmd.extend(["-g", glob])
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Apply head limit if specified
                if "head_limit" in kwargs and kwargs["head_limit"]:
                    lines = output.split('\n')
                    output = '\n'.join(lines[:kwargs["head_limit"]])
                
                return {
                    "error": None,
                    "result": output,
                    "pattern": pattern,
                    "search_path": search_path,
                    "output_mode": output_mode
                }
            else:
                # No matches found
                if result.returncode == 1:
                    return {
                        "error": None,
                        "result": "",
                        "pattern": pattern,
                        "search_path": search_path,
                        "output_mode": output_mode,
                        "message": "No matches found"
                    }
                else:
                    return {
                        "error": f"Ripgrep error: {result.stderr}",
                        "result": None
                    }
                    
        except FileNotFoundError:
            return {
                "error": "Ripgrep not found. Please install ripgrep (rg) to use the Grep tool.",
                "result": None
            }
        except Exception as e:
            return {
                "error": f"Error executing grep: {str(e)}",
                "result": None
            }
