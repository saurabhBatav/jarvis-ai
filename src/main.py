"""Jarvis Interactive Chat Interface"""

import os
import sys
from src.agents.base import JarvisAssistant
from src.agents.domain import FinanceAgent, ResearchAgent, WorkLifeAgent, HealthAgent, SearchAgent
from src.memory import MemoryManager


class Jarvis:
    """Main Jarvis interface with domain agents"""
    
    def __init__(self):
        # Set up environment
        os.environ.setdefault('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY', ''))
        os.environ.setdefault('OPENAI_BASE_URL', 'https://api.groq.com/openai/v1')
        
        # Initialize main assistant
        self.assistant = JarvisAssistant(llm="llama-3.1-8b-instant")
        
        # Initialize domain agents
        self.finance = FinanceAgent()
        self.research = ResearchAgent()
        self.worklife = WorkLifeAgent()
        self.health = HealthAgent()
        self.search = SearchAgent()
        
        # Memory
        self.memory = MemoryManager()
        self.memory.initialize()
        
        print("✅ Jarvis initialized and ready!")
    
    def route_task(self, message: str) -> str:
        """Route message to appropriate agent"""
        msg_lower = message.lower()
        
        # Finance keywords
        if any(k in msg_lower for k in ['stock', 'share', 'portfolio', 'crypto', 'invest', 'price', 'trading']):
            return self._handle_finance(message)
        
        # Research keywords
        elif any(k in msg_lower for k in ['research', 'paper', 'academic', 'study', 'find information', 'arxiv', 'pubmed']):
            return self._handle_research(message)
        
        # Work-Life keywords
        elif any(k in msg_lower for k in ['weather', 'task', 'todo', 'news', 'time', 'holiday', 'calendar']):
            return self._handle_worklife(message)
        
        # Health keywords
        elif any(k in msg_lower for k in ['health', 'weight', 'exercise', 'sleep', 'mood', 'bmi', 'water', 'symptom']):
            return self._handle_health(message)
        
        # Search keywords
        elif any(k in msg_lower for k in ['search', 'find', 'look up', 'google', 'web']):
            return self._handle_search(message)
        
        # Default to main assistant
        else:
            return self.assistant.start(message)
    
    def _handle_finance(self, message: str) -> str:
        msg = message.lower()
        if 'portfolio' in msg or 'my holding' in msg:
            return self.finance.check_portfolio()
        elif 'add' in msg:
            # Extract symbol, quantity, price
            return "To add a holding, say: 'Add 10 shares of AAPL at 150'"
        else:
            # Extract stock symbol
            import re
            symbols = re.findall(r'\b[A-Z]{2,5}\b', message)
            if symbols:
                return self.finance.get_stock_info(symbols[0])
            return self.finance.check_portfolio()
    
    def _handle_research(self, message: str) -> str:
        return self.research.research(message.replace('research', '').strip())
    
    def _handle_worklife(self, message: str) -> str:
        msg = message.lower()
        if 'weather' in msg:
            return self.worklife.weather()
        elif 'task' in msg or 'todo' in msg:
            return self.worklife.list_tasks()
        elif 'news' in msg:
            return self.worklife.news()
        else:
            return self.worklife.daily_briefing()
    
    def _handle_health(self, message: str) -> str:
        msg = message.lower()
        if 'bmi' in msg:
            return "Enter: weight in kg and height in cm"
        elif 'tip' in msg or 'advice' in msg:
            return self.health.quick_tip()
        elif 'summary' in msg or 'report' in msg:
            return self.health.summary()
        else:
            return self.health.quick_tip()
    
    def _handle_search(self, message: str) -> str:
        query = message.replace('search', '').replace('find', '').strip()
        return self.search.quick_search(query)
    
    def chat(self, message: str) -> str:
        """Main chat method"""
        # Store in memory
        self.memory.add_message('user', message)
        
        # Get response
        response = self.route_task(message)
        
        # Store response
        self.memory.add_message('assistant', response)
        
        return response
    
    def help(self) -> str:
        return """🎯 Jarvis Commands:

Finance:
- "What's the price of AAPL?" 
- "Check my portfolio"
- "Add 10 shares of AAPL at 150"

Research:
- "Research quantum computing"
- "Find papers on AI"

Work-Life:
- "What's the weather?"
- "Show my tasks"
- "Latest tech news"

Health:
- "Health summary"
- "BMI tip"
- "What's my water goal?"

Search:
- "Search for AI news"
- "Find information about..."

General:
- Just chat normally! 🤖"""


def main():
    """Interactive Jarvis chat"""
    print("\n" + "="*50)
    print("🤖 JARVIS - AI ASSISTANT")
    print("="*50)
    print("Type 'help' for commands or 'quit' to exit\n")
    
    jarvis = Jarvis()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye! Jarvis shutting down...")
                break
            
            if user_input.lower() == 'help':
                print(jarvis.help())
                continue
            
            if user_input.lower() == 'status':
                print(f"Memory: {jarvis.memory.get_stats()}")
                continue
            
            # Get Jarvis response
            response = jarvis.chat(user_input)
            print(f"\n🤖 Jarvis: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {str(e)}\n")


if __name__ == "__main__":
    main()