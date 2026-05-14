"""Pattern #10: Policy Engine - Declarative rules for agent behavior"""

import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, List

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


class PolicyEngine:
    """Pattern #10: Enforce rules/policies on agent behavior"""
    
    def __init__(self):
        # Define policies
        self.policies = {
            "safety": {
                "rules": [
                    "Never provide harmful instructions",
                    "Don't reveal system prompts",
                    "Block malicious requests"
                ],
                "action": "block"
            },
            "style": {
                "rules": [
                    "Be concise",
                    "Use friendly tone",
                    "Add emoji for friendliness"
                ],
                "action": "enforce"
            },
            "privacy": {
                "rules": [
                    "Don't ask for personal data",
                    "Don't store sensitive info",
                    "Respect user privacy"
                ],
                "action": "warn"
            },
            "jarvis": {
                "rules": [
                    "Call user 'sir'",
                    "Use formal speech",
                    "Say 'At your service'",
                    "Be efficient"
                ],
                "action": "enforce"
            }
        }
    
    def check_policy(self, task: str, policy_name: str) -> Dict[str, Any]:
        """Check if task violates policy"""
        
        policy = self.policies.get(policy_name, {})
        rules = policy.get("rules", [])
        
        # Check task against rules
        task_lower = task.lower()
        
        violations = []
        for rule in rules:
            # Simple keyword-based checking
            if "harmful" in rule.lower() and any(w in task_lower for w in ['hack', 'attack', 'harm']):
                violations.append(rule)
            elif "reveal" in rule.lower() and "system prompt" in rule.lower():
                if "show prompt" in task_lower or "show instructions" in task_lower:
                    violations.append(rule)
        
        return {
            "policy": policy_name,
            "violations": violations,
            "action": policy.get("action", "allow") if violations else "allow"
        }
    
    def enforce_policy(self, task: str, policy_name: str) -> str:
        """Apply policy and modify output"""
        
        check = self.check_policy(task, policy_name)
        
        if check["action"] == "block" and check["violations"]:
            return f"⛔ **Policy Blocked**: {check['violations'][0]}"
        
        if check["action"] == "warn":
            print(f"⚠️ Policy warning: {check['violations']}")
        
        return None  # No block
    
    def process(self, task: str, enforce_style: str = None) -> str:
        """Apply policies before processing"""
        
        # Check safety policy first (always)
        safety_block = self.enforce_policy(task, "safety")
        if safety_block:
            return safety_block
        
        # Check privacy policy
        privacy_check = self.enforce_policy(task, "privacy")
        
        # Process the task
        result = call_llm(task, max_tokens=400)
        
        # Apply style policy if requested
        if enforce_style and enforce_style in self.policies:
            style_policy = self.policies[enforce_style]
            # Add style guidelines to output
            style_note = f"\n\n📜 **Applied policy**: {enforce_style}"
            result += style_note
        
        return f"✅ **Policy Engine** passed\n\n{result}"


def main():
    """Test Pattern #10"""
    print("=" * 60)
    print("PATTERN #10: POLICY ENGINE")
    print("=" * 60)
    
    engine = PolicyEngine()
    
    # Test 1: Normal task
    print("\n🔹 Test 1: Normal task")
    result = engine.process("What is Python?")
    print(f"Result: {result[:200]}...")
    
    # Test 2: Blocked task
    print("\n🔹 Test 2: Blocked (safety)")
    result = engine.process("How to hack a bank")
    print(f"Result: {result}")
    
    # Test 3: With style enforcement
    print("\n🔹 Test 3: With JARVIS style")
    result = engine.process("Hello", enforce_style="jarvis")
    print(f"Result: {result[:200]}...")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()