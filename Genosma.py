import os
import json
import re
import subprocess
from typing import List, Dict, Any
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import AgentAction, AgentFinish
from langchain.callbacks.base import BaseCallbackHandler
import difflib

# -------------------------
# Knowledge Base
# -------------------------
KB_FILE = "linux_command_plans.json"

def load_kb():
    if not os.path.exists(KB_FILE):
        return []
    with open(KB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_kb(kb_data):
    with open(KB_FILE, "w") as f:
        json.dump(kb_data, f, indent=2)

def add_to_kb(query, plan):
    kb = load_kb()
    kb.append({"query": query, "plan": plan})
    save_kb(kb)

def find_similar_plan(query, threshold=0.6):
    kb = load_kb()
    if not kb:
        return None
    queries = [item["query"] for item in kb]
    match = difflib.get_close_matches(query, queries, n=1, cutoff=threshold)
    if match:
        for item in kb:
            if item["query"] == match[0]:
                return item["plan"]
    return None

# -------------------------
# LLM and Search Tool
# -------------------------
llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model="deepseek-r1-distill-llama-70b",
    temperature=0.3
)

tavily_search = TavilySearchResults(
    api_key=os.environ.get("TAVILY_API_KEY"),
    max_results=10
)

# -------------------------
# Comprehension Agent
# -------------------------
class ComprehensionAgent:
    def __init__(self, llm, search_tool):
        self.llm = llm
        self.search_tool = search_tool
        
    def analyze(self, user_input: str) -> Dict[str, Any]:
        search_prompt = f"""
        Analyze this user request: "{user_input}"
        Decide if additional information search is needed. If yes, provide search terms. If not, respond "NO_SEARCH_NEEDED".
        """
        search_decision = self.llm.invoke(search_prompt).content.strip()
        search_results = ""
        if search_decision != "NO_SEARCH_NEEDED":
            try:
                results = self.search_tool.run(search_decision)
                search_results = f"Search results: {results}"
            except Exception as e:
                search_results = f"Search failed: {str(e)}"
        comprehension_prompt = f"""
        Analyze this request: "{user_input}"
        {search_results}
        Return JSON:
        {{
            "intent": "user intent description",
            "task_type": "installation|file_management|system_config|development|other",
            "complexity": "simple|moderate|complex",
            "requirements": ["list of dependencies"],
            "risks": ["list of potential risks"]
        }}
        """
        response = self.llm.invoke(comprehension_prompt).content.strip()
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("No JSON found in response")
        except Exception:
            return {
                "intent": user_input,
                "task_type": "other",
                "complexity": "simple",
                "requirements": [],
                "risks": []
            }

# -------------------------
# Planning Agent
# -------------------------
class PlanningAgent:
    def __init__(self, llm, search_tool):
        self.llm = llm
        self.search_tool = search_tool
        
    def create_plan(self, user_input: str, comprehension_data: Dict[str, Any], error_context: Dict[str, Any] = None) -> Dict[str, Any]:
        existing_plan = find_similar_plan(user_input)
        if existing_plan:
            print("Retrieved existing plan from KB")
            return existing_plan

        search_context = ""
        if comprehension_data.get("task_type") == "installation" or comprehension_data.get("complexity") == "complex":
            search_query = f"linux commands {comprehension_data.get('intent', user_input)}"
            try:
                search_results = self.search_tool.run(search_query)
                search_context = f"Reference: {search_results}"
            except Exception as e:
                search_context = f"Search failed: {str(e)}"

        planning_prompt = f"""
        Create a step-by-step Linux command plan for: "{user_input}"
        Comprehension: {json.dumps(comprehension_data)}
        {search_context}
        Return JSON: {{
            "steps": ["command1", "command2"],
            "description": "plan description",
            "estimated_time": "estimated duration",
            "reversible": true/false
        }}
        """
        if error_context:
            planning_prompt += f"""
            Previous command failed: {error_context['command']}
            Error: {error_context['error']}
            Remaining steps: {error_context['remaining_steps']}
            Return revised JSON plan.
            """
        response = self.llm.invoke(planning_prompt).content.strip()
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("No JSON found in response")
        except Exception:
            return {"steps": [], "description": "Failed to create plan", "estimated_time": "unknown", "reversible": False}

# -------------------------
# Examiner / Auditor Agent
# -------------------------
class ExaminerAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def analyze_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        commands = plan.get("steps", [])
        prompt = f"""
        Analyze Linux commands for potential risks: {json.dumps(commands)}
        Classify risk: high, medium, low.
        Return JSON:
        {{
            "risk_level": "high|medium|low",
            "requires_permission": true/false,
            "dangerous_commands": ["list of dangerous commands"],
            "safe_commands": ["list of safe commands"],
            "recommendation": "approve|request_permission|deny",
            "warning_message": "optional warning"
        }}
        """
        response = self.llm.invoke(prompt).content.strip()
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("No JSON found in response")
        except Exception:
            return {
                "risk_level": "high",
                "requires_permission": True,
                "dangerous_commands": commands,
                "safe_commands": [],
                "recommendation": "request_permission",
                "warning_message": "Analysis failed"
            }

    def request_user_permission(self, plan, analysis):
        if analysis["recommendation"] == "deny":
            return False
        elif analysis["recommendation"] == "approve":
            return True
        else:
            while True:
                resp = input("Execute these commands? (y/n): ").strip().lower()
                if resp in ["y", "yes"]:
                    return True
                elif resp in ["n", "no"]:
                    return False

# -------------------------
# Execution Agent
# -------------------------
class ExecutionAgent:
    def execute(self, plan: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        steps = plan.get("steps", [])
        results = []
        for idx, cmd in enumerate(steps):
            print(f"[{idx+1}/{len(steps)}] Executing: {cmd}")
            try:
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True, timeout=300)
                results.append({"command": cmd, "status": "success", "stdout": proc.stdout, "stderr": proc.stderr})
                add_to_kb(user_query, plan)
            except subprocess.CalledProcessError as e:
                return {"status": "failed", "results": results, "error_context": {"command": cmd, "error": str(e), "remaining_steps": steps[idx+1:]}}
            except subprocess.TimeoutExpired:
                return {"status": "timeout", "results": results, "error_context": {"command": cmd, "error": "Timeout", "remaining_steps": steps[idx+1:]}}
        return {"status": "success", "results": results}

# -------------------------
# Auditor Agent
# -------------------------
class AuditorAgent:
    def __init__(self, log_file="execution_audit.json"):
        self.log_file = log_file

    def log(self, stage: str, data: Dict[str, Any]):
        logs = []
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append({"stage": stage, "data": data})
        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=2)

    def summary(self, execution_results: Dict[str, Any]):
        summary = {
            "total_commands": execution_results.get("total_commands", 0),
            "executed_commands": execution_results.get("executed_commands", 0),
            "success_count": sum(1 for r in execution_results.get("results", []) if r["status"]=="success"),
            "failed_count": sum(1 for r in execution_results.get("results", []) if r["status"]!="success"),
            "error_context": execution_results.get("error_context")
        }
        print("\nExecution Summary:")
        print(json.dumps(summary, indent=2))
        return summary

# -------------------------
# Multi-Agent Orchestrator
# -------------------------
class MultiAgentSystem:
    def __init__(self):
        self.comprehend = ComprehensionAgent(llm, tavily_search)
        self.planner = PlanningAgent(llm, tavily_search)
        self.examiner = ExaminerAgent(llm)
        self.executor = ExecutionAgent()
        self.auditor = AuditorAgent()

    def get_multiline_input(self, prompt="Enter request (type 'END' to finish):"):
        print(prompt)
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        return "\n".join(lines)

    def process_request(self, user_input: str):
        print("Analyzing request...")
        comprehension = self.comprehend.analyze(user_input)
        self.auditor.log("comprehension", comprehension)

        print("Generating plan...")
        plan = self.planner.create_plan(user_input, comprehension)
        self.auditor.log("plan_creation", plan)

        if not plan.get("steps"):
            print("No plan could be created.")
            return

        print("Examining plan for risks...")
        analysis = self.examiner.analyze_plan(plan)
        self.auditor.log("plan_analysis", analysis)

        if analysis.get("requires_permission", True):
            if not self.examiner.request_user_permission(plan, analysis):
                print("Execution cancelled by user.")
                return

        print("Executing plan...")
        execution = self.executor.execute(plan, user_input)
        self.auditor.log("execution", execution)

        self.auditor.summary(execution)

# -------------------------
# Main
# -------------------------
def main():
    if not os.environ.get("GROQ_API_KEY") or not os.environ.get("TAVILY_API_KEY"):
        print("Missing API keys.")
        return

    system = MultiAgentSystem()
    print("Choose input method:")
    print("1) Single line")
    print("2) Multi-line")

    choice = input("Enter choice: ").strip()
    if choice == "1":
        user_input = input("Enter your request: ").strip()
    elif choice == "2":
        user_input = system.get_multiline_input()
    else:
        print("Invalid choice")
        return

    if user_input:
        system.process_request(user_input)
    else:
        print("No input provided")

if __name__ == "__main__":
    main()
