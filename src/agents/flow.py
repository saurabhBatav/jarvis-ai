"""AgentFlow - Deterministic pipeline patterns for Jarvis"""

from typing import Callable, Optional, Any, List
from praisonaiagents import AgentFlow as PraisonFlow
from praisonaiagents import Agent


class FlowPatterns:
    """
    Implements AgentFlow patterns for Jarvis:
    - route(): Conditional branching based on agent output
    - parallel(): Simultaneous execution with aggregator
    - loop(): Iterative processing over collections
    - repeat(): Evaluator-Optimizer pattern
    """

    @staticmethod
    def route(
        agents: List[Agent],
        condition_fn: Callable[[str], str],
        default_agent: Agent = None
    ) -> Callable:
        """
        Create a routing flow that selects agent based on condition.
        
        Args:
            agents: List of agents to route between
            condition_fn: Function that takes input and returns agent name
            default_agent: Fallback agent if no condition matches
        """
        def route_flow(input_data: str) -> str:
            selected = condition_fn(input_data)
            for agent in agents:
                if agent.name == selected:
                    return agent.start(input_data)
            if default_agent:
                return default_agent.start(input_data)
            return "No matching agent found"
        return route_flow

    @staticmethod
    def parallel(
        agents: List[Agent],
        aggregator: Optional[Callable[[List[str]], str]] = None
    ) -> Callable:
        """
        Execute multiple agents simultaneously and aggregate results.
        
        Args:
            agents: List of agents to run in parallel
            aggregator: Optional function to combine results
        """
        import concurrent.futures

        def parallel_flow(input_data: str) -> str:
            results = []

            def run_agent(agent):
                return agent.start(input_data)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(run_agent, agent) for agent in agents]
                results = [f.result() for f in futures]

            if aggregator:
                return aggregator(results)
            return "\n\n".join(results)
        return parallel_flow

    @staticmethod
    def loop(
        agent: Agent,
        collection: List[Any],
        item_transform: Optional[Callable] = None
    ) -> Callable:
        """
        Iterate over a collection and process each item.
        
        Args:
            agent: Agent to process each item
            collection: List/CSV/JSON to iterate over
            item_transform: Optional transform function for items
        """
        def loop_flow() -> List[str]:
            results = []
            for item in collection:
                if item_transform:
                    processed = item_transform(item)
                else:
                    processed = str(item)
                result = agent.start(processed)
                results.append(result)
            return results
        return loop_flow

    @staticmethod
    def repeat(
        agent: Agent,
        validator: Callable[[str], bool],
        max_iterations: int = 5
    ) -> Callable:
        """
        Evaluator-Optimizer pattern: repeat until validation passes.
        
        Args:
            agent: Agent that refines output
            validator: Function that returns True if output is acceptable
            max_iterations: Maximum refinement attempts
        """
        def repeat_flow(input_data: str) -> str:
            current_output = agent.start(input_data)

            for _ in range(max_iterations):
                if validator(current_output):
                    return current_output
                current_output = agent.start(f"Refine this: {current_output}")

            return current_output
        return repeat_flow


class JarvisFlow:
    """High-level flow orchestration for Jarvis"""

    def __init__(self):
        self.patterns = FlowPatterns()
        self._current_flow = None

    def create_workflow(self, steps: List[dict]) -> Any:
        """
        Create a workflow from step definitions.
        
        Example steps:
        [
            {"type": "agent", "agent": research_agent, "task": "Research AI"},
            {"type": "agent", "agent": writer_agent, "task": "Write summary"},
            {"type": "parallel", "agents": [agent1, agent2], "task": "multi-task"}
        ]
        """
        results = []

        for step in steps:
            step_type = step.get("type", "agent")

            if step_type == "agent":
                agent = step.get("agent")
                task = step.get("task")
                result = agent.start(task)
                results.append(result)

            elif step_type == "parallel":
                agents = step.get("agents", [])
                task = step.get("task")
                flow = self.patterns.parallel(agents)
                result = flow(task)
                results.append(result)

            elif step_type == "loop":
                agent = step.get("agent")
                collection = step.get("collection")
                flow = self.patterns.loop(agent, collection)
                result = flow()
                results.append(result)

            elif step_type == "repeat":
                agent = step.get("agent")
                validator = step.get("validator")
                flow = self.patterns.repeat(agent, validator)
                result = flow(step.get("task", ""))
                results.append(result)

        return results

    def __repr__(self) -> str:
        return f"JarvisFlow()"