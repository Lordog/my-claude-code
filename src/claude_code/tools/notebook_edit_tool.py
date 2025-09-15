"""
NotebookEdit tool for editing Jupyter notebooks
"""

import json
import os
from typing import Dict, Any, Optional
from .base_tool import BaseTool


class NotebookEditTool(BaseTool):
    """Tool for editing Jupyter notebook cells"""
    
    def __init__(self):
        super().__init__(
            name="NotebookEdit",
            description="Completely replaces the contents of a specific cell in a Jupyter notebook (.ipynb file) with new source. Jupyter notebooks are interactive documents that combine code, text, and visualizations, commonly used for data analysis and scientific computing. The notebook_path parameter must be an absolute path, not a relative path. The cell_number is 0-indexed. Use edit_mode=insert to add a new cell at the index specified by cell_number. Use edit_mode=delete to delete the cell at the index specified by cell_number.",
            input_schema={
                "type": "object",
                "properties": {
                    "notebook_path": {
                        "type": "string",
                        "description": "The absolute path to the Jupyter notebook file to edit (must be absolute, not relative)"
                    },
                    "cell_id": {
                        "type": "string",
                        "description": "The ID of the cell to edit. When inserting a new cell, the new cell will be inserted after the cell with this ID, or at the beginning if not specified."
                    },
                    "new_source": {
                        "type": "string",
                        "description": "The new source for the cell"
                    },
                    "cell_type": {
                        "type": "string",
                        "enum": [
                            "code",
                            "markdown"
                        ],
                        "description": "The type of the cell (code or markdown). If not specified, it defaults to the current cell type. If using edit_mode=insert, this is required."
                    },
                    "edit_mode": {
                        "type": "string",
                        "enum": [
                            "replace",
                            "insert",
                            "delete"
                        ],
                        "description": "The type of edit to make (replace, insert, delete). Defaults to replace."
                    }
                },
                "required": [
                    "notebook_path",
                    "new_source"
                ],
                "additionalProperties": False,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        )
    
    async def execute(self, notebook_path: str, new_source: str, cell_id: Optional[str] = None, 
                     cell_type: Optional[str] = None, edit_mode: str = "replace") -> Dict[str, Any]:
        """Execute notebook editing"""
        if not self.validate_input(notebook_path=notebook_path, new_source=new_source):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        try:
            # Check if file exists
            if not os.path.exists(notebook_path):
                return {
                    "error": f"Notebook does not exist: {notebook_path}",
                    "result": None
                }
            
            # Read current notebook
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)
            
            if edit_mode == "insert":
                # Insert new cell
                if not cell_type:
                    return {
                        "error": "cell_type is required when edit_mode is 'insert'",
                        "result": None
                    }
                
                new_cell = {
                    "cell_type": cell_type,
                    "metadata": {},
                    "source": new_source.split('\n') if isinstance(new_source, str) else new_source
                }
                
                if cell_type == "code":
                    new_cell["execution_count"] = None
                    new_cell["outputs"] = []
                
                if cell_id:
                    # Find the cell with the specified ID and insert after it
                    for i, cell in enumerate(notebook["cells"]):
                        if cell.get("id") == cell_id:
                            notebook["cells"].insert(i + 1, new_cell)
                            break
                    else:
                        return {
                            "error": f"Cell with ID '{cell_id}' not found",
                            "result": None
                        }
                else:
                    # Insert at the beginning
                    notebook["cells"].insert(0, new_cell)
                
                result_message = f"Successfully inserted new {cell_type} cell"
                
            elif edit_mode == "delete":
                # Delete cell
                if not cell_id:
                    return {
                        "error": "cell_id is required when edit_mode is 'delete'",
                        "result": None
                    }
                
                cell_found = False
                for i, cell in enumerate(notebook["cells"]):
                    if cell.get("id") == cell_id:
                        del notebook["cells"][i]
                        cell_found = True
                        break
                
                if not cell_found:
                    return {
                        "error": f"Cell with ID '{cell_id}' not found",
                        "result": None
                    }
                
                result_message = f"Successfully deleted cell with ID '{cell_id}'"
                
            else:  # replace mode
                # Replace cell content
                if not cell_id:
                    return {
                        "error": "cell_id is required when edit_mode is 'replace'",
                        "result": None
                    }
                
                cell_found = False
                for cell in notebook["cells"]:
                    if cell.get("id") == cell_id:
                        cell["source"] = new_source.split('\n') if isinstance(new_source, str) else new_source
                        if cell_type:
                            cell["cell_type"] = cell_type
                        cell_found = True
                        break
                
                if not cell_found:
                    return {
                        "error": f"Cell with ID '{cell_id}' not found",
                        "result": None
                    }
                
                result_message = f"Successfully replaced content of cell with ID '{cell_id}'"
            
            # Write back to file
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=1, ensure_ascii=False)
            
            return {
                "error": None,
                "result": result_message,
                "notebook_path": notebook_path,
                "edit_mode": edit_mode,
                "cell_id": cell_id
            }
            
        except PermissionError:
            return {
                "error": f"Permission denied: {notebook_path}",
                "result": None
            }
        except json.JSONDecodeError as e:
            return {
                "error": f"Invalid JSON in notebook file: {str(e)}",
                "result": None
            }
        except Exception as e:
            return {
                "error": f"Error editing notebook: {str(e)}",
                "result": None
            }

