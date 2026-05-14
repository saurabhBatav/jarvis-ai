"""Pattern #3: Agent Handoffs - Dynamic task transfer between specialized agents"""

import os
import requests
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

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
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    data = {"model": MODEL, "messages": messages, "temperature": 0.3, "max_tokens": max_tokens}
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"Error: {resp.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


class AgentHandoffs:
    """Implements Pattern #3: Agent Handoffs - dynamic agent-to-agent task transfer"""
    
    def __init__(self):
        self.handoff_history: List[Dict[str, Any]] = []
        self.agents = {
            "research": "You are a research expert. Find accurate, detailed information.",
            "writer": "You are a professional writer. Create clear, engaging content.",
            "analyst": "You are a data analyst. Extract insights and patterns.",
            "technical": "You are a technical specialist. Solve technical problems.",
        }
    
    def analyze_and_route(self, task: str) -> Dict[str, Any]:
        """Analyze task and decide which agent to route to"""
        
        prompt = f"""Analyze this task and determine the best specialist to handle it.

Task: {task}

Choose from: research, writer, analyst, technical

Respond in format:
AGENT: [best agent]
REASON: [why this agent]"""

        result = call_llm(prompt, max_tokens=200)
        
        agent = "research"  # default
        for key in self.agents.keys():
            if key in result.lower():
                agent = key
                break
        
        return {"agent": agent, "analysis": result}
    
    def process(self, task: str) -> str:
        """Process task with automatic handoff routing"""
        
        route = self.analyze_and_route(task)
        target_agent = route["agent"]
        system = self.agents[target_agent]
        
        result = call_llm(task, system=system, max_tokens=500)
        
        self.handoff_history.append({
            "task": task,
            "routed_to": target_agent,
            "result": result,
        })
        
        return f"🔄 **Agent Handoffs Pattern**\n\n[Routed to: {target_agent}]\n\n{result}"
    
    def llm_driven_handoff(self, task: str) -> str:
        """LLM decides when to handoff to another agent"""
        
        # First agent tries to handle
        first_result = call_llm(task, system=self.agents["research"], max_tokens=300)
        
        # Check if needs handoff
        check_prompt = f"""Original task: {task}
Current result: {first_result}

Does this need to be handed off to another specialist? (writer/analyst/technical)
Respond YES or NO and why."""
        
        needs_handoff = call_llm(check_prompt, max_tokens=100)
        
        if "YES" in needs_handoff.upper():
            for agent_type, system in self.agents.items():
                if agent_type in needs_handoff.upper():
                    improved = call_llm(f"Improve based on: {first_result}\n\nTask: {task}", 
                                       system=system, max_tokens=400)
                    return f"🔄 Handoff to {agent_type}:\n\n{improved}"
        
        return f"🔄 LLM-driven handoff:\n\n{first_result}"
    
    def programmatic_handoff(self, task: str, target: str) -> str:
        """Programmatic handoff to specific agent"""
        
        if target not in self.agents:
            return f"Unknown agent: {target}. Available: {list(self.agents.keys())}"
        
        system = self.agents[target]
        result = call_llm(task, system=system, max_tokens=500)
        
        return f"🔄 Programmatic handoff to {target}:\n\n{result}"
    
    def handoff_chain(self, tasks: List[str]) -> List[Dict[str, Any]]:
        """Execute chain of handoffs"""
        
        results = []
        context = ""
        
        for i, task in enumerate(tasks):
            if i == 0:
                result = call_llm(task, system=self.agents["research"], max_tokens=400)
            else:
                result = call_llm(f"Previous: {context}\n\nTask: {task}", 
                                system=self.agents["writer"], max_tokens=400)
            
            results.append({"step": i+1, "task": task, "result": result})
            context = result[:200]
        
        return results
    
    def get_handoff_stats(self) -> Dict[str, Any]:
        return {
            "total_handoffs": len(self.handoff_history),
            "agents_available": list(self.agents.keys()),
        }


def main():
    print("=" * 60)
    print("PATTERN #3: AGENT HANDOFFS")
    print("=" * 60)
    
    handoffs = AgentHandoffs()
    
    print("\n🔹 Test 1: Auto routing")
    result = handoffs.process("Explain quantum computing")
    print(f"Result: {result[:300]}...")
    
    print("\n🔹 Test 2: Programmatic handoff")
    result = handoffs.programmatic_handoff("Write a story", "writer")
    print(f"Result: {result[:300]}...")
    
    print("\n🔹 Test 3: Handoff chain")
    chain = handoffs.handoff_chain([
        "Research Python async",
        "Write summary"
    ])
    for c in chain:
        print(f"Step {c['step']}: {c['result'][:100]}...")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()