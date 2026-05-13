"""Domain-specific agents for Jarvis"""

from .finance import FinanceAgent
from .research import ResearchAgent
from .worklife import WorkLifeAgent
from .health import HealthAgent
from .search import SearchAgent

__all__ = [
    "FinanceAgent",
    "ResearchAgent", 
    "WorkLifeAgent",
    "HealthAgent",
    "SearchAgent"
]