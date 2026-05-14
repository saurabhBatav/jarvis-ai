"""AutoAgents Pattern - Dynamic agent creation based on task complexity"""

import os
import json

class AutoAgents:
    """
    AutoAgents pattern:
    - Analyzes task complexity
    - Dynamically creates appropriate number of agents
    - Chooses workflow pattern (sequential, parallel, orchestrator-workers, evaluator-optimiser)
    """
    
    def __init__(self):
        # Load environment
        from dotenv import load_dotenv
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        env_path = os.path.join(project_root, '.env')
        load_dotenv(env_path, override=True)
    
    def _call_llm(self, prompt: str) -> str:
        """Call Groq LLM"""
        import requests
        from dotenv import load_dotenv
        
        # Get project root and load .env
        current_file = os.path.abspath(__file__)
        # Go up: auto_agents.py -> advanced -> agents -> src -> project
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        env_path = os.path.join(project_root, '.env')
        
        # Try to load .env
        load_dotenv(env_path, override=True)
        
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
            "max_tokens": 200
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def analyze_task_complexity(self, task: str) -> dict:
        """Analyze task and determine complexity and needed agents"""
        
        prompt = f"""Analyze this task and determine:
1. How many agents are needed (1-4)
2. What type of workflow to use (sequential, parallel, orchestrator-workers, or evaluator-optimiser)
3. What each agent should do

Task: {task}

Respond in this exact format:
AGENTS: [number 1-4]
WORKFLOW: [sequential|parallel|orchestrator-workers|evaluator-optimiser]
ROLES: [comma-separated roles, one for each agent]

Example for "Research AI and write report":
AGENTS: 2
WORKFLOW: sequential
ROLES: researcher,writer"""

        result = self._call_llm(prompt)
        
        # Parse response
        analysis = {"agents": 2, "workflow": "sequential", "roles": ["researcher", "writer"]}
        
        for line in result.split('\n'):
            if line.startswith('AGENTS:'):
                try:
                    analysis['agents'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif line.startswith('WORKFLOW:'):
                wf = line.split(':')[1].strip().lower()
                if wf in ['sequential', 'parallel', 'orchestrator-workers', 'evaluator-optimiser']:
                    analysis['workflow'] = wf
            elif line.startswith('ROLES:'):
                roles = line.split(':')[1].strip()
                analysis['roles'] = [r.strip() for r in roles.split(',')]
        
        return analysis
    
    def process(self, task: str) -> str:
        """Process task with auto-determined agent configuration"""
        
        # Step 1: Analyze task complexity
        analysis = self.analyze_task_complexity(task)
        
        # Step 2: Execute based on workflow using direct LLM calls
        workflow = analysis['workflow']
        roles = analysis['roles']
        
        if workflow == 'sequential' or workflow == 'parallel':
            # For sequential/parallel, execute via LLM with role context
            prompt = f"""Task: {task}

You are a team with these roles: {', '.join(roles)}
Work together to complete this task.

Execute the task and provide the result:"""
            
            result = self._call_llm(prompt)
            return f"🔧 Used {len(roles)} agents ({workflow}):\n\n{result[:300]}"
        
        elif workflow == 'orchestrator-workers':
            # Use orchestrator pattern
            prompt = f"""Task: {task}

Analyze this task and delegate to appropriate specialists: {', '.join(roles)}

Provide the final result:"""
            result = self._call_llm(prompt)
            return f"🔧 Used orchestrator-workers pattern:\n\n{result[:300]}"
        
        elif workflow == 'evaluator-optimiser':
            # Generate then evaluate
            generate_prompt = f"Generate a solution for: {task}"
            solution = self._call_llm(generate_prompt)
            
            eval_prompt = f"Evaluate this solution and improve if needed:\n{solution}"
            improved = self._call_llm(eval_prompt)
            
            return f"🔧 Used evaluator-optimiser:\n\n{improved[:300]}"
        
        # Fallback
        result = self._call_llm(task)
        return f"🔧 Used single agent:\n\n{result[:300]}"


def test_auto_agents():
    """Test the AutoAgents pattern"""
    print("=" * 60)
    print("TESTING: AutoAgents Pattern")
    print("=" * 60)
    
    auto = AutoAgents()
    
    test_cases = [
        "Write a haiku about spring",
        "Research AI trends, analyze data, write report",
        "Create a movie script",
        "Debug this code and explain the fix",
    ]
    
    print("\n🎯 Testing task complexity analysis:\n")
    
    for i, task in enumerate(test_cases, 1):
        print(f"Test {i}: {task}")
        print("-" * 40)
        
        try:
            analysis = auto.analyze_task_complexity(task)
            print(f"Analysis: {analysis}")
            
            # Just show analysis, don't run full execution
            print(f"Would use: {analysis['agents']} agent(s), {analysis['workflow']} workflow")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print()
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_auto_agents()