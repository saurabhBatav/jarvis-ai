"""Pattern #7: Async/Background Tasks - Fire-and-forget agents"""

import os
import requests
from dotenv import load_dotenv
import threading
import queue
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, Future
import time

# Load env
_base = os.path.dirname(os.path.abspath(__file__))
_project = os.path.dirname(os.path.dirname(_base))
load_dotenv(os.path.join(_project, '.env'), override=True)

API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_BASE = os.environ.get("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = "llama-3.1-8b-instant"


def call_llm(prompt: str, system: str = None, max_tokens: int = 400) -> str:
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


class AsyncAgents:
    """Pattern #7: Execute tasks asynchronously in background"""
    
    def __init__(self):
        self.task_queue = queue.Queue()
        self.results = {}
        self.running = {}
    
    def background_task(self, task_id: str, task: str, callback: Callable = None):
        """Run task in background thread"""
        self.running[task_id] = True
        
        try:
            result = call_llm(task, max_tokens=300)
            self.results[task_id] = {"status": "done", "result": result}
        except Exception as e:
            self.results[task_id] = {"status": "error", "result": str(e)}
        finally:
            self.running[task_id] = False
        
        if callback:
            callback(task_id, self.results[task_id])
    
    def submit_background(self, task_id: str, task: str, callback: Callable = None):
        """Submit task to run in background"""
        thread = threading.Thread(target=self.background_task, args=(task_id, task, callback))
        thread.daemon = True
        thread.start()
        return f"🔔 Task '{task_id}' submitted in background"
    
    def get_result(self, task_id: str) -> Dict[str, Any]:
        """Get result of background task"""
        if task_id in self.results:
            return self.results[task_id]
        if task_id in self.running and self.running[task_id]:
            return {"status": "running", "result": "Task still processing..."}
        return {"status": "not_found", "result": "Task not found"}
    
    def wait_all(self, timeout: float = 30) -> Dict[str, Any]:
        """Wait for all tasks to complete"""
        start = time.time()
        while time.time() - start < timeout:
            if not any(self.running.values()):
                break
            time.sleep(0.5)
        
        return self.results
    
    def process(self, task: str) -> str:
        """Process multiple tasks in parallel using ThreadPoolExecutor"""
        
        # Parse multiple tasks from input
        prompt = f"""What are the independent subtasks in this? List as comma-separated:

Task: {task}

Example: "Search news, check weather, find stock prices" → search news, check weather, find stock prices"""

        response = call_llm(prompt, max_tokens=100)
        subtasks = [s.strip() for s in response.split(',')][:5]
        
        if len(subtasks) < 2:
            return call_llm(task)  # Single task, just run normally
        
        # Execute all in parallel (async-like)
        with ThreadPoolExecutor(max_workers=len(subtasks)) as executor:
            futures = {executor.submit(call_llm, f"Complete: {t}", max_tokens=300): t for t in subtasks}
            results = {}
            for future in futures:
                task_name = futures[future]
                try:
                    results[task_name] = future.result(timeout=30)
                except:
                    results[task_name] = "Error"
        
        # Format output
        output = f"⚡ **Async Parallel** ({len(subtasks)} tasks)\n\n"
        for task_name, result in results.items():
            output += f"**{task_name}:**\n{result[:150]}...\n\n"
        
        return output


def main():
    """Test Pattern #7"""
    print("=" * 60)
    print("PATTERN #7: ASYNC/BACKGROUND TASKS")
    print("=" * 60)
    
    async_agents = AsyncAgents()
    
    # Test 1: Background submission
    print("\n🔹 Test 1: Background task")
    msg = async_agents.submit_background("task1", "Explain quantum computing")
    print(f"  {msg}")
    time.sleep(2)  # Wait a bit
    result = async_agents.get_result("task1")
    print(f"  Result: {result}")
    
    # Test 2: Parallel async
    print("\n🔹 Test 2: Multiple async tasks")
    result = async_agents.process("Search news, check weather, find stock price for AAPL")
    print(f"Result: {result[:400]}...")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()