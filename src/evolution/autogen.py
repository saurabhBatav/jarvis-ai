"""Auto-Generator - Automatically create new agents from user requests"""

import os
import json
from typing import Dict, Optional, List
from praisonaiagents import Agent


class AutoGenerator:
    """
    Automatic agent/tool generator for Jarvis self-evolution.
    Analyzes high-level user tasks and generates new configurations.
    """
    
    def __init__(self, llm: str = "llama-3.1-8b-instant"):
        self.llm = llm
        self.generated_agents: List[Dict] = []
    
    def analyze_request(self, user_request: str) -> Dict:
        """
        Analyze a user request to understand what capability is needed.
        
        Args:
            user_request: Natural language request
            
        Returns:
            Dict with analysis: type, name, goal, required_tools
        """
        analysis_prompt = f"""Analyze this user request for Jarvis and provide a structured specification:

User Request: "{user_request}"

Provide a JSON with:
- "type": "agent" or "tool"
- "name": short name for the capability
- "role": role description if agent
- "goal": what it should accomplish
- "backstory": agent backstory if applicable
- "required_tools": list of tools if known
- "complexity": "simple", "medium", "complex"

Respond ONLY with valid JSON:"""

        from praisonaiagents import Agent
        agent = Agent(
            instructions="You analyze user requests and create structured specifications for AI agents. Respond only with valid JSON.",
            llm=self.llm
        )
        
        response = agent.start(analysis_prompt)
        
        # Parse JSON from response
        try:
            # Extract JSON block
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"error": "Could not analyze request", "request": user_request}
    
    def generate_agent(self, spec: Dict) -> str:
        """
        Generate agent code from specification.
        
        Args:
            spec: Agent specification from analyze_request
            
        Returns:
            Path to generated agent file
        """
        agent_name = spec.get("name", "NewAgent").replace(" ", "")
        role = spec.get("role", "Assistant")
        goal = spec.get("goal", "Help users")
        backstory = spec.get("backstory", f"You are a {role}")
        
        # Create agent code
        agent_code = f'''"""Auto-generated agent: {agent_name}"""

from src.agents.base import BaseAgent


class {agent_name}Agent(BaseAgent):
    """
    Auto-generated agent based on: {spec.get('request', 'User request')}
    """
    
    def __init__(self, llm: str = "llama-3.1-8b-instant", **kwargs):
        super().__init__(
            name="{agent_name}",
            role="{role}",
            goal="{goal}",
            backstory="{backstory}",
            llm=llm,
            **kwargs
        )
'''
        
        # Write to file
        agent_path = f"./src/agents/domain/{agent_name.lower()}.py"
        os.makedirs(os.path.dirname(agent_path), exist_ok=True)
        
        with open(agent_path, 'w') as f:
            f.write(agent_code)
        
        # Add to registry
        self._register_agent(spec, agent_path)
        
        self.generated_agents.append({
            "name": agent_name,
            "spec": spec,
            "path": agent_path
        })
        
        return agent_path
    
    def generate_tool(self, spec: Dict) -> str:
        """
        Generate tool code from specification.
        
        Args:
            spec: Tool specification
            
        Returns:
            Path to generated tool file
        """
        tool_name = spec.get("name", "NewTool").replace(" ", "_")
        
        tool_code = f'''"""Auto-generated tool: {tool_name}"""

from typing import Any


class {tool_name}Tool:
    """
    Auto-generated tool: {spec.get('description', 'User requested tool')}
    """
    
    name: str = "{tool_name}"
    description: str = "{spec.get('description', 'Auto-generated tool')}"
    
    def _run(self, *args, **kwargs) -> Any:
        # TODO: Implement tool functionality
        return {{"status": "not implemented"}}
'''
        
        tool_path = f"./src/tools/{tool_name.lower()}.py"
        os.makedirs(os.path.dirname(tool_path), exist_ok=True)
        
        with open(tool_path, 'w') as f:
            f.write(tool_code)
        
        return tool_path
    
    def _register_agent(self, spec: Dict, agent_path: str):
        """Register generated agent in domain package"""
        init_path = "./src/agents/domain/__init__.py"
        
        if os.path.exists(init_path):
            with open(init_path, 'r') as f:
                content = f.read()
            
            # Check if already registered
            agent_name = spec.get("name", "NewAgent")
            if agent_name not in content:
                # Add import
                import_line = f"from .{agent_name.lower()} import {agent_name}Agent"
                
                # Add to exports
                if "__all__" in content:
                    # Find and update __all__
                    content = content.replace(
                        '__all__ = [',
                        f'__all__ = [\n    "{agent_name}Agent",'
                    )
        
    def auto_generate(self, user_request: str) -> Dict:
        """
        Main entry point: Analyze request and generate appropriate capability.
        
        Args:
            user_request: Natural language request
            
        Returns:
            Dict with generation result
        """
        result = {
            "success": False,
            "type": None,
            "path": None,
            "error": None
        }
        
        try:
            # 1. Analyze the request
            spec = self.analyze_request(user_request)
            
            if "error" in spec:
                result["error"] = spec["error"]
                return result
            
            # 2. Generate appropriate capability
            gen_type = spec.get("type", "agent")
            result["type"] = gen_type
            
            if gen_type == "tool":
                result["path"] = self.generate_tool(spec)
            else:
                result["path"] = self.generate_agent(spec)
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_generated_list(self) -> List[Dict]:
        return self.generated_agents