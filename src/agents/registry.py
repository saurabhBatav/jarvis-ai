"""Agent Registry - Central registry of all Jarvis agents and capabilities"""

from typing import Dict, List, Any


class AgentRegistry:
    """Central registry of all available agents"""
    
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self._register_all_agents()
    
    def _register_all_agents(self):
        """Register all available agents with their capabilities"""
        
        # Finance Agent
        self.register_agent(
            name="FinanceAgent",
            description="Handles financial queries - stock prices, crypto, investments, portfolio analysis",
            keywords=["stock", "share", "portfolio", "crypto", "invest", "price", "trading", "aapl", "googl", "msft", "tsla", "bitcoin", "eth", "market", "fund", "bond", "dividend", "nasdaq", "nyse"],
            handler_name="finance",
            capabilities=[
                "Get stock prices",
                "Get crypto prices", 
                "Portfolio analysis",
                "Investment recommendations",
                "Market news"
            ]
        )
        
        # Research Agent
        self.register_agent(
            name="ResearchAgent",
            description="Academic research, papers, scientific articles, arxiv searches",
            keywords=["research", "paper", "academic", "study", "find information", "arxiv", "pubmed", "scientific", "journal", "thesis", "article"],
            handler_name="research",
            capabilities=[
                "Search arXiv for papers",
                "Academic paper search",
                "Research topic exploration"
            ]
        )
        
        # Work-Life Agent
        self.register_agent(
            name="WorkLifeAgent",
            description="Weather, tasks, calendar, daily briefings, news, productivity",
            keywords=["weather", "task", "todo", "time", "holiday", "calendar", "news", "briefing", "schedule", "meeting", "event"],
            handler_name="worklife",
            capabilities=[
                "Get weather updates",
                "Task/todo management",
                "Daily briefing",
                "Weather forecast"
            ]
        )
        
        # Health Agent
        self.register_agent(
            name="HealthAgent",
            description="Health tracking, BMI calculation, exercise, sleep, nutrition, wellness",
            keywords=["health", "weight", "exercise", "sleep", "mood", "bmi", "water", "symptom", "fitness", "diet", "nutrition", "wellness"],
            handler_name="health",
            capabilities=[
                "BMI calculation",
                "Health tips",
                "Exercise recommendations",
                "Sleep tracking",
                "Water intake reminders"
            ]
        )
        
        # Search Agent
        self.register_agent(
            name="SearchAgent",
            description="Web search, URL fetching, information retrieval",
            keywords=["search", "find", "look up", "google", "web", "fetch", "http", "https", "url"],
            handler_name="search",
            capabilities=[
                "Web search",
                "URL content fetching",
                "Information retrieval"
            ]
        )
        
        # News Summary Agent
        self.register_agent(
            name="NewsSummaryAgent",
            description="Create news summaries and presentations from the web",
            keywords=["news summary", "news slides", "create presentation", "10 slides", "news presentation", "summarize news", "presentation about"],
            handler_name="news_summary",
            capabilities=[
                "Generate 10-slide news presentation",
                "Summarize news for any topic",
                "Create markdown presentations"
            ]
        )
        
        # Documentation Agent
        self.register_agent(
            name="DocumentationAgent",
            description="Search documentation and code examples for building agents/workflows",
            keywords=["documentation", "doc", "how to", "example", "help me build", "create agent", "show me code", "reference", "code example", "implementation"],
            handler_name="documentation",
            capabilities=[
                "Search PraisonAI docs",
                "Find code examples from local examples folder",
                "Reference agent/workflow implementations"
            ]
        )
    
    def register_agent(self, name: str, description: str, keywords: List[str], 
                       handler_name: str, capabilities: List[str]):
        """Register an agent"""
        self.agents[name] = {
            "description": description,
            "keywords": keywords,
            "handler": handler_name,
            "capabilities": capabilities
        }
    
    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered agents"""
        return self.agents
    
    def find_agent_by_keyword(self, query: str) -> List[Dict[str, str]]:
        """Find agents that match keywords in the query"""
        query_lower = query.lower()
        matches = []
        
        for name, info in self.agents.items():
            for keyword in info["keywords"]:
                if keyword.lower() in query_lower:
                    matches.append({
                        "agent": name,
                        "handler": info["handler"],
                        "keyword_matched": keyword,
                        "description": info["description"]
                    })
                    break
        
        return matches
    
    def get_agent_info(self, agent_name: str) -> Dict[str, Any]:
        """Get information about a specific agent"""
        return self.agents.get(agent_name, {})
    
    def get_system_prompt(self) -> str:
        """Generate a system prompt describing all available agents"""
        prompt = """You are Jarvis, an AI assistant with access to multiple specialized agents.

Available Agents:
"""
        for name, info in self.agents.items():
            prompt += f"""
- {name}: {info['description']}
  Keywords: {', '.join(info['keywords'][:10])}...
  Capabilities: {', '.join(info['capabilities'])}
"""
        prompt += """
When a user asks something, match their query against agent keywords to route to the correct specialized agent.
If no specific agent matches, use the main assistant to handle general requests.
"""
        return prompt
    
    def get_capabilities_summary(self) -> str:
        """Get a summary of all agent capabilities"""
        summary = "Jarvis has the following capabilities:\n\n"
        for name, info in self.agents.items():
            summary += f"**{name}**: {info['description']}\n"
            for cap in info['capabilities']:
                summary += f"  - {cap}\n"
            summary += "\n"
        return summary


# Global registry instance
registry = AgentRegistry()