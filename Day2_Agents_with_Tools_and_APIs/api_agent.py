"""
AI Agent with REST API Integration

This example demonstrates an AI agent that interacts with REST APIs
to fetch and process data from external services.
"""

import os
import json
import requests
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from datetime import datetime


class APIAgent:
    """An AI agent that can interact with REST APIs."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the agent."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Define available APIs (using free public APIs for examples)
        self.available_apis = {
            "jsonplaceholder": {
                "base_url": "https://jsonplaceholder.typicode.com",
                "description": "Fake REST API for testing - provides posts, users, comments"
            },
            "restcountries": {
                "base_url": "https://restcountries.com/v3.1",
                "description": "Country information API"
            },
        }
    
    def fetch_api_data(self, api_name: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Fetch data from a REST API.
        
        Args:
            api_name: Name of the API to use
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            API response data
        """
        if api_name not in self.available_apis:
            return {"error": f"Unknown API: {api_name}"}
        
        base_url = self.available_apis[api_name]["base_url"]
        url = f"{base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return {
                "success": True,
                "data": response.json(),
                "status_code": response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_api_data(self, data: Dict[str, Any], query: str) -> str:
        """
        Process API data using LLM to answer user query.
        
        Args:
            data: API response data
            query: Original user query
            
        Returns:
            Processed response
        """
        if not data.get("success"):
            return f"Error fetching data: {data.get('error', 'Unknown error')}"
        
        api_data = data.get("data", {})
        
        # Format data for LLM
        data_str = json.dumps(api_data, indent=2)
        
        prompt = f"""The user asked: {query}

I fetched the following data from an API:
{data_str}

Based on this data, provide a helpful answer to the user's question.
If the data is a list, summarize the key information.
If the data is an object, extract the relevant details."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error processing data: {str(e)}"
    
    def determine_api_call(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Determine which API to call based on the query.
        
        Returns:
            Dict with api_name, endpoint, and params, or None
        """
        query_lower = query.lower()
        
        # Simple rule-based API selection (in production, use LLM)
        if any(keyword in query_lower for keyword in ["post", "user", "comment", "todo"]):
            if "post" in query_lower or "posts" in query_lower:
                return {
                    "api_name": "jsonplaceholder",
                    "endpoint": "/posts",
                    "params": {"_limit": 5} if "first" in query_lower or "few" in query_lower else None
                }
            elif "user" in query_lower:
                return {
                    "api_name": "jsonplaceholder",
                    "endpoint": "/users",
                    "params": None
                }
        
        if any(keyword in query_lower for keyword in ["country", "countries", "nation"]):
            if "all" in query_lower:
                return {
                    "api_name": "restcountries",
                    "endpoint": "/all",
                    "params": {"fields": "name,capital,population"}
                }
            else:
                # Extract country name (simplified)
                words = query_lower.split()
                for word in words:
                    if len(word) > 3:  # Potential country name
                        return {
                            "api_name": "restcountries",
                            "endpoint": f"/name/{word}",
                            "params": None
                        }
        
        return None
    
    def chat(self, message: str) -> str:
        """Process a message, potentially calling APIs."""
        api_call = self.determine_api_call(message)
        
        if api_call:
            print(f"🌐 Calling API: {api_call['api_name']} - {api_call['endpoint']}")
            api_data = self.fetch_api_data(
                api_call["api_name"],
                api_call["endpoint"],
                api_call.get("params")
            )
            
            return self.process_api_data(api_data, message)
        else:
            # No API call needed, use LLM directly
            try:
                response = self.model.generate_content(message)
                return response.text
            except Exception as e:
                return f"Error: {str(e)}"
    
    def run(self, query: str) -> dict:
        """Run the agent with a query."""
        api_call = self.determine_api_call(query)
        response = self.chat(query)
        
        return {
            "query": query,
            "response": response,
            "api_used": api_call["api_name"] if api_call else None,
            "available_apis": list(self.available_apis.keys())
        }


def main():
    """Example usage of the APIAgent."""
    
    print("=" * 60)
    print("AI Agent with REST API Integration")
    print("=" * 60)
    print()
    
    try:
        agent = APIAgent()
        print("✓ Agent initialized successfully")
        print(f"✓ Available APIs: {', '.join(agent.available_apis.keys())}")
        print()
    except ValueError as e:
        print(f"✗ Error: {e}")
        return
    
    # Example queries
    examples = [
        "Get me the first 3 posts from the API",
        "What information do you have about users?",
        "Tell me about countries",
        "What is machine learning?",
    ]
    
    print("Running example queries...")
    print("-" * 60)
    print()
    
    for i, query in enumerate(examples, 1):
        print(f"Query {i}: {query}")
        print()
        
        result = agent.run(query)
        print(f"Response: {result['response']}")
        if result['api_used']:
            print(f"\n[Used API: {result['api_used']}]")
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()

