# GenOS-SMA
An agentic framework for automating Linux terminal workflows.



# Linux Multi-Agent Command Orchestrator

An AI-driven system that interprets user instructions in plain English and executes Linux commands safely through a coordinated multi-agent framework.

## Core Capabilities

- **Natural Language Understanding**: Translates user requests into structured Linux commands.  
- **Agent-Based Workflow**: Four dedicated agents for comprehension, planning, auditing, and execution.  
- **Command Safety**: Evaluates risk levels and requests user approval for sensitive operations.  
- **Knowledge Retention**: Stores successful command plans for future reuse.  
- **Online Reference Search**: Fetches current instructions and best practices when required.  
- **Error Handling**: Automatically adapts plans when commands fail.  
- **Execution Audit**: Maintains logs of executed commands for transparency.

---

## System Components

### Comprehension Agent
- Parses user instructions and determines the intended task.  
- Assesses complexity and prerequisites.  
- Suggests searches for missing context or dependencies.

### Planning Agent
- Constructs step-by-step command sequences.  
- Checks the knowledge base for similar past tasks.  
- Generates commands optimized for reliability and correctness.

### Auditor Agent
- Reviews the planned commands for potential hazards.  
- Classifies commands into risk tiers: low, medium, or high.  
- Requests user confirmation for commands that may alter the system.

### Execution Agent
- Runs approved commands with proper monitoring.  
- Tracks success, errors, and timeouts.  
- Feeds failures back to the Planning Agent for automatic replanning.

---

## Getting Started

### Requirements
- Linux environment  
- Python 3.8+  
- Internet access for search functionality  

### Required API Keys
- **Groq API Key**: Provides AI model access.  
- **Tavily API Key**: Enables search for installation guides or latest information.  

### Setup Steps
1. **Clone the repository**
```bash
git clone https://github.com/YourUsername/linux-mas.git
cd linux-mas
Install dependencies

bash
Copy code
pip install -r requirements.txt
Set environment variables

bash
Copy code
export GROQ_API_KEY="your_groq_api_key"
export TAVILY_API_KEY="your_tavily_api_key"
Start the orchestrator

bash
Copy code
python3 orchestrator.py
User Interaction
The system supports two modes of input:

Single-line requests: Quick commands like "Create a folder project".

Multi-line requests: Detailed instructions spanning multiple lines (finish input with END).

Sample Commands
Basic Tasks

text
Copy code
Create a folder structure for a Python project
Install Node.js and npm
Set up a virtual environment with required packages
Dynamic Content

text
Copy code
Generate a file with today’s stock prices
Fetch and save the top 5 trending repositories from GitHub
Create a summary of current AI news articles
Safety & Auditing
The Auditor Agent evaluates the command plan before execution:

Risk Levels
Low Risk: File creation, directory navigation

Medium Risk: Installing packages, editing non-critical files

High Risk: Modifying system directories, changing network configuration, altering users/permissions

Protections
User confirmation for high-risk commands

Timeout protection (5 minutes per command)

Automatic error handling and replanning

Logs all executed commands in command_audit_log.json

Knowledge Base
The system stores previous successful plans in linux_command_history.json, allowing:

Faster processing of repeated tasks

Improved accuracy through past solutions

Fuzzy matching to retrieve similar requests

Configuration
Model Adjustments
Customize AI behavior by modifying:

python
Copy code
llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model="deepseek-r1-distill-llama-70b",
    temperature=0.25
)
Risk Tuning
Adjust the thresholds for command categorization in AuditorAgent.examine_plan() if needed.

Contributing
Fork the repository

Create a new branch

bash
Copy code
git checkout -b feature/your-feature-name
Commit your changes

bash
Copy code
git commit -m "Add new feature"
Push to your branch

bash
Copy code
git push origin feature/your-feature-name
Open a pull request for review

Troubleshooting
API Key Errors

text
Copy code
Error: GROQ_API_KEY environment variable not set
Ensure the environment variables are set correctly.

Confirm that internet access is available.

Search Failures

text
Copy code
Search failed: Timeout
Check the Tavily API key.

Verify your network connection.

