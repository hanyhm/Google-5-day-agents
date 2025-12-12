# Day 2: AI Agents with Tools and APIs

## Overview

Day 2 focuses on enhancing AI agents by integrating external tools and APIs. You'll learn how to enable agents to perform actions beyond text generation, making them capable of interacting with various services to execute real-world tasks.

## Learning Objectives

- Learn to integrate external tools with AI agents
- Understand tool selection and execution patterns
- Implement agents that interact with REST APIs
- Build agents capable of performing complex multi-step tasks

## Key Concepts

### Tool Integration Patterns

Agents use tools to extend their capabilities beyond text generation:

1. **Function Calling**: LLM requests specific tool execution
2. **Tool Selection**: Agent chooses appropriate tool based on context
3. **Tool Execution**: External service performs the action
4. **Result Integration**: Tool output fed back to agent for reasoning

### Tool Execution Flow

```
User Query
    │
    ▼
Agent Reasoning (LLM)
    │
    ├──► Tool Selection
    │       │
    │       ▼
    │   Tool Execution
    │       │
    │       ▼
    └──► Result Processing
            │
            ▼
        Final Response
```

### Common Tool Types

- **Search Tools**: Web search, database queries
- **Calculation Tools**: Mathematical operations, data processing
- **API Tools**: REST APIs, GraphQL endpoints
- **System Tools**: File operations, system commands
- **Custom Tools**: Domain-specific functionality

## Code Examples

### Example 1: Tool Integration (`tool_integration.py`)

Demonstrates an agent that uses multiple tools (calculator, web search, text processing) to answer complex queries.

**Features:**
- Multiple tool definitions
- Tool selection logic
- Tool execution and result handling
- Error handling for tool failures

**Usage:**
```bash
export GOOGLE_API_KEY="your-api-key"
python tool_integration.py
```

### Example 2: API Agent (`api_agent.py`)

An agent that interacts with REST APIs to fetch and process data from external services.

**Features:**
- REST API integration
- JSON data processing
- Error handling and retries
- Response formatting

**Usage:**
```bash
export GOOGLE_API_KEY="your-api-key"
python api_agent.py
```

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys:**
   ```bash
   export GOOGLE_API_KEY="your-gemini-api-key"
   ```

3. **For API examples, you may need:**
   - Public API endpoints (examples use free APIs)
   - Or configure your own API endpoints

## Key Takeaways

- Tools extend agent capabilities beyond text generation
- Proper tool design enables modular and reusable functionality
- Error handling is critical for robust tool integration
- Tool descriptions help agents make better selection decisions
- API integration enables agents to interact with real-world services

## Tool Design Best Practices

1. **Clear Descriptions**: Provide detailed tool descriptions for better selection
2. **Error Handling**: Always handle tool failures gracefully
3. **Input Validation**: Validate inputs before tool execution
4. **Result Formatting**: Structure tool outputs for easy processing
5. **Idempotency**: Design tools to be safely retryable

## Next Steps

- Day 3: Implement memory systems for context management
- Day 4: Add observability and debugging capabilities
- Day 5: Deploy agents to production

