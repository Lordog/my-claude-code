"""
TodoWrite tool for managing task lists
"""

from typing import Dict, Any, List, Optional
from .base_tool import BaseTool


class TodoWriteTool(BaseTool):
    """Tool for creating and managing task lists"""
    
    def __init__(self):
        super().__init__(
            name="TodoWrite",
            description="Use this tool to create and manage a structured task list for your current coding session.",
            input_schema={
                "type": "object",
                "properties": {
                    "todos": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "minLength": 1
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed"]
                                },
                                "id": {
                                    "type": "string"
                                }
                            },
                            "required": ["content", "status", "id"],
                            "additionalProperties": False
                        },
                        "description": "The updated todo list"
                    }
                },
                "required": ["todos"],
                "additionalProperties": False
            }
        )
        self.todos = {}
    
    async def execute(self, todos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute todo list management"""
        if not self.validate_input(todos=todos):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        try:
            # Update todos
            updated_count = 0
            for todo in todos:
                todo_id = todo.get("id")
                if todo_id:
                    self.todos[todo_id] = {
                        "content": todo["content"],
                        "status": todo["status"],
                        "id": todo_id
                    }
                    updated_count += 1
            
            # Get current status
            pending = [t for t in self.todos.values() if t["status"] == "pending"]
            in_progress = [t for t in self.todos.values() if t["status"] == "in_progress"]
            completed = [t for t in self.todos.values() if t["status"] == "completed"]
            
            status_summary = f"Updated {updated_count} todos. Status: {len(pending)} pending, {len(in_progress)} in progress, {len(completed)} completed"
            
            return {
                "error": None,
                "result": status_summary,
                "todos": list(self.todos.values()),
                "counts": {
                    "pending": len(pending),
                    "in_progress": len(in_progress),
                    "completed": len(completed),
                    "total": len(self.todos)
                }
            }
            
        except Exception as e:
            return {
                "error": f"Error managing todos: {str(e)}",
                "result": None
            }
    
    def get_todos(self) -> List[Dict[str, Any]]:
        """Get current todos"""
        return list(self.todos.values())
    
    def clear_todos(self):
        """Clear all todos"""
        self.todos.clear()
