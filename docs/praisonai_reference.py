"""
PraisonAI Documentation Reference
================================

This file contains comprehensive documentation about PraisonAI for Jarvis AI to reference
when implementing new tools, agents, skills, and features.

Source: https://docs.praison.ai

================================================================================
1. CORE CONCEPTS
================================================================================

1.1 Framework Overview
-----------------------
- Built on unification of AG2 (AutoGen) + CrewAI
- Low-code interface for multi-agent collaboration
- 100+ LLM providers supported
- 140+ built-in tools
- Self-reflection for error recovery
- Hierarchical/Sequential/Parallel orchestration

1.2 System Entity Hierarchy
---------------------------
- Agent: Fundamental execution unit with role/goal/backstory
- AgentTeam: Collaborative orchestration (sequential/hierarchical)
- AgentFlow: Deterministic pipelines (route/parallel/loop/repeat)
- AgentOS: REST API deployment layer

1.3 Core Components
--------------------
- Agent: Single agent with instructions
- AgentTeam: Multi-agent coordination  
- AgentFlow: Workflow orchestration
- AgentOS: Production deployment

================================================================================
2. INSTALLATION
================================================================================

pip install praisonaiagents           # Core SDK (~21 tools)
pip install praisonai-tools          # Extended tools (135+ tools)
pip install "praisonai[all]"         # Everything
pip install "praisonai[llm]"         # LiteLLM for model support

Environment Variables:
- OPENAI_API_KEY
- OPENAI_BASE_URL (for Groq: https://api.groq.com/openai/v1)

================================================================================
3. BUILT-IN TOOLS (21 Core + 135+ Extended)
================================================================================

3.1 CORE TOOLS (from praisonaiagents)
--------------------------------------
Search Tools:
- tavily, tavily_search, tavily_extract (AI-optimized search)
- exa, exa_search, exa_search_contents (Neural search)
- duckduckgo, internet_search
- searxng_search
- search_web (auto-fallback)

Scraping Tools:
- crawl4ai, crawl4ai_extract
- spider_tools, scrape_page, extract_links

File/Shell Tools:
- read_file, write_file, list_files
- execute_command, list_processes
- execute_code, analyze_code

Training Tools:
- cot_save, cot_upload_to_huggingface
- cot_generate, cot_improve

3.2 EXTENDED TOOLS (from praisonai_tools)
-----------------------------------------
Data Format Tools:
- read_json, write_json, validate_json
- read_yaml, write_yaml, validate_yaml
- read_xml, write_xml, transform_xml
- read_csv, write_csv, merge_csv
- read_excel, write_excel, merge_excel

Research Tools:
- search_arxiv, get_arxiv_paper
- wikipedia_search
- pubmed_search

Finance/Analytics:
- get_stock_price (YFinance)
- calculate, solve_equation
- duckdb_query, pandas_read_csv

Integration Tools:
- EmailTool, SlackTool, DiscordTool
- GitHubTool, NotionTool, TrelloTool
- PostgresTool, MongoDBTool, RedisTool

3.3 TOOL USAGE EXAMPLES
-----------------------
# Single tool
agent = Agent(
    instructions="Search the web",
    tools=[tavily]
)

# Multiple tools
agent = Agent(
    instructions="Research and process data",
    tools=[tavily, read_json, write_file]
)

# MCP tools
from praisonaiagents import MCP
agent = Agent(
    instructions="Use external tools",
    tools=MCP(command="npx", args=["-y", "@some/mcp-server"])
)

================================================================================
4. AGENT CREATION
================================================================================

4.1 Single Agent
----------------
from praisonaiagents import Agent

agent = Agent(
    name="Assistant",
    instructions="You are a helpful AI assistant",
    llm="llama-3.1-8b-instant",  # or "gpt-4o", "gemini-1.5-flash", etc.
    tools=[tool1, tool2],
    allow_code_execution=True,
    allow_delegation=True
)

result = agent.start("Your task here")

4.2 AgentTeam (Multi-Agent)
--------------------------
from praisonaiagents import Agent, AgentTeam

researcher = Agent(
    name="Researcher",
    instructions="Research topics thoroughly"
)
writer = Agent(
    name="Writer",
    instructions="Write clear content"
)

team = AgentTeam(
    agents=[researcher, writer],
    process="sequential",  # or "hierarchical"
    planning=True
)

result = team.start("Create content about AI")

4.3 AgentFlow (Workflow)
-----------------------
from praisonaiagents import Agent, AgentFlow

researcher = Agent(name="Researcher", instructions="Research topics")
writer = Agent(name="Writer", instructions="Write content")

workflow = AgentFlow(steps=[researcher, writer])
result = workflow.start("Research and write about AI")

4.4 YAML Configuration
----------------------
# agents.yaml
framework: praisonai
topic: Research AI trends
agents:
  researcher:
    role: Research Analyst
    goal: Find latest AI developments
    instructions: You research thoroughly
    tools:
      - tavily
    tasks:
      research_task:
        description: Research AI trends
        expected_output: Comprehensive report

================================================================================
5. CLI COMMANDS
================================================================================

praisonai agents.yaml              # Run from YAML
praisonai "Your prompt"           # No-code mode
praisonai claw                    # Launch dashboard (http://localhost:8082)
praisonai bot telegram --token $TOKEN  # Telegram bot
praisonai bot slack --token $TOKEN --app-token $APP_TOKEN
praisonai bot discord --token $TOKEN
praiseonai browser navigate https://example.com
praisonai browser run "Click submit"
praisonai skills list
praisonai skills check --verbose
praisonai plugins list --enabled
praisonai plugins doctor
praisonai sandbox status
paisonai doctor                    # Diagnostics

================================================================================
6. LLM MODELS
================================================================================

Usage: llm parameter in Agent

OpenAI: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
Anthropic: claude-3.5-sonnet, claude-3-haiku
Google: gemini-2.5-flash, gemini-1.5-flash, gemini-2.0-flash-lite
Groq: llama-3.1-70b-versatile, llama-3.1-8b-instant
Ollama: llama2, mistral, codellama

Provider Format:
- "llama-3.1-8b-instant" (Groq default)
- "gemini/gemini-2.5-flash" (Google)
- "claude-3-5-sonnet-20241022" (Anthropic)

Environment Setup:
# Groq
OPENAI_API_KEY=your_groq_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1

# Google Gemini
export GEMINI_API_KEY=your_gemini_key

# Ollama (local)
export OPENAI_BASE_URL=http://localhost:11434/v1

================================================================================
7. MEMORY & KNOWLEDGE
================================================================================

7.1 Memory Types
---------------
- Short-term (STM): Rolling buffer, FIFO eviction
- Long-term (LTM): ChromaDB vector store, semantic search
- Entity: Structured entity tracking (JSON)
- Episodic: Chronological interaction history

7.2 Knowledge/RAG
-----------------
- Vector stores: ChromaDB, Pinecone, Qdrant, Weaviate
- Document loaders: PDF, HTML, Text, JSON, CSV
- Retrieval strategies: similarity, threshold, filtering

================================================================================
8. PROCESS TYPES
================================================================================

Sequential: Linear task execution (agent1 -> agent2 -> agent3)
Hierarchical: Manager LLM delegates to worker agents
Parallel: Simultaneous execution with aggregator
Planning: plan -> execute -> reason cycle

================================================================================
9. ADVANCED FEATURES
================================================================================

9.1 Self-Reflection
-------------------
Agents evaluate and improve their own responses
Enabled by default, disable with reflection=False

9.2 Planning Mode
----------------
Agents break down complex tasks before execution
agent = Agent(planning=True)

9.3 Code Execution
------------------
allow_code_execution=True
Sandboxed execution available

9.4 MCP Integration
------------------
Model Context Protocol for external tools
MCP servers as tools for agents

9.5 Handoffs
------------
Agent-to-agent task delegation
Configured via handoffs parameter

================================================================================
10. CONFIGURATION OPTIONS
================================================================================

Agent Parameters:
- name: Agent identifier
- role: Functional expertise
- goal: Success condition
- backstory: Professional context
- instructions: Detailed prompt
- llm: Model to use
- tools: List of tools
- allow_delegation: Enable handoffs
- allow_code_execution: Enable code tools
- memory: Enable memory system
- knowledge: RAG knowledge base
- planning: Enable planning mode
- reflection: Enable self-reflection
- max_iterations: Execution limit
- timeout: Request timeout

================================================================================
11. USE CASES
================================================================================

- Research & Analysis (Deep Research Agent)
- Code Generation (Programming Agent)
- Content Creation (Blog posts, documentation)
- Data Pipelines (ETL, analytics)
- Customer Support (24/7 bots)
- Workflow Automation (Multi-step processes)

================================================================================
12. PLATFORM INTEGRATIONS
================================================================================

Messaging: Telegram, Discord, Slack, WhatsApp
Productivity: Google Workspace, Notion, Jira, Trello
Development: GitHub (PRs, issues, repos)
Communication: Email, Slack notifications
Databases: PostgreSQL, MongoDB, Redis, SQLite

================================================================================
13. QUICK REFERENCE
================================================================================

Basic Agent:
from praisonaiagents import Agent
agent = Agent(instructions="You are helpful")
agent.start("Hello")

With Tools:
from praisonaiagents import Agent, tavily
agent = Agent(instructions="Researcher", tools=[tavily])
agent.start("Find AI trends")

Team:
from praisonaiagents import Agent, AgentTeam
a1 = Agent(name="R1", instructions="Research")
a2 = Agent(name="W1", instructions="Write")
team = AgentTeam(agents=[a1, a2], process="sequential")
team.start("Topic")

YAML Mode:
praisonai agents.yaml

Dashboard:
praisonai claw  # Opens http://localhost:8082
"""

# This file serves as a reference for Jarvis AI
# Import this to access documentation knowledge