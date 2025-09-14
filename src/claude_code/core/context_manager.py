"""
Context Manager - Manages conversation history and project state
"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Message:
    """Represents a message in the conversation"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }
        if self.tool_calls:
            result['tool_calls'] = self.tool_calls
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create from dictionary"""
        return cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata'),
            tool_calls=data.get('tool_calls')
        )


@dataclass
class ProjectInfo:
    """Information about the current project"""
    path: str
    name: str
    files: Dict[str, Any]  # file_path -> file_info
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'path': self.path,
            'name': self.name,
            'files': self.files,
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectInfo':
        """Create from dictionary"""
        return cls(
            path=data['path'],
            name=data['name'],
            files=data['files'],
            last_updated=datetime.fromisoformat(data['last_updated'])
        )


class ContextManager:
    """Manages conversation history and project state"""
    
    def __init__(self, max_messages: int = 100, persist_context: bool = True):
        self.max_messages = max_messages
        self.persist_context = persist_context
        self.context_file = "claude_code_context.json"
        
        # Initialize context
        self.messages: List[Message] = []
        self.project: Optional[ProjectInfo] = None
        self.session_data: Dict[str, Any] = {}
        
        # Load existing context if persistence is enabled
        if self.persist_context:
            self._load_context()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None, tool_calls: Optional[List[Dict[str, Any]]] = None):
        """
        Add a message to the conversation history
        
        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata
            tool_calls: Optional tool calls for assistant messages
        """
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata,
            tool_calls=tool_calls
        )
        
        self.messages.append(message)
        
        # Trim messages if we exceed the limit
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        # Save context if persistence is enabled
        if self.persist_context:
            self._save_context()
    
    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """
        Get conversation messages
        
        Args:
            limit: Maximum number of messages to return (None for all)
            
        Returns:
            List of messages
        """
        if limit is None:
            return self.messages.copy()
        return self.messages[-limit:] if limit > 0 else []
    
    def get_messages_dict(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation messages as dictionaries
        
        Args:
            limit: Maximum number of messages to return (None for all)
            
        Returns:
            List of message dictionaries
        """
        messages = self.get_messages(limit)
        return [msg.to_dict() for msg in messages]
    
    def set_project(self, project_path: str, project_name: str = None):
        """
        Set the current project
        
        Args:
            project_path: Path to the project directory
            project_name: Optional project name (defaults to directory name)
        """
        if not os.path.exists(project_path):
            raise ValueError(f"Project path does not exist: {project_path}")
        
        if not os.path.isdir(project_path):
            raise ValueError(f"Project path is not a directory: {project_path}")
        
        if project_name is None:
            project_name = os.path.basename(os.path.abspath(project_path))
        
        # Scan project files
        files = self._scan_project_files(project_path)
        
        self.project = ProjectInfo(
            path=os.path.abspath(project_path),
            name=project_name,
            files=files,
            last_updated=datetime.now()
        )
        
        # Save context if persistence is enabled
        if self.persist_context:
            self._save_context()
    
    def get_project(self) -> Optional[ProjectInfo]:
        """Get current project information"""
        return self.project
    
    def update_project_files(self):
        """Update the project files information"""
        if self.project and os.path.exists(self.project.path):
            files = self._scan_project_files(self.project.path)
            self.project.files = files
            self.project.last_updated = datetime.now()
            
            if self.persist_context:
                self._save_context()
    
    def _scan_project_files(self, project_path: str) -> Dict[str, Any]:
        """
        Scan project directory for files
        
        Args:
            project_path: Path to scan
            
        Returns:
            Dictionary mapping file paths to file information
        """
        files = {}
        
        try:
            for root, dirs, filenames in os.walk(project_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                
                for filename in filenames:
                    if filename.startswith('.'):
                        continue
                    
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, project_path)
                    
                    try:
                        stat = os.stat(file_path)
                        files[rel_path] = {
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'is_file': os.path.isfile(file_path),
                            'is_dir': os.path.isdir(file_path)
                        }
                    except OSError:
                        # Skip files we can't access
                        continue
        
        except OSError:
            # If we can't scan the directory, return empty dict
            pass
        
        return files
    
    def set_session_data(self, key: str, value: Any):
        """Set session data"""
        self.session_data[key] = value
        
        if self.persist_context:
            self._save_context()
    
    def get_session_data(self, key: str, default: Any = None) -> Any:
        """Get session data"""
        return self.session_data.get(key, default)
    
    def get_context(self) -> Dict[str, Any]:
        """Get the complete context as a dictionary"""
        context = {
            'messages': self.get_messages_dict(),
            'project': self.project.to_dict() if self.project else None,
            'session_data': self.session_data
        }
        return context
    
    def clear_context(self):
        """Clear all context data"""
        self.messages = []
        self.project = None
        self.session_data = {}
        
        if self.persist_context:
            self._save_context()
    
    def _save_context(self):
        """Save context to file"""
        try:
            context_data = {
                'messages': [msg.to_dict() for msg in self.messages],
                'project': self.project.to_dict() if self.project else None,
                'session_data': self.session_data,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            # If we can't save, just continue without error
            pass
    
    def _load_context(self):
        """Load context from file"""
        try:
            if os.path.exists(self.context_file):
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    context_data = json.load(f)
                
                # Load messages
                if 'messages' in context_data:
                    self.messages = [Message.from_dict(msg) for msg in context_data['messages']]
                
                # Load project
                if 'project' in context_data and context_data['project']:
                    self.project = ProjectInfo.from_dict(context_data['project'])
                
                # Load session data
                if 'session_data' in context_data:
                    self.session_data = context_data['session_data']
        
        except Exception as e:
            # If we can't load, start with empty context
            self.messages = []
            self.project = None
            self.session_data = {}
    
    def get_context_summary(self) -> str:
        """Get a summary of the current context"""
        summary_parts = []
        
        # Message count
        summary_parts.append(f"Messages: {len(self.messages)}")
        
        # Project info
        if self.project:
            file_count = len(self.project.files)
            summary_parts.append(f"Project: {self.project.name} ({file_count} files)")
        else:
            summary_parts.append("Project: None")
        
        # Session data
        if self.session_data:
            summary_parts.append(f"Session data: {len(self.session_data)} items")
        
        return " | ".join(summary_parts)
