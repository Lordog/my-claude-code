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
            description="A powerful search tool built on ripgrep\n\n  Usage:\n  - ALWAYS use Grep for search tasks. NEVER invoke `grep` or `rg` as a Bash command. The Grep tool has been optimized for correct permissions and access.\n  - Supports full regex syntax (e.g., \"log.*Error\", \"function\\s+\\w+\")\n  - Filter files with glob parameter (e.g., \"*.js\", \"**/*.tsx\") or type parameter (e.g., \"js\", \"py\", \"rust\")\n  - Output modes: \"content\" shows matching lines, \"files_with_matches\" shows file paths (default), \"count\" shows match counts\n  - Use Task tool for open-ended searches requiring multiple rounds\n  - Pattern syntax: Uses ripgrep (not grep) - literal braces need escaping (use `interface\\{\\}` to find `interface{}` in Go code)\n  - Multiline matching: By default patterns match within single lines only. For cross-line patterns like `struct \\{[\\s\\S]*?field`, use `multiline: true`\n",
            input_schema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The regular expression pattern to search for in file contents"
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory to search in (rg PATH). Defaults to current working directory."
                    },
                    "glob": {
                        "type": "string",
                        "description": "Glob pattern to filter files (e.g. \"*.js\", \"*.{ts,tsx}\") - maps to rg --glob"
                    },
                    "output_mode": {
                        "type": "string",
                        "enum": [
                            "content",
                            "files_with_matches",
                            "count"
                        ],
                        "description": "Output mode: \"content\" shows matching lines (supports -A/-B/-C context, -n line numbers, head_limit), \"files_with_matches\" shows file paths (supports head_limit), \"count\" shows match counts (supports head_limit). Defaults to \"files_with_matches\"."
                    },
                    "-B": {
                        "type": "number",
                        "description": "Number of lines to show before each match (rg -B). Requires output_mode: \"content\", ignored otherwise."
                    },
                    "-A": {
                        "type": "number",
                        "description": "Number of lines to show after each match (rg -A). Requires output_mode: \"content\", ignored otherwise."
                    },
                    "-C": {
                        "type": "number",
                        "description": "Number of lines to show before and after each match (rg -C). Requires output_mode: \"content\", ignored otherwise."
                    },
                    "-n": {
                        "type": "boolean",
                        "description": "Show line numbers in output (rg -n). Requires output_mode: \"content\", ignored otherwise."
                    },
                    "-i": {
                        "type": "boolean",
                        "description": "Case insensitive search (rg -i)"
                    },
                    "type": {
                        "type": "string",
                        "description": "File type to search (rg --type). Common types: js, py, rust, go, java, etc. More efficient than include for standard file types."
                    },
                    "head_limit": {
                        "type": "number",
                        "description": "Limit output to first N lines/entries, equivalent to \"| head -N\". Works across all output modes: content (limits output lines), files_with_matches (limits file paths), count (limits count entries). When unspecified, shows all results from ripgrep."
                    },
                    "multiline": {
                        "type": "boolean",
                        "description": "Enable multiline mode where . matches newlines and patterns can span lines (rg -U --multiline-dotall). Default: false."
                    }
                },
                "required": [
                    "pattern"
                ],
                "additionalProperties": False,
                "$schema": "http://json-schema.org/draft-07/schema#"
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
