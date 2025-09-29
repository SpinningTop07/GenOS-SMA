# GenOS-SMA
An agentic framework for automating Linux terminal workflows.

# GenOS-SMA: Multi-Agent Linux Command Orchestrator

An advanced AI-driven system that interprets natural language requests into secure and executable Linux commands using a multi-agent architecture. The system continuously learns from successful executions and incorporates risk assessment and auditing mechanisms.

---

## Features

- **Natural Language Understanding**: Converts plain English instructions into Linux commands  
- **Multi-Agent Design**: Specialized agents for comprehension, planning, auditing, examination, and execution  
- **Safety & Risk Analysis**: Built-in risk assessment and user approval for sensitive commands  
- **Knowledge Base**: Stores executed plans for faster future responses  
- **Web Search Integration**: Queries the web for context when needed  
- **Multi-Line Input Support**: Accepts detailed, multi-step requests  
- **Auditing & Logging**: Tracks all actions and generates execution summaries  

---

## Architecture

The system consists of five cooperating agents:

### 1. Comprehension Agent
- Analyzes user input and identifies intent, task type, complexity, requirements, and potential risks  
- Uses web search for additional context if needed  

### 2. Planning Agent
- Creates a step-by-step command plan based on comprehension results  
- Retrieves previous plans from the knowledge base if available  
- Revises plans in case of errors or failures  

### 3. Examiner Agent
- Evaluates command plans for potential risks  
- Categorizes commands by danger level  
- Requests user permission for high-risk operations  

### 4. Execution Agent
- Safely executes approved commands  
- Handles errors and timeouts gracefully  
- Adds executed plans to the knowledge base  

### 5. Auditor Agent
- Logs all stages of processing: comprehension, planning, analysis, and execution  
- Provides execution summaries and statistics  

---

## Installation

### Prerequisites
- Python 3.8+  
- Linux environment  
- Internet connection for web search  

### Required API Keys
1. **Groq API Key** – For AI language model access  
   - Sign up at [Groq Console](https://console.groq.com) and generate an API key  

2. **Tavily API Key** – For web search functionality  
   - Sign up at [Tavily](https://app.tavily.com) and get an API key  

### Setup
1. Clone the repository:
```bash
git clone https://github.com/SpinningTop07/GenOS-SMA.git
cd GenOS-SMA

# Installation and Setup

### Install dependencies

```bash
pip install -r requirements.txt
```

### Set environment variables

```bash
export GROQ_API_KEY="your_groq_api_key"
export TAVILY_API_KEY="your_tavily_api_key"
```

or create a `.env` file:

```bash
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### Start the orchestrator

```bash
python3 genosma.py
```

---

## User Interaction

The system supports two input modes:

* **Single-line requests**: Quick commands, e.g., `"Create a Python project scaffold"`
* **Multi-line requests**: Detailed instructions spanning multiple lines (finish input with `END`)

---

## Sample Commands

### Basic Tasks

```text
Set up a Node.js project with Express and MongoDB
Create directories for a React frontend project
Install Python packages for data analysis
```

### Dynamic / Context-Aware Tasks

```text
Generate a CSV of the top 10 trending GitHub repositories
Fetch latest Ubuntu security patches and save them
Create a backup script for user documents with timestamp
```

---

## Safety & Auditing

### Risk Levels

* **Low Risk**: File creation, directory navigation
* **Medium Risk**: Installing packages, editing non-critical files
* **High Risk**: System-level changes, modifying users or permissions, network configuration

### Protections

* Examiner Agent reviews all commands before execution
* User confirmation required for high-risk commands
* Timeout protection (5 minutes per command)
* Automatic error handling and replanning
* All actions logged in `execution_audit.json`

---

## Knowledge Base

The system stores previous successful command plans in `linux_command_plans.json`, allowing:

* Faster processing of repeated tasks
* Improved accuracy through past solutions
* Fuzzy matching to retrieve similar requests

---

## Configuration

### LLM Model

Modify the model configuration in the code:

```python
llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model="deepseek-r1-distill-llama-70b",
    temperature=0.3
)
```

### Risk Thresholds

Adjust risk thresholds in `ExaminerAgent.analyze_plan()` if needed.

---

## Contributing

1. Fork the repository
2. Create a feature branch:

```bash
git checkout -b feature/your-feature-name
```

3. Commit your changes:

```bash
git commit -m "Add new feature"
```

4. Push to your branch:

```bash
git push origin feature/your-feature-name
```

5. Open a Pull Request for review

---

## Troubleshooting

### API Key Errors

```text
Error: GROQ_API_KEY or TAVILY_API_KEY environment variable not set
```

* Ensure environment variables are correctly set
* Verify internet connectivity

### Execution / Search Failures

```text
Search failed: Timeout
```

* Check Tavily API key
* Verify network connection

---

## Logging & Auditing

* All stages logged in `execution_audit.json`
* Execution summary includes total commands, successes, failures, and error contexts

