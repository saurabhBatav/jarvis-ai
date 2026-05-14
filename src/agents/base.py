"""Base Agent - Foundation for all Jarvis agents"""

import os
import requests
from dotenv import load_dotenv
from typing import Optional, Callable
from praisonaiagents import Agent as PraisonAgent

# Load .env with override - use __file__ for correct path resolution
_base_path = os.path.dirname(os.path.abspath(__file__))  # src/agents/
_jarvis_root = os.path.dirname(_base_path)  # src/
_project_root = os.path.dirname(_jarvis_root)  # project root
load_dotenv(os.path.join(_project_root, '.env'), override=True)

# Now set from loaded .env - these override shell env
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
os.environ['OPENAI_BASE_URL'] = os.getenv('OPENAI_BASE_URL', 'https://api.groq.com/openai/v1')

API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_BASE = os.environ.get("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = "llama-3.1-8b-instant"


def call_llm(prompt: str, system: str = None, max_tokens: int = 500) -> str:
    """Direct Groq API call - bypasses PraisonAI issues"""
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
        return f"Error: {resp.status_code} - {resp.text[:100]}"
    except Exception as e:
        return f"Error: {str(e)}"


class BaseAgent:
    """
    Base class for all Jarvis agents.
    Provides common functionality and configuration.
    """

    DEFAULT_LLM = "llama-3.1-8b-instant"

    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        instructions: Optional[str] = None,
        llm: str = None,
        tools: Optional[list] = None,
        allow_delegation: bool = True,
        allow_code_execution: bool = False,
        use_memory: bool = True
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.instructions = instructions or self._build_instructions()
        self.llm = llm or self.DEFAULT_LLM
        self.tools = tools or []
        self.allow_delegation = allow_delegation
        self.allow_code_execution = allow_code_execution
        self.use_memory = use_memory
        self._agent = None

    def _build_instructions(self) -> str:
        return f"You are {self.name}, {self.role}. Your goal is: {self.goal}. {self.backstory}"

    def _create_praison_agent(self) -> PraisonAgent:
        return PraisonAgent(
            name=self.name,
            instructions=self.instructions,
            llm=self.llm,
            tools=self.tools if self.tools else None,
            allow_delegation=self.allow_delegation,
            allow_code_execution=self.allow_code_execution,
            memory=self.use_memory
        )

    def initialize(self) -> None:
        """Initialize the underlying PraisonAI agent"""
        if self._agent is None:
            self._agent = self._create_praison_agent()

    def start(self, task: str) -> str:
        """Execute a task"""
        self.initialize()
        return self._agent.start(task)

    def chat(self, message: str) -> str:
        """Send a message and get response"""
        self.initialize()
        return self._agent.chat(message)

    def get_agent(self) -> Optional[PraisonAgent]:
        """Get the underlying PraisonAI agent"""
        if self._agent is None:
            self.initialize()
        return self._agent

    def clear_memory(self) -> None:
        """Clear the agent's built-in memory"""
        if self._agent is not None and hasattr(self._agent, 'memory'):
            self._agent.memory.reset_all()

    def __repr__(self) -> str:
        return f"BaseAgent(name={self.name}, role={self.role}, llm={self.llm})"


def create_agent(
    name: str,
    role: str,
    goal: str,
    backstory: str,
    llm: str = "llama-3.1-8b-instant",
    tools: Optional[list] = None,
    **kwargs
) -> BaseAgent:
    """Factory function to create a Jarvis agent"""
    return BaseAgent(
        name=name,
        role=role,
        goal=goal,
        backstory=backstory,
        llm=llm,
        tools=tools,
        **kwargs
    )


class JarvisAssistant(BaseAgent):
    """Default Jarvis assistant agent with built-in memory and session persistence"""

    def __init__(self, llm: str = "llama-3.1-8b-instant", use_memory: bool = True, session_id: str = "jarvis_main", **kwargs):
        # Get agent capabilities from registry
        from src.agents.registry import registry
        capabilities = registry.get_capabilities_summary()
        
        backstory = f"""You are Jarvis, a helpful AI assistant.

You have access to these specialized agents:
{capabilities}

When a user asks about specific topics (finance, health, research, etc), 
you can route to the appropriate agent. For general questions, answer directly."""

        super().__init__(
            name="Jarvis Assistant",
            role="General Assistant",
            goal="Help the user with any task they request",
            backstory=backstory,
            llm=llm,
            use_memory=use_memory,
            **kwargs
        )
        self.session_id = session_id

    def _create_praison_agent(self) -> PraisonAgent:
        return PraisonAgent(
            name=self.name,
            instructions=self.instructions,
            llm=self.llm,
            tools=self.tools if self.tools else None,
            allow_delegation=self.allow_delegation,
            allow_code_execution=self.allow_code_execution,
            memory={
                "session_id": self.session_id,
                "user_id": "main_user",
                "auto_memory": True
            }
        )

    def chat(self, message: str) -> str:
        """Use direct API call instead of PraisonAI"""
        return call_llm(f"{self.instructions}\n\nUser: {message}", max_tokens=500)

    def start(self, task: str) -> str:
        """Use direct API call instead of PraisonAI"""
        return call_llm(f"{self.instructions}\n\nTask: {task}", max_tokens=500)