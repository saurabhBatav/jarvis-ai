# Jarvis - AI Operating System

<p align="center">
  <img src="https://img.shields.io/badge/Framework-PraisonAI-blue" alt="Framework">
  <img src="https://img.shields.io/badge/LLM-Groq-orange" alt="LLM">
  <img src="https://img.shields.io/badge/Memory-ChromaDB-green" alt="Memory">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

> An autonomous, multimodal, self-evolving AI Operating System for personal life optimization.

## Table of Contents

- [Vision](#vision)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Memory System](#memory-system)
- [Agents](#agents)
- [Development](#development)
- [Roadmap](#roadmap)
- [License](#license)

---

## Vision

Jarvis is not a chatbot; it is a **Persistent AI Workforce** designed to bridge the gap between human intent and autonomous execution. The goal is to move from a reactive tool to a **proactive teammate** that understands the user's codebase, financial status, health, and work-life goals.

### Primary Objectives

- **Total Life Orchestration:** Manage finance, health, learning, and work-life balance through specialized agents
- **Autonomous Evolution:** When a capability gap is identified, Jarvis must autonomously task an internal Programming Agent to build, test, and commit new tools or workflows
- **Cognitive Persistence:** Maintain a consistent persona and long-term memory across years of interaction

---

## Architecture

Jarvis is built on **PraisonAI**, a meta-framework that unifies:
- **AG2 (AutoGen):** Dialogue-based multi-agent capabilities
- **CrewAI:** Role-based orchestration

### System Entity Hierarchy

| Component | Description | Operational Role |
|-----------|-------------|------------------|
| Agent | The fundamental execution unit | Operates as an autonomous worker with specific instructions, personas, and tool access |
| AgentTeam | Collaborative orchestration layer | Manages agent groups via sequential or hierarchical patterns |
| AgentFlow | Deterministic pipeline system | Orchestrates complex, non-linear tasks through branching, parallelization, and iterative loops |
| AgentOS | Production operating layer | Operationalizes deployment, exposing agents as RESTful APIs |

### Core System Pillars

1. **The Brain (Orchestration):** Hierarchical Process where a Manager Agent decomposes goals and delegates to worker agents
2. **The Senses (Multimodal):** Gemini Live API for real-time voice interaction
3. **The Hands (Evolution):** Internal Programming Agent with code execution and GitHubTool access

---

## Features

### Implemented

- ✅ Multi-agent orchestration with hierarchical process
- ✅ Groq LLM integration (llama-3.1-8b-instant)
- ✅ Google Gemini for voice/multimodal (backup)
- ✅ 4-tier memory architecture (STM, LTM, Entity, Episodic)
- ✅ ChromaDB vector store for semantic search
- ✅ 140+ built-in tools (search, data processing, DevOps, enterprise)
- ✅ Self-reflection for error recovery

### Planned

- 🔄 Gemini Live voice interface
- 🔄 Self-evolution system (Programming Agent)
- 🔄 Domain-specific agents (Finance, Research, Health, Work-Life)
- 🔄 Shadow Git checkpoints for auto-rollback

---

## Quick Start

### Prerequisites

- Python 3.10+
- API Keys (see Configuration below)

### Installation

```bash
# Clone repository
git clone https://github.com/saurabhBatav/jarvis-ai.git
cd jarvis-ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install praisonaiagents praisonai-tools chromadb "praisonaiagents[llm]"
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required: OPENAI_API_KEY (Groq)
# Optional: GEMINI_API_KEY (for voice)
```

### Run

```python
from praisonaiagents import Agent

agent = Agent(
    instructions="You are Jarvis, a helpful AI assistant.",
    llm="llama-3.1-8b-instant"
)

result = agent.start("Hello! What can you do?")
print(result)
```

---

## Project Structure

```
jarvis/
├── .env                 # Environment variables (API keys)
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── LICENSE              # MIT License
│
├── src/                 # Source code
│   ├── __init__.py      # Package init
│   ├── main.py          # Main entry point
│   ├── config/          # Configuration
│   │   └── settings.py  # Settings management
│   ├── memory/          # Memory system
│   │   ├── __init__.py
│   │   ├── short_term.py    # STM - Rolling buffer
│   │   ├── long_term.py     # LTM - Semantic search
│   │   ├── entity.py        # Entity tracking
│   │   └── episodic.py      # Interaction history
│   ├── agents/          # Agent definitions
│   │   ├── base.py          # Base agent
│   │   ├── manager.py       # Manager agent
│   │   └── domain/          # Domain agents
│   ├── tools/           # Custom tools
│   │   └── __init__.py
│   └── utils/           # Utilities
│       ├── logger.py
│       └── helpers.py
│
├── config/              # Configuration files
│   ├── agents.yaml      # Agent definitions
│   └── memory.yaml      # Memory config
│
├── memory/             # Memory storage (runtime)
│   └── chroma_db/      # ChromaDB persistence
│
├── logs/               # Log files (runtime)
│
└── tests/              # Test files
    ├── __init__.py
    ├── test_memory.py
    └── test_agents.py
```

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Groq API key for LLM |
| `OPENAI_BASE_URL` | Yes | `https://api.groq.com/openai/v1` |
| `GEMINI_API_KEY` | No | Google Gemini for voice |
| `GOOGLE_API_KEY` | No | Same as GEMINI_API_KEY |
| `CHROMA_PERSISTENT_DIRECTORY` | No | Default: `./memory/chroma_db` |
| `LOG_LEVEL` | No | Default: `INFO` |
| `TAVILY_API_KEY` | No | For research agents |
| `GITHUB_TOKEN` | No | For evolution system |

### Agent Configuration (agents.yaml)

```yaml
framework: praisonai
model: llama-3.1-8b-instant
provider: groq

manager:
  name: Jarvis Manager
  role: Chief Operations Officer
  goal: Coordinate all specialized agents
  backstory: You are the central intelligence of Jarvis

agents:
  - name: Assistant
    role: General Assistant
    goal: Help the user with any task

process: hierarchical
verbose: true
```

---

## Memory System

Jarvis implements a **4-tier memory architecture** for persistent cognition:

### 1. Short-Term Memory (STM)

- Rolling buffer for immediate context
- FIFO (First-In, First-Out) eviction policy
- Prevents context window overflow

### 2. Long-Term Memory (LTM)

- Persistent fact storage
- Semantic search via ChromaDB
- Key user preferences and knowledge

### 3. Entity Memory

- Structured tracking of named entities
- People, organizations, relationships
- Graph-based storage

### 4. Episodic Memory

- Chronological interaction history
- Session boundaries
- Learning from past interactions

### Memory Injection

The framework automatically synthesizes all tiers into a context string injected into the LLM system prompt.

---

## Agents

### Manager Agent (Brain)

- Uses hierarchical process
- Coordinates all specialized agents
- Dynamic task decomposition

### Domain Agents (Planned)

- **Finance Agent:** Stock tracking (YFinance), market analysis (DuckDB)
- **Research Agent:** Tavily, ArXiv, PubMed integration
- **Work-Life Agent:** Google Workspace, Notion integration
- **Health Agent:** Health data tracking via episodic memory

---

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

This project follows:
- PEP 8 for Python style
- Type hints where beneficial

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Roadmap

### Phase 1 - Foundation ✅
- [x] Project setup
- [x] Environment configuration
- [x] Basic agent verification

### Phase 2 - Memory Infrastructure 🔄
- [x] STM implementation
- [ ] LTM with ChromaDB
- [ ] Entity memory
- [ ] Episodic memory
- [ ] Memory injection pipeline

### Phase 3 - Agent Architecture
- [ ] Manager Agent setup
- [ ] AgentTeam configuration
- [ ] AgentFlow pipelines

### Phase 4 - Domain Agents
- [ ] Finance Agent
- [ ] Research Agent
- [ ] Work-Life Agent
- [ ] Health Agent

### Phase 5 - Self-Evolution
- [ ] Programming Agent
- [ ] Tool auto-generation
- [ ] Shadow Git checkpoints

### Phase 6 - Voice Interface
- [ ] Gemini Live integration
- [ ] PCM audio handling

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [PraisonAI](https://praison.ai) - Multi-agent framework
- [Groq](https://groq.com) - LLM inference
- [ChromaDB](https://chromadb.ai) - Vector database