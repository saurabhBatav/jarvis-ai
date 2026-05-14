# PraisonAI Documentation

PraisonAI documentation for Jarvis.

## Contents

| Document | Description |
|----------|-------------|
| [Memory](./memory.md) | Conversation memory and history management |
| [Sessions](./sessions.md) | Persistent conversation history |

## Quick Reference

### Enable Memory
```python
from praisonaiagents import Agent

agent = Agent(
    instructions="Remember our conversation",
    memory=True
)
```

### Session Persistence
```python
from praisonaiagents import Session

session = Session.load("user-123")  # Load existing
# or
session = Session.new("user-123")   # Create new

agent = Agent(session=session)
```

### Memory Backends

| Backend | Config |
|---------|--------|
| In-Memory | `memory=True` |
| ChromaDB | `memory="chromadb"` |
| SQLite | `memory="sqlite"` |
| Redis | `memory="redis"` |
| Mem0 | `memory="mem0"` |

## Source

- [PraisonAI Docs](https://docs.praison.ai)