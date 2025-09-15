"""
Task tool for routing tasks to sub-agents
"""

import asyncio
from typing import Dict, Any, Optional
from .base_tool import BaseTool


class TaskTool(BaseTool):
    """Tool for routing tasks to specialized sub-agents"""
    
    def __init__(self, sub_agents: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="Task",
            description="Launch a new agent to handle complex, multi-step tasks autonomously. \n\nAvailable agent types and the tools they have access to:\n- general-purpose: General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you. (Tools: *)\n- statusline-setup: Use this agent to configure the user's Claude Code status line setting. (Tools: Read, Edit)\n- output-style-setup: Use this agent to create a Claude Code output style. (Tools: Read, Write, Edit, Glob, LS, Grep)\n\nWhen using the Task tool, you must specify a subagent_type parameter to select which agent type to use.\n\n\n\nWhen NOT to use the Agent tool:\n- If you want to read a specific file path, use the Read or Glob tool instead of the Agent tool, to find the match more quickly\n- If you are searching for a specific class definition like \"class Foo\", use the Glob tool instead, to find the match more quickly\n- If you are searching for code within a specific file or set of 2-3 files, use the Read tool instead of the Agent tool, to find the match more quickly\n- Other tasks that are not related to the agent descriptions above\n\n\nUsage notes:\n1. Launch multiple agents concurrently whenever possible, to maximize performance; to do that, use a single message with multiple tool uses\n2. When the agent is done, it will return a single message back to you. The result returned by the agent is not visible to the user. To show the user the result, you should send a text message back to the user with a concise summary of the result.\n3. Each agent invocation is stateless. You will not be able to send additional messages to the agent, nor will the agent be able to communicate with you outside of its final report. Therefore, your prompt should contain a highly detailed task description for the agent to perform autonomously and you should specify exactly what information the agent should return back to you in its final and only message to you.\n4. The agent's outputs should generally be trusted\n5. Clearly tell the agent whether you expect it to write code or just to do research (search, file reads, web fetches, etc.), since it is not aware of the user's intent\n6. If the agent description mentions that it should be used proactively, then you should try your best to use it without the user having to ask for it first. Use your judgement.\n\nExample usage:\n\n<example_agent_descriptions>\n\"code-reviewer\": use this agent after you are done writing a signficant piece of code\n\"greeting-responder\": use this agent when to respond to user greetings with a friendly joke\n</example_agent_description>\n\n<example>\nuser: \"Please write a function that checks if a number is prime\"\nassistant: Sure let me write a function that checks if a number is prime\nassistant: First let me use the Write tool to write a function that checks if a number is prime\nassistant: I'm going to use the Write tool to write the following code:\n<code>\nfunction isPrime(n) {\n  if (n <= 1) return false\n  for (let i = 2; i * i <= n; i++) {\n    if (n % i === 0) return false\n  }\n  return true\n}\n</code>\n<commentary>\nSince a signficant piece of code was written and the task was completed, now use the code-reviewer agent to review the code\n</commentary>\nassistant: Now let me use the code-reviewer agent to review the code\nassistant: Uses the Task tool to launch the with the code-reviewer agent \n</example>\n\n<example>\nuser: \"Hello\"\n<commentary>\nSince the user is greeting, use the greeting-responder agent to respond with a friendly joke\n</commentary>\nassistant: \"I'm going to use the Task tool to launch the with the greeting-responder agent\"\n</example>\n",
            input_schema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "A short (3-5 word) description of the task"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "The task for the agent to perform"
                    },
                    "subagent_type": {
                        "type": "string",
                        "description": "The type of specialized agent to use for this task"
                    }
                },
                "required": [
                    "description",
                    "prompt",
                    "subagent_type"
                ],
                "additionalProperties": False,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        )
        self.sub_agents = sub_agents or {}
    
    def set_sub_agents(self, sub_agents: Dict[str, Any]):
        """Set the available sub-agents"""
        self.sub_agents = sub_agents
    
    async def execute(self, description: str, prompt: str, subagent_type: str) -> Dict[str, Any]:
        """Route the task to the appropriate sub-agent for execution"""
        if not self.validate_input(description=description, prompt=prompt, subagent_type=subagent_type):
            return {
                "error": "Invalid input parameters",
                "result": None
            }
        
        # Check if sub-agent type is available
        if subagent_type not in self.sub_agents:
            available_types = list(self.sub_agents.keys())
            return {
                "error": f"Unknown subagent type '{subagent_type}'. Available types: {available_types}",
                "result": None
            }
        
        try:
            # Get the sub-agent
            sub_agent = self.sub_agents[subagent_type]
            
            # Route the task to the sub-agent for execution
            result = await sub_agent.execute(prompt, {"description": description})
            
            return {
                "error": None,
                "result": result,
                "subagent_type": subagent_type,
                "description": description
            }
            
        except Exception as e:
            return {
                "error": f"Error routing task to {subagent_type}: {str(e)}",
                "result": None
            }
