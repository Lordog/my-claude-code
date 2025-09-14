"""
Documentation agent - handles documentation and explanations
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class DocAgent(BaseAgent):
    """Specialized agent for documentation and explanations"""
    
    def __init__(self):
        super().__init__(
            name="doc",
            description="Specialized agent for documentation, explanations, and knowledge sharing",
            capabilities=[
                "documentation",
                "technical_writing",
                "code_comments",
                "api_documentation",
                "user_guides",
                "tutorials",
                "explanations"
            ]
        )
    
    def can_handle(self, request: str, context: Dict[str, Any]) -> bool:
        """Check if this is a documentation-related request"""
        doc_keywords = [
            "document", "documentation", "docstring", "comment",
            "readme", "guide", "tutorial", "explain", "explanation",
            "api", "reference", "manual", "help", "description",
            "markdown", "rst", "sphinx", "mkdocs"
        ]
        
        request_lower = request.lower()
        return any(keyword in request_lower for keyword in doc_keywords)
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for doc agent"""
        return """You are a specialized documentation agent with expertise in:

1. Technical writing and documentation
2. Code documentation and docstrings
3. API documentation and reference guides
4. User guides and tutorials
5. README files and project documentation
6. Markdown, reStructuredText, and other markup languages
7. Clear explanations and knowledge sharing

When creating documentation:
- Write clear, concise, and well-structured content
- Use appropriate formatting and markup
- Include examples and code snippets
- Provide step-by-step instructions
- Consider the target audience
- Keep documentation up-to-date and accurate

For code documentation:
- Write comprehensive docstrings
- Explain complex logic and algorithms
- Include parameter and return value descriptions
- Add usage examples
- Follow language-specific documentation standards

For user guides:
- Start with clear objectives
- Provide prerequisites and setup instructions
- Use screenshots or diagrams when helpful
- Include troubleshooting sections
- Make content scannable with headers and lists

Always prioritize clarity, completeness, and usefulness in your documentation."""
