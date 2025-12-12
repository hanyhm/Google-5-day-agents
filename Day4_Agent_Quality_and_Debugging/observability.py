"""
Comprehensive Observability for AI Agents

This example demonstrates observability implementation with logging,
tracing, and metrics collection.
"""

import os
import json
import time
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from datetime import datetime
from collections import defaultdict
import uuid


class MetricsCollector:
    """Collects and aggregates metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "total_response_time": 0.0,
            "total_tokens": 0,
            "errors_by_type": defaultdict(int),
        }
        self.request_times: List[float] = []
    
    def record_request(self, success: bool, response_time: float, tokens: int = 0, error_type: Optional[str] = None):
        """Record a request metric."""
        self.metrics["requests_total"] += 1
        self.metrics["total_response_time"] += response_time
        self.metrics["total_tokens"] += tokens
        self.request_times.append(response_time)
        
        if success:
            self.metrics["requests_success"] += 1
        else:
            self.metrics["requests_error"] += 1
            if error_type:
                self.metrics["errors_by_type"][error_type] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics."""
        total = self.metrics["requests_total"]
        if total == 0:
            return {"message": "No requests recorded"}
        
        avg_response_time = self.metrics["total_response_time"] / total
        success_rate = (self.metrics["requests_success"] / total) * 100
        
        sorted_times = sorted(self.request_times)
        p50 = sorted_times[len(sorted_times) // 2] if sorted_times else 0
        p95 = sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0
        
        return {
            "total_requests": total,
            "success_rate": f"{success_rate:.2f}%",
            "error_rate": f"{(100 - success_rate):.2f}%",
            "average_response_time_seconds": f"{avg_response_time:.3f}",
            "p50_response_time_seconds": f"{p50:.3f}",
            "p95_response_time_seconds": f"{p95:.3f}",
            "total_tokens": self.metrics["total_tokens"],
            "errors_by_type": dict(self.metrics["errors_by_type"])
        }


class TraceSpan:
    """Represents a span in a trace."""
    
    def __init__(self, name: str, parent_id: Optional[str] = None):
        """Initialize a trace span."""
        self.span_id = str(uuid.uuid4())
        self.parent_id = parent_id
        self.name = name
        self.start_time = time.time()
        self.end_time = None
        self.tags: Dict[str, Any] = {}
        self.logs: List[Dict[str, Any]] = []
    
    def finish(self):
        """Finish the span."""
        self.end_time = time.time()
    
    def add_tag(self, key: str, value: Any):
        """Add a tag to the span."""
        self.tags[key] = value
    
    def add_log(self, message: str, **kwargs):
        """Add a log entry to the span."""
        self.logs.append({
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        })
    
    def duration(self) -> float:
        """Get span duration in seconds."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary."""
        return {
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration(),
            "tags": self.tags,
            "logs": self.logs
        }


class Tracer:
    """Distributed tracing for agent operations."""
    
    def __init__(self):
        """Initialize tracer."""
        self.traces: List[Dict[str, Any]] = []
    
    def start_trace(self, operation: str, request_id: str) -> TraceSpan:
        """Start a new trace."""
        span = TraceSpan(name=operation)
        span.add_tag("request_id", request_id)
        return span
    
    def finish_trace(self, span: TraceSpan, trace_id: Optional[str] = None):
        """Finish a trace and store it."""
        span.finish()
        trace = {
            "trace_id": trace_id or str(uuid.uuid4()),
            "spans": [span.to_dict()],
            "timestamp": datetime.utcnow().isoformat()
        }
        self.traces.append(trace)
        return trace
    
    def get_recent_traces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent traces."""
        return self.traces[-limit:]


class ObservableAgent:
    """An AI agent with comprehensive observability."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize observable agent."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize observability components
        self.metrics = MetricsCollector()
        self.tracer = Tracer()
        self.request_id = None
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        return str(uuid.uuid4())
    
    def chat(self, message: str, user_id: Optional[str] = None) -> str:
        """Process message with full observability."""
        self.request_id = self._generate_request_id()
        
        # Start trace
        trace_span = self.tracer.start_trace("agent.chat", self.request_id)
        trace_span.add_tag("user_id", user_id or "anonymous")
        trace_span.add_tag("message_length", len(message))
        
        try:
            # Log LLM call start
            trace_span.add_log("Calling LLM", model="gemini-pro")
            
            start_time = time.time()
            response = self.model.generate_content(message)
            end_time = time.time()
            
            response_time = end_time - start_time
            response_text = response.text
            
            # Estimate tokens (rough approximation)
            estimated_tokens = len(message.split()) + len(response_text.split())
            
            # Record metrics
            self.metrics.record_request(
                success=True,
                response_time=response_time,
                tokens=estimated_tokens
            )
            
            # Finish trace
            trace_span.add_tag("success", True)
            trace_span.add_tag("response_length", len(response_text))
            trace_span.add_tag("response_time_seconds", response_time)
            trace_span.add_log("LLM call completed", tokens=estimated_tokens)
            
            self.tracer.finish_trace(trace_span, self.request_id)
            
            return response_text
        
        except Exception as e:
            # Record error metrics
            error_type = type(e).__name__
            self.metrics.record_request(
                success=False,
                response_time=time.time() - start_time,
                error_type=error_type
            )
            
            # Finish trace with error
            trace_span.add_tag("success", False)
            trace_span.add_tag("error", str(e))
            trace_span.add_tag("error_type", error_type)
            trace_span.add_log("Error occurred", error=str(e))
            
            self.tracer.finish_trace(trace_span, self.request_id)
            
            return f"Error: {str(e)}"
    
    def get_observability_report(self) -> Dict[str, Any]:
        """Get comprehensive observability report."""
        return {
            "metrics": self.metrics.get_stats(),
            "recent_traces": self.tracer.get_recent_traces(5)
        }
    
    def run(self, query: str, user_id: Optional[str] = None) -> dict:
        """Run agent with observability."""
        response = self.chat(query, user_id=user_id)
        
        return {
            "query": query,
            "response": response,
            "request_id": self.request_id
        }


def main():
    """Example usage of ObservableAgent."""
    
    print("=" * 60)
    print("AI Agent with Comprehensive Observability")
    print("=" * 60)
    print()
    
    try:
        agent = ObservableAgent()
        print("✓ Agent initialized successfully")
        print("✓ Observability enabled (metrics, tracing, logging)")
        print()
    except ValueError as e:
        print(f"✗ Error: {e}")
        return
    
    # Run example queries
    examples = [
        ("What is artificial intelligence?", "user1"),
        ("Explain machine learning.", "user1"),
        ("What are neural networks?", "user2"),
    ]
    
    print("Running example queries...")
    print("-" * 60)
    print()
    
    for i, (query, user_id) in enumerate(examples, 1):
        print(f"Query {i}: {query}")
        result = agent.run(query, user_id=user_id)
        print(f"Response: {result['response'][:100]}...")
        print()
    
    # Display observability report
    print("=" * 60)
    print("Observability Report")
    print("=" * 60)
    print()
    
    report = agent.get_observability_report()
    print("Metrics:")
    print(json.dumps(report["metrics"], indent=2))
    print()
    print(f"Recent Traces: {len(report['recent_traces'])}")
    print()


if __name__ == "__main__":
    main()

