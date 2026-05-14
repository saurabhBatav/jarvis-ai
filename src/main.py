"""Jarvis Interactive Chat Interface"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env
from dotenv import load_dotenv

# Find .env file in project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path, override=True)  # override shell env vars

from src.agents.base import JarvisAssistant
from src.agents.domain import FinanceAgent, ResearchAgent, WorkLifeAgent, HealthAgent, SearchAgent
from src.agents.domain.news_summary import NewsSummaryAgent
from src.agents.documentation.doc_agent import DocAgent
from src.agents.registry import registry
from src.memory import MemoryManager
from src.user_profile import profile


class Jarvis:
    """Main Jarvis interface with domain agents"""
    
    def __init__(self):
        # Set up environment
        if not os.getenv('OPENAI_API_KEY'):
            os.environ['OPENAI_API_KEY'] = os.getenv('GROQ_API_KEY', '')
        if not os.getenv('OPENAI_BASE_URL'):
            os.environ['OPENAI_BASE_URL'] = 'https://api.groq.com/openai/v1'
        
        # Initialize main assistant
        self.assistant = JarvisAssistant(llm="llama-3.1-8b-instant")
        
        # Initialize domain agents
        self.finance = FinanceAgent()
        self.research = ResearchAgent()
        self.worklife = WorkLifeAgent()
        self.health = HealthAgent()
        self.search = SearchAgent()
        self.news_summary = NewsSummaryAgent()
        self.documentation = DocAgent()
        
        # Memory
        self.memory = MemoryManager()
        self.memory.initialize()
        
        # Agent Registry
        self.registry = registry
        
        # User Profile
        self.profile = profile
        self.profile.increment_conversation()
        
        # Personalized greeting
        print(f"\n{self.profile.get_welcome_message()}")
        print(f"\n📋 Available Agents: {len(self.registry.get_all_agents())}")
        for name, info in self.registry.get_all_agents().items():
            print(f"  - {name}: {info['description'][:60]}...")
    
    def route_task(self, message: str) -> str:
        """Route message to appropriate agent"""
        # Extract the actual user message (before Context: prefix)
        if "\n\nContext:" in message:
            actual_message = message.split("\n\nContext:")[0]
            msg_lower = actual_message.lower()
        else:
            msg_lower = message.lower()
        
        # URL detection FIRST - fetch web pages
        if 'http://' in message or 'https://' in message:
            return self._handle_search(message)
        
        # Search keywords FIRST (before news/other)
        if any(k in msg_lower for k in ['search', 'find', 'look up', 'google', 'web']):
            return self._handle_search(message)
        
        # News Summary keywords - BEFORE general news
        if any(k in msg_lower for k in ['news summary', 'news slides', 'create presentation', '10 slides', 'news presentation', 'summarize news']):
            return self._handle_news_summary(message)
        
        # Documentation Agent keywords
        if any(k in msg_lower for k in ['documentation', 'doc', 'how to', 'example', 'help me build', 'create agent', 'show me code', 'reference']):
            return self._handle_documentation(message)
        
        # Personalization commands - more specific patterns first
        if any(k in msg_lower for k in ['my name is', 'call me']):
            return self._handle_set_name(message)
        
        if ' i am ' in msg_lower and 'interested' not in msg_lower:
            return self._handle_set_name(message)
        
        if any(k in msg_lower for k in ['personality', 'be my', 'act as', 'behave']):
            return self._handle_set_personality(message)
        
        if any(k in msg_lower for k in ['prefer', 'i like', 'i want', 'settings', 'configure']):
            return self._handle_set_preferences(message)
        
        if 'profile' in msg_lower or 'about me' in msg_lower:
            return self._handle_show_profile(message)
        
        # EXPLICIT REMEMBER COMMANDS - Route to custom LTM
        remember_patterns = ['remember', 'memorize', "don't forget", 'dont forget']
        if any(k in msg_lower for k in remember_patterns):
            # Store to custom LTM (ChromaDB)
            self._store_to_ltm(message, "")
            return "Got it! I've stored that in my memory. You can ask me to remember things and I'll store them persistently."
        
        # MEMORY QUERIES - Let LLM agent handle (has built-in memory)
        # Pass to assistant - PraisonAI built-in memory will handle it
        # BUT also search custom LTM as context
        
        # Finance keywords
        if any(k in msg_lower for k in ['stock', 'share', 'portfolio', 'crypto', 'invest', 'price', 'trading', 'aapl', 'googl', 'msft', 'tsla']):
            return self._handle_finance(message)
        
        # Research keywords
        elif any(k in msg_lower for k in ['research', 'paper', 'academic', 'study', 'find information', 'arxiv', 'pubmed']):
            return self._handle_research(message)
        
        # Work-Life keywords
        elif any(k in msg_lower for k in ['weather', 'task', 'todo', 'time', 'holiday', 'calendar']):
            return self._handle_worklife(message)
        
        # News only (without search keyword)
        elif 'news' in msg_lower:
            return self._handle_worklife(message)
        
        # Health keywords
        elif any(k in msg_lower for k in ['health', 'weight', 'exercise', 'sleep', 'mood', 'bmi', 'water', 'symptom']):
            return self._handle_health(message)
        
        # Default to main assistant (with built-in PraisonAI memory + session)
        else:
            # Check custom LTM for relevant context and pass to LLM
            custom_memory_context = ""
            if self.memory.ltm.count() > 0:
                # Try multiple search approaches
                results = []
                
                # 1. Direct search
                direct_results = self.memory.search_memory(message, n_results=10)
                results.extend(direct_results)
                
                # 2. Extract key nouns and search (for "favorite X" patterns)
                msg_lower = message.lower()
                if 'favorite' in msg_lower or 'my fav' in msg_lower:
                    # Extract what they're asking about
                    import re
                    match = re.search(r'favorite\s+(\w+)', msg_lower)
                    if match:
                        topic = match.group(1)
                        topic_results = self.memory.search_memory(topic, n_results=10)
                        results.extend(topic_results)
                
                # Get unique results with good similarity
                seen = set()
                relevant_memories = []
                for r in results:
                    text = r['text']
                    if text in seen:
                        continue
                    
                    dist = r.get('distance', 999)
                    # Accept if: good distance OR explicit memory
                    if dist < 1.4 or 'User memory:' in text or 'explicitly remembered' in text:
                        clean_text = text.replace("User memory: ", "").replace("User preference: ", "").replace("User explicitly remembered: ", "")
                        relevant_memories.append(clean_text)
                        seen.add(text)
                    
                    if len(relevant_memories) >= 3:
                        break
                
                if relevant_memories:
                    custom_memory_context = "\n\n[Your persistent memories: " + " | ".join(relevant_memories[:3]) + "]"
            
            return self.assistant.start(message + custom_memory_context)
    
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
    
    def _handle_news_summary(self, message: str) -> str:
        """Handle news summary and presentation requests"""
        import re
        msg_lower = message.lower()
        
        # Extract topic from message
        # Patterns like "news summary about X" or "news slides for X"
        topic = "technology"  # default
        
        # Try to extract topic
        patterns = [
            r'news\s+(?:summary|slides)\s+(?:about|for|on)?\s*(\w+)',
            r'create\s+(?:news|presentation)\s+(?:about|for)?\s*(\w+)',
            r'summarize\s+(?:news|about)\s*(\w+)',
            r'(\w+)\s+news\s+(?:summary|slides)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, msg_lower)
            if match:
                topic = match.group(1)
                break
        
        # Remove trigger words to get the topic
        for word in ['news summary', 'news slides', 'create presentation', 'summarize', 'about', 'for']:
            if word in msg_lower:
                topic = msg_lower.split(word)[-1].strip()
                break
        
        # Run the news summary agent
        result = self.news_summary.run(topic, "news_summary.md")
        
        # Read the generated file
        try:
            with open("news_summary.md", "r") as f:
                content = f.read()
            return f"📰 Generated 10-slide news summary for '{topic}':\n\n{content[:1500]}...\n\nSaved to: news_summary.md"
        except:
            return result
    
    def _handle_documentation(self, message: str) -> str:
        """Handle documentation and code example requests"""
        import re
        msg_lower = message.lower()
        
        # Extract the topic from message
        # Patterns: "help me build X", "show me example for X", "documentation for X"
        patterns = [
            r'(?:show me|help me|find|get)\s+(?:example\s+)?(?:for|about)?\s+(\w+)',
            r'documentation\s+(?:for|about)?\s+(\w+)',
            r'doc\s+(?:for|about)?\s+(\w+)',
            r'how to\s+(\w+)',
            r'reference\s+(?:for|about)?\s+(\w+)',
        ]
        
        topic = "agent"  # default
        for pattern in patterns:
            match = re.search(pattern, msg_lower)
            if match:
                topic = match.group(1)
                break
        
        # If no pattern matched, try last resort
        if topic == "agent":
            for word in ['agent', 'workflow', 'memory', 'mcp', 'serve', 'tool']:
                if word in msg_lower:
                    topic = word
                    break
        
        # Run the documentation agent
        try:
            result = self.documentation.search_documentation(topic)
            # Limit response length
            if len(result) > 1500:
                return f"📚 Documentation for '{topic}':\n\n{result[:1500]}...\n\nSee full result in docs or run again."
            return f"📚 Documentation for '{topic}':\n\n{result}"
        except Exception as e:
            return f"Documentation Agent error: {str(e)}. Try: 'show me example for agent' or 'help me build workflow'"
    
    def _handle_set_name(self, message: str) -> str:
        """Handle setting user's name"""
        import re
        msg_lower = message.lower()
        
        patterns = [
            r'my name is (\w+)',
            r'call me (\w+)',
        ]
        
        name = None
        for pattern in patterns:
            match = re.search(pattern, msg_lower)
            if match:
                name = match.group(1).capitalize()
                break
        
        if not name:
            return "What would you like me to call you?"
        
        self.profile.set_name(name)
        return f"✅ Got it! I'll call you {name} from now on. Nice to meet you!"
    
    def _handle_set_personality(self, message: str) -> str:
        """Handle personality mode changes"""
        msg_lower = message.lower()
        
        if 'friend' in msg_lower or 'friendly' in msg_lower:
            self.profile.set_personality_mode("friend")
            return "😊 Got it! I'll be your friendly companion from now on."
        elif 'teacher' in msg_lower or 'tutor' in msg_lower:
            self.profile.set_personality_mode("teacher")
            return "📚 Got it! I'll be your patient teacher from now on."
        elif 'professional' in msg_lower or 'assistant' in msg_lower:
            self.profile.set_personality_mode("assistant")
            return "💼 Got it! I'll be your professional assistant from now on."
        elif 'companion' in msg_lower:
            self.profile.set_personality_mode("companion")
            return "🤝 Got it! I'll be your companion from now on."
        else:
            return "I can be: Assistant (professional), Companion (friendly), Teacher (educational), or Friend (casual). Which would you like?"
    
    def _handle_set_preferences(self, message: str) -> str:
        """Handle user preference settings"""
        msg_lower = message.lower()
        
        # Communication style
        if 'brief' in msg_lower or 'short' in msg_lower:
            self.profile.set_preference("response_length", "short")
            return "✅ I'll give you brief, concise responses."
        elif 'detailed' in msg_lower or 'long' in msg_lower:
            self.profile.set_preference("response_length", "long")
            return "✅ I'll give you detailed responses with more information."
        elif 'balanced' in msg_lower:
            self.profile.set_preference("response_length", "medium")
            return "✅ I'll balance between brief and detailed."
        
        # Formality
        if 'formal' in msg_lower:
            self.profile.set_preference("formality", "formal")
            return "✅ I'll be more formal in my responses."
        elif 'casual' in msg_lower:
            self.profile.set_preference("formality", "casual")
            return "✅ I'll be more casual and friendly."
        
        # Interests
        if 'interested in' in msg_lower or 'like' in msg_lower:
            # Extract topic
            for word in ['interested in', 'like', 'love', 'enjoy']:
                if word in msg_lower:
                    topic = msg_lower.split(word)[-1].strip().strip('.')
                    if topic:
                        self.profile.add_interest(topic)
                        return f"✅ Added '{topic}' to your interests!"
        
        return "I understand preferences like: brief/detailed responses, formal/casual style. Say 'I'm interested in [topic]' to add interests."
    
    def _handle_show_profile(self, message: str) -> str:
        """Show user profile"""
        name = self.profile.get_name()
        mode = self.profile.get_preference("personality_mode", "assistant")
        style = self.profile.get_preference("response_length", "medium")
        interests = self.profile.profile.get("interests", [])
        conv_count = self.profile.profile.get("conversation_count", 0)
        
        return f"""👤 Your Jarvis Profile:

📛 Name: {name}
🤖 Personality: {mode}
📝 Response style: {style}
💬 Conversations: {conv_count}
⭐ Interests: {', '.join(interests) if interests else 'None yet'}

Say 'my name is [Name]' to change your name.
Say 'be my friend' to change personality.
Say 'prefer brief responses' to adjust style."""
    
    def _handle_search(self, message: str) -> str:
        # Check if it's a URL
        if 'http://' in message or 'https://' in message:
            # Extract URL and fetch content
            import re
            urls = re.findall(r'https?://[^\s]+', message)
            if urls:
                return self.search.fetch(urls[0])
        
        query = message.replace('search', '').replace('find', '').replace('research about', '').strip()
        return self.search.quick_search(query)
    
    def _handle_memory_query(self, message: str) -> str:
        """Handle queries about user's stored memories"""
        msg_lower = message.lower()
        
        # Extract the query topic
        query = message.lower()
        memory_phrases = ["what is my", "what's my", "tell me about my", "remember my", "where do i", "where am i", "what do i like", "who am i"]
        for phrase in memory_phrases:
            if phrase in query:
                query = query.split(phrase, 1)[1].strip()
                break
        
        # If query is short, also search with full message for better matching
        if len(query) < 5:
            search_queries = [query, message.lower()]
        else:
            search_queries = [query]
        
        # Search LTM for relevant memories
        results = []
        for sq in search_queries:
            r = self.memory.search_memory(sq, n_results=10)
            for item in r:
                # Only accept results with good similarity (distance < 1.2)
                if item.get('distance', 999) < 1.2:
                    if item not in results:
                        results.append(item)
        
        # Fallback: if no good results, do keyword search on all LTM
        if not results:
            all_ltm = self.memory.ltm.get_all(limit=50)
            query_words = set(query.lower().split())
            for item in all_ltm:
                text_lower = item['text'].lower()
                if any(word in text_lower for word in query_words if len(word) > 2):
                    results.append(item)
                    if len(results) >= 5:
                        break
        
        # Also get entities
        entities = self.memory.entity.get_entities()
        entity_info = []
        for e in entities[:5]:
            attrs = e.attributes if hasattr(e, 'attributes') else {}
            entity_info.append(f"{e.name}: {attrs}")
        
        if results or entity_info:
            lines = ["📝 Here's what I remember:"]
            
            # Add LTM results
            for r in results:
                text = r['text']
                # Clean up the text
                text = text.replace("User preference: ", "").replace("User explicitly remembered: ", "").replace("User memory: ", "")
                lines.append(f"• {text}")
            
            # Add entity info
            if entity_info:
                lines.append("\n👤 Known about you:")
                for e in entity_info[:3]:
                    lines.append(f"  - {e}")
            
            return "\n".join(lines)
        else:
            # No memories found
            return "I don't have any stored memories about that. You can say 'Remember that...' to store something!"
    
    def _extract_entities(self, message: str) -> None:
        """Extract and track named entities from message"""
        import re
        # Extract capitalized words (potential names/entities)
        potential_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', message)
        
        # Common entity types to track
        entity_keywords = {
            'person': ['i am', 'my name is', 'called'],
            'company': ['company', 'work at', 'working at', 'employer'],
            'location': ['live in', 'located in', 'city', 'country'],
            'preference': ['i like', 'i prefer', 'i love', 'hate', 'favorite'],
        }
        
        msg_lower = message.lower()
        
        for entity in potential_entities[:3]:
            if len(entity) > 2:
                # Determine entity type
                entity_type = 'unknown'
                for etype, keywords in entity_keywords.items():
                    if any(k in msg_lower for k in keywords):
                        entity_type = etype
                        break
                
                # Add to entity memory
                self.memory.add_entity(entity, entity_type, {'source': 'chat'})
    
    def _store_to_ltm(self, message: str, response: str) -> None:
        """Store important information to LTM for semantic search"""
        msg_lower = message.lower()
        
        # DON'T store questions - they pollute memory
        if msg_lower.startswith('what') or msg_lower.startswith('how') or msg_lower.startswith('where') or msg_lower.startswith('when') or msg_lower.startswith('who'):
            return
        
        # EXPLICIT REMEMBER COMMANDS
        if 'remember' in msg_lower or 'memorize' in msg_lower or 'don\'t forget' in msg_lower:
            # Extract what to remember (everything after remember)
            remember_text = message
            if 'remember' in msg_lower:
                remember_text = message.lower().split('remember', 1)[1].strip()
            elif 'memorize' in msg_lower:
                remember_text = message.lower().split('memorize', 1)[1].strip()
            elif 'don\'t forget' in msg_lower:
                remember_text = message.lower().split('don\'t forget', 1)[1].strip()
            
            if remember_text and remember_text != message.lower():
                # Add context for better semantic search
                enriched_text = f"User memory: {remember_text}"
                self.memory.add_to_memory(
                    enriched_text,
                    metadata={'type': 'explicit_memory', 'source': 'chat'}
                )
            return
        
        # Store user preferences ONLY for factual statements (not questions)
        preference_patterns = ['i like', 'i prefer', 'i love', 'i hate', 'i hate']
        if any(k in msg_lower for k in preference_patterns):
            # Make sure it's a statement, not a question
            if '?' not in message and 'what' not in msg_lower[:10]:
                self.memory.add_to_memory(
                    f"User preference: {message}",
                    metadata={'type': 'preference', 'source': 'chat'}
                )
        
        # Store important facts from responses
        if 'portfolio' in msg_lower or 'holdings' in msg_lower:
            self.memory.add_to_memory(
                f"Finance query: {response[:200]}",
                metadata={'type': 'finance', 'source': 'chat'}
            )
        
        # Store research topics
        if any(k in msg_lower for k in ['research', 'learn', 'understand']):
            self.memory.add_to_memory(
                f"Research topic: {message}",
                metadata={'type': 'research', 'source': 'chat'}
            )
    
    def chat(self, message: str) -> str:
        """Main chat method with full 4-tier memory integration"""
        # 1. Store in STM (Short-Term Memory)
        self.memory.add_message('user', message)
        
        # 2. Extract entities (Entity Memory)
        self._extract_entities(message)
        
        # 3. Get context from LTM for better response
        ltm_context = ""
        if self.memory.ltm.count() > 0:
            results = self.memory.search_memory(message, n_results=2)
            if results:
                ltm_context = "Previous relevant info: " + " | ".join([r['text'][:100] for r in results])
        
        # 4. Get response (with LTM context if available)
        if ltm_context:
            enhanced_message = f"{message}\n\nContext: {ltm_context}"
            response = self.route_task(enhanced_message)
        else:
            response = self.route_task(message)
        
        # 5. Store to LTM for semantic search
        self._store_to_ltm(message, response)
        
        # 6. Store in STM (assistant response)
        self.memory.add_message('assistant', response)
        
        # 7. Track in Episodic Memory
        self.memory.track_interaction(
            user_input=message,
            response=response[:500] if len(response) > 500 else response,
            episode_type='chat',
            metadata={'source': 'interactive'}
        )
        
        return response
    
    def help(self) -> str:
        """Get help with available commands using registry"""
        return f"""🎯 Jarvis Commands:

{self.registry.get_capabilities_summary()}

Personalization:
- "My name is [Name]" - Set your name
- "Be my friend/teacher/assistant" - Change personality
- "I prefer brief/detailed responses" - Adjust style
- "I'm interested in [topic]" - Add interests
- "Profile" or "About me" - View your profile

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