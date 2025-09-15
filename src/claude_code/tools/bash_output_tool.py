"""
BashOutput tool for retrieving output from background bash sessions
"""

import re
from typing import Dict, Any, Optional
from .base_tool import BaseTool


class BashOutputTool(BaseTool):
    """Tool for retrieving output from background bash sessions"""
    
    def __init__(self):
        super().__init__(
            name="BashOutput",
            description="\n- Retrieves output from a running or completed background bash shell\n- Takes a shell_id parameter identifying the shell\n- Always returns only new output since the last check\n- Returns stdout and stderr output along with shell status\n- Supports optional regex filtering to show only lines matching a pattern\n- Use this tool when you need to monitor or check the output of a long-running shell\n- Shell IDs can be found using the /bashes command\n",
            input_schema={
                "type": "object",
                "properties": {
                    "bash_id": {
                        "type": "string",
                        "description": "The ID of the background shell to retrieve output from"
                    },
                    "filter": {
                        "type": "string",
                        "description": "Optional regular expression to filter the output lines. Only lines matching this regex will be included in the result. Any lines that do not match will no longer be available to read."
                    }
                },
                "required": [
                    "bash_id"
                ],
                "additionalProperties": False,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        )
        self.shell_outputs = {}  # Store output history for each shell
    
    async def execute(self, bash_id: str, filter: Optional[str] = None) -> Dict[str, Any]:
        """Execute bash output retrieval"""
        if not self.validate_input(bash_id=bash_id):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        try:
            # This is a mock implementation - in a real system, this would
            # connect to the actual background shell session
            if bash_id not in self.shell_outputs:
                return {
                    "error": f"Shell with ID '{bash_id}' not found",
                    "result": None
                }
            
            # Get the shell output
            shell_info = self.shell_outputs[bash_id]
            output = shell_info.get("output", "")
            
            # Apply filter if specified
            if filter:
                try:
                    pattern = re.compile(filter)
                    lines = output.split('\n')
                    filtered_lines = [line for line in lines if pattern.search(line)]
                    output = '\n'.join(filtered_lines)
                except re.error as e:
                    return {
                        "error": f"Invalid regex pattern: {str(e)}",
                        "result": None
                    }
            
            # Check if shell is still running
            is_running = shell_info.get("running", False)
            
            return {
                "error": None,
                "result": output,
                "bash_id": bash_id,
                "running": is_running,
                "return_code": shell_info.get("return_code"),
                "filtered": filter is not None
            }
            
        except Exception as e:
            return {
                "error": f"Error retrieving bash output: {str(e)}",
                "result": None
            }
    
    def register_shell(self, bash_id: str, output: str = "", running: bool = True, return_code: Optional[int] = None):
        """Register a shell session for output tracking"""
        self.shell_outputs[bash_id] = {
            "output": output,
            "running": running,
            "return_code": return_code
        }
    
    def update_shell_output(self, bash_id: str, new_output: str):
        """Update the output for a shell session"""
        if bash_id in self.shell_outputs:
            self.shell_outputs[bash_id]["output"] += new_output

