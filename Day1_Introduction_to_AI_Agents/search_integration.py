"""
AI Agent with Google Search Integration

This example demonstrates an AI agent that combines Google Gemini's reasoning
with Google Search for real-time information retrieval.
"""

import os
import google.generativeai as genai
import requests
from typing import Optional, List, Dict
from urllib.parse import quote


class SearchIntegratedAgent:
    """An AI agent that integrates Google Search for real-time information."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        search_api_key: Optional[str] = None,
        search_engine_id: Optional[str] = None
    ):
        """
        Initialize the agent with API keys.
        
        Args:
            api_key: Google Gemini API key
            search_api_key: Google Custom Search API key
            search_engine_id: Google Custom Search Engine ID
        """
        # Configure Gemini
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Configure Google Search
        self.search_api_key = search_api_key or os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = search_engine_id or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        if not self.search_api_key or not self.search_engine_id:
            print("Warning: Search API not configured. Search functionality disabled.")
            print("Set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID to enable.")
            self.search_enabled = False
        else:
            self.search_enabled = True
            self.search_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """
        Search Google for information.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results with title, snippet, and link
        """
        if not self.search_enabled:
            return []
        
        try:
            params = {
                "key": self.search_api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": num_results
            }
            
            response = requests.get(self.search_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", "")
                })
            
            return results
        
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def needs_search(self, query: str) -> bool:
        """
        Determine if a query requires real-time information.
        
        Args:
            query: User query
            
        Returns:
            True if search is needed, False otherwise
        """
        # Simple heuristic: check for time-sensitive or current event keywords
        time_sensitive_keywords = [
            "current", "latest", "recent", "today", "now", "2024", "2025",
            "news", "happening", "what is", "who is", "when did"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in time_sensitive_keywords)
    
    def chat(self, message: str) -> str:
        """
        Process a message with optional search integration.
        
        Args:
            message: User's message/query
            
        Returns:
            Agent's response
        """
        # Check if search is needed
        if self.search_enabled and self.needs_search(message):
            print("🔍 Searching for real-time information...")
            search_results = self.search(message)
            
            if search_results:
                # Build context from search results
                context = "Search Results:\n\n"
                for i, result in enumerate(search_results, 1):
                    context += f"{i}. {result['title']}\n"
                    context += f"   {result['snippet']}\n"
                    context += f"   Source: {result['link']}\n\n"
                
                # Combine search results with user query
                prompt = f"""Based on the following search results, answer the user's question.

{context}

User Question: {message}

Provide a comprehensive answer using the search results above. Cite sources when appropriate."""
            else:
                prompt = message
        else:
            prompt = message
        
        try:
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
            Dictionary with query, response, and search info
        """
        used_search = self.search_enabled and self.needs_search(query)
        response = self.chat(query)
        
        return {
            "query": query,
            "response": response,
            "used_search": used_search,
            "model": "gemini-pro"
        }


def main():
    """Example usage of the SearchIntegratedAgent."""
    
    print("=" * 60)
    print("AI Agent with Google Search Integration")
    print("=" * 60)
    print()
    
    # Initialize the agent
    try:
        agent = SearchIntegratedAgent()
        print("✓ Agent initialized successfully")
        if agent.search_enabled:
            print("✓ Search integration enabled")
        else:
            print("⚠ Search integration disabled (API keys not set)")
        print()
    except ValueError as e:
        print(f"✗ Error: {e}")
        return
    
    # Example queries
    examples = [
        "What is the current weather in San Francisco?",
        "Explain the concept of machine learning.",
        "What are the latest developments in AI?",
    ]
    
    print("Running example queries...")
    print("-" * 60)
    print()
    
    for i, query in enumerate(examples, 1):
        print(f"Query {i}: {query}")
        print()
        
        result = agent.run(query)
        print(f"Response: {result['response']}")
        if result['used_search']:
            print("\n[Used Google Search for real-time information]")
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()

