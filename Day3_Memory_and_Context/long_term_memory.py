"""
AI Agent with Long-Term Memory

This example demonstrates an agent with persistent storage for user preferences
and historical data (long-term memory).
"""

import os
import json
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path


class LongTermMemory:
    """Manages long-term memory (persistent storage) for an agent."""
    
    def __init__(self, storage_path: str = "agent_memory.json"):
        """
        Initialize long-term memory storage.
        
        Args:
            storage_path: Path to JSON file for persistent storage
        """
        self.storage_path = Path(storage_path)
        self.memory: Dict[str, Any] = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from persistent storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memory: {e}")
                return self._initialize_memory()
        return self._initialize_memory()
    
    def _initialize_memory(self) -> Dict[str, Any]:
        """Initialize empty memory structure."""
        return {
            "users": {},
            "preferences": {},
            "conversations": [],
            "learned_patterns": {}
        }
    
    def _save_memory(self):
        """Save memory to persistent storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def get_user_preferences(self, user_id: str = "default") -> Dict[str, Any]:
        """Get user preferences."""
        if user_id not in self.memory["users"]:
            self.memory["users"][user_id] = {
                "preferences": {},
                "created_at": datetime.now().isoformat()
            }
        return self.memory["users"][user_id].get("preferences", {})
    
    def save_user_preference(self, user_id: str, key: str, value: Any):
        """Save a user preference."""
        if user_id not in self.memory["users"]:
            self.memory["users"][user_id] = {
                "preferences": {},
                "created_at": datetime.now().isoformat()
            }
        
        self.memory["users"][user_id]["preferences"][key] = value
        self.memory["users"][user_id]["last_updated"] = datetime.now().isoformat()
        self._save_memory()
    
    def add_conversation(self, user_id: str, query: str, response: str):
        """Add a conversation to history."""
        conversation = {
            "user_id": user_id,
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        self.memory["conversations"].append(conversation)
        
        # Keep only recent conversations (last 100)
        if len(self.memory["conversations"]) > 100:
            self.memory["conversations"] = self.memory["conversations"][-100:]
        
        self._save_memory()
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's conversation history."""
        user_conversations = [
            conv for conv in self.memory["conversations"]
            if conv["user_id"] == user_id
        ]
        return user_conversations[-limit:]
    
    def learn_pattern(self, pattern_key: str, pattern_data: Any):
        """Learn and store a pattern."""
        self.memory["learned_patterns"][pattern_key] = {
            "data": pattern_data,
            "learned_at": datetime.now().isoformat()
        }
        self._save_memory()
    
    def get_learned_pattern(self, pattern_key: str) -> Optional[Any]:
        """Retrieve a learned pattern."""
        if pattern_key in self.memory["learned_patterns"]:
            return self.memory["learned_patterns"][pattern_key]["data"]
        return None


class AgentWithLongTermMemory:
    """An AI agent with long-term memory capabilities."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        storage_path: str = "agent_memory.json",
        user_id: str = "default"
    ):
        """
        Initialize the agent with long-term memory.
        
        Args:
            api_key: Google Gemini API key
            storage_path: Path to memory storage file
            user_id: Current user ID
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize long-term memory
        self.memory = LongTermMemory(storage_path=storage_path)
        self.user_id = user_id
    
    def _extract_preference(self, message: str) -> Optional[tuple[str, Any]]:
        """Extract preference information from message."""
        message_lower = message.lower()
        
        # Simple pattern matching (in production, use more sophisticated NLP)
        if "i like" in message_lower or "i prefer" in message_lower or "my favorite" in message_lower:
            # Extract preference
            if "programming" in message_lower or "language" in message_lower:
                if "python" in message_lower:
                    return ("favorite_language", "Python")
                elif "javascript" in message_lower:
                    return ("favorite_language", "JavaScript")
            elif "color" in message_lower:
                colors = ["red", "blue", "green", "yellow", "purple", "orange"]
                for color in colors:
                    if color in message_lower:
                        return ("favorite_color", color)
        
        return None
    
    def chat(self, message: str) -> str:
        """Process a message with long-term memory context."""
        # Check for preference updates
        preference = self._extract_preference(message)
        if preference:
            key, value = preference
            self.memory.save_user_preference(self.user_id, key, value)
            print(f"💾 Saved preference: {key} = {value}")
        
        # Get user preferences
        preferences = self.memory.get_user_preferences(self.user_id)
        
        # Get recent conversation history
        history = self.memory.get_user_history(self.user_id, limit=3)
        
        # Build context
        context_parts = []
        
        if preferences:
            prefs_str = ", ".join([f"{k}: {v}" for k, v in preferences.items()])
            context_parts.append(f"User preferences: {prefs_str}")
        
        if history:
            context_parts.append("\nRecent conversation history:")
            for conv in history:
                context_parts.append(f"  User: {conv['query']}")
                context_parts.append(f"  Assistant: {conv['response']}")
        
        context = "\n".join(context_parts)
        
        # Build prompt
        if context:
            prompt = f"""You are a helpful AI assistant with memory of user preferences and past conversations.

{context}

Now respond to the user's message: {message}

Use the context to provide personalized responses."""
        else:
            prompt = message
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Save conversation to long-term memory
            self.memory.add_conversation(self.user_id, message, response_text)
            
            return response_text
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_user_info(self) -> Dict:
        """Get information about the current user."""
        preferences = self.memory.get_user_preferences(self.user_id)
        history = self.memory.get_user_history(self.user_id)
        
        return {
            "user_id": self.user_id,
            "preferences": preferences,
            "conversation_count": len(history)
        }
    
    def run(self, query: str) -> dict:
        """Run the agent with a query."""
        response = self.chat(query)
        
        return {
            "query": query,
            "response": response,
            "user_id": self.user_id
        }


def main():
    """Example usage of the AgentWithLongTermMemory."""
    
    print("=" * 60)
    print("AI Agent with Long-Term Memory")
    print("=" * 60)
    print()
    
    try:
        agent = AgentWithLongTermMemory(user_id="alice")
        print("✓ Agent initialized successfully")
        print("✓ Long-term memory enabled")
        print(f"✓ Storage: {agent.memory.storage_path}")
        print()
    except ValueError as e:
        print(f"✗ Error: {e}")
        return
    
    # Simulate conversations across sessions
    conversations = [
        "I like Python programming.",
        "What's my favorite programming language?",
        "My favorite color is blue.",
        "What do you know about my preferences?",
    ]
    
    print("Simulating conversations (memory persists across sessions)...")
    print("-" * 60)
    print()
    
    for i, query in enumerate(conversations, 1):
        print(f"Query {i}: {query}")
        print()
        
        result = agent.run(query)
        print(f"Response: {result['response']}")
        print()
        print("-" * 60)
        print()
    
    # Show user info
    user_info = agent.get_user_info()
    print(f"User Information:")
    print(f"  User ID: {user_info['user_id']}")
    print(f"  Preferences: {user_info['preferences']}")
    print(f"  Conversation Count: {user_info['conversation_count']}")
    print()


if __name__ == "__main__":
    main()

