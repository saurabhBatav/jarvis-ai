# Jarvis Documentation Reference

This file contains quick reference documentation for Jarvis and related systems.

## Table of Contents

1. [PraisonAI Memory](#praisonai-memory)
2. [PraisonAI Sessions](#praisonai-sessions)
3. [Jarvis Memory System](#jarvis-memory-system)

---

# PraisonAI Memory

**Source:** https://docs.praison.ai/docs/rust/memory

## Enable Memory
```python
from praisonaiagents import Agent

agent = Agent(
    instructions="Remember our conversation",
    memory=True  # Enable memory
)
```

## Memory Backends

| Backend | Config Value | Description |
|---------|--------------|-------------|
| In-Memory | `True` or `"memory"` | Simple dict storage |
| ChromaDB | `"chromadb"` | Vector semantic search |
| SQLite | `"sqlite"` | File-based persistence |
| Redis | `"redis"` | Distributed memory |
| PostgreSQL | `"postgres"` | Server-based storage |
| Mem0 | `"mem0"` | Managed memory service |
| MongoDB | `"mongodb"` | Document storage |

## Memory Methods

| Method | Description |
|--------|-------------|
| `agent.chat(message)` | Send message (auto-stores history) |
| `agent.clear_memory()` | Clear all stored messages |
| `agent.get_history()` | Get conversation history |
| `agent.search_history(query)` | Search past messages |

---

# PraisonAI Sessions

**Source:** https://docs.praison.ai/docs/rust/sessions

## Create/Load Session
```python
from praisonaiagents import Session

# Create new
session = Session.new("user-123")

# Load existing
session = Session.load("user-123")
```

## Session Methods

| Method | Description |
|--------|-------------|
| `Session.new(id)` | Create new session |
| `Session.load(id)` | Load existing session |
| `session.save()` | Save to disk |
| `session.add_message(msg)` | Add message |
| `session.get_history()` | Get history |
| `session.clear()` | Clear messages |
| `session.delete()` | Delete session |

## Session with Agent
```python
agent = Agent(
    name="Assistant",
    session=session,
    memory=True
)
```

---

# Jarvis Memory System

## 4-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Jarvis Memory                             │
├──────────────┬──────────────┬──────────────┬───────────────┤
│    STM       │    LTM       │   Entity    │   Episodic    │
│ Short-Term   │  Long-Term   │   Memory    │    Memory     │
├──────────────┼──────────────┼──────────────┼───────────────┤
│ Rolling buf  │ ChromaDB     │ JSON file   │  JSON file    │
│ (deque 20)   │ (vectors)    │ (entities)  │ (history)     │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

## Storage Flow

| Tier | Storage Trigger | Storage Content |
|------|-----------------|-----------------|
| STM | Every message | "user: ...", "assistant: ..." |
| LTM | "remember"/preferences | "User memory: ...", "User preference: ..." |
| Entity | Auto-extracted | Names, places, preferences |
| Episodic | Every interaction | Full conversation record |

## Retrieval Flow

1. **Search LTM** on every message (semantic search)
2. **Extract Entities** from message
3. **Build Context** for LLM prompt
4. **Store to LTM** based on patterns

## Memory Commands

| Command | Action |
|---------|--------|
| `remember this` | Explicit memory store |
| `what do you remember` | List MCP memories |
| `status` | Show all memory stats |

## Configuration

```python
# In src/main.py
memory = MemoryManager()
memory.initialize()

# Stats
memory.get_stats()
# {'stm_size': 0, 'ltm_count': 50, 'entity_count': 20, 'episodic_count': 165}
```

## Files

| File | Location | Purpose |
|------|----------|---------|
| manager.py | src/memory/ | Memory coordinator |
| short_term.py | src/memory/ | Rolling buffer |
| long_term.py | src/memory/ | ChromaDB vectors |
| entity.py | src/memory/ | Named entities |
| episodic.py | src/memory/ | Conversation history |

## MCP Memory

```python
from src.mcp_tools import get_mcp_tools

mcp_tools = get_mcp_tools()
mcp_tools['memory'].set(key, value)  # Store
mcp_tools['memory'].get(key)         # Retrieve
mcp_tools['memory'].list_keys()      # List all
```

---

**Last Updated:** 2024-05-14