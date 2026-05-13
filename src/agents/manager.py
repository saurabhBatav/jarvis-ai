"""Manager Agent - Central orchestration for Jarvis"""

from typing import Optional, List, Dict, Any
from praisonaiagents import Agent, AgentTeam
from .base import BaseAgent


class JarvisManager:
    """
    Manager Agent that coordinates specialized agents using hierarchical process.
    Acts as the "Brain" of Jarvis.
    """

    DEFAULT_LLM = "llama-3.1-70b-versatile"  # More capable for manager

    def __init__(
        self,
        llm: str = None,
        worker_llm: str = "llama-3.1-8b-instant",
        max_manager_retries: int = 3,
        max_invalid_selections: int = 3
    ):
        self.llm = llm or self.DEFAULT_LLM
        self.worker_llm = worker_llm
        self.max_manager_retries = max_manager_retries
        self.max_invalid_selections = max_invalid_selections

        self.manager_agent = None
        self.worker_agents: Dict[str, BaseAgent] = {}
        self.agent_team = None

    def set_manager(
        self,
        name: str = "Jarvis Manager",
        role: str = "Chief Operations Officer",
        goal: str = "Coordinate all specialized agents to accomplish user goals efficiently",
        backstory: str = "You are the central intelligence of Jarvis, an AI operating system. You delegate tasks to specialized agents and ensure seamless orchestration."
    ) -> None:
        """Configure the manager agent"""
        self.manager = Agent(
            name=name,
            instructions=f"You are {name}, {role}. {goal} {backstory}",
            llm=self.llm
        )

    def add_worker(
        self,
        agent_id: str,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[list] = None
    ) -> None:
        """Add a worker agent to the team"""
        worker = Agent(
            name=name,
            instructions=f"You are {name}, {role}. Your goal is: {goal}. {backstory}",
            llm=self.worker_llm,
            tools=tools if tools else None
        )
        self.worker_agents[agent_id] = worker

    def create_team(
        self,
        agents: list,
        process: str = "hierarchical",
        planning: bool = False
    ) -> AgentTeam:
        """Create an AgentTeam with hierarchical process"""
        self.agent_team = AgentTeam(
            agents=agents,
            process=process,
            planning=planning
        )
        return self.agent_team

    def start(self, task: str) -> str:
        """Execute task through the agent team"""
        if self.agent_team is None:
            if not self.worker_agents:
                raise ValueError("No workers added. Add workers before starting.")
            agents_list = list(self.worker_agents.values())
            self.create_team(agents_list, process="hierarchical")

        return self.agent_team.start(task)

    def chat(self, message: str) -> str:
        """Chat with the team"""
        if self.agent_team is None:
            raise ValueError("Team not initialized. Call start() first.")
        return self.agent_team.chat(message)

    def get_available_agents(self) -> list:
        """Get list of available worker agents"""
        return list(self.worker_agents.keys())

    def __repr__(self) -> str:
        return f"JarvisManager(workers={len(self.worker_agents)}, llm={self.llm})"