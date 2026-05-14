"""Pattern #4: Conditional Routing - Dynamic task routing based on conditions"""

import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional

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


class ConditionalRouter:
    """Implements Pattern #4: Conditional Routing - dynamic task routing based on conditions"""
    
    def __init__(self):
        self.route_history = []
        
        self.routes = {
            "research": {
                "condition": "task asks to research, find, look up, investigate, or gather information",
                "system": "You are a research expert. Find accurate, detailed information with sources.",
                "priority": "high"
            },
            "analysis": {
                "condition": "task asks to analyze, compare, evaluate, assess, or identify patterns",
                "system": "You are a data analyst. Analyze data and extract insights.",
                "priority": "medium"
            },
            "writing": {
                "condition": "task asks to write, create, draft, compose, or generate content",
                "system": "You are a professional writer. Create clear, engaging content.",
                "priority": "medium"
            },
            "technical": {
                "condition": "task asks to code, debug, fix, implement, or solve technical problems",
                "system": "You are a technical specialist. Provide precise technical solutions.",
                "priority": "high"
            },
            "creative": {
                "condition": "task asks to imagine, design, invent, create something original",
                "system": "You are a creative specialist. Generate innovative ideas.",
                "priority": "low"
            }
        }
    
    def classify_task(self, task: str) -> Dict[str, Any]:
        """Classify task to determine routing"""
        
        prompt = f"""Analyze this task and classify it.

Task: {task}

Determine:
1. Type: research, analysis, writing, technical, or creative
2. Complexity: simple (1 step), moderate (2-3 steps), complex (many steps)
3. Priority: low, medium, high

Respond in format:
TYPE: [type]
COMPLEXITY: [level]
PRIORITY: [priority]"""

        result = call_llm(prompt, max_tokens=150)
        
        task_type = "writing"  # default
        complexity = "moderate"
        priority = "medium"
        
        for line in result.split('\n'):
            if line.startswith('TYPE:'):
                t = line.split(':')[1].strip().lower()
                for r in self.routes:
                    if r in t:
                        task_type = r
                        break
            elif line.startswith('COMPLEXITY:'):
                c = line.split(':')[1].strip().lower()
                if c in ['simple', 'moderate', 'complex']:
                    complexity = c
            elif line.startswith('PRIORITY:'):
                p = line.split(':')[1].strip().lower()
                if p in ['low', 'medium', 'high']:
                    priority = p
        
        return {"type": task_type, "complexity": complexity, "priority": priority}
    
    def route_task(self, task: str) -> str:
        """Route task to appropriate handler based on classification"""
        
        classification = self.classify_task(task)
        task_type = classification["type"]
        
        route = self.routes.get(task_type, self.routes["writing"])
        system = route["system"]
        
        result = call_llm(task, system=system, max_tokens=500)
        
        self.route_history.append({
            "task": task,
            "classification": classification,
            "route": task_type,
            "result": result
        })
        
        return f"🚦 **Conditional Routing Pattern**\n\n[Classified as: {task_type}] [Priority: {classification['priority']}]\n\n{result}"
    
    def route_with_fallback(self, task: str) -> str:
        """Route with fallback chain if first route fails"""
        
        classification = self.classify_task(task)
        task_type = classification["type"]
        
        # Try primary route
        route = self.routes.get(task_type, self.routes["writing"])
        result = call_llm(task, system=route["system"], max_tokens=400)
        
        # Check if result is insufficient
        if len(result) < 50 or "error" in result.lower():
            # Try fallback to writing
            fallback = self.routes["writing"]
            result = call_llm(task, system=fallback["system"], max_tokens=400)
        
        return f"🚦 Route: {task_type} → Result: {result[:300]}..."
    
    def multi_path_routing(self, task: str) -> Dict[str, Any]:
        """Route to multiple paths based on task characteristics"""
        
        classification = self.classify_task(task)
        
        paths = []
        
        if classification["complexity"] in ["moderate", "complex"]:
            # Multiple agents for complex tasks
            for route_name, route_info in self.routes.items():
                if route_info["priority"] == "high":
                    result = call_llm(task, system=route_info["system"], max_tokens=300)
                    paths.append({"route": route_name, "result": result})
        
        if not paths:
            # Simple task - single route
            route = self.routes.get(classification["type"], self.routes["writing"])
            result = call_llm(task, system=route["system"], max_tokens=400)
            paths.append({"route": classification["type"], "result": result})
        
        return {
            "task": task,
            "classification": classification,
            "paths": paths
        }
    
    def get_routing_stats(self) -> Dict[str, Any]:
        return {
            "total_routes": len(self.route_history),
            "routes": list(self.routes.keys())
        }


def main():
    print("=" * 60)
    print("PATTERN #4: CONDITIONAL ROUTING")
    print("=" * 60)
    
    router = ConditionalRouter()
    
    test_cases = [
        "Research the latest AI trends",
        "Write a poem about winter",
        "Debug this Python code",
        "Analyze sales data trends",
    ]
    
    for i, task in enumerate(test_cases, 1):
        print(f"\n🔹 Test {i}: {task}")
        
        result = router.route_task(task)
        print(f"Result: {result[:300]}...")
    
    print("\n" + "=" * 60)
    
    # Test multi-path
    print("\n🔹 Multi-path routing test:")
    result = router.multi_path_routing("Research AI and analyze trends")
    print(f"Paths: {len(result['paths'])} routes taken")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()