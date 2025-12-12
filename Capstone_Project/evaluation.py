"""
Evaluation Framework for Capstone Agent

This module provides evaluation and testing capabilities for the Capstone agent.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from capstone_agent import CapstoneAgent


class AgentEvaluator:
    """Evaluates agent performance and functionality."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize evaluator."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.test_results: List[Dict[str, Any]] = []
    
    def test_tool_use(self, agent: CapstoneAgent) -> Dict[str, Any]:
        """Test tool usage functionality."""
        print("Testing Tool Use...")
        
        test_cases = [
            ("Calculate 10 + 5", "calculator"),
            ("Count words in: Hello world", "text_processor"),
        ]
        
        results = []
        for query, expected_tool in test_cases:
            try:
                response = agent.chat(query)
                # Check if tool was used (simplified check)
                tool_used = expected_tool in response.lower() or "result" in response.lower()
                results.append({
                    "query": query,
                    "expected_tool": expected_tool,
                    "tool_used": tool_used,
                    "response": response[:100],
                    "passed": tool_used
                })
            except Exception as e:
                results.append({
                    "query": query,
                    "expected_tool": expected_tool,
                    "error": str(e),
                    "passed": False
                })
        
        passed = sum(1 for r in results if r.get("passed", False))
        total = len(results)
        
        return {
            "test_name": "Tool Use",
            "passed": passed,
            "total": total,
            "success_rate": f"{(passed/total)*100:.1f}%",
            "results": results
        }
    
    def test_memory(self, agent: CapstoneAgent) -> Dict[str, Any]:
        """Test memory functionality."""
        print("Testing Memory...")
        
        # Test short-term memory
        agent.chat("My name is Alice")
        response1 = agent.chat("What's my name?")
        short_term_works = "alice" in response1.lower()
        
        # Test long-term memory
        agent.chat("I like Python programming")
        response2 = agent.chat("What programming language do I like?")
        long_term_works = "python" in response2.lower()
        
        return {
            "test_name": "Memory",
            "short_term_memory": short_term_works,
            "long_term_memory": long_term_works,
            "passed": short_term_works and long_term_works,
            "results": [
                {"test": "Short-term memory", "passed": short_term_works},
                {"test": "Long-term memory", "passed": long_term_works}
            ]
        }
    
    def test_observability(self, agent: CapstoneAgent) -> Dict[str, Any]:
        """Test observability features."""
        print("Testing Observability...")
        
        # Run some queries
        agent.chat("Hello")
        agent.chat("Calculate 5 + 3")
        
        # Get metrics
        report = agent.get_observability_report()
        
        metrics_available = "metrics" in report
        metrics_have_data = report.get("metrics", {}).get("total_requests", 0) > 0
        
        return {
            "test_name": "Observability",
            "metrics_available": metrics_available,
            "metrics_have_data": metrics_have_data,
            "passed": metrics_available and metrics_have_data,
            "metrics": report.get("metrics", {})
        }
    
    def test_performance(self, agent: CapstoneAgent, num_queries: int = 5) -> Dict[str, Any]:
        """Test agent performance."""
        print(f"Testing Performance ({num_queries} queries)...")
        
        queries = [
            "What is AI?",
            "Calculate 10 * 5",
            "Count words in: Hello world",
            "Explain machine learning",
            "What is 100 / 4?",
        ]
        
        response_times = []
        successes = 0
        
        for query in queries[:num_queries]:
            start = time.time()
            try:
                response = agent.chat(query)
                response_time = time.time() - start
                response_times.append(response_time)
                successes += 1
            except Exception as e:
                response_times.append(None)
        
        avg_time = sum(t for t in response_times if t) / len([t for t in response_times if t]) if response_times else 0
        
        return {
            "test_name": "Performance",
            "average_response_time": f"{avg_time:.3f}s",
            "success_rate": f"{(successes/num_queries)*100:.1f}%",
            "response_times": response_times
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all evaluation tests."""
        print("=" * 60)
        print("Capstone Agent Evaluation")
        print("=" * 60)
        print()
        
        agent = CapstoneAgent(user_id="test_user")
        
        results = {
            "tool_use": self.test_tool_use(agent),
            "memory": self.test_memory(agent),
            "observability": self.test_observability(agent),
            "performance": self.test_performance(agent),
        }
        
        # Calculate overall score
        total_tests = 0
        passed_tests = 0
        
        for test_name, test_result in results.items():
            if isinstance(test_result, dict):
                if "passed" in test_result:
                    total_tests += 1
                    if test_result["passed"]:
                        passed_tests += 1
                elif "success_rate" in test_result:
                    # Performance test
                    total_tests += 1
                    if float(test_result["success_rate"].rstrip("%")) > 80:
                        passed_tests += 1
        
        results["overall"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%"
        }
        
        return results
    
    def print_report(self, results: Dict[str, Any]):
        """Print evaluation report."""
        print()
        print("=" * 60)
        print("Evaluation Report")
        print("=" * 60)
        print()
        
        for test_name, test_result in results.items():
            if test_name == "overall":
                continue
            
            print(f"{test_name.upper().replace('_', ' ')}:")
            if isinstance(test_result, dict):
                if "passed" in test_result:
                    status = "✓ PASSED" if test_result["passed"] else "✗ FAILED"
                    print(f"  Status: {status}")
                if "success_rate" in test_result:
                    print(f"  Success Rate: {test_result['success_rate']}")
                if "average_response_time" in test_result:
                    print(f"  Avg Response Time: {test_result['average_response_time']}")
            print()
        
        if "overall" in results:
            overall = results["overall"]
            print("Overall Score:")
            print(f"  Tests Passed: {overall['passed_tests']}/{overall['total_tests']}")
            print(f"  Success Rate: {overall['success_rate']}")
            print()


def main():
    """Run evaluation."""
    evaluator = AgentEvaluator()
    results = evaluator.run_all_tests()
    evaluator.print_report(results)
    
    # Save results
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Results saved to evaluation_results.json")


if __name__ == "__main__":
    main()

