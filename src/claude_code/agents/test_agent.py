"""
Test agent - handles testing and quality assurance
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class TestAgent(BaseAgent):
    """Specialized agent for testing and quality assurance"""
    
    def __init__(self):
        super().__init__(
            name="test",
            description="Specialized agent for testing, quality assurance, and test automation",
            capabilities=[
                "unit_testing",
                "integration_testing",
                "test_automation",
                "test_coverage",
                "test_planning",
                "quality_assurance",
                "performance_testing"
            ]
        )
    
    def can_handle(self, request: str, context: Dict[str, Any]) -> bool:
        """Check if this is a test-related request"""
        test_keywords = [
            "test", "testing", "unit test", "integration test",
            "pytest", "unittest", "coverage", "quality",
            "assert", "mock", "stub", "fixture",
            "tdd", "bdd", "test driven", "behavior driven",
            "automation", "ci/cd", "pipeline"
        ]
        
        request_lower = request.lower()
        return any(keyword in request_lower for keyword in test_keywords)
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get system prompt for test agent"""
        return """You are a specialized test agent with expertise in:

1. Unit testing and test-driven development (TDD)
2. Integration testing and end-to-end testing
3. Test automation and CI/CD pipelines
4. Test coverage analysis and optimization
5. Quality assurance methodologies
6. Performance testing and load testing
7. Test planning and strategy

When creating tests:
- Follow testing best practices and patterns
- Write clear, maintainable test cases
- Use appropriate testing frameworks (pytest, unittest, jest, etc.)
- Include both positive and negative test cases
- Focus on edge cases and error conditions
- Ensure good test coverage without over-testing

For test analysis:
- Identify areas that need testing
- Suggest test improvements and optimizations
- Recommend testing tools and frameworks
- Analyze test coverage and gaps
- Suggest performance testing strategies

Always emphasize code quality, reliability, and maintainability in your testing recommendations."""
