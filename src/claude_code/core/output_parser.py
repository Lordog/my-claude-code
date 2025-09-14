"""
Output Parser - Parses agent responses into content and tool actions
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ToolAction:
    """Represents a tool action to be executed"""
    tool_name: str
    parameters: Dict[str, Any]
    action_id: Optional[str] = None


@dataclass
class ParsedOutput:
    """Represents parsed agent output"""
    content: str
    tool_actions: List[ToolAction]
    has_tool_actions: bool = False


class OutputParser:
    """Parses agent responses to extract content and tool actions"""
    
    def __init__(self):
        # Pattern to match tool calls in various formats
        self.tool_patterns = [
            # Format: <tool_name>{"param1": "value1", "param2": "value2"}</tool_name>
            r'<(\w+)>({.*?})</\1>',
            # Format: [tool_name: {"param1": "value1", "param2": "value2"}]
            r'\[(\w+):\s*({.*?})\]',
            # Format: TOOL_CALL: tool_name {"param1": "value1"}
            r'TOOL_CALL:\s*(\w+)\s*({.*?})',
            # Format: <tool_call tool="tool_name" params='{"param1": "value1"}' />
            r'<tool_call\s+tool="(\w+)"\s+params=\'({.*?})\'\s*/>',
        ]
        
        # Pattern to match action IDs
        self.action_id_pattern = r'action_id["\']?\s*:\s*["\']?([^"\']+)["\']?'
    
    def parse(self, response: str) -> ParsedOutput:
        """
        Parse agent response into content and tool actions
        
        Args:
            response: Raw agent response string
            
        Returns:
            ParsedOutput containing content and tool actions
        """
        content = response
        tool_actions = []
        
        # Try each pattern to find tool calls
        for pattern in self.tool_patterns:
            matches = re.finditer(pattern, response, re.DOTALL)
            for match in matches:
                tool_name = match.group(1)
                params_str = match.group(2)
                
                try:
                    # Parse parameters JSON
                    parameters = json.loads(params_str)
                    
                    # Extract action ID if present
                    action_id = self._extract_action_id(parameters)
                    
                    # Create tool action
                    tool_action = ToolAction(
                        tool_name=tool_name,
                        parameters=parameters,
                        action_id=action_id
                    )
                    
                    tool_actions.append(tool_action)
                    
                    # Remove the tool call from content
                    content = content.replace(match.group(0), '').strip()
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract parameters as key-value pairs
                    parameters = self._parse_parameters_text(params_str)
                    if parameters:
                        tool_action = ToolAction(
                            tool_name=tool_name,
                            parameters=parameters
                        )
                        tool_actions.append(tool_action)
                        content = content.replace(match.group(0), '').strip()
        
        # Clean up content
        content = self._clean_content(content)
        
        return ParsedOutput(
            content=content,
            tool_actions=tool_actions,
            has_tool_actions=len(tool_actions) > 0
        )
    
    def _extract_action_id(self, parameters: Dict[str, Any]) -> Optional[str]:
        """Extract action ID from parameters"""
        if isinstance(parameters, dict):
            return parameters.get('action_id')
        return None
    
    def _parse_parameters_text(self, params_str: str) -> Dict[str, Any]:
        """Parse parameters from text format when JSON parsing fails"""
        parameters = {}
        
        # Try to extract key-value pairs
        # Format: key1="value1" key2="value2"
        kv_pattern = r'(\w+)=["\']([^"\']*)["\']'
        matches = re.findall(kv_pattern, params_str)
        
        for key, value in matches:
            # Try to convert to appropriate type
            if value.lower() in ['true', 'false']:
                parameters[key] = value.lower() == 'true'
            elif value.isdigit():
                parameters[key] = int(value)
            else:
                parameters[key] = value
        
        return parameters
    
    def _clean_content(self, content: str) -> str:
        """Clean up the content string"""
        # Remove extra whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()
        
        # Remove any remaining tool call artifacts
        content = re.sub(r'<[^>]*>', '', content)
        content = re.sub(r'\[[^\]]*\]', '', content)
        
        return content
    
    def format_tool_call(self, tool_name: str, parameters: Dict[str, Any], 
                        action_id: Optional[str] = None) -> str:
        """
        Format a tool call for the agent to use
        
        Args:
            tool_name: Name of the tool
            parameters: Parameters for the tool
            action_id: Optional action ID
            
        Returns:
            Formatted tool call string
        """
        if action_id:
            parameters['action_id'] = action_id
        
        params_json = json.dumps(parameters, indent=2)
        return f'<{tool_name}>{params_json}</{tool_name}>'
    
    def get_tool_usage_instructions(self) -> str:
        """Get instructions for agents on how to use tools"""
        return """
To use tools, format your tool calls in one of these ways:

1. <tool_name>{"param1": "value1", "param2": "value2"}</tool_name>
2. [tool_name: {"param1": "value1", "param2": "value2"}]
3. TOOL_CALL: tool_name {"param1": "value1", "param2": "value2"}

Examples:
- <Read>{"file_path": "/path/to/file.txt"}</Read>
- [Bash: {"command": "ls -la"}]
- TOOL_CALL: WebSearch {"query": "python best practices"}

You can include multiple tool calls in a single response. The content outside tool calls will be shown to the user.
"""
