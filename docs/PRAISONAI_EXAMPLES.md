# PraisonAI Examples Reference

Reference: https://github.com/MervinPraison/PraisonAI/tree/main/examples

## Directory Structure

```
examples/
├── python/
│   ├── agents/        # Single, multi, router agents
│   ├── workflows/     # Routing, parallel, loop patterns
│   ├── tools/         # Custom tools
│   ├── mcp/           # Model Context Protocol
│   ├── memory/       # Memory and sessions
│   ├── code/         # Code editing & external CLI
│   ├── providers/    # LLM providers (OpenAI, Groq, etc.)
│   └── ...
├── serve/            # Server & endpoints
├── yaml/             # YAML workflows (no-code)
├── cookbooks/        # Complete use cases
├── knowledge/        # RAG & knowledge bases
├── rag/              # Retrieval-Augmented Generation
├── mcp/              # MCP examples
├── hooks/            # Event hooks
├── guardrails/       # Safety guardrails
├── reflection/       # Self-reflection
└── ...
```

## Quick Examples

### Single Agent
```python
from praisonaiagents import Agent

agent = Agent(instructions="You are a helpful assistant")
agent.start("Write a haiku about AI")
```

### Multi-Agent (Sequential)
```python
from praisonaiagents import Agent, AgentTeam

researcher = Agent(instructions="Research about AI trends")
writer = Agent(instructions="Write a summary based on research")

team = AgentTeam(agents=[researcher, writer], process="sequential")
team.start()
```

### Multi-Agent (Parallel)
```python
from praisonaiagents import Agent, AgentTeam

agent1 = Agent(instructions="Research AI")
agent2 = Agent(instructions="Research Crypto")

team = AgentTeam(agents=[agent1, agent2], process="parallel")
team.start()
```

### With Custom Tools
```python
from praisonaiagents import Agent, tool

@tool
def search(query: str) -> str:
    return f"Results for: {query}"

agent = Agent(instructions="You are a research assistant", tools=[search])
agent.start("Search for AI news")
```

### With Memory (Session)
```python
from praisonaiagents import Agent

agent = Agent(
    instructions="You are Jarvis",
    memory={"session_id": "jarvis_session", "auto_memory": True}
)
```

### With LLM Provider (Groq)
```python
from praisonaiagents import Agent

agent = Agent(
    instructions="You are a helpful assistant",
    llm="llama-3.1-8b-instant"  # Uses Groq
)
```

### YAML (No-Code)
```yaml
# agents.yaml
framework: praisonai
topic: "Write about AI"

agents:
  researcher:
    role: Research Analyst
    goal: Research AI trends
    instructions: "Find information about AI"

  writer:
    role: Writer
    goal: Write blog post
    instructions: "Write based on research"
```
Run: `praisonai agents.yaml`

## Key Example Categories

| Category | Path | Description |
|----------|------|-------------|
| **Consolidated Params** | `consolidated_params/` | Unified parameter system |
| **Agents** | `python/agents/` | Single, multi, router agents |
| **Workflows** | `python/workflows/` | Sequential, parallel, loop |
| **MCP** | `python/mcp/` | Model Context Protocol |
| **Memory** | `python/memory/` | Sessions, persistence |
| **Tools** | `python/tools/` | Custom tools |
| **Code** | `python/code/` | Code editing, external CLI |
| **YAML** | `yaml/` | No-code workflows |
| **Serve** | `serve/` | HTTP servers, endpoints |
| **Knowledge** | `knowledge/` | RAG, knowledge bases |
| **Guardrails** | `guardrails/` | Safety, validation |
| **Hooks** | `hooks/` | Event callbacks |

## Important Examples to Review

1. **Basic Agent** - `examples/consolidated_params/basic_agent.py`
2. **Multi Agent** - `examples/consolidated_params/basic_agents.py`  
3. **Workflow** - `examples/consolidated_params/basic_workflow.py`
4. **Memory** - `examples/consolidated_params/basic_memory.py`
5. **Guardrails** - `examples/consolidated_params/basic_guardrails.py`

## Related Documentation
- [PraisonAI Docs](https://docs.paison.ai/)
- [Agent Building Guide](../AGENT_BUILD_GUIDE.md)
- [Documentation Sitemap](DOCUMENTATION_SITEMAP.md)