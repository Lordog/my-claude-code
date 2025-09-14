"""
Context manager for maintaining conversation and project state
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Message:
    """Represents a message in the conversation"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectContext:
    """Represents project-specific context"""
    project_path: str
    files: Dict[str, str] = field(default_factory=dict)  # file_path -> content
    git_info: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)


class ContextManager:
    """Manages conversation and project context"""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.messages: List[Message] = []
        self.project_context: Optional[ProjectContext] = None
        self.session_metadata: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a message to the conversation history"""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        
        # Maintain max history limit
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """Get conversation messages"""
        if limit:
            return self.messages[-limit:]
        return self.messages.copy()
    
    def get_conversation_text(self, limit: Optional[int] = None) -> str:
        """Get conversation as formatted text"""
        messages = self.get_messages(limit)
        text = ""
        for msg in messages:
            text += f"{msg.role.upper()}: {msg.content}\n\n"
        return text.strip()
    
    def set_project_context(self, project_path: str, **kwargs) -> None:
        """Set project context"""
        self.project_context = ProjectContext(
            project_path=project_path,
            **kwargs
        )
    
    def update_project_file(self, file_path: str, content: str) -> None:
        """Update a file in project context"""
        if not self.project_context:
            return
        self.project_context.files[file_path] = content
    
    def get_project_file(self, file_path: str) -> Optional[str]:
        """Get file content from project context"""
        if not self.project_context:
            return None
        return self.project_context.files.get(file_path)
    
    def list_project_files(self) -> List[str]:
        """List all files in project context"""
        if not self.project_context:
            return []
        return list(self.project_context.files.keys())
    
    def update_context(self, context: Dict[str, Any]) -> None:
        """Update session metadata context"""
        self.session_metadata.update(context)
    
    def get_context(self) -> Dict[str, Any]:
        """Get full context including conversation and project info"""
        context = {
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata
                }
                for msg in self.messages
            ],
            "session_metadata": self.session_metadata
        }
        
        if self.project_context:
            context["project"] = {
                "path": self.project_context.project_path,
                "files": self.project_context.files,
                "git_info": self.project_context.git_info,
                "dependencies": self.project_context.dependencies,
                "environment": self.project_context.environment
            }
        
        return context
    
    def clear_context(self) -> None:
        """Clear all context"""
        self.messages.clear()
        self.project_context = None
        self.session_metadata.clear()
    
    def save_context(self, file_path: str) -> None:
        """Save context to file"""
        context = self.get_context()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2, ensure_ascii=False)
    
    def load_context(self, file_path: str) -> None:
        """Load context from file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            context = json.load(f)
        
        # Restore messages
        self.messages.clear()
        for msg_data in context.get("messages", []):
            message = Message(
                role=msg_data["role"],
                content=msg_data["content"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                metadata=msg_data.get("metadata", {})
            )
            self.messages.append(message)
        
        # Restore session metadata
        self.session_metadata = context.get("session_metadata", {})
        
        # Restore project context
        if "project" in context:
            project_data = context["project"]
            self.project_context = ProjectContext(
                project_path=project_data["path"],
                files=project_data.get("files", {}),
                git_info=project_data.get("git_info", {}),
                dependencies=project_data.get("dependencies", []),
                environment=project_data.get("environment", {})
            )
