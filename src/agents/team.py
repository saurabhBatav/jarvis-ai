"""Fixed AgentTeam - Workaround for PraisonAI version issues with Groq"""

import os
from typing import List, Optional
from praisonaiagents import Agent


class JarvisTeam:
    """
    Jarvis AgentTeam with workaround for Groq compatibility issues.
    Uses sequential task execution instead of internal AgentTeam.
    """

    def __init__(
        self,
        agents: List[Agent],
        process: str = "sequential",
        llm: str = "llama-3.1-8b-instant"
    ):
        self.agents = agents
        self.process = process
        self.llm = llm
        self._last_results = {}

    def start(self, task: str) -> str:
        """
        Execute task across agents sequentially.
        Each agent's output becomes context for the next.
        """
        results = []
        current_context = task

        for i, agent in enumerate(self.agents):
            # Add previous results to context if sequential
            if self.process == "sequential" and i > 0:
                previous_summary = f"\n\nPrevious agent's work:\n{results[-1][:500]}"
                current_context = task + previous_summary
            elif self.process == "parallel":
                current_context = task

            try:
                result = agent.start(current_context)
                results.append(result)
                self._last_results[agent.name] = result
            except Exception as e:
                error_result = f"Error in {agent.name}: {str(e)}"
                results.append(error_result)
                self._last_results[agent.name] = error_result

        if self.process == "parallel":
            return "\n\n".join(results)
        else:
            return results[-1] if results else "No results"

    def chat(self, message: str) -> str:
        """Chat with the team"""
        return self.start(message)

    def get_results(self) -> dict:
        """Get results from all agents"""
        return self._last_results

    def __repr__(self) -> str:
        return f"JarvisTeam(agents={len(self.agents)}, process={self.process})"


def create_team(
    agent_configs: List[dict],
    llm: str = "llama-3.1-8b-instant",
    process: str = "sequential"
) -> JarvisTeam:
    """
    Factory function to create a JarvisTeam from configs.
    
    Args:
        agent_configs: List of dicts with name, role, goal, backstory
        llm: Model to use
        process: "sequential" or "parallel"
    
    Example:
        create_team([
            {"name": "Researcher", "role": "Research", "goal": "Research topics", "backstory": "Expert researcher"},
            {"name": "Writer", "role": "Writer", "goal": "Write content", "backstory": "Skilled writer"}
        ])
    """
    agents = []
    for config in agent_configs:
        agent = Agent(
            name=config.get("name", "Agent"),
            instructions=f"You are {config.get('role', 'Assistant')}. {config.get('goal', 'Help user')}. {config.get('backstory', '')}",
            llm=llm
        )
        agents.append(agent)

    return JarvisTeam(agents=agents, process=process, llm=llm)