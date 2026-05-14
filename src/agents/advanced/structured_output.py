"""Pattern #9: Structured Output - Agent returns structured data (JSON)"""

import os
import requests
import json
from dotenv import load_dotenv

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


class StructuredOutputAgent:
    """Pattern #9: Returns structured data (JSON)"""
    
    def __init__(self):
        self.schemas = {
            "stock_analysis": {
                "symbol": "string",
                "price": "number", 
                "trend": "string",
                "recommendation": "string"
            },
            "weather": {
                "location": "string",
                "temperature": "string",
                "conditions": "string",
                "advice": "string"
            },
            "task": {
                "title": "string",
                "priority": "string",
                "deadline": "string", 
                "steps": "array"
            }
        }
    
    def generate_structured(self, task: str, schema_name: str) -> str:
        """Generate output in specific schema"""
        
        schema = self.schemas.get(schema_name, {})
        schema_str = json.dumps(schema, indent=2)
        
        prompt = f"""Task: {task}

Respond ONLY in this JSON schema (no other text):
{schema_str}

Respond with valid JSON only:"""

        result = call_llm(prompt, max_tokens=300)
        
        # Try to parse as JSON
        try:
            # Find JSON in response
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            parsed = json.loads(result.strip())
            return json.dumps(parsed, indent=2)
        except:
            return result  # Return as-is if not valid JSON
    
    def detect_schema(self, task: str) -> str:
        """Auto-detect what schema to use"""
        
        task_lower = task.lower()
        
        if any(w in task_lower for w in ['stock', 'share', 'price', 'trading']):
            return "stock_analysis"
        elif any(w in task_lower for w in ['weather', 'temperature', 'forecast']):
            return "weather"
        elif any(w in task_lower for w in ['task', 'todo', 'plan', 'create']):
            return "task"
        else:
            return "task"  # Default
    
    def process(self, task: str) -> str:
        """Process with structured output"""
        
        schema_name = self.detect_schema(task)
        result = self.generate_structured(task, schema_name)
        
        return f"📋 **Structured Output** (schema: {schema_name})\n\n```json\n{result}\n```"


def main():
    """Test Pattern #9"""
    print("=" * 60)
    print("PATTERN #9: STRUCTURED OUTPUT")
    print("=" * 60)
    
    agent = StructuredOutputAgent()
    
    print("\n🔹 Test 1: Stock analysis")
    result = agent.process("Analyze stock AAPL")
    print(f"Result: {result[:300]}...")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()