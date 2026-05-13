"""Programming Agent - Self-evolution through code generation"""

import os
import sys
import subprocess
import tempfile
import json
import traceback
from typing import Optional, Dict, List
from praisonaiagents import Agent


class CodeExecutor:
    """Safe code execution environment"""
    
    def __init__(self, timeout: int = 30, sandbox_level: str = "basic"):
        self.timeout = timeout
        self.sandbox_level = sandbox_level
        self.execution_history = []
    
    def execute(self, code: str, language: str = "python") -> Dict:
        """
        Execute code safely and return results.
        
        Args:
            code: Code to execute
            language: python, bash, javascript
            
        Returns:
            Dict with output, error, and execution time
        """
        result = {
            "success": False,
            "output": "",
            "error": "",
            "execution_time": 0
        }
        
        import time
        start_time = time.time()
        
        try:
            if language == "python":
                # Execute Python code
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                
                try:
                    # Run with timeout and capture output
                    proc = subprocess.run(
                        [sys.executable, temp_file],
                        capture_output=True,
                        text=True,
                        timeout=self.timeout,
                        cwd=os.getcwd()
                    )
                    result["output"] = proc.stdout
                    result["error"] = proc.stderr
                    result["success"] = proc.returncode == 0
                finally:
                    os.unlink(temp_file)
                    
            elif language == "bash":
                # Execute bash command
                proc = subprocess.run(
                    code,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=os.getcwd()
                )
                result["output"] = proc.stdout
                result["error"] = proc.stderr
                result["success"] = proc.returncode == 0
                
            else:
                result["error"] = f"Unsupported language: {language}"
                
        except subprocess.TimeoutExpired:
            result["error"] = f"Execution timed out after {self.timeout} seconds"
        except Exception as e:
            result["error"] = f"Execution error: {str(e)}\n{traceback.format_exc()}"
        
        result["execution_time"] = time.time() - start_time
        self.execution_history.append(result)
        
        return result
    
    def get_history(self) -> List[Dict]:
        return self.execution_history[-10:]
    
    def clear_history(self):
        self.execution_history.clear()


class FileTool:
    """File operations tool for the Programming Agent"""
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """Read file contents"""
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    @staticmethod
    def write_file(file_path: str, content: str) -> str:
        """Write content to file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
            return f"✅ Written to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        return os.path.exists(file_path)
    
    @staticmethod
    def list_directory(dir_path: str = ".") -> List[str]:
        try:
            return os.listdir(dir_path)
        except Exception as e:
            return [f"Error: {str(e)}"]


class ProgrammingAgent:
    """
    Internal Programming Agent for Jarvis self-evolution.
    Can write code, execute it, and extend Jarvis capabilities.
    """
    
    def __init__(
        self,
        llm: str = "llama-3.1-8b-instant",
        code_executor: Optional[CodeExecutor] = None
    ):
        self.llm = llm
        self.executor = code_executor or CodeExecutor()
        self.file_tool = FileTool()
        self._agent = None
        self._instructions = """You are Jarvis Programming Agent, an expert software developer.
Your role is to write code, fix bugs, and extend Jarvis capabilities.

Capabilities:
- Write Python code for new features
- Execute code and fix errors
- Read and modify files
- Create new agents and tools
- Debug issues

Always:
- Write clean, working code
- Handle errors gracefully
- Test your code before finalizing
- Document what you create"""
    
    def _create_agent(self) -> Agent:
        return Agent(
            name="Programming Agent",
            instructions=self._instructions,
            llm=self.llm
        )
    
    def initialize(self):
        if self._agent is None:
            self._agent = self._create_agent()
    
    def write_code(self, task: str) -> str:
        """Get code suggestions from the LLM"""
        self.initialize()
        return self._agent.start(task)
    
    def execute_code(self, code: str, language: str = "python") -> Dict:
        """Execute code and return results"""
        return self.executor.execute(code, language)
    
    def create_tool(self, name: str, description: str, code: str) -> str:
        """Create a new tool for Jarvis"""
        tool_path = f"./src/tools/{name.lower().replace(' ', '_')}.py"
        
        template = f'''"""Auto-generated tool: {name}"""

def {name.lower().replace(' ', '_').replace('-', '_')}():
    """{description}"""
    # Your code here
    pass
'''
        
        result = self.file_tool.write_file(tool_path, code)
        
        # Also add to tools registry
        registry_path = "./src/tools/__init__.py"
        if self.file_tool.file_exists(registry_path):
            current = self.file_tool.read_file(registry_path)
            new_entry = f'\n# Auto-generated: {name}\n# {description}'
            self.file_tool.write_file(registry_path, current + new_entry)
        
        return result
    
    def fix_error(self, error_message: str, code: str) -> str:
        """Analyze error and suggest fix"""
        prompt = f"""Analyze this error and fix the code:

Error: {error_message}

Code:
{code}

Provide the fixed code:"""
        
        return self.write_code(prompt)
    
    def analyze_code(self, code: str) -> str:
        """Analyze code and provide feedback"""
        prompt = f"""Analyze this code and provide feedback:

{code}

Provide:
1. What it does
2. Any issues or improvements
3. Security concerns"""
        
        return self.write_code(prompt)
    
    def __repr__(self):
        return f"ProgrammingAgent(llm={self.llm})"