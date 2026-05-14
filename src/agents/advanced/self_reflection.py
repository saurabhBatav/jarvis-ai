"""Pattern #8: Self Reflection - Agent reviews and improves its own output"""

import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any

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


class SelfReflectingAgent:
    """Pattern #8: Agent reviews and improves its own output"""
    
    def __init__(self):
        self.max_reflections = 2
    
    def generate(self, task: str) -> str:
        """Initial generation"""
        return call_llm(f"Complete this task thoroughly:\n\n{task}", max_tokens=400)
    
    def reflect(self, task: str, output: str) -> Dict[str, Any]:
        """Review the output and identify improvements"""
        
        review_prompt = f"""Review this output for the task: "{task}"

Output:
{output}

Check for:
1. Accuracy - is the information correct?
2. Completeness - did it cover everything?
3. Clarity - is it easy to understand?
4. Quality - is it well-written?

Respond in format:
NEEDS_IMPROVEMENT: yes/no
ISSUES: (what's wrong, if any)
IMPROVEMENTS: (specific suggestions, if any)"""

        return call_llm(review_prompt, max_tokens=200)
    
    def improve(self, task: str, output: str, feedback: str) -> str:
        """Apply improvements based on feedback"""
        
        improve_prompt = f"""Task: {task}

Original output:
{output}

Feedback/Improvements needed:
{feedback}

Please provide an improved version:"""

        return call_llm(improve_prompt, max_tokens=400)
    
    def process(self, task: str) -> str:
        """Generate → Reflect → Improve (loop)"""
        
        # Step 1: Generate initial output
        print("  📝 Generating initial output...")
        output = self.generate(task)
        
        # Step 2-3: Reflect and improve (up to max_reflections)
        for i in range(self.max_reflections):
            print(f"  🔍 Reflection {i+1}...")
            feedback = self.reflect(task, output)
            
            # Check if needs improvement
            if "NEEDS_IMPROVEMENT: no" in feedback or "NEEDS_IMPROVEMENT: No" in feedback:
                print(f"  ✓ Reflection {i+1}: No improvements needed")
                break
            
            print(f"  🔧 Applying improvements...")
            output = self.improve(task, output, feedback)
        
        # Format output with reflection info
        return f"🪞 **Self Reflection** (generated + refined)\n\n{output}"


def main():
    """Test Pattern #8"""
    print("=" * 60)
    print("PATTERN #8: SELF REFLECTION")
    print("=" * 60)
    
    agent = SelfReflectingAgent()
    
    print("\n🔹 Test: Self-reflecting on answer")
    result = agent.process("Explain what is quantum computing in simple terms")
    print(f"Result:\n{result[:500]}...")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()