"""Orchestrator-Workers Pattern - Multi-agent task routing"""

import os
import json

class OrchestratorWorkers:
    """
    Orchestrator-Workers pattern:
    - Orchestrator analyzes task and routes to appropriate workers
    - Workers handle specific types of tasks
    - Synthesizer combines results
    """
    
    def __init__(self):
        # Load environment variables
        from dotenv import load_dotenv
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        env_path = os.path.join(project_root, '.env')
        load_dotenv(env_path, override=True)
        from praisonaiagents import Agent
        
        # Create worker agents
        self.research_worker = Agent(
            name="ResearchWorker",
            role="Research Specialist",
            goal="Find information and conduct research",
            instructions="You research topics thoroughly. Provide detailed information with sources.",
        )
        
        self.code_worker = Agent(
            name="CodeWorker",
            role="Programming Specialist", 
            goal="Write, debug, and explain code",
            instructions="You help with programming tasks. Write clean code and explain concepts.",
        )
        
        self.general_worker = Agent(
            name="GeneralWorker",
            role="General Assistant",
            goal="Handle general questions and tasks",
            instructions="You answer general questions and help with various tasks efficiently.",
        )
        
        self.finance_worker = Agent(
            name="FinanceWorker",
            role="Finance Specialist",
            goal="Handle financial queries and analysis",
            instructions="You provide financial information, stock data, and investment insights.",
        )
        
        # Orchestrator - decides which worker to use
        self.orchestrator = Agent(
            name="Orchestrator",
            role="Task Router",
            goal="Analyze request and route to appropriate worker",
            instructions="""Analyze the user's request and determine which worker can best handle it:

- For research, information gathering, papers, topics - use: ResearchWorker
- For code, programming, debugging, technical tasks - use: CodeWorker  
- For financial queries, stocks, investments - use: FinanceWorker
- For general questions, conversation, other tasks - use: GeneralWorker

Respond with ONLY the worker name: ResearchWorker, CodeWorker, FinanceWorker, or GeneralWorker
No other text.""",
            llm="llama-3.1-8b-instant"
        )
        
        # Synthesizer - combines results
        self.synthesizer = Agent(
            name="Synthesizer",
            role="Result Combiner",
            goal="Combine worker outputs into final response",
            instructions="Combine the worker's response into a clear, concise answer. Keep it natural.",
            llm="llama-3.1-8b-instant"
        )
    
    def _call_llm(self, prompt: str) -> str:
        """Call Groq LLM"""
        import requests
        
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY", "")
        
        if not api_key:
            return "API key not configured"
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 100
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=20)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def process(self, user_request: str) -> str:
        """Process request through orchestrator-workers pattern"""
        
        # Step 1: Orchestrator decides which worker
        orchestrator_prompt = f"""Request: {user_request}

Which worker should handle this? Respond with only: ResearchWorker, CodeWorker, FinanceWorker, or GeneralWorker"""
        
        worker_name = self._call_llm(orchestrator_prompt).strip()
        
        # Clean up worker name
        for name in ["ResearchWorker", "CodeWorker", "FinanceWorker", "GeneralWorker"]:
            if name.lower() in worker_name.lower():
                worker_name = name
                break
        else:
            worker_name = "GeneralWorker"
        
        # Step 2: Selected worker processes the task
        # Map worker names to attributes
        worker_map = {
            "ResearchWorker": "research_worker",
            "CodeWorker": "code_worker", 
            "FinanceWorker": "finance_worker",
            "GeneralWorker": "general_worker"
        }
        
        worker_attr = worker_map.get(worker_name, "general_worker")
        worker = getattr(self, worker_attr)
        
        prompt = f"""Task: {user_request}

Provide a helpful response."""
        
        worker_result = self._call_llm(prompt)
        
        return f"🔄 Routed to {worker_name}:\n\n{worker_result}"


def test_orchestrator_workers():
    """Test the orchestrator-workers pattern"""
    print("=" * 60)
    print("TESTING: Orchestrator-Workers Pattern")
    print("=" * 60)
    
    orch = OrchestratorWorkers()
    
    test_cases = [
        "What's the price of Apple stock?",
        "Write a Python function to reverse a string",
        "Research about quantum computing",
        "What is the weather today?",
    ]
    
    print("\n🎯 Testing each request:\n")
    
    for i, request in enumerate(test_cases, 1):
        print(f"Test {i}: {request}")
        print("-" * 40)
        
        try:
            result = orch.process(request)
            print(f"Result: {result[:200]}...")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print()
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_orchestrator_workers()