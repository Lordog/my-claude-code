"""
Bash tool for executing shell commands
"""

import asyncio
import subprocess
import os
from typing import Dict, Any, Optional
from .base_tool import BaseTool


class BashTool(BaseTool):
    """Tool for executing bash commands"""
    
    def __init__(self):
        super().__init__(
            name="Bash",
            description="Executes a given bash command in a persistent shell session with optional timeout, ensuring proper handling and security measures.",
            input_schema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Optional timeout in milliseconds (max 600000)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Clear, concise description of what this command does in 5-10 words"
                    },
                    "run_in_background": {
                        "type": "boolean",
                        "description": "Set to true to run this command in the background"
                    }
                },
                "required": ["command"],
                "additionalProperties": False
            }
        )
        self.shell_sessions = {}
        self.next_session_id = 1
    
    async def execute(self, command: str, timeout: Optional[int] = None, 
                     description: Optional[str] = None, run_in_background: bool = False) -> Dict[str, Any]:
        """Execute a bash command"""
        if not self.validate_input(command=command):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        # Set default timeout
        if timeout is None:
            timeout = 120000  # 2 minutes default
        
        # Convert timeout to seconds
        timeout_seconds = min(timeout, 600000) / 1000  # Max 10 minutes
        
        try:
            if run_in_background:
                # Run in background
                session_id = str(self.next_session_id)
                self.next_session_id += 1
                
                # Start background process
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.getcwd()
                )
                
                self.shell_sessions[session_id] = {
                    "process": process,
                    "command": command,
                    "description": description or "Background command"
                }
                
                return {
                    "error": None,
                    "result": f"Command started in background with session ID: {session_id}",
                    "session_id": session_id,
                    "command": command
                }
            else:
                # Run synchronously
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    cwd=os.getcwd()
                )
                
                output = result.stdout
                if result.stderr:
                    output += f"\nSTDERR:\n{result.stderr}"
                
                # Truncate if too long
                if len(output) > 30000:
                    output = output[:30000] + "\n... (output truncated)"
                
                return {
                    "error": None,
                    "result": output,
                    "return_code": result.returncode,
                    "command": command
                }
                
        except subprocess.TimeoutExpired:
            return {
                "error": f"Command timed out after {timeout_seconds} seconds",
                "result": None
            }
        except Exception as e:
            return {
                "error": f"Error executing command: {str(e)}",
                "result": None
            }
    
    def get_background_sessions(self) -> Dict[str, Any]:
        """Get information about background sessions"""
        sessions = {}
        for session_id, session_info in self.shell_sessions.items():
            process = session_info["process"]
            sessions[session_id] = {
                "command": session_info["command"],
                "description": session_info["description"],
                "running": process.poll() is None,
                "return_code": process.returncode
            }
        return sessions
    
    def get_background_output(self, session_id: str) -> Dict[str, Any]:
        """Get output from a background session"""
        if session_id not in self.shell_sessions:
            return {
                "error": f"Session {session_id} not found",
                "result": None
            }
        
        session = self.shell_sessions[session_id]
        process = session["process"]
        
        if process.poll() is None:
            # Still running
            return {
                "error": None,
                "result": "Command is still running",
                "running": True
            }
        else:
            # Finished
            stdout, stderr = process.communicate()
            output = stdout
            if stderr:
                output += f"\nSTDERR:\n{stderr}"
            
            return {
                "error": None,
                "result": output,
                "running": False,
                "return_code": process.returncode
            }
