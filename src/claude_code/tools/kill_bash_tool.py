"""
KillBash tool for terminating background bash sessions
"""

from typing import Dict, Any
from .base_tool import BaseTool


class KillBashTool(BaseTool):
    """Tool for killing background bash sessions"""
    
    def __init__(self):
        super().__init__(
            name="KillBash",
            description="\n- Kills a running background bash shell by its ID\n- Takes a shell_id parameter identifying the shell to kill\n- Returns a success or failure status \n- Use this tool when you need to terminate a long-running shell\n- Shell IDs can be found using the /bashes command\n",
            input_schema={
                "type": "object",
                "properties": {
                    "shell_id": {
                        "type": "string",
                        "description": "The ID of the background shell to kill"
                    }
                },
                "required": [
                    "shell_id"
                ],
                "additionalProperties": False,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        )
        self.active_shells = set()  # Track active shell sessions
    
    async def execute(self, shell_id: str) -> Dict[str, Any]:
        """Execute bash session termination"""
        if not self.validate_input(shell_id=shell_id):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        try:
            # This is a mock implementation - in a real system, this would
            # actually terminate the background process
            if shell_id not in self.active_shells:
                return {
                    "error": f"Shell with ID '{shell_id}' not found or already terminated",
                    "result": None
                }
            
            # Remove from active shells
            self.active_shells.discard(shell_id)
            
            return {
                "error": None,
                "result": f"Successfully terminated shell with ID '{shell_id}'",
                "shell_id": shell_id,
                "terminated": True
            }
            
        except Exception as e:
            return {
                "error": f"Error killing bash session: {str(e)}",
                "result": None
            }
    
    def register_shell(self, shell_id: str):
        """Register a shell session as active"""
        self.active_shells.add(shell_id)
    
    def is_shell_active(self, shell_id: str) -> bool:
        """Check if a shell session is active"""
        return shell_id in self.active_shells

