# Google 5-Day AI Agents Intensive Course

A comprehensive repository containing summaries, code examples, and implementations from Google's 5-Day AI Agents Intensive Course.

## Overview

This repository documents the complete journey through Google's intensive 5-day course on building AI agents. Each day covers essential concepts and includes working code examples that demonstrate practical implementations.

## Course Structure

- **[Day 1: Introduction to AI Agents](Day1_Introduction_to_AI_Agents/)** - Fundamentals of AI agents, architecture, and Gemini integration
- **[Day 2: Agents with Tools and APIs](Day2_Agents_with_Tools_and_APIs/)** - Tool integration and API interactions
- **[Day 3: Memory and Context Engineering](Day3_Memory_and_Context/)** - Short-term and long-term memory systems
- **[Day 4: Agent Quality, Debugging, and Observability](Day4_Agent_Quality_and_Debugging/)** - Logging, tracing, and performance metrics
- **[Day 5: Prototype to Production](Day5_Prototype_to_Production/)** - Deployment strategies and multi-agent systems
- **[Capstone Project](Capstone_Project/)** - Comprehensive agent integrating multiple course concepts

## Prerequisites

- Python 3.9 or higher
- Google Cloud account (for Vertex AI and Gemini API access)
- API keys for:
  - Google Gemini API
  - Google Search API (optional, for Day 1 examples)
  - Google Cloud Platform (for Day 5 deployment)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd 5-day-agents
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   export GOOGLE_API_KEY="your-gemini-api-key"
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   ```

5. **Navigate to a specific day's directory:**
   ```bash
   cd Day1_Introduction_to_AI_Agents
   pip install -r requirements.txt
   python basic_agent.py
   ```

## Repository Contents

Each day's directory contains:
- `README.md` - Detailed explanation of concepts and examples
- Code examples demonstrating key concepts
- `requirements.txt` - Day-specific dependencies

## Course Summary

For a comprehensive overview of all course content, see [SUMMARY.md](SUMMARY.md).

## Capstone Project

The Capstone Project demonstrates the integration of multiple course concepts:
- Tool use (Day 2)
- Memory management (Day 3)
- Evaluation and quality metrics (Day 4)

See the [Capstone Project](Capstone_Project/) directory for details.

## Contributing

This repository serves as a learning resource. Feel free to:
- Report issues
- Suggest improvements
- Share your own implementations

## License

This repository is for educational purposes as part of Google's 5-Day AI Agents Intensive Course.

## Resources

- [Google Generative AI Documentation](https://ai.google.dev/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [LangChain Documentation](https://python.langchain.com/)

