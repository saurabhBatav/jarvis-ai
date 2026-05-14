"""Pattern #5: Parallel Execution - Multiple agents work simultaneously"""

import os
import requests
import time
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


# ============================================================
# 📊 VERBOSE LOGGING
# ============================================================
class Logger:
    @staticmethod
    def step(msg):
        print(f"  📍 {msg}")
    
    @staticmethod
    def agent_start(role):
        print(f"    🤖 Starting {role}...")
    
    @staticmethod
    def agent_done(role, time_taken):
        print(f"    ✓ {role} done ({time_taken:.2f}s)")
    
    @staticmethod
    def result(role, preview):
        print(f"    📝 {role}: {preview[:80]}...")


def call_llm(prompt: str, system: str = None, max_tokens: int = 600) -> str:
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
        """Execute multiple agents in parallel with verbose logging"""
        
        Logger.step(f"Executing {len(roles)} agents in parallel: {', '.join(roles)}")
        
        def run_agent(role):
            start = time.time()
            Logger.agent_start(role)
            
            system = self.role_prompts.get(role, f"You are a {role} specialist.")
            result = call_llm(f"Task: {task}\n\nYour role: {role}", system=system, max_tokens=600)
            
            elapsed = time.time() - start
            Logger.agent_done(role, elapsed)
            Logger.result(role, result)
            
            return {"role": role, "result": result, "time": elapsed}
        
        results = {}
        start_total = time.time()
        
        with ThreadPoolExecutor(max_workers=len(roles)) as executor:
            futures = {executor.submit(run_agent, role): role for role in roles}
            for future in as_completed(futures):
                role = futures[future]
                try:
                    results[role] = future.result()
                except Exception as e:
                    results[role] = {"role": role, "result": f"Error: {str(e)}", "time": 0}
        
        total_time = time.time() - start_total
        Logger.step(f"All agents completed in {total_time:.2f}s")
        
        return results
    
    def process(self, task: str) -> str:
        """Auto-detect needed parallel agents and execute"""
        
        print("\n" + "="*50)
        print("⚡ PARALLEL EXECUTION PATTERN")
        print("="*50)
        
        # Analyze task to determine roles
        Logger.step("Analyzing task to determine roles...")
        analysis = call_llm(f"""What roles are needed for this task? Choose from: research, writer, analyst, coder, reviewer

Task: {task}

Respond with comma-separated roles:""", max_tokens=100)
        
        # Parse roles
        roles = [r.strip().lower() for r in analysis.split(',')][:4]
        if not roles or "Error" in analysis:
            roles = ["research", "analyst", "writer"]  # Default
        
        Logger.step(f"Selected roles: {', '.join(roles)}")
        
        # Execute in parallel
        results = self.execute_parallel(task, roles)
        
        # Format detailed output
        output = f"\n{'='*50}"
        output += f"\n⚡ PARALLEL EXECUTION RESULTS ({len(roles)} agents)"
        output += f"\n{'='*50}\n\n"
        
        for role, data in results.items():
            output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            output += f"🤖 **{data['role'].upper()}** (completed in {data.get('time', 0):.2f}s)\n"
            output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            output += f"{data['result']}\n\n"
        
        return output


def main():
    """Test Pattern #5"""
    print("=" * 60)
    print("PATTERN #5: PARALLEL EXECUTION")
    print("=" * 60)
    
    pa = ParallelAgents()
    
    print("\n🔹 Test: Research + Write + Analyze in parallel")
    result = pa.process("Explain AI trends")
    print(result)


if __name__ == "__main__":
    main()