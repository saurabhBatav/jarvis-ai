# PraisonAI Web Documentation Index

## Key Resources
- Main Docs: https://docs.praison.ai
- API Reference: https://docs.paison.ai/docs/api.md
- Agents: https://docs.praison.ai/docs/concepts/agents.md
- Tools: https://docs.praison.ai/docs/concepts/tools.md
- Memory: https://docs.praison.ai/docs/concepts/memory.md
- Knowledge: https://docs.praison.ai/docs/concepts/knowledge.md

## Installation
```bash
pip install praisonaiagents           # Core SDK
pip install praisonai-tools          # Extended tools (135+)
pip install "praisonai[all]"         # Everything
```

## Core Concepts
- **Agent**: Single agent with role/goal/backstory
- **AgentTeam**: Multi-agent coordination (sequential/hierarchical)
- **AgentFlow**: Deterministic workflow orchestration
- **AgentOS**: REST API deployment layer

## 100+ LLM Providers
OpenAI, Anthropic, Google Gemini, Groq, Ollama, DeepSeek, Mistral, Cohere, and 80+ more

## 140+ Built-in Tools
- Search: tavily, exa, duckduckgo, searxng
- Scraping: crawl4ai, spider_tools
- File: read_file, write_file, execute_command
- Data: JSON, YAML, CSV, Excel handling
- Research: arxiv, wikipedia, pubmed
- Finance: stock prices via YFinance

## CLI Commands
- `praisonai claw` - Launch dashboard (localhost:8082)
- `praisonai agents.yaml` - Run from YAML
- `praisonai "prompt"` - No-code mode
- `praisonai bot telegram --token $TOKEN` - Telegram bot
- `praisonai bot discord --token $TOKEN` - Discord bot

## Memory & Knowledge
- Memory: Short-term (STM), Long-term (LTM), Entity, Episodic
- Knowledge: ChromaDB, Pinecone, Qdrant, Weaviate vector stores
- RAG: Retrieval Augmented Generation with semantic search

## Advanced Features
- Self-reflection for error recovery
- Planning mode for complex tasks
- Code execution in sandbox
- MCP integration for external tools
- Handoffs for agent-to-agent delegation

## Platform Integrations
- Messaging: Telegram, Discord, Slack, WhatsApp
- Productivity: Google Workspace, Notion, Jira, Trello
- Databases: PostgreSQL, MongoDB, Redis, SQLite