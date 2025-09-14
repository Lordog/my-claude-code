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
User Request → Lead Agent → Output Parser → Tool Executor → Context Update → Response
```

**Step-by-step process:**

1. **User Input**: User submits a request through CLI or API
2. **Lead Agent Processing**: The Lead Agent receives the request and generates a response
3. **Output Parsing**: The response is parsed to extract content and tool actions
4. **Tool Execution**: Any tool actions are executed by the Tool Executor
5. **Context Update**: Results are stored in the Context Manager
6. **Response**: Final response is returned to the user

### 2. Agent Task Routing Flow

```
Request → LeadAgent → Task Tool (Router) → Sub-Agent Processing → Tool Execution → Response
```

**When sub-agents are involved:**

1. **LeadAgent Processing**: The LeadAgent receives the request and determines if a sub-agent is needed
2. **Task Tool Routing**: The LeadAgent calls the Task tool with the task details and subagent_type
3. **Sub-Agent Selection**: The Task tool routes the task to the specified sub-agent based on subagent_type
4. **Processing**: The sub-agent processes the request using its specialized tools and capabilities
5. **Result Integration**: Results are returned through the Task tool back to the LeadAgent

## Core Components

### 1. Workflow Pipeline (`workflow_pipeline.py`)

**Purpose**: Main orchestrator that coordinates all system components

**Key Features**:
- Processes user requests through the complete workflow
- Manages task routing to sub-agents via Task Tool
- Handles context updates and result integration
- Provides unified interface for the system

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

### 4. Agent Registry (`agent_registry.py`)

**Purpose**: Manages sub-agents and their capabilities

**Key Features**:
- Agent registration and discovery
- Sub-agent management and routing
- Agent capability tracking
- Agent information management

**Agent Types**:
- **Lead Agent**: Main orchestrator with access to all tools, routes tasks via Task Tool
- **General Purpose Agent**: Handles complex research and multi-step tasks (Tools: All available)
- **Statusline Setup Agent**: Handles Claude Code status line configuration (Tools: Read, Edit)
- **Output Style Setup Agent**: Handles Claude Code output style creation (Tools: Read, Write, Edit, Glob, LS, Grep)

### 5. Task Tool (`task_tool.py`)

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

### 6. Context Manager (`context_manager.py`)

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
Lead Agent (or selected sub-agent)
    ↓
Model Manager (LLM API)
    ↓
Output Parser
    ↓
Tool Executor (if tool actions found)
    ↓
Context Manager (update state)
    ↓
Response to User
```

### 2. Tool Execution

```
Tool Actions (from parser)
    ↓
Tool Executor
    ↓
Individual Tools
    ↓
Tool Results
    ↓
Context Update
    ↓
Result Formatting
```

### 3. Agent Task Routing

```
LeadAgent Request Processing
    ↓
Task Tool Call (with subagent_type)
    ↓
Sub-Agent Validation
    ↓
Sub-Agent Processing
    ↓
Result Return via Task Tool
```

## Key Features

### 1. Modular Architecture
- Clear separation of concerns
- Easy to extend with new agents and tools
- Pluggable components

### 2. Intelligent Agent Management
- Direct task routing via Task Tool
- Sub-agent type-based routing
- Specialized agent capabilities

### 3. Robust Tool System
- Unified tool interface
- Error handling and recovery
- Result tracking and formatting

### 4. Context Awareness
- Conversation history management
- Project state tracking
- Session data persistence

### 5. Flexible Output Parsing
- Multiple tool call formats
- JSON parameter extraction
- Content cleaning and formatting

## Extension Points

### 1. Adding New Agents
```python
# Create new agent
class MyAgent(BaseAgent):
    def __init__(self, model_manager):
        super().__init__(
            name="MyAgent",
            description="My custom agent",
            capabilities=["my_capability"]
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