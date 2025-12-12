"""
Basic AI Agent using Google Gemini API

This example demonstrates a simple AI agent that uses Google's Gemini model
to answer questions and perform reasoning tasks.
"""

import os
import google.generativeai as genai
from typing import Optional


class BasicAgent:
    """A basic AI agent using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the agent with API key.
        
        Args:
            api_key: Google Gemini API key. If not provided, reads from GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-pro')
    
    def chat(self, message: str, context: Optional[str] = None) -> str:
        """
        Send a message to the agent and get a response.
        
        Args:
            message: User's message/query
            context: Optional context to provide to the agent
            
        Returns:
            Agent's response
        """
        try:
            # Build the prompt with optional context
            prompt = message
            if context:
                prompt = f"Context: {context}\n\nUser: {message}\n\nAssistant:"
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            return response.text
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def run(self, query: str) -> dict:
        """
        Run the agent with a query and return structured response.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with query and response
        """
        response = self.chat(query)
        return {
            "query": query,
            "response": response,
            "model": "gemini-pro"
        }


def main():
    """Example usage of the BasicAgent."""
    
    print("=" * 60)
    print("Basic AI Agent - Google Gemini")
    print("=" * 60)
    print()
    
    # Initialize the agent
    try:
        agent = BasicAgent()
        print("✓ Agent initialized successfully")
        print()
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("\nPlease set your GOOGLE_API_KEY environment variable:")
        print("export GOOGLE_API_KEY='your-api-key'")
        return
    
    # Example queries
    examples = [
        "What is artificial intelligence?",
        "Explain the difference between AI agents and traditional LLMs.",
        "Write a Python function to calculate the factorial of a number.",
    ]
    
    print("Running example queries...")
    print("-" * 60)
    print()
    
    for i, query in enumerate(examples, 1):
        print(f"Query {i}: {query}")
        print()
        
        result = agent.run(query)
        print(f"Response: {result['response']}")
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()

