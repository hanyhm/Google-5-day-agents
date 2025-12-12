"""
Structured Logging Setup for AI Agents

This example demonstrates structured logging implementation for agent operations
with different log levels and contextual information.
"""

import os
import json
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class StructuredLogger:
    """Structured logger for AI agent operations."""
    
    def __init__(self, name: str = "agent", log_level: str = "INFO"):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create console handler with JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method with structured data."""
        extra = {
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        getattr(self.logger, level.lower())(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log("CRITICAL", message, **kwargs)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": record.created,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "msecs",
                          "message", "pathname", "process", "processName", "relativeCreated",
                          "thread", "threadName", "exc_info", "exc_text", "stack_info"]:
                log_data[key] = value
        
        return json.dumps(log_data)


class AgentWithLogging:
    """An AI agent with structured logging."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize agent with logging."""
        import google.generativeai as genai
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize logger
        self.logger = StructuredLogger(name="agent", log_level="INFO")
        self.request_id = None
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return str(uuid.uuid4())
    
    def chat(self, message: str, user_id: Optional[str] = None) -> str:
        """
        Process a message with comprehensive logging.
        
        Args:
            message: User's message
            user_id: Optional user identifier
            
        Returns:
            Agent's response
        """
        # Generate request ID for tracing
        self.request_id = self._generate_request_id()
        
        # Log request start
        self.logger.info(
            "Request started",
            request_id=self.request_id,
            user_id=user_id or "anonymous",
            message_length=len(message),
            action="chat"
        )
        
        try:
            # Log model call
            self.logger.debug(
                "Calling LLM",
                request_id=self.request_id,
                model="gemini-pro"
            )
            
            start_time = datetime.utcnow()
            response = self.model.generate_content(message)
            end_time = datetime.utcnow()
            
            response_time = (end_time - start_time).total_seconds()
            response_text = response.text
            
            # Log successful response
            self.logger.info(
                "Request completed successfully",
                request_id=self.request_id,
                response_length=len(response_text),
                response_time_seconds=response_time,
                action="chat"
            )
            
            return response_text
        
        except Exception as e:
            # Log error
            self.logger.error(
                "Request failed",
                request_id=self.request_id,
                error=str(e),
                error_type=type(e).__name__,
                action="chat"
            )
            return f"Error: {str(e)}"
    
    def run(self, query: str, user_id: Optional[str] = None) -> dict:
        """Run the agent with logging."""
        response = self.chat(query, user_id=user_id)
        
        return {
            "query": query,
            "response": response,
            "request_id": self.request_id
        }


def main():
    """Example usage of AgentWithLogging."""
    
    print("=" * 60)
    print("AI Agent with Structured Logging")
    print("=" * 60)
    print()
    print("Note: Logs are output in JSON format")
    print("-" * 60)
    print()
    
    try:
        agent = AgentWithLogging()
        print("✓ Agent initialized successfully")
        print("✓ Structured logging enabled")
        print()
    except ValueError as e:
        print(f"✗ Error: {e}")
        return
    
    # Example queries with logging
    examples = [
        ("What is machine learning?", "user123"),
        ("Explain neural networks.", "user123"),
        ("Invalid query that might cause issues", "user456"),
    ]
    
    print("Running example queries with logging...")
    print("-" * 60)
    print()
    
    for i, (query, user_id) in enumerate(examples, 1):
        print(f"Query {i}: {query}")
        print(f"User ID: {user_id}")
        print()
        
        result = agent.run(query, user_id=user_id)
        print(f"Response: {result['response']}")
        print(f"Request ID: {result['request_id']}")
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()

