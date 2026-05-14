"""Pattern #5: Parallel Execution - Multiple agents work simultaneously"""

import os
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Load env
_base = os.path.dirname(os.path.abspath(__file__))
_project = os.path.dirname(os.path.dirname(_base))
load_dotenv(os.path.join(_project, '.env'), override=True)

API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_BASE = os.environ.get("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = "llama-3.1-8b-instant"


def call_llm(prompt: str, system: str = None, max_tokens: int = 400) -> str:
    """Direct Groq API call"""
    if not API_KEY:
        return "Error: No API key"
    
    url = f"{API_BASE}/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    try:
        resp = requests.post(url, headers=headers, json={
            "model": MODEL, "messages": messages, "temperature": 0.3, "max_tokens": max_tokens
        }, timeout=60)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"Error: {resp.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


class ParallelAgents:
    """Pattern #5: Execute multiple agents in parallel for speed"""
    
    def __init__(self):
        self.role_prompts = {
            "research": "You are a research expert. Find accurate, detailed information.",
            "writer": "You are a professional writer. Create clear, engaging content.",
            "analyst": "You are a data analyst. Analyze data and extract insights.",
            "coder": "You are a programmer. Write clean, correct code.",
            "reviewer": "You are a reviewer. Provide feedback and improvements.",
        }
    
    def execute_parallel(self, task: str, roles: List[str]) -> Dict[str, Any]:
        """Execute multiple agents in parallel"""
        
        def run_agent(role):
            system = self.role_prompts.get(role, f"You are a {role} specialist.")
            result = call_llm(f"Task: {task}\n\nYour role: {role}", system=system, max_tokens=300)
            return {"role": role, "result": result}
        
        results = {}
        with ThreadPoolExecutor(max_workers=len(roles)) as executor:
            futures = {executor.submit(run_agent, role): role for role in roles}
            for future in as_completed(futures):
                role = futures[future]
                try:
                    results[role] = future.result()
                except Exception as e:
                    results[role] = {"role": role, "result": f"Error: {str(e)}"}
        
        return results
    
    def process(self, task: str) -> str:
        """Auto-detect needed parallel agents and execute"""
        
        # Analyze task to determine roles
        analysis = call_llm(f"""What roles are needed for this task? Choose from: research, writer, analyst, coder, reviewer

Task: {task}

Respond with comma-separated roles:""", max_tokens=100)
        
        # Parse roles
        roles = [r.strip().lower() for r in analysis.split(',')][:4]  # Max 4
        if not roles or "Error" in analysis:
            roles = ["research", "writer"]  # Default
        
        # Execute in parallel
        results = self.execute_parallel(task, roles)
        
        # Format output
        output = f"⚡ **Parallel Execution** ({len(roles)} agents)\n\n"
        for role, data in results.items():
            output += f"**{data['role'].upper()}:**\n{data['result'][:200]}...\n\n"
        
        return output


def main():
    """Test Pattern #5"""
    print("=" * 60)
    print("PATTERN #5: PARALLEL EXECUTION")
    print("=" * 60)
    
    pa = ParallelAgents()
    
    # Test 1: Simple parallel
    print("\n🔹 Test 1: Research + Write in parallel")
    result = pa.execute_parallel("Explain AI to a beginner", ["research", "writer"])
    for role, data in result.items():
        print(f"  {role}: {data['result'][:100]}...")
    
    # Test 2: Auto-detect
    print("\n🔹 Test 2: Auto-detect parallel")
    result = pa.process("Create a blog post about Python programming")
    print(f"Result: {result[:300]}...")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()