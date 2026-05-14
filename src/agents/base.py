"""Base Agent - Foundation for all Jarvis agents"""

from typing import Optional, Callable
from praisonaiagents import Agent as PraisonAgent


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