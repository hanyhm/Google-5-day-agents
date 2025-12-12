"""
AI Agent with Tool Integration

This example demonstrates an AI agent that uses multiple tools to answer
complex queries requiring calculations, searches, and data processing.
"""

import os
import json
import math
import google.generativeai as genai
from typing import Optional, Dict, Any, List
import re


class Tool:
    """Base class for tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters."""
        raise NotImplementedError


class CalculatorTool(Tool):
    """Tool for performing mathematical calculations."""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Performs mathematical calculations. Input: mathematical expression as string."
        )
    
    def execute(self, expression: str) -> str:
        """Evaluate a mathematical expression safely."""
        try:
            # Remove any non-math characters for safety
            expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            result = eval(expression, {"__builtins__": {}}, {"math": math})
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating: {str(e)}"


class TextProcessorTool(Tool):
    """Tool for text processing operations."""
    
    def __init__(self):
        super().__init__(
            name="text_processor",
            description="Processes text: count words, characters, reverse, uppercase, lowercase."
        )
    
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


class ToolIntegratedAgent:
    """An AI agent that can use multiple tools."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the agent with tools."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Register available tools
        self.tools = {
            "calculator": CalculatorTool(),
            "text_processor": TextProcessorTool(),
        }
    
    def get_tool_descriptions(self) -> str:
        """Get descriptions of all available tools."""
        descriptions = []
        for tool_name, tool in self.tools.items():
            descriptions.append(f"- {tool_name}: {tool.description}")
        return "\n".join(descriptions)
    
    def select_tool(self, query: str) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Determine which tool to use based on the query.
        
        Returns:
            Tuple of (tool_name, parameters) or (None, None)
        """
        # Simple rule-based tool selection (in production, use LLM for this)
        query_lower = query.lower()
        
        # Check for calculator needs
        if any(keyword in query_lower for keyword in ["calculate", "compute", "math", "add", "multiply", "divide"]):
            # Extract mathematical expression
            # Simple extraction - in production, use more sophisticated parsing
            numbers = re.findall(r'\d+\.?\d*', query)
            if len(numbers) >= 2:
                return "calculator", {"expression": query}
        
        # Check for text processing needs
        if any(keyword in query_lower for keyword in ["count words", "count characters", "reverse", "uppercase", "lowercase"]):
            operation = "count_words"
            if "characters" in query_lower or "chars" in query_lower:
                operation = "count_chars"
            elif "reverse" in query_lower:
                operation = "reverse"
            elif "uppercase" in query_lower or "upper" in query_lower:
                operation = "uppercase"
            elif "lowercase" in query_lower or "lower" in query_lower:
                operation = "lowercase"
            
            # Extract text (simplified - in production, use better extraction)
            return "text_processor", {"text": query, "operation": operation}
        
        return None, None
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool with given parameters."""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found"
        
        try:
            tool = self.tools[tool_name]
            return tool.execute(**parameters)
        except Exception as e:
            return f"Error executing tool: {str(e)}"
    
    def chat(self, message: str) -> str:
        """Process a message, potentially using tools."""
        # Check if tools are needed
        tool_name, parameters = self.select_tool(message)
        
        if tool_name:
            print(f"🔧 Using tool: {tool_name}")
            tool_result = self.execute_tool(tool_name, parameters)
            
            # Build prompt with tool result
            prompt = f"""User asked: {message}

I used the {tool_name} tool and got this result: {tool_result}

Now provide a helpful response to the user based on this result."""
        else:
            # No tool needed, use LLM directly
            prompt = message
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def run(self, query: str) -> dict:
        """Run the agent with a query."""
        tool_name, _ = self.select_tool(query)
        response = self.chat(query)
        
        return {
            "query": query,
            "response": response,
            "tool_used": tool_name,
            "available_tools": list(self.tools.keys())
        }


def main():
    """Example usage of the ToolIntegratedAgent."""
    
    print("=" * 60)
    print("AI Agent with Tool Integration")
    print("=" * 60)
    print()
    
    try:
        agent = ToolIntegratedAgent()
        print("✓ Agent initialized successfully")
        print(f"✓ Available tools: {', '.join(agent.tools.keys())}")
        print()
    except ValueError as e:
        print(f"✗ Error: {e}")
        return
    
    # Example queries
    examples = [
        "Calculate 25 * 4 + 10",
        "What is 100 divided by 5?",
        "Count the words in: The quick brown fox jumps over the lazy dog",
        "Reverse this text: Hello World",
        "What is artificial intelligence?",
    ]
    
    print("Running example queries...")
    print("-" * 60)
    print()
    
    for i, query in enumerate(examples, 1):
        print(f"Query {i}: {query}")
        print()
        
        result = agent.run(query)
        print(f"Response: {result['response']}")
        if result['tool_used']:
            print(f"\n[Used tool: {result['tool_used']}]")
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()

