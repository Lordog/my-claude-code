"""
Code agent - handles code generation, analysis, and modification
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class CodeAgent(BaseAgent):
    """Specialized agent for code-related tasks"""
    
    def __init__(self):
        super().__init__(
            name="code",
            description="Specialized agent for code generation, analysis, modification, and review",
            capabilities=[
                "code_generation",
                "code_analysis", 
                "code_review",
                "refactoring",
                "syntax_help",
                "best_practices",
                "language_specific_help"
            ]
        )
    
    def can_handle(self, request: str, context: Dict[str, Any]) -> bool:
        """Check if this is a code-related request"""
        code_keywords = [
            "code", "function", "class", "method", "variable", "import",
            "write", "create", "generate", "implement", "define",
            "analyze", "review", "refactor", "optimize", "fix",
            "python", "javascript", "typescript", "java", "go", "rust",
            "syntax", "error", "bug", "debug"
        ]
        
        request_lower = request.lower()
        return any(keyword in request_lower for keyword in code_keywords)
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for code agent"""
        base_prompt = """You are a specialized code agent with expertise in:

1. Code generation and implementation
2. Code analysis and review
3. Refactoring and optimization
4. Debugging and error fixing
5. Best practices and coding standards
6. Multiple programming languages (Python, JavaScript, TypeScript, Java, Go, Rust, etc.)

When working with code:
- Always provide clean, well-documented code
- Follow language-specific best practices
- Include proper error handling
- Add meaningful comments and docstrings
- Consider performance and maintainability
- Suggest improvements when appropriate

For code analysis:
- Identify potential issues and improvements
- Explain complex logic clearly
- Suggest optimizations
- Point out security concerns
- Recommend best practices

Always be precise and technical in your responses."""
        
        # Add project context
        if "project" in context and "project" in context:
            project = context["project"]
            if project.get("files"):
                base_prompt += f"\n\nCurrent project files:\n"
                for file_path, content in project["files"].items():
                    base_prompt += f"- {file_path}\n"
        
        return base_prompt
