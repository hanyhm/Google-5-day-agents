"""
AI Agent with Short-Term Memory

This example demonstrates an agent with conversation history management
within a session (short-term memory).
"""

import os
import google.generativeai as genai
from typing import Optional, List, Dict
from datetime import datetime


class ShortTermMemory:
    """Manages short-term memory (conversation history) for an agent."""
    
    def __init__(self, max_history: int = 10):
        """
        Initialize short-term memory.
        
        Args:
            max_history: Maximum number of conversation turns to keep
        """
        self.max_history = max_history
        self.conversation_history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """
        Add a message to conversation history.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only the most recent messages
        if len(self.conversation_history) > self.max_history * 2:  # *2 for user+assistant pairs
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def get_context(self) -> str:
        """Get formatted conversation context."""
        if not self.conversation_history:
            return ""
        
        context_parts = []
        for msg in self.conversation_history:
            role = msg["role"].capitalize()
            content = msg["content"]
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_recent_context(self, num_turns: int = 3) -> str:
        """
        Get recent conversation context.
        
        Args:
            num_turns: Number of recent turns to include
        """
        if not self.conversation_history:
            return ""
        
        recent = self.conversation_history[-num_turns * 2:]  # *2 for user+assistant pairs
        context_parts = []
        for msg in recent:
            role = msg["role"].capitalize()
            content = msg["content"]
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)


class AgentWithShortTermMemory:
    """An AI agent with short-term memory capabilities."""
    
    def __init__(self, api_key: Optional[str] = None, max_history: int = 10):
        """
        Initialize the agent with short-term memory.
        
        Args:
            api_key: Google Gemini API key
            max_history: Maximum conversation history to keep
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize short-term memory
        self.memory = ShortTermMemory(max_history=max_history)
    
    def chat(self, message: str) -> str:
        """
        Process a message with conversation context.
        
        Args:
            message: User's message
            
        Returns:
            Agent's response
        """
        # Add user message to history
        self.memory.add_message("user", message)
        
        # Get conversation context
        context = self.memory.get_recent_context(num_turns=5)
        
        # Build prompt with context
        if context:
            prompt = f"""You are a helpful AI assistant. Here is the recent conversation context:

{context}

Now respond to the user's latest message: {message}

Provide a helpful response that takes into account the conversation context."""
        else:
            prompt = message
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Add assistant response to history
            self.memory.add_message("assistant", response_text)
            
            return response_text
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.memory.add_message("assistant", error_msg)
            return error_msg
    
    def get_conversation_summary(self) -> Dict:
        """Get a summary of the conversation."""
        return {
            "total_turns": len(self.memory.conversation_history) // 2,
            "history": self.memory.conversation_history.copy()
        }
    
    def clear_memory(self):
        """Clear conversation history."""
        self.memory.clear()
    
    def run(self, query: str) -> dict:
        """Run the agent with a query."""
        response = self.chat(query)
        
        return {
            "query": query,
            "response": response,
            "conversation_turns": len(self.memory.conversation_history) // 2
        }


def main():
    """Example usage of the AgentWithShortTermMemory."""
    
    print("=" * 60)
    print("AI Agent with Short-Term Memory")
    print("=" * 60)
    print()
    
    try:
        agent = AgentWithShortTermMemory(max_history=5)
        print("✓ Agent initialized successfully")
        print("✓ Short-term memory enabled (max 5 conversation turns)")
        print()
    except ValueError as e:
        print(f"✗ Error: {e}")
        return
    
    # Simulate a multi-turn conversation
    conversation = [
        "My name is Alice.",
        "What's my name?",
        "I like Python programming.",
        "What programming language do I like?",
        "Tell me about my preferences.",
    ]
    
    print("Simulating a multi-turn conversation...")
    print("-" * 60)
    print()
    
    for i, query in enumerate(conversation, 1):
        print(f"Turn {i} - User: {query}")
        print()
        
        result = agent.run(query)
        print(f"Assistant: {result['response']}")
        print()
        print("-" * 60)
        print()
    
    # Show conversation summary
    summary = agent.get_conversation_summary()
    print(f"Conversation Summary:")
    print(f"  Total turns: {summary['total_turns']}")
    print(f"  Total messages: {len(summary['history'])}")
    print()


if __name__ == "__main__":
    main()

