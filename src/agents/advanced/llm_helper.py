"""LLM Helper for direct calls"""

import os
import requests
from dotenv import load_dotenv


def call_llm(prompt: str, model: str = "llama-3.1-8b-instant", max_tokens: int = 500) -> str:
    """Make direct LLM call via Groq API"""
    
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path, override=True)
    
    api_key = os.environ.get("OPENAI_API_KEY", "")
    
    if not api_key:
        return "Error: API key not configured"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"