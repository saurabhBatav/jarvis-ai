"""Jarvis Interactive Chat Interface - Enhanced with verbose logging"""

import os
import sys
import time

# FIRST: Fix protobuf compatibility for ChromaDB
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# FIRST: Load env vars before any other imports
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_path = os.path.join(_project_root, '.env')
if os.path.exists(_env_path):
    with open(_env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                if key in ['OPENAI_API_KEY', 'OPENAI_BASE_URL']:
                    os.environ[key] = val

# Add project root to path
sys.path.insert(0, _project_root)

# ============================================================
# 📊 VERBOSE LOGGING SYSTEM
# ============================================================

class JarvisLogger:
    """Colored logging for Jarvis operations"""

    COLORS = {
        'HEADER': '\033[95m',
        'BLUE': '\033[94m',
        'CYAN': '\033[96m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'RED': '\033[91m',
        'END': '\033[0m',
        'BOLD': '\033[1m',
    }

    @staticmethod
    def agent(name):
        print(f"{JarvisLogger.COLORS['GREEN']}🤖[AGENT]{JarvisLogger.COLORS['END']} {name}")

    @staticmethod
    def tool(name):
        print(f"{JarvisLogger.COLORS['CYAN']}🔧[TOOL]{JarvisLogger.COLORS['END']} {name}")

    @staticmethod
    def pattern(name):
        print(f"{JarvisLogger.COLORS['YELLOW']}🔀[PATTERN]{JarvisLogger.COLORS['END']} {name}")

    @staticmethod
    def memory(op):
        print(f"{JarvisLogger.COLORS['BLUE']}💾[MEMORY]{JarvisLogger.COLORS['END']} {op}")

    @staticmethod
    def step(msg):
        print(f"{JarvisLogger.COLORS['HEADER']}  →{JarvisLogger.COLORS['END']} {msg}")

    @staticmethod
    def thinking(msg):
        print(f"{JarvisLogger.COLORS['CYAN']}  💭{JarvisLogger.COLORS['END']} {msg}")

    @staticmethod
    def success(msg):
        print(f"{JarvisLogger.COLORS['GREEN']}  ✓{JarvisLogger.COLORS['END']} {msg}")

    @staticmethod
    def error(msg):
        print(f"{JarvisLogger.COLORS['RED']}  ✗{JarvisLogger.COLORS['END']} {msg}")

logger = JarvisLogger()


from src.agents.base import JarvisAssistant
from src.agents.domain import FinanceAgent, ResearchAgent, WorkLifeAgent, HealthAgent, SearchAgent
from src.agents.domain.news_summary import NewsSummaryAgent
from src.agents.domain.planner import TodoPlanner
from src.agents.documentation.doc_agent import DocAgent
from src.agents.registry import registry
from src.memory import MemoryManager
from src.user_profile import profile
from src.mcp_tools import get_mcp_tools


class Jarvis:
    """Main Jarvis interface with domain agents - Enhanced logging"""

    def __init__(self):
        logger.step("Initializing Jarvis...")

        # Initialize main assistant
        logger.step("Loading main Jarvis assistant...")
        self.assistant = JarvisAssistant(llm="llama-3.1-8b-instant")
        logger.success("Jarvis assistant loaded")

        # Initialize domain agents
        logger.step("Loading domain agents...")
        self.finance = FinanceAgent()
        logger.tool("FinanceAgent loaded")
        self.research = ResearchAgent()
        logger.tool("ResearchAgent loaded")
        self.worklife = WorkLifeAgent()
        logger.tool("WorkLifeAgent loaded")
        self.health = HealthAgent()
        logger.tool("HealthAgent loaded")
        self.search = SearchAgent()
        logger.tool("SearchAgent loaded")
        self.news_summary = NewsSummaryAgent()
        logger.tool("NewsSummaryAgent loaded")
        self.documentation = DocAgent()
        logger.tool("DocumentationAgent loaded")
        self.planner = TodoPlanner()
        logger.tool("PlannerAgent loaded")

        # Memory
        logger.step("Initializing memory system...")
        self.memory = MemoryManager()
        self.memory.initialize()
        logger.success("4-tier memory initialized")

        # Agent Registry
        self.registry = registry
        logger.success(f"Agent registry: {len(self.registry.get_all_agents())} agents")

        # User Profile
        self.profile = profile
        self.profile.increment_conversation()

        # Personalized greeting
        print(f"\n{self.profile.get_welcome_message()}")

        # Add weather/time info for JARVIS mode
        if self.profile.is_jarvis_mode():
            self._jarvis_status_report()

        logger.step(f"Available agents: {len(self.registry.get_all_agents())}")
        for name, info in self.registry.get_all_agents().items():
            print(f"  • {name}")

    def _jarvis_status_report(self):
        from datetime import datetime
        now = datetime.now()
        hour = now.hour
        time_greeting = "Good morning" if 6 <= hour < 12 else "Good afternoon" if 12 <= hour < 18 else "Good evening"
        name = self.profile.get_name()
        print(f"🤖 {time_greeting}, {name}.")
        print(f"   It's {now.strftime('%I:%M %A')}")
        import random
        statuses = [
            "Systems online. All subsystems operational.",
            "Running diagnostic checks. Everything looks good.",
            "At your service, sir.",
            "Ready for your instructions.",
            "Monitoring your requests.",
        ]
        print(f"   {random.choice(statuses)}")

    def route_task(self, message: str) -> str:
        """Route message with verbose logging"""

        # Extract actual message
        if "\n\nContext:" in message:
            actual_message = message.split("\n\nContext:")[0]
            msg_lower = actual_message.lower()
        else:
            msg_lower = message.lower()

        logger.step(f"Processing: '{message[:50]}...'")

        # Check custom memory first
        relevant_memories = []
        if self.memory.ltm.count() > 0:
            logger.step("Step 1: Searching memory...")
            logger.memory("Searching memory...")
            results = self.memory.search_memory(message, n_results=5)
            for r in results:
                dist = r.get('distance', 999)
                # Use higher threshold (1.5) for better recall
                if dist < 1.5:
                    clean = r['text'].replace("User memory: ", "").replace("User preference: ", "")[:80]
                    relevant_memories.append(clean)
                    if len(relevant_memories) >= 2:
                        break
            if relevant_memories:
                logger.success(f"Found {len(relevant_memories)} memory match(es)")
                for mem in relevant_memories:
                    logger.step(f"  → Memory: '{mem[:60]}...'")
            else:
                logger.step("No relevant memories found")

        # === ROUTING LOGIC ===

        # URL detection
        if 'http://' in message or 'https://' in message:
            logger.agent("Routing to: SearchAgent (URL detected)")
            return self._handle_search(message)

        # GitHub MCP - check BEFORE general search
        if any(k in msg_lower for k in ['search github', 'find repo', 'github search', 'github repo', 'popular github', 'viral github', 'top github', 'github trending', 'github popular']):
            logger.agent("Routing to: GitHub MCP")
            return self._handle_github_search(message)

        # Content/Carousel Creation
        if any(k in msg_lower for k in ['carousel', 'linkedin post', 'social media', 'build post', 'create post']):
            logger.agent("Routing to: ContentAgent")
            return self._handle_content_creation(message)

        # Search (general)
        if any(k in msg_lower for k in ['search', 'find', 'look up', 'google', 'web']):
            logger.agent("Routing to: SearchAgent")
            return self._handle_search(message)

        # News Summary
        if any(k in msg_lower for k in ['news summary', 'news slides', 'create presentation', '10 slides', 'news presentation', 'summarize news']):
            logger.agent("Routing to: NewsSummaryAgent")
            return self._handle_news_summary(message)

        # Planner
        if any(k in msg_lower for k in ['create todo', 'make todo', 'add todo', 'plan', 'make plan', 'create plan', 'planning', 'create list', 'add to my list']):
            logger.agent("Routing to: PlannerAgent")
            return self._handle_planner(message)

        # Documentation
        if any(k in msg_lower for k in ['documentation', 'doc', 'how to', 'example', 'help me build', 'create agent', 'show me code', 'reference']):
            logger.agent("Routing to: DocumentationAgent")
            return self._handle_documentation(message)

        # Personalization
        if any(k in msg_lower for k in ['my name is', 'call me']):
            logger.agent("Routing to: UserProfile (name setting)")
            return self._handle_set_name(message)

        if any(k in msg_lower for k in ['personality', 'be my', 'act as', 'behave']):
            logger.agent("Routing to: UserProfile (personality)")
            return self._handle_set_personality(message)

        # === PATTERN DETECTION WITH LOGGING ===
        if any(k in msg_lower for k in ['parallel', 'simultaneously', 'at the same time']):
            logger.pattern("Detected: Parallel Execution pattern")
            from src.agents.advanced.parallel_execution import ParallelAgents
            pa = ParallelAgents()
            result = pa.process(message)
            # Store results for expand
            if hasattr(pa, '_last_results'):
                self._last_pattern_results = pa._last_results
            return result

        if any(k in msg_lower for k in ['loop', 'iterate', 'each item', 'for each']):
            logger.pattern("Detected: Loop/Iteration pattern")
            from src.agents.advanced.loop_iteration import LoopAgents
            return LoopAgents().process(message)

        if any(k in msg_lower for k in ['async', 'background', 'fire and forget']):
            logger.pattern("Detected: Async/Background pattern")
            from src.agents.advanced.async_tasks import AsyncAgents
            return AsyncAgents().process(message)

        if any(k in msg_lower for k in ['reflect', 'review', 'improve', 'self-critique']):
            logger.pattern("Detected: Self Reflection pattern")
            from src.agents.advanced.self_reflection import SelfReflectingAgent
            return SelfReflectingAgent().process(message)

        if any(k in msg_lower for k in ['structured', 'json', 'format as']):
            logger.pattern("Detected: Structured Output pattern")
            from src.agents.advanced.structured_output import StructuredOutputAgent
            return StructuredOutputAgent().process(message)

        if any(k in msg_lower for k in ['policy', 'rules', 'enforce', 'check policy']):
            logger.pattern("Detected: Policy Engine pattern")
            from src.agents.advanced.policy_engine import PolicyEngine
            return PolicyEngine().process(message)

        # === MCP TOOLS ===
        mcp_tools = get_mcp_tools()

        # Memory MCP
        if any(k in msg_lower for k in ['remember this', 'store this', 'save to memory']):
            logger.tool("Using: Memory MCP (store)")
            return self._handle_memory_store(message)

        if any(k in msg_lower for k in ['what do you remember', 'show memories', 'list memory']):
            logger.tool("Using: Memory MCP (list)")
            return mcp_tools['memory'].list_keys()

        # Time MCP
        if any(k in msg_lower for k in ['what time', 'current time', 'time in']):
            logger.tool("Using: Time MCP")
            tz = "UTC"
            if 'in' in msg_lower:
                tz = msg_lower.split('in')[-1].strip()
            return mcp_tools['time'].now(tz)

        # Filesystem MCP
        if msg_lower.strip().startswith('ls') or 'list files' in msg_lower or 'show directory' in msg_lower:
            logger.tool("Using: Filesystem MCP")
            path = "."
            if 'in' in msg_lower:
                path = msg_lower.split('in')[-1].strip()
            return mcp_tools['filesystem'].list_dir(path)

        # === DOMAIN AGENTS ===

        # Finance
        if any(k in msg_lower for k in ['stock', 'share', 'portfolio', 'crypto', 'invest', 'price', 'trading', 'aapl', 'googl', 'msft', 'tsla']):
            logger.agent("Routing to: FinanceAgent")
            return self._handle_finance(message)

        # Research
        elif any(k in msg_lower for k in ['research', 'paper', 'academic', 'study', 'find information', 'arxiv', 'pubmed']):
            logger.agent("Routing to: ResearchAgent")
            return self._handle_research(message)

        # Work-Life
        elif any(k in msg_lower for k in ['weather', 'task', 'todo', 'time', 'holiday', 'calendar']):
            logger.agent("Routing to: WorkLifeAgent")
            return self._handle_worklife(message)

        # News
        elif 'news' in msg_lower:
            logger.agent("Routing to: WorkLifeAgent (news)")
            return self._handle_worklife(message)

        # Health
        elif any(k in msg_lower for k in ['health', 'weight', 'exercise', 'sleep', 'mood', 'bmi', 'water', 'symptom']):
            logger.agent("Routing to: HealthAgent")
            return self._handle_health(message)

        # === DEFAULT: Jarvis Main Assistant ===
        else:
            logger.agent("Routing to: Jarvis (main assistant)")
            if self.profile.is_jarvis_mode():
                logger.thinking("Using JARVIS personality")

            # Build context
            memory_info = ""
            if relevant_memories:
                memory_info = f" Known: {relevant_memories[0][:60]}"

            system_prefix = f"""J.A.R.V.I.S. - Reply as Tony Stark's AI. Formal, brief, add "sir". {memory_info}

User: {message[:200]}
"""

            start_time = time.time()
            logger.step("Calling LLM...")
            response = self.assistant.start(system_prefix)
            elapsed = time.time() - start_time

            logger.success(f"Response generated in {elapsed:.2f}s")
            return response

    def _format_jarvis_response(self, response: str) -> str:
        if not self.profile.is_jarvis_mode():
            return response
        user = self.profile.get_name()
        if not response.startswith(("At ", "Very ", "Indeed", "I ", "The ", "As ")):
            import random
            openings = [
                f"Very well, {user}. ",
                f"Of course, {user}. ",
                f"Understood, {user}. ",
                f"Certainly, {user}. ",
            ]
            if random.random() < 0.3:
                response = random.choice(openings) + response[0].lower() + response[1:]
        return response

    def _handle_github_search(self, message: str) -> str:
        """Handle GitHub search with step-by-step logging"""
        from src.agents.base import call_llm
        msg_lower = message.lower()

        logger.step("Step 1: Parsing GitHub query...")
        for word in ['search github', 'find repo', 'github search', 'github repo', 'popular github', 'viral github', 'top github', 'github trending', 'github popular', 'github', 'repository']:
            msg_lower = msg_lower.replace(word, '').strip()

        query = msg_lower if msg_lower and msg_lower not in ['popular', 'viral', 'top', 'trending', ''] else "artificial intelligence machine learning"
        logger.success(f"Query: '{query}'")

        logger.step("Step 2: Calling GitHub MCP...")
        mcp_tools = get_mcp_tools()
        start_mcp = time.time()
        result = mcp_tools['github'].search_repos(query)
        mcp_elapsed = time.time() - start_mcp

        if "not configured" in result or "Could not search" in result or "Error" in result:
            logger.tool("GitHub MCP unavailable, using LLM fallback")
            logger.step("Step 2: Calling LLM for GitHub search...")
            llm_start = time.time()
            result = call_llm(f"""Search GitHub for popular/trending repositories related to: {query}

Return ONLY a numbered list (1-10) with:
- Repository name (format: owner/repo)
- Number of stars
- Brief description
- URL

Focus on recent popular AI/ML repos with high stars.""", max_tokens=800)
            llm_elapsed = time.time() - llm_start
            logger.success(f"Step 2: LLM completed ({llm_elapsed:.2f}s)")
        else:
            logger.success(f"Step 2: MCP completed ({mcp_elapsed:.2f}s)")

        return result

    def _handle_finance(self, message: str) -> str:
        """Handle finance with step-by-step logging"""
        msg = message.lower()

        logger.step("Step 1: Analyzing finance query...")
        if 'portfolio' in msg or 'my holding' in msg:
            logger.success("Query type: portfolio check")
            logger.step("Step 2: Calling FinanceAgent.get_portfolio()...")
            return self.finance.check_portfolio()
        elif 'add' in msg:
            logger.success("Query type: add holding")
            return "To add a holding, say: 'Add 10 shares of AAPL at 150'"
        else:
            import re
            symbols = re.findall(r'\b[A-Z]{2,5}\b', message)
            if symbols:
                logger.success(f"Query type: stock lookup for {symbols[0]}")
                logger.step(f"Step 2: Calling FinanceAgent.get_stock_info({symbols[0]})...")
                return self.finance.get_stock_info(symbols[0])
            logger.step("Step 2: Calling FinanceAgent.check_portfolio()...")
            return self.finance.check_portfolio()

    def _handle_research(self, message: str) -> str:
        """Handle research with step-by-step logging"""
        topic = message.replace('research', '').strip()

        logger.step(f"Step 1: Topic identified: '{topic}'")
        logger.step("Step 2: Calling ResearchAgent.research()...")
        start = time.time()
        result = self.research.research(topic)
        elapsed = time.time() - start
        logger.success(f"Step 2: Research completed ({elapsed:.2f}s)")
        return result

    def _handle_worklife(self, message: str) -> str:
        """Handle work-life with step-by-step logging"""
        msg = message.lower()

        if 'weather' in msg:
            logger.step("Step 1: Query type: weather")
            logger.step("Step 2: Calling WorkLifeAgent.weather()...")
            start = time.time()
            result = self.worklife.weather()
            elapsed = time.time() - start
            logger.success(f"Step 2: Weather fetched ({elapsed:.2f}s)")
            return result
        elif 'task' in msg or 'todo' in msg:
            logger.step("Step 1: Query type: tasks/todos")
            logger.step("Step 2: Calling WorkLifeAgent.list_tasks()...")
            return self.worklife.list_tasks()
        elif 'news' in msg:
            logger.step("Step 1: Query type: news")
            logger.step("Step 2: Calling WorkLifeAgent.news()...")
            return self.worklife.news()
        else:
            logger.step("Step 1: Query type: daily briefing")
            logger.step("Step 2: Calling WorkLifeAgent.daily_briefing()...")
            return self.worklife.daily_briefing()

    def _handle_health(self, message: str) -> str:
        """Handle health with step-by-step logging"""
        msg = message.lower()

        if 'bmi' in msg:
            logger.step("Step 1: Query type: BMI calculation")
            return "Enter: weight in kg and height in cm"
        elif 'tip' in msg or 'advice' in msg:
            logger.step("Step 1: Query type: health tip")
            logger.step("Step 2: Calling HealthAgent.quick_tip()...")
            return self.health.quick_tip()
        elif 'summary' in msg or 'report' in msg:
            logger.step("Step 1: Query type: health summary")
            logger.step("Step 2: Calling HealthAgent.summary()...")
            return self.health.summary()
        else:
            logger.step("Step 1: Query type: general health")
            logger.step("Step 2: Calling HealthAgent.quick_tip()...")
            return self.health.quick_tip()

    def _handle_news_summary(self, message: str) -> str:
        """Handle news summary with step-by-step logging"""
        import re
        msg_lower = message.lower()
        topic = "technology"

        logger.step("Step 1: Extracting topic...")
        patterns = [
            r'news\s+(?:summary|slides)\s+(?:about|for|on)?\s*(\w+)',
            r'create\s+(?:news|presentation)\s+(?:about|for)?\s*(\w+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, msg_lower)
            if match:
                topic = match.group(1)
                break
        for word in ['news summary', 'news slides', 'create presentation', 'summarize', 'about', 'for']:
            if word in msg_lower:
                topic = msg_lower.split(word)[-1].strip()
                break
        logger.success(f"Topic: '{topic}'")

        logger.step("Step 2: Calling NewsSummaryAgent.run()...")
        start = time.time()
        result = self.news_summary.run(topic, "news_summary.md")
        elapsed = time.time() - start
        logger.success(f"Step 2: News summary generated ({elapsed:.2f}s)")

        try:
            with open("news_summary.md", "r") as f:
                content = f.read()
            return f"📰 Generated 10-slide news summary for '{topic}':\n\n{content[:1500]}...\n\nSaved to: news_summary.md"
        except:
            return result

    def _handle_planner(self, message: str) -> str:
        """Handle planner with step-by-step logging"""
        import re
        msg_lower = message.lower()

        logger.step("Step 1: Parsing task/plan...")
        topic = None
        for word in ['create todo for', 'make todo for', 'plan for', 'create plan for', 'create list for', 'add to my list']:
            if word in msg_lower:
                topic = msg_lower.split(word)[-1].strip()
                break
        if not topic and 'about' in msg_lower:
            topic = msg_lower.split('about')[-1].strip()
        if not topic:
            match = re.search(r'(?:todo|plan|list)\s+(?:for|to|about)?\s*(.+)', msg_lower)
            if match:
                topic = match.group(1).strip()
        if not topic:
            return "What would you like to plan? Say 'create todo for [topic]' or 'make a plan for [topic]'"
        logger.success(f"Task topic: '{topic}'")

        if 'show' in msg_lower or 'list' in msg_lower or 'my todos' in msg_lower or 'view' in msg_lower:
            logger.step("Step 2: Calling PlannerAgent.list_todos()...")
            return self.planner.list_todos()
        if 'complete' in msg_lower or 'done' in msg_lower or 'finish' in msg_lower:
            match = re.search(r'(\d+)', message)
            if match:
                todo_id = int(match.group(1))
                logger.step(f"Step 2: Completing todo #{todo_id}...")
                return self.planner.complete_todo(todo_id)

        logger.step("Step 2: Creating plan and todo...")
        start = time.time()
        try:
            result = self.planner.plan_and_create_todo(topic)
            elapsed = time.time() - start
            logger.success(f"Step 2: Plan created ({elapsed:.2f}s)")
            return result
        except Exception as e:
            return f"Error creating todo: {str(e)}"

    def _handle_documentation(self, message: str) -> str:
        """Handle documentation with step-by-step logging"""
        import re
        msg_lower = message.lower()

        logger.step("Step 1: Identifying documentation topic...")
        patterns = [
            r'(?:show me|help me|find|get)\s+(?:example\s+)?(?:for|about)?\s+(\w+)',
            r'documentation\s+(?:for|about)?\s+(\w+)',
            r'doc\s+(?:for|about)?\s+(\w+)',
            r'how to\s+(\w+)',
        ]
        topic = "agent"
        for pattern in patterns:
            match = re.search(pattern, msg_lower)
            if match:
                topic = match.group(1)
                break
        if topic == "agent":
            for word in ['agent', 'workflow', 'memory', 'mcp', 'serve', 'tool']:
                if word in msg_lower:
                    topic = word
                    break
        logger.success(f"Documentation topic: '{topic}'")

        logger.step("Step 2: Searching documentation...")
        start = time.time()
        try:
            result = self.documentation.search_documentation(topic)
            elapsed = time.time() - start
            logger.success(f"Step 2: Documentation found ({elapsed:.2f}s)")
            if len(result) > 1500:
                return f"📚 Documentation for '{topic}':\n\n{result[:1500]}...\n\nSee full result in docs or run again."
            return f"📚 Documentation for '{topic}':\n\n{result}"
        except Exception as e:
            return f"Documentation Agent error: {str(e)}. Try: 'show me example for agent' or 'help me build workflow'"

    def _handle_memory_store(self, message: str) -> str:
        """Handle memory storage with step-by-step logging"""
        msg_lower = message.lower()

        logger.step("Step 1: Extracting memory content...")
        key = msg_lower.split('remember')[1].split('to')[0].strip() if 'remember' in msg_lower else message
        logger.success(f"Memory key: '{key[:50]}...'")

        logger.step("Step 2: Storing to memory...")
        mcp_tools = get_mcp_tools()
        result = mcp_tools['memory'].set(key, message)
        logger.success("Memory stored")
        return result

    def _handle_set_name(self, message: str) -> str:
        """Handle name setting with step-by-step logging"""
        import re
        msg_lower = message.lower()

        logger.step("Step 1: Extracting name...")
        patterns = [r'my name is (\w+)', r'call me (\w+)']
        name = None
        for pattern in patterns:
            match = re.search(pattern, msg_lower)
            if match:
                name = match.group(1).capitalize()
                break
        if not name:
            return "What would you like me to call you?"
        logger.success(f"Name: {name}")

        logger.step("Step 2: Updating user profile...")
        self.profile.set_name(name)
        logger.success("Profile updated")
        return f"✅ Got it! I'll call you {name} from now on. Nice to meet you!"

    def _handle_set_personality(self, message: str) -> str:
        """Handle personality change with step-by-step logging"""
        msg_lower = message.lower()

        logger.step("Step 1: Detecting personality mode...")
        if 'friend' in msg_lower or 'friendly' in msg_lower:
            logger.success("Mode: Friend")
            self.profile.set_personality_mode("friend")
            return "😊 Got it! I'll be your friendly companion from now on."
        elif 'teacher' in msg_lower or 'tutor' in msg_lower:
            logger.success("Mode: Teacher")
            self.profile.set_personality_mode("teacher")
            return "📚 Got it! I'll be your patient teacher from now on."
        elif 'professional' in msg_lower or 'assistant' in msg_lower:
            logger.success("Mode: Professional")
            self.profile.set_personality_mode("assistant")
            return "💼 Got it! I'll be your professional assistant from now on."
        elif 'jarvis' in msg_lower or 'iron man' in msg_lower or 'tony' in msg_lower:
            logger.success("Mode: JARVIS")
            self.profile.set_personality_mode("jarvis")
            return "😎 At your service, sir. Initializing JARVIS personality protocol. How may I assist you today?"
        else:
            return "I can be: JARVIS (Iron Man's AI), Assistant (professional), Companion (friendly), Teacher (educational), or Friend (casual). Which would you prefer?"

    def _handle_search(self, message: str) -> str:
        """Handle search with step-by-step logging"""
        if 'http://' in message or 'https://' in message:
            import re
            urls = re.findall(r'https?://[^\s]+', message)
            if urls:
                logger.step(f"Step 1: URL detected: {urls[0][:50]}...")
                logger.step("Step 2: Fetching URL content...")
                start = time.time()
                result = self.search.fetch(urls[0])
                elapsed = time.time() - start
                logger.success(f"Step 2: Content fetched ({elapsed:.2f}s)")
                return result

        msg_lower = message.lower()
        query = message.replace('search', '').replace('find', '').replace('research about', '').strip()

        logger.step(f"Step 1: Query parsed: '{query}'")

        if 'news' in msg_lower or 'last week' in msg_lower or 'latest' in msg_lower:
            logger.step("Step 2: Detected news query, enhancing for recency...")
            query = f"{query} May 2026 latest"

        logger.step(f"Step 2: Calling SearchAgent.search()...")
        start = time.time()
        result = self.search.search(query, max_results=8)
        elapsed = time.time() - start
        logger.success(f"Step 2: Search completed ({elapsed:.2f}s)")
        return result

    def _handle_content_creation(self, message: str) -> str:
        """Handle carousel/LinkedIn post creation with step-by-step logging"""
        from src.agents.base import call_llm
        import time

        msg_lower = message.lower()

        logger.step("Step 1: Parsing content request...")
        topic = message
        for word in ['carousel', 'linkedin post', 'social media', 'build', 'create post', 'for']:
            topic = topic.replace(word, '').strip()
        logger.success(f"Topic: '{topic}'")

        # If asking for news, search first
        if 'news' in msg_lower or 'latest' in msg_lower or 'last week' in msg_lower:
            logger.step("Step 2: News/content detected, searching web...")
            search_start = time.time()
            search_results = self.search.search(f"{topic} May 2026 latest", max_results=8)
            search_elapsed = time.time() - search_start
            result_count = search_results.count('\n') // 3
            logger.success(f"Step 2: Found {result_count} results ({search_elapsed:.2f}s)")

            logger.step("Step 3: Calling LLM to generate carousel...")
            llm_start = time.time()
            carousel = call_llm(f"""Based on these search results, create a LinkedIn carousel post with 10 slides:

{search_results}

Format each slide as:
### Slide X: [Title]
[Content]

Make it engaging, professional, and ready to post.""", max_tokens=2000)
            llm_elapsed = time.time() - llm_start
            logger.success(f"Step 3: LLM completed ({llm_elapsed:.2f}s)")

            return f"📱 **LinkedIn Carousel Created**:\n\n{carousel}"

        # Otherwise, generate content directly
        logger.step("Step 2: Calling LLM to generate carousel...")
        start = time.time()
        content = call_llm(f"""Create a LinkedIn carousel post about: {topic}

Format as 10 slides:
### Slide 1: [Hook/Title]
### Slide 2-9: [Key points, tips, or content]
### Slide 10: [CTA - Call to action]

Make it engaging, professional, and ready to post.""", max_tokens=2000)
        elapsed = time.time() - start
        logger.success(f"Step 2: Carousel generated ({elapsed:.2f}s)")

        return f"📱 **LinkedIn Carousel Created**:\n\n{content}"

    def chat(self, message: str) -> str:
        """Main chat method with full 4-tier memory integration"""

        print(f"\n{'='*50}")
        print(f"📥 INPUT: {message[:60]}{'...' if len(message) > 60 else ''}")
        print(f"{'='*50}")

        # Store in STM
        self.memory.add_message('user', message)

        # Extract entities
        self._extract_entities(message)

        # Route and get response
        start_total = time.time()
        response = self.route_task(message)
        elapsed_total = time.time() - start_total

        print(f"\n{'='*50}")
        print(f"⏱️ Total processing time: {elapsed_total:.2f}s")
        print(f"{'='*50}")

        # Store to LTM
        self._store_to_ltm(message, response)

        # Store in STM (assistant)
        self.memory.add_message('assistant', response)

        # Track in Episodic
        self.memory.track_interaction(
            user_input=message,
            response=response[:500] if len(response) > 500 else response,
            episode_type='chat',
            metadata={'source': 'interactive'}
        )

        # Format in JARVIS style
        response = self._format_jarvis_response(response)

        return response

    def _extract_entities(self, message: str) -> None:
        import re
        potential_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', message)
        entity_keywords = {
            'person': ['i am', 'my name is', 'called'],
            'company': ['company', 'work at', 'working at', 'employer'],
            'location': ['live in', 'located in', 'city', 'country'],
            'preference': ['i like', 'i prefer', 'i love', 'hate', 'favorite'],
        }
        msg_lower = message.lower()
        for entity in potential_entities[:3]:
            if len(entity) > 2:
                entity_type = 'unknown'
                for etype, keywords in entity_keywords.items():
                    if any(k in msg_lower for k in keywords):
                        entity_type = etype
                        break
                self.memory.add_entity(entity, entity_type, {'source': 'chat'})

    def _store_to_ltm(self, message: str, response: str) -> None:
        msg_lower = message.lower()
        
        # Skip questions - don't store queries
        if msg_lower.startswith('what') or msg_lower.startswith('how') or msg_lower.startswith('where') or msg_lower.startswith('when') or msg_lower.startswith('who') or msg_lower.startswith('do ') or msg_lower.startswith('can '):
            return
        
        # Explicit memory commands (handle typos too)
        if any(k in msg_lower for k in ['remember', 'remeber', 'rember', 'memorize', 'memorise', 'dont forget', "don't forget", 'store this', 'keep in mind']):
            # Extract the memory content
            remember_text = message
            for word in ['remember', 'remeber', 'rember', 'memorize', 'memorise', 'dont forget', "don't forget", 'store this', 'keep in mind']:
                if word in msg_lower:
                    remember_text = msg_lower.split(word, 1)[-1].strip()
                    break
            if remember_text and len(remember_text) > 2:
                enriched_text = f"User memory: {remember_text}"
                logger.step(f"Storing to LTM: '{remember_text[:50]}...'")
                self.memory.add_to_memory(enriched_text, metadata={'type': 'explicit_memory', 'source': 'chat'})
                return
        
        # Preference patterns
        preference_patterns = ['i like', 'i prefer', 'i love', 'i hate', 'my favorite', 'fav movie', 'fav food', 'fav color']
        if any(k in msg_lower for k in preference_patterns):
            if '?' not in message and 'what' not in msg_lower[:10]:
                self.memory.add_to_memory(f"User preference: {message}", metadata={'type': 'preference', 'source': 'chat'})
                logger.step(f"Storing preference: '{message[:50]}...'")
                return
        
        # Finance queries
        if 'portfolio' in msg_lower or 'holdings' in msg_lower:
            self.memory.add_to_memory(f"Finance query: {response[:200]}", metadata={'type': 'finance', 'source': 'chat'})
            return
        
        # Research queries
        if any(k in msg_lower for k in ['research', 'learn', 'understand']):
            self.memory.add_to_memory(f"Research topic: {message}", metadata={'type': 'research', 'source': 'chat'})
            return

    def help(self) -> str:
        return f"""🎯 Jarvis Commands:

Agent Routing:
- Finance: stock, crypto, portfolio, invest
- Research: research, paper, academic, study
- Health: health, weight, exercise, sleep, bmi
- Work-Life: weather, tasks, news, calendar

Patterns (use these keywords):
- "parallel" → Parallel Execution
- "loop" → Loop/Iteration
- "async" → Background Tasks
- "reflect" → Self Reflection
- "structured" → JSON Output
- "policy" → Policy Engine

MCP Tools:
- "remember X" → Store to memory
- "what time" → Get current time
- "search github X" → GitHub search
- "ls" or "list files" → Filesystem

Personalization:
- "My name is X" → Set name
- "Be my friend/teacher/jarvis" → Change personality
- "Profile" → View profile

Just chat normally! 🤖"""


def main():
    print("\n" + "="*50)
    print("🤖 JARVIS - AI ASSISTANT (Enhanced Logging)")
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

            response = jarvis.chat(user_input)

            # Clean response
            lines = response.split('\n\n')
            clean = response

            print(f"\n🤖 Jarvis: {clean}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {str(e)}\n")


if __name__ == "__main__":
    main()