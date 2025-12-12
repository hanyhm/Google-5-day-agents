"""
Multi-Agent System Implementation

This example demonstrates a multi-agent system with agent coordination,
communication, and task delegation.
"""

import os
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from enum import Enum
import json


class AgentRole(Enum):
    """Agent roles in the multi-agent system."""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYZER = "analyzer"
    WRITER = "writer"


class AgentMessage:
    """Message structure for agent-to-agent communication."""
    
    def __init__(self, from_agent: str, to_agent: str, content: str, message_type: str = "task"):
        """
        Initialize agent message.
        
        Args:
            from_agent: Sender agent name
            to_agent: Recipient agent name
            content: Message content
            message_type: Type of message (task, result, query)
        """
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.content = content
        self.message_type = message_type
        self.timestamp = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "from": self.from_agent,
            "to": self.to_agent,
            "content": self.content,
            "type": self.message_type
        }


class BaseAgent:
    """Base class for agents in the multi-agent system."""
    
    def __init__(self, name: str, role: AgentRole, api_key: Optional[str] = None):
        """
        Initialize base agent.
        
        Args:
            name: Agent name
            role: Agent role
            api_key: Google Gemini API key
        """
        self.name = name
        self.role = role
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        self.inbox: List[AgentMessage] = []
        self.capabilities = []
    
    def receive_message(self, message: AgentMessage):
        """Receive a message from another agent."""
        self.inbox.append(message)
    
    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process a received message and optionally respond."""
        raise NotImplementedError
    
    def send_message(self, to_agent: str, content: str, message_type: str = "task") -> AgentMessage:
        """Create and return a message to send."""
        return AgentMessage(
            from_agent=self.name,
            to_agent=to_agent,
            content=content,
            message_type=message_type
        )
    
    def think(self, prompt: str) -> str:
        """Use LLM for reasoning."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"


class CoordinatorAgent(BaseAgent):
    """Coordinator agent that manages other agents."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize coordinator agent."""
        super().__init__("Coordinator", AgentRole.COORDINATOR, api_key)
        self.capabilities = ["coordination", "task_delegation", "result_aggregation"]
        self.agents: Dict[str, BaseAgent] = {}
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent in the system."""
        self.agents[agent.name] = agent
        print(f"✓ Registered agent: {agent.name} ({agent.role.value})")
    
    def delegate_task(self, task: str, target_role: AgentRole) -> Optional[str]:
        """Delegate a task to an agent with specific role."""
        # Find agent with target role
        target_agent = None
        for agent in self.agents.values():
            if agent.role == target_role:
                target_agent = agent
                break
        
        if not target_agent:
            return f"No agent available with role: {target_role.value}"
        
        # Create and send task message
        message = self.send_message(target_agent.name, task, message_type="task")
        target_agent.receive_message(message)
        
        # Process the message
        response = target_agent.process_message(message)
        
        if response:
            return response.content
        return "Task completed but no response received"
    
    def coordinate_task(self, task: str) -> str:
        """Coordinate a complex task using multiple agents."""
        prompt = f"""You are coordinating a multi-agent system. Analyze this task and determine which agents should be involved:

Task: {task}

Available agents: {[agent.name for agent in self.agents.values()]}

Provide a coordination plan in JSON format with steps and agent assignments."""
        
        plan = self.think(prompt)
        
        # Simple execution (in production, parse plan and execute)
        results = []
        for agent_name, agent in self.agents.items():
            if agent.role != AgentRole.COORDINATOR:
                result = self.delegate_task(task, agent.role)
                results.append(f"{agent_name}: {result}")
        
        return "\n".join(results)
    
    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process messages received by coordinator."""
        if message.message_type == "result":
            # Aggregate results from agents
            return None
        return None


class ResearcherAgent(BaseAgent):
    """Researcher agent that gathers information."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize researcher agent."""
        super().__init__("Researcher", AgentRole.RESEARCHER, api_key)
        self.capabilities = ["information_gathering", "fact_checking"]
    
    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process research tasks."""
        if message.message_type == "task":
            prompt = f"""You are a research agent. Research and provide information about:

{message.content}

Provide a comprehensive research summary."""
            
            research_result = self.think(prompt)
            
            return self.send_message(
                message.from_agent,
                research_result,
                message_type="result"
            )
        return None


class AnalyzerAgent(BaseAgent):
    """Analyzer agent that processes and analyzes data."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize analyzer agent."""
        super().__init__("Analyzer", AgentRole.ANALYZER, api_key)
        self.capabilities = ["data_analysis", "pattern_recognition"]
    
    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process analysis tasks."""
        if message.message_type == "task":
            prompt = f"""You are an analysis agent. Analyze and provide insights about:

{message.content}

Provide detailed analysis and key findings."""
            
            analysis_result = self.think(prompt)
            
            return self.send_message(
                message.from_agent,
                analysis_result,
                message_type="result"
            )
        return None


class WriterAgent(BaseAgent):
    """Writer agent that creates written content."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize writer agent."""
        super().__init__("Writer", AgentRole.WRITER, api_key)
        self.capabilities = ["content_creation", "writing"]
    
    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process writing tasks."""
        if message.message_type == "task":
            prompt = f"""You are a writing agent. Create well-written content about:

{message.content}

Provide clear, engaging written content."""
            
            writing_result = self.think(prompt)
            
            return self.send_message(
                message.from_agent,
                writing_result,
                message_type="result"
            )
        return None


class MultiAgentSystem:
    """Multi-agent system coordinator."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize multi-agent system."""
        self.coordinator = CoordinatorAgent(api_key)
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        # Register agents
        self.coordinator.register_agent(ResearcherAgent(api_key))
        self.coordinator.register_agent(AnalyzerAgent(api_key))
        self.coordinator.register_agent(WriterAgent(api_key))
    
    def execute_task(self, task: str) -> str:
        """Execute a task using the multi-agent system."""
        return self.coordinator.coordinate_task(task)
    
    def delegate_to_role(self, task: str, role: AgentRole) -> str:
        """Delegate a task to a specific agent role."""
        return self.coordinator.delegate_task(task, role)


def main():
    """Example usage of MultiAgentSystem."""
    
    print("=" * 60)
    print("Multi-Agent System")
    print("=" * 60)
    print()
    
    try:
        system = MultiAgentSystem()
        print("✓ Multi-agent system initialized")
        print()
    except ValueError as e:
        print(f"✗ Error: {e}")
        return
    
    # Example tasks
    tasks = [
        ("Research task", "Research the history of artificial intelligence"),
        ("Analysis task", "Analyze the benefits and challenges of AI agents"),
        ("Writing task", "Write a summary about multi-agent systems"),
    ]
    
    print("Running example tasks...")
    print("-" * 60)
    print()
    
    for task_type, task in tasks:
        print(f"Task Type: {task_type}")
        print(f"Task: {task}")
        print()
        
        # Determine which agent to use
        if "research" in task_type.lower():
            result = system.delegate_to_role(task, AgentRole.RESEARCHER)
        elif "analysis" in task_type.lower():
            result = system.delegate_to_role(task, AgentRole.ANALYZER)
        elif "writing" in task_type.lower():
            result = system.delegate_to_role(task, AgentRole.WRITER)
        else:
            result = system.execute_task(task)
        
        print(f"Result: {result}")
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()

