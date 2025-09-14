"""
Exit tool for terminating agent execution loops
"""

from typing import Dict, Any, Optional
from .base_tool import BaseTool


class ExitTool(BaseTool):
    """Tool for terminating agent execution loops"""
    
    def __init__(self):
        super().__init__(
            name="Exit",
            description="Terminate the current execution loop. Use this when you have completed the task or encountered an error that cannot be resolved.",
            input_schema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["success", "failed"],
                        "description": "The status of the task completion - 'success' if completed successfully, 'failed' if encountered an error"
                    },
                    "message": {
                        "type": "string",
                        "description": "Optional message explaining the completion status or any issues encountered"
                    }
                },
                "required": ["status"],
                "additionalProperties": False
            }
        )
    
    async def execute(self, status: str, message: str = "") -> Dict[str, Any]:
        """Execute the exit action"""
        if not self.validate_input(status=status, message=message):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        if status not in ["success", "failed"]:
            return {
                "error": "Status must be 'success' or 'failed'",
                "result": None
            }
        
        try:
            result_message = f"Execution terminated with status: {status}"
            if message:
                result_message += f" - {message}"
            
            return {
                "error": None,
                "result": result_message,
                "status": status,
                "message": message,
                "terminated": True
            }
            
        except Exception as e:
            return {
                "error": f"Error executing exit: {str(e)}",
                "result": None
            }
