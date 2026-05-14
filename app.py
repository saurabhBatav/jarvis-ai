"""Jarvis app for Claw dashboard"""

import os

# Load env from project root
_project = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_project, '.env')
if os.path.exists(_env_path):
    with open(_env_path, 'r') as f:
        for line in f:
            if line.strip().startswith('OPENAI_API_KEY'):
                os.environ['OPENAI_API_KEY'] = line.split('=', 1)[1].strip()

import praisonaiui as aiui
from praisonai.ui._aiui_datastore import PraisonAISessionDataStore

# Set up datastore
aiui.set_datastore(PraisonAISessionDataStore())
aiui.set_style("dashboard")
aiui.set_pages([
    "chat", "channels", "agents", "skills", "memory", 
    "knowledge", "cron", "guardrails", "sessions", 
    "usage", "config", "logs", "debug"
])

# Check for existing memory
memory_dir = os.path.join(_project, 'memory')
if os.path.exists(memory_dir):
    print(f"📂 Found memory at: {memory_dir}")

# Agent definitions (matching Claw's format)
AGENTS = [
    {
        "agent_id": "jarvis",
        "name": "Jarvis",
        "description": "Main AI assistant - Iron Man's JARVIS",
        "instructions": "You are J.A.R.V.I.S. Call user 'sir'. Use 'At your service'. Be efficient.",
        "model": "llama-3.1-8b-instant",
        "icon": "🤖",
    },
    {
        "agent_id": "finance",
        "name": "FinanceAgent",
        "description": "Stock, crypto, investment analysis",
        "instructions": "You are a financial expert. Analyze stocks and investments.",
        "model": "llama-3.1-8b-instant", 
        "icon": "📈",
    },
    {
        "agent_id": "research",
        "name": "ResearchAgent", 
        "description": "Academic research and information",
        "instructions": "You research topics thoroughly and accurately.",
        "model": "llama-3.1-8b-instant",
        "icon": "🔬",
    },
    {
        "agent_id": "health",
        "name": "HealthAgent",
        "description": "Health and wellness advice",
        "instructions": "You provide health and wellness guidance.",
        "model": "llama-3.1-8b-instant",
        "icon": "💪",
    },
    {
        "agent_id": "planner",
        "name": "PlannerAgent",
        "description": "Task planning and todos",
        "instructions": "You help create and manage todo lists.",
        "model": "llama-3.1-8b-instant",
        "icon": "📋",
    },
    {
        "agent_id": "search",
        "name": "SearchAgent",
        "description": "Web search and fetching",
        "instructions": "You search the web and retrieve information.",
        "model": "llama-3.1-8b-instant",
        "icon": "🔍",
    },
]

# Register agents into dashboard
def _register():
    try:
        from praisonaiui.features.agents import get_agent_registry
        registry = get_agent_registry()
        existing = registry.list_all()
        existing_names = {a.get("name") for a in existing}
        
        for agent_def in AGENTS:
            if agent_def["name"] in existing_names:
                continue
            registry.create(agent_def)
            print(f"   ✓ {agent_def['icon']} {agent_def['name']}")
    except Exception as e:
        print(f"   ⚠️ Agent registration: {e}")

print("🤖 Jarvis agents loaded")
_register()