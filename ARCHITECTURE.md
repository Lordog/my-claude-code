# Claude-Code-Python Architecture

## Overview

Claude-Code-Python is an agent framework that implements a sophisticated workflow pipeline for processing user requests through intelligent agents and tool execution. The system follows a clear separation of concerns with modular components that work together to provide a seamless user experience.

## Core Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude-Code-Python                          │
├─────────────────────────────────────────────────────────────────┤
│  User Interface Layer (CLI/Web/API)                            │
├─────────────────────────────────────────────────────────────────┤
│  Workflow Pipeline (Main Orchestrator)                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Lead Agent → Task Tool → Sub-Agents → Tool Executor   │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Agent Management System                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Agent Registry │  │  Task Tool      │  │  Sub-Agents     │  │
│  │  (Agent Info)   │  │  (Task Router)  │  │  (Specialized)  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  Tool Execution System                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Tool Executor  │  │  Tool Registry  │  │  Tool Results   │  │
│  │  (Execution)    │  │  (Management)   │  │  (Processing)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  Context Management System                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Context Manager│  │  Message Store  │  │  Project State  │  │
│  │  (State Mgmt)   │  │  (History)      │  │  (File Info)    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  Model Integration Layer                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Model Manager  │  │  OpenRouter     │  │  Mock Provider  │  │
│  │  (Abstraction)  │  │  (Primary)      │  │  (Fallback)     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Pipeline

The core of the system is the **Workflow Pipeline**, which orchestrates the entire process:

### 1. Request Processing Flow

```
User Request → Lead Agent (Loop-based Execution) → Response
```

**Step-by-step process:**

1. **User Input**: User submits a request through CLI or API
2. **Lead Agent Processing**: The Lead Agent receives the request and enters a loop-based execution mode
3. **Loop Execution**: The agent can make multiple tool calls and task delegations in a loop
4. **Tool Execution**: Tools are executed within the agent loop with results fed back to the agent
5. **Task Delegation**: Lead Agent can delegate tasks to sub-agents via Task tool
6. **Exit Condition**: Loop continues until the agent calls the Exit tool (success/failed)
7. **Response**: Final response is returned to the user

### 2. Agent Task Routing Flow

```
Request → LeadAgent (Loop) → Task Tool (Router) → Sub-Agent (Loop) → Exit Tool → Response
```

**When sub-agents are involved:**

1. **LeadAgent Processing**: The LeadAgent receives the request and enters loop-based execution
2. **Task Tool Routing**: The LeadAgent calls the Task tool with the task details and subagent_type
3. **Sub-Agent Selection**: The Task tool routes the task to the specified sub-agent based on subagent_type
4. **Sub-Agent Loop**: The sub-agent processes the request in its own loop with multiple tool calls
5. **Exit Condition**: Sub-agent continues until it calls the Exit tool (success/failed)
6. **Result Integration**: Results are returned through the Task tool back to the LeadAgent
7. **LeadAgent Continuation**: LeadAgent continues its loop until it calls the Exit tool

## Core Components

### 1. Workflow Pipeline (`workflow_pipeline.py`)

**Purpose**: Main orchestrator that coordinates all system components

**Key Features**:
- Processes user requests through loop-based execution
- Manages task routing to sub-agents via Task Tool
- Handles context updates and result integration
- Provides unified interface for the system
- Supports multi-step tool calling and task delegation

**Main Methods**:
- `process_request()`: Process requests through Lead Agent
- `process_with_sub_agent()`: Process requests with specific sub-agents
- `route_task_to_subagent()`: Route tasks to sub-agents via Task Tool

### 2. Output Parser (`output_parser.py`)

**Purpose**: Parses agent responses to extract content and tool actions

**Key Features**:
- Supports multiple tool call formats
- Extracts JSON parameters from tool calls
- Handles action IDs for tool tracking
- Cleans content for user display

**Supported Formats**:
- `<tool_name>{"param": "value"}</tool_name>`
- `[tool_name: {"param": "value"}]`
- `TOOL_CALL: tool_name {"param": "value"}`

### 3. Tool Executor (`tool_executor.py`)

**Purpose**: Executes tool actions and manages tool results

**Key Features**:
- Sequential tool execution to avoid conflicts
- Error handling and result tracking
- Tool registry management
- Result formatting for display

**Tool Categories**:
- File operations (Read, Write, Edit, LS, Glob, Grep)
- System operations (Bash)
- Web operations (WebSearch, WebFetch)
- Task management (TodoWrite, Task - routes to sub-agents)

### 4. LoopAgent (`loop_agent.py`)

**Purpose**: Base agent class that supports loop-based execution with tool calling

**Key Features**:
- Loop-based execution until Exit tool is called
- Multiple tool calls per execution cycle
- Tool result integration back to agent
- Configurable available tools per agent
- Support for task delegation (LeadAgent only)

**Execution Flow**:
1. Agent receives request and enters execution loop
2. Agent generates response with potential tool calls
3. Tools are executed and results fed back to agent
4. Loop continues until Exit tool is called
5. Final response is returned

### 5. Agent Registry (`agent_registry.py`)

**Purpose**: Manages sub-agents and their capabilities

**Key Features**:
- Agent registration and discovery
- Sub-agent management and routing
- Agent capability tracking
- Agent information management

**Agent Types**:
- **Lead Agent**: Main orchestrator with access to all tools, routes tasks via Task Tool (can delegate)
- **General Purpose Agent**: Handles complex research and multi-step tasks (Tools: All available, cannot delegate)
- **Statusline Setup Agent**: Handles Claude Code status line configuration (Tools: Read, Edit, cannot delegate)
- **Output Style Setup Agent**: Handles Claude Code output style creation (Tools: Read, Write, Edit, Glob, LS, Grep, cannot delegate)

### 6. Task Tool (`task_tool.py`)

**Purpose**: Routes tasks to specialized sub-agents based on subagent_type

**Key Features**:
- Direct task routing based on subagent_type parameter
- Sub-agent validation and error handling
- Task context passing to sub-agents
- Result formatting and error reporting

**Supported Sub-Agent Types**:
- `general-purpose`: For complex research and multi-step tasks
- `statusline-setup`: For Claude Code status line configuration
- `output-style-setup`: For Claude Code output style creation

### 7. Exit Tool (`exit_tool.py`)

**Purpose**: Terminates agent execution loops

**Key Features**:
- Required tool for all agents to exit execution loops
- Supports success and failed status
- Optional message for completion details
- Prevents infinite loops in agent execution

**Parameters**:
- `status`: "success" or "failed" - completion status
- `message`: Optional explanation of completion or issues

### 8. Context Manager (`context_manager.py`)

**Purpose**: Manages conversation history and project state

**Key Features**:
- Message history with timestamps and metadata
- Project file scanning and tracking
- Session data management
- Context persistence and loading

**Data Structures**:
- **Messages**: Conversation history with roles and timestamps
- **Project Info**: File system state and project metadata
- **Session Data**: Temporary data for the current session

## Data Flow

### 1. Request Processing

```
User Request
    ↓
Workflow Pipeline
    ↓
Lead Agent (Loop-based Execution)
    ↓
Model Manager (LLM API) → Tool Calls → Tool Executor
    ↓
Loop continues until Exit tool called
    ↓
Context Manager (update state)
    ↓
Response to User
```

### 2. Loop-based Tool Execution

```
Agent Response with Tool Calls
    ↓
Tool Executor (within agent loop)
    ↓
Individual Tools
    ↓
Tool Results fed back to Agent
    ↓
Agent continues loop or calls Exit tool
    ↓
Final Response
```

### 3. Agent Task Routing

```
LeadAgent Loop Processing
    ↓
Task Tool Call (with subagent_type)
    ↓
Sub-Agent Loop Processing
    ↓
Sub-Agent calls Exit tool
    ↓
Result Return via Task Tool
    ↓
LeadAgent continues loop or calls Exit tool
```

## Key Features

### 1. Modular Architecture
- Clear separation of concerns
- Easy to extend with new agents and tools
- Pluggable components

### 2. Loop-based Agent Execution
- Multi-step tool calling within agent loops
- Automatic loop termination via Exit tool
- Tool result integration back to agents
- Support for complex multi-step tasks

### 3. Intelligent Task Routing
- Direct task routing via Task Tool
- Sub-agent type-based routing
- Specialized agent capabilities
- LeadAgent can delegate, sub-agents cannot

### 4. Robust Tool System
- Unified tool interface
- Error handling and recovery
- Result tracking and formatting
- Loop-based tool execution

### 5. Context Awareness
- Conversation history management
- Project state tracking
- Session data persistence

### 6. Flexible Output Parsing
- Multiple tool call formats
- JSON parameter extraction
- Content cleaning and formatting

## Extension Points

### 1. Adding New Agents
```python
# Create new agent
class MyAgent(LoopAgent):
    def __init__(self, model_manager):
        super().__init__(
            name="MyAgent",
            description="My custom agent",
            capabilities=["my_capability"],
            available_tools=["Read", "Write", "Exit"],  # Specify available tools
            can_delegate=False  # Set to True only for LeadAgent
        )
        self.model_manager = model_manager

# Register with workflow pipeline
workflow_pipeline.register_sub_agent(MyAgent(model_manager))
```

### 2. Adding New Tools
```python
# Create new tool
class MyTool(BaseTool):
    def execute(self, parameters, context):
        # Tool implementation
        return result

# Register with tool executor
tool_executor.tools["MyTool"] = MyTool()
```

### 3. Custom Output Parsers
```python
# Extend output parser
class CustomOutputParser(OutputParser):
    def parse(self, response):
        # Custom parsing logic
        return parsed_output
```

## Configuration

### Environment Variables
- `OPENROUTER_API_KEY`: API key for OpenRouter provider
- `CLAUDE_CODE_DEBUG`: Enable debug mode
- `CLAUDE_CODE_MODEL`: Default model to use

### Configuration Options
- Model selection and fallback providers
- Context persistence settings
- Message history limits
- Tool execution timeouts

## Security Considerations

### 1. Tool Execution Safety
- Sandboxed tool execution
- Parameter validation
- Resource limits

### 2. API Security
- Secure API key management
- Request rate limiting
- Error message sanitization

### 3. Data Privacy
- Local context storage
- Sensitive data filtering
- User data protection

## Performance Optimizations

### 1. Context Management
- Message history limits
- Lazy project file scanning
- Efficient context serialization

### 2. Tool Execution
- Sequential execution to avoid conflicts
- Result caching where appropriate
- Timeout handling

### 3. Agent Management
- Direct sub-agent routing via Task Tool
- Sub-agent type-based selection
- Efficient agent registration and management

## Future Enhancements

### 1. Advanced Agent Capabilities
- Multi-agent collaboration
- Agent communication protocols
- Dynamic agent creation

### 2. Enhanced Tool System
- Tool composition and chaining
- Tool result streaming
- Tool dependency management

### 3. Improved Context Management
- Vector-based context search
- Context summarization
- Multi-project support

### 4. Better User Experience
- Interactive tool execution
- Real-time progress updates
- Rich output formatting

This architecture provides a solid foundation for building sophisticated AI-powered development tools while maintaining flexibility and extensibility.