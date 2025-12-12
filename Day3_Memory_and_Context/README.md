# Day 3: Memory and Context Engineering

## Overview

Day 3 focuses on developing agents with short-term and long-term memory capabilities. You'll learn techniques for maintaining context and improving agent performance over extended interactions.

## Learning Objectives

- Understand the difference between short-term and long-term memory
- Implement conversation history management (short-term memory)
- Build persistent storage systems (long-term memory)
- Explore context management strategies for multi-turn conversations
- Improve agent performance through effective memory systems

## Key Concepts

### Memory Types

#### Short-Term Memory
- **Purpose**: Maintain context within a single session
- **Storage**: In-memory buffers (cleared when session ends)
- **Use Cases**: Conversation history, recent context, immediate decisions
- **Characteristics**: Fast access, limited capacity, session-scoped

#### Long-Term Memory
- **Purpose**: Persistent storage across sessions
- **Storage**: Databases, vector stores, file systems
- **Use Cases**: User preferences, learned patterns, historical data
- **Characteristics**: Persistent, scalable, cross-session

### Memory Architecture

```
┌─────────────┐
│   Agent     │
└──────┬──────┘
       │
       ├──► Short-Term Memory
       │    └──► Conversation History Buffer
       │    └──► Recent Context Window
       │    └──► Session State
       │
       └──► Long-Term Memory
            └──► User Preferences (Database)
            └──► Historical Patterns (Vector Store)
            └──► Learned Knowledge (Persistent Storage)
```

### Context Management Strategies

1. **Sliding Window**: Keep most recent N messages
2. **Summarization**: Compress old context into summaries
3. **Semantic Search**: Retrieve relevant past context
4. **Hybrid Approach**: Combine multiple strategies

## Code Examples

### Example 1: Short-Term Memory (`short_term_memory.py`)

Demonstrates an agent with conversation history management within a session.

**Features:**
- Conversation history buffer
- Context window management
- Message formatting and context injection
- Session-based memory

**Usage:**
```bash
export GOOGLE_API_KEY="your-api-key"
python short_term_memory.py
```

### Example 2: Long-Term Memory (`long_term_memory.py`)

An agent with persistent storage for user preferences and historical data.

**Features:**
- File-based persistent storage
- User preference management
- Historical data retrieval
- Cross-session memory

**Usage:**
```bash
export GOOGLE_API_KEY="your-api-key"
python long_term_memory.py
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

3. **For long-term memory:**
   - The example uses JSON file storage
   - In production, consider using databases or vector stores

## Key Takeaways

- Memory enables agents to handle complex, multi-turn conversations
- Short-term memory handles immediate context efficiently
- Long-term memory enables personalization and learning
- Context management balances performance and relevance
- Proper memory design improves user experience significantly

## Memory Best Practices

1. **Context Limits**: Set reasonable limits to avoid token overflow
2. **Summarization**: Compress old context when needed
3. **Relevance**: Only include relevant historical context
4. **Performance**: Balance memory depth with response speed
5. **Privacy**: Handle user data securely and responsibly

## Next Steps

- Day 4: Add observability and debugging capabilities
- Day 5: Deploy agents to production

