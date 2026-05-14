"""Pattern #6: Loop/Iteration - Agents iterate over items until condition met"""

import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any

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


class LoopAgents:
    """Pattern #6: Iterate over items until condition is met"""
    
    def __init__(self):
        self.max_iterations = 5
    
    def process_items(self, items: List[str], task_template: str) -> List[Dict[str, Any]]:
        """Process each item with loop until done"""
        
        results = []
        
        for i, item in enumerate(items):
            print(f"  → Iteration {i+1}: Processing '{item}'")
            
            # Execute task for this item
            prompt = task_template.replace("{{item}}", item)
            result = call_llm(prompt, max_tokens=300)
            
            results.append({
                "iteration": i + 1,
                "item": item,
                "result": result
            })
            
            # Check if we should stop early (for quality results)
            if len(result) > 50 and i >= 2:  # Good result after 2 items
                print(f"  ✓ Good quality reached, stopping early")
                break
        
        return results
    
    def process_with_condition(self, items: List[str], task: str) -> str:
        """Loop until condition is met (e.g., 'comprehensive', 'done')"""
        
        all_results = []
        iterations = 0
        
        while iterations < self.max_iterations:
            # Check if we need more iterations
            if iterations > 0:
                check = call_llm(f"Is the current result comprehensive enough? Task: {task}\n\nCurrent: {all_results[-1]['result'][:200]}", max_tokens=50)
                if "yes" in check.lower() or "comprehensive" in check.lower() or "done" in check.lower():
                    break
            
            # Process next item
            item = items[iterations % len(items)]
            result = call_llm(f"Task: {task}\n\nProcess: {item}", max_tokens=300)
            
            all_results.append({
                "iteration": iterations + 1,
                "item": item,
                "result": result
            })
            
            iterations += 1
            
            if iterations >= self.max_iterations:
                break
        
        # Format output
        output = f"🔄 **Loop Execution** ({iterations} iterations)\n\n"
        for r in all_results:
            output += f"**Iteration {r['iteration']}** ({r['item']}):\n{r['result'][:150]}...\n\n"
        
        return output
    
    def process(self, task: str) -> str:
        """Auto-detect items to loop over"""
        
        # Extract items from task
        prompt = f"""What items should be processed one by one in this task? 

Task: {task}

Examples:
- "Review these 3 articles: A, B, C" → items: A, B, C
- "Analyze these stocks: AAPL, GOOGL, TSLA" → items: AAPL, GOOGL, TSLA
- "Write about Python, Java, Rust" → items: Python, Java, Rust

Respond with comma-separated items:"""

        response = call_llm(prompt, max_tokens=100)
        items = [i.strip() for i in response.split(',')][:5]  # Max 5
        
        if not items or len(items) < 2:
            return "Loop requires multiple items. Try: 'Analyze AAPL, GOOGL, TSLA'"
        
        return self.process_with_condition(items, task)


def main():
    """Test Pattern #6"""
    print("=" * 60)
    print("PATTERN #6: LOOP/ITERATION")
    print("=" * 60)
    
    loop = LoopAgents()
    
    # Test 1: Items list
    print("\n🔹 Test 1: Process items list")
    results = loop.process_items(
        ["Python", "JavaScript", "Rust"], 
        "Explain {{item}} programming language benefits"
    )
    for r in results:
        print(f"  {r['item']}: {r['result'][:80]}...")
    
    # Test 2: Auto-detect
    print("\n🔹 Test 2: Auto-detect loop")
    result = loop.process("Analyze these stocks: AAPL, GOOGL, TSLA, MSFT")
    print(f"Result: {result[:400]}...")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()