"""Launch Jarvis with Claw Dashboard - Full UI"""

import os
import sys

# Load env
_project_root = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_project_root, '.env')
if os.path.exists(_env_path):
    with open(_env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                if key in ['OPENAI_API_KEY', 'OPENAI_BASE_URL', 'TAVILY_API_KEY', 'GITHUB_TOKEN']:
                    os.environ[key] = val

print("""
╔══════════════════════════════════════════════════════════════╗
║           🤖 JARVIS + CLAW DASHBOARD                        ║
╠══════════════════════════════════════════════════════════════╣
║  Starting dashboard at: http://localhost:8082             ║
║                                                              ║
║  Features available:                                        ║
║  • 💬 Chat - Talk to Jarvis                                  ║
║  • 📡 Channels - Telegram, Slack, Discord, WhatsApp         ║
║  • 🤖 Agents - Manage AI agents                              ║
║  • 🧠 Memory - View agent memory                            ║
║  • 📚 Knowledge - RAG and knowledge base                    ║
║  • 🛡️ Guardrails - Safety rules                             ║
║  • ⏰ Cron - Scheduled tasks                                ║
║  • 📈 Usage - Token usage tracking                           ║
╚══════════════════════════════════════════════════════════════╝
""")

# Run Claw dashboard
os.system("praisonai claw --port 8082")