"""
Capstone Project: Comprehensive AI Agent

This agent integrates multiple course concepts:
- Tool Use (Day 2)
- Memory Management (Day 3)
- Observability (Day 4)
"""

import os
import json
import time
import logging
import uuid
import math
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from collections import defaultdict
from pathlib import Path

import google.generativeai as genai


# ============================================================================
# Tool System (Day 2)
# ============================================================================

class CalculatorTool:
    """Tool for mathematical calculations."""
    
    def __init__(self):
        self.name = "calculator"
        self.description = "Performs mathematical calculations"
    
    def execute(self, expression: str) -> str:
        """Safely evaluate mathematical expressions."""
        try:
            expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            result = eval(expression, {"__builtins__": {}}, {"math": math})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"


class TextProcessorTool:
    """Tool for text processing operations."""
    
    def __init__(self):
        self.name = "text_processor"
        self.description = "Processes text (count, reverse, transform)"
    
    def execute(self, text: str, operation: str = "count_words") -> str:
        """Process text based on operation."""
        operations = {
            "count_words": lambda t: f"Word count: {len(t.split())}",
            "count_chars": lambda t: f"Character count: {len(t)}",
            "reverse": lambda t: f"Reversed: {t[::-1]}",
            "uppercase": lambda t: f"Uppercase: {t.upper()}",
            "lowercase": lambda t: f"Lowercase: {t.lower()}",
        }
        
        if operation in operations:
            return operations[operation](text)
        return f"Unknown operation: {operation}"


# ============================================================================
# Memory System (Day 3)
# ============================================================================

class ShortTermMemory:
    """Short-term memory for conversation history."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversation_history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def get_recent_context(self, num_turns: int = 5) -> str:
        """Get recent conversation context."""
        if not self.conversation_history:
            return ""
        
        recent = self.conversation_history[-num_turns * 2:]
        return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent])


class LongTermMemory:
    """Long-term memory for user preferences."""
    
    def __init__(self, storage_path: str = "capstone_memory.json"):
        self.storage_path = Path(storage_path)
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except:
                return {"users": {}, "preferences": {}}
        return {"users": {}, "preferences": {}}
    
    def _save_memory(self):
        """Save memory to storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences."""
        if user_id not in self.memory["users"]:
            self.memory["users"][user_id] = {"preferences": {}}
        return self.memory["users"][user_id].get("preferences", {})
    
    def save_preference(self, user_id: str, key: str, value: Any):
        """Save user preference."""
        if user_id not in self.memory["users"]:
            self.memory["users"][user_id] = {"preferences": {}}
        self.memory["users"][user_id]["preferences"][key] = value
        self._save_memory()


# ============================================================================
# Observability System (Day 4)
# ============================================================================

class MetricsCollector:
    """Collects performance metrics."""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "total_response_time": 0.0,
            "total_tokens": 0,
            "tools_used": defaultdict(int),
        }
        self.request_times: List[float] = []
    
    def record_request(self, success: bool, response_time: float, tokens: int = 0, tool_used: Optional[str] = None):
        """Record request metrics."""
        self.metrics["requests_total"] += 1
        self.metrics["total_response_time"] += response_time
        self.metrics["total_tokens"] += tokens
        self.request_times.append(response_time)
        
        if success:
            self.metrics["requests_success"] += 1
        else:
            self.metrics["requests_error"] += 1
        
        if tool_used:
            self.metrics["tools_used"][tool_used] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics."""
        total = self.metrics["requests_total"]
        if total == 0:
            return {"message": "No requests recorded"}
        
        avg_time = self.metrics["total_response_time"] / total
        success_rate = (self.metrics["requests_success"] / total) * 100
        
        return {
            "total_requests": total,
            "success_rate": f"{success_rate:.2f}%",
            "average_response_time_seconds": f"{avg_time:.3f}",
            "total_tokens": self.metrics["total_tokens"],
            "tools_used": dict(self.metrics["tools_used"])
        }


class StructuredLogger:
    """Structured logger for agent operations."""
    
    def __init__(self, name: str = "capstone_agent"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
    
    def log(self, level: str, message: str, **kwargs):
        """Log with structured data."""
        extra_msg = f" | {json.dumps(kwargs)}" if kwargs else ""
        getattr(self.logger, level.lower())(f"{message}{extra_msg}")


# ============================================================================
# Main Capstone Agent
# ============================================================================

class CapstoneAgent:
    """Comprehensive AI agent integrating tools, memory, and observability."""
    
    def __init__(self, api_key: Optional[str] = None, user_id: str = "default"):
        """Initialize capstone agent."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize tools (Day 2)
        self.tools = {
            "calculator": CalculatorTool(),
            "text_processor": TextProcessorTool(),
        }
        
        # Initialize memory (Day 3)
        self.short_term_memory = ShortTermMemory(max_history=10)
        self.long_term_memory = LongTermMemory()
        self.user_id = user_id
        
        # Initialize observability (Day 4)
        self.metrics = MetricsCollector()
        self.logger = StructuredLogger()
        self.request_id = None
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        return str(uuid.uuid4())
    
    def _select_tool(self, query: str) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Determine which tool to use."""
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["calculate", "compute", "math", "add", "multiply"]):
            return "calculator", {"expression": query}
        
        if any(kw in query_lower for kw in ["count", "reverse", "uppercase", "lowercase"]):
            operation = "count_words"
            if "characters" in query_lower:
                operation = "count_chars"
            elif "reverse" in query_lower:
                operation = "reverse"
            elif "uppercase" in query_lower:
                operation = "uppercase"
            elif "lowercase" in query_lower:
                operation = "lowercase"
            return "text_processor", {"text": query, "operation": operation}
        
        return None, None
    
    def _extract_preference(self, message: str) -> Optional[tuple[str, Any]]:
        """Extract user preference from message."""
        message_lower = message.lower()
        
        if "i like" in message_lower or "i prefer" in message_lower:
            if "python" in message_lower:
                return ("favorite_language", "Python")
            elif "javascript" in message_lower:
                return ("favorite_language", "JavaScript")
        
        return None
    
    def chat(self, message: str) -> str:
        """Process message with full capabilities."""
        self.request_id = self._generate_request_id()
        start_time = time.time()
        
        # Log request start
        self.logger.log("INFO", "Request started", request_id=self.request_id, user_id=self.user_id)
        
        try:
            # Check for preference updates
            preference = self._extract_preference(message)
            if preference:
                key, value = preference
                self.long_term_memory.save_preference(self.user_id, key, value)
                self.logger.log("INFO", "Preference saved", key=key, value=value)
            
            # Add user message to short-term memory
            self.short_term_memory.add_message("user", message)
            
            # Get context
            context = self.short_term_memory.get_recent_context(num_turns=3)
            preferences = self.long_term_memory.get_user_preferences(self.user_id)
            
            # Check if tool is needed
            tool_name, tool_params = self._select_tool(message)
            tool_result = None
            
            if tool_name:
                self.logger.log("INFO", "Tool selected", tool=tool_name)
                tool_result = self.tools[tool_name].execute(**tool_params)
                self.metrics.record_request(True, 0, tool_used=tool_name)
            
            # Build prompt
            prompt_parts = []
            
            if preferences:
                prefs_str = ", ".join([f"{k}: {v}" for k, v in preferences.items()])
                prompt_parts.append(f"User preferences: {prefs_str}")
            
            if context:
                prompt_parts.append(f"Recent conversation:\n{context}")
            
            if tool_result:
                prompt_parts.append(f"Tool result: {tool_result}")
            
            prompt_parts.append(f"User message: {message}")
            
            prompt = "\n\n".join(prompt_parts)
            
            # Generate response
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Add response to short-term memory
            self.short_term_memory.add_message("assistant", response_text)
            
            # Record metrics
            response_time = time.time() - start_time
            estimated_tokens = len(message.split()) + len(response_text.split())
            self.metrics.record_request(True, response_time, tokens=estimated_tokens, tool_used=tool_name)
            
            self.logger.log("INFO", "Request completed", 
                          request_id=self.request_id, 
                          response_time=response_time,
                          tokens=estimated_tokens)
            
            return response_text
        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.record_request(False, response_time)
            self.logger.log("ERROR", "Request failed", 
                          request_id=self.request_id, 
                          error=str(e))
            return f"Error: {str(e)}"
    
    def get_observability_report(self) -> Dict[str, Any]:
        """Get comprehensive observability report."""
        return {
            "metrics": self.metrics.get_stats(),
            "user_preferences": self.long_term_memory.get_user_preferences(self.user_id),
            "conversation_turns": len(self.short_term_memory.conversation_history) // 2
        }
    
    def run(self, query: str) -> dict:
        """Run agent with query."""
        response = self.chat(query)
        return {
            "query": query,
            "response": response,
            "request_id": self.request_id
        }


def main():
    """Example usage of CapstoneAgent."""
    
    print("=" * 60)
    print("Capstone Project: Comprehensive AI Agent")
    print("=" * 60)
    print()
    
    try:
        agent = CapstoneAgent(user_id="alice")
        print("✓ Capstone agent initialized")
        print("✓ Tools: calculator, text_processor")
        print("✓ Memory: short-term and long-term")
        print("✓ Observability: logging and metrics")
        print()
    except ValueError as e:
        print(f"✗ Error: {e}")
        return
    
    # Example queries demonstrating all features
    examples = [
        "Calculate 25 * 4 + 10",
        "I like Python programming.",
        "What's my favorite programming language?",
        "Count the words in: The quick brown fox",
        "Tell me about my preferences.",
    ]
    
    print("Running example queries...")
    print("-" * 60)
    print()
    
    for i, query in enumerate(examples, 1):
        print(f"Query {i}: {query}")
        result = agent.run(query)
        print(f"Response: {result['response']}")
        print()
    
    # Display observability report
    print("=" * 60)
    print("Observability Report")
    print("=" * 60)
    print()
    
    report = agent.get_observability_report()
    print(json.dumps(report, indent=2))
    print()


if __name__ == "__main__":
    main()

