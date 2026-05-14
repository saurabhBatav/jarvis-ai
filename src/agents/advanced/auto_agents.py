"""AutoAgents Pattern - REAL multi-agent system using direct API calls"""

import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any

current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path, override=True)

API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_BASE = os.environ.get("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = "llama-3.1-8b-instant"


def call_llm(prompt: str, system: str = None, max_tokens: int = 500) -> str:
    """Direct Groq API call"""
    if not API_KEY:
        return "Error: No API key"
    
    url = f"{API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"Error: {resp.status_code} - {resp.text[:100]}"
    except Exception as e:
        return f"Error: {str(e)}"


class AutoAgents:
    """
    AutoAgents pattern - REAL multi-agent system using direct API calls
    - Each agent is a separate LLM call with distinct system prompt
    - Real parallel execution (threading)
    """
    
    def __init__(self):
        self.agents = []
    
    def analyze_task_complexity(self, task: str) -> dict:
        """Analyze task to determine agent count and workflow"""
        
        prompt = f"""Analyze this task and determine:
1. How many agents needed (1-4)
2. Best workflow (sequential, parallel, orchestrator-workers, evaluator-optimiser)
3. Role for each agent

Task: {task}

Respond in EXACT format:
AGENTS: [number]
WORKFLOW: [workflow type]
ROLES: [role1, role2, ...]"""

        result = call_llm(prompt, max_tokens=200)
        
        analysis = {"agents": 2, "workflow": "sequential", "roles": ["researcher", "writer"]}
        
        for line in result.split('\n'):
            if line.startswith('AGENTS:'):
                try:
                    analysis['agents'] = int(line.split(':')[1].strip())
                except: pass
            elif line.startswith('WORKFLOW:'):
                wf = line.split(':')[1].strip().lower()
                if wf in ['sequential', 'parallel', 'orchestrator-workers', 'evaluator-optimiser']:
                    analysis['workflow'] = wf
            elif line.startswith('ROLES:'):
                roles = line.split(':')[1].strip()
                analysis['roles'] = [r.strip() for r in roles.split(',')]
        
        return analysis
    
    def _get_agent_prompt(self, role: str) -> str:
        """Get system prompt for specific agent role"""
        role_prompts = {
            "researcher": "You are a research expert. Find accurate, detailed information.",
            "writer": "You are a professional writer. Create clear, engaging content.",
            "editor": "You are an editor. Review and improve content quality.",
            "analyst": "You are a data analyst. Extract insights from information.",
            "coder": "You are a programmer. Write clean, correct code.",
            "planner": "You are a planner. Organize tasks strategically.",
            "coordinator": "You are a coordinator. Delegate tasks and synthesize results.",
        }
        return role_prompts.get(role.lower(), f"You are a {role} specialist.")
    
    def process_sequential(self, task: str, roles: List[str]) -> str:
        """Execute with sequential workflow - each agent passes output to next"""
        
        results = []
        context = task
        
        for role in roles:
            system = self._get_agent_prompt(role)
            prompt = f"Task: {context}\n\nComplete your part of this task as a {role}."
            result = call_llm(prompt, system=system, max_tokens=400)
            results.append(f"[{role.upper()}]\n{result}")
            context = result  # Pass to next agent
        
        return "Sequential Workflow:\n\n" + "\n\n--- Next Agent ---\n\n".join(results)
    
    def process_parallel(self, task: str, roles: List[str]) -> str:
        """Execute with parallel workflow - all agents work simultaneously"""
        
        import concurrent.futures
        
        def call_agent(role):
            system = self._get_agent_prompt(role)
            prompt = f"Task: {task}\n\nAs a {role}, complete your part of this task."
            result = call_llm(prompt, system=system, max_tokens=300)
            return f"[{role.upper()}]\n{result}"
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(call_agent, roles))
        
        return "Parallel Workflow:\n\n" + "\n\n---\n\n".join(results)
    
    def process_orchestrator(self, task: str, roles: List[str]) -> str:
        """Orchestrator decides delegate, workers execute, coordinator synthesizes"""
        
        # Step 1: Coordinator analyzes and delegates
        coord_system = "You are a coordinator. Analyze the task and assign to specialists."
        coord_prompt = f"Task: {task}\n\nAnalyze and break down into subtasks for: {', '.join(roles)}\n\nGive specific subtask for each role."
        delegation = call_llm(coord_prompt, system=coord_system, max_tokens=400)
        
        # Step 2: Workers execute in parallel
        worker_system = "You are a specialist. Execute your assigned task carefully."
        worker_prompt = f"Overall task: {task}\n\nYour delegation: {delegation}\n\nComplete your part."
        workers_result = call_llm(worker_prompt, system=worker_system, max_tokens=500)
        
        # Step 3: Coordinator synthesizes
        synth_system = "You are a coordinator. Synthesize multiple inputs into coherent output."
        synth_prompt = f"Original task: {task}\n\nWorker results: {workers_result}\n\nSynthesize into final answer."
        final = call_llm(synth_prompt, system=synth_system, max_tokens=400)
        
        return f"Orchestrator-Workers:\n\n{delegation}\n\n---\n\n{final}"
    
    def process_evaluator_optimiser(self, task: str, roles: List[str]) -> str:
        """Generate solution, then evaluate and improve"""
        
        # Generate
        gen_system = "You are a generator. Create a solution for the given task."
        gen_prompt = f"Task: {task}\n\nGenerate a solution."
        solution = call_llm(gen_prompt, system=gen_system, max_tokens=400)
        
        # Evaluate and improve
        eval_system = "You are an evaluator. Review and improve the solution."
        eval_prompt = f"Original task: {task}\n\nSolution to evaluate:\n{solution}\n\nReview and improve if needed."
        improved = call_llm(eval_prompt, system=eval_system, max_tokens=400)
        
        return f"Evaluator-Optimiser:\n\n=== Generated ===\n{solution}\n\n=== Improved ===\n{improved}"
    
    def process(self, task: str) -> str:
        """Process task with real multi-agent system"""
        
        # Analyze
        analysis = self.analyze_task_complexity(task)
        
        workflow = analysis['workflow']
        roles = analysis['roles'][:analysis['agents']]
        
        if not roles:
            roles = ["assistant"]
        
        # Execute with appropriate workflow
        if workflow == 'sequential':
            return "🔧 " + self.process_sequential(task, roles)
        elif workflow == 'parallel':
            return "🔧 " + self.process_parallel(task, roles)
        elif workflow == 'orchestrator-workers':
            return "🔧 " + self.process_orchestrator(task, roles)
        elif workflow == 'evaluator-optimiser':
            return "🔧 " + self.process_evaluator_optimiser(task, roles)
        else:
            return call_llm(task)


def main():
    print("=" * 60)
    print("PATTERN #2: AUTOAGENTS (REAL MULTI-AGENT)")
    print("=" * 60)
    
    auto = AutoAgents()
    
    test_cases = [
        "Write a haiku about spring",
        "Research AI trends and summarize",
        "Explain quantum computing simply",
    ]
    
    for i, task in enumerate(test_cases, 1):
        print(f"\n🔹 Test {i}: {task}")
        print("-" * 40)
        
        result = auto.process(task)
        print(f"Result: {result[:500]}...")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()