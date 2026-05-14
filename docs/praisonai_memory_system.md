# PraisonAI Memory System Documentation

## Quick Start - Enable Agent Memory

```python
from praisonaiagents import Agent

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    memory=True  # Enable memory
)

# Conversation persists between calls
agent.start("My name is Alice")
response = agent.start("What's my name?")  # "Your name is Alice"
```

## Memory Configuration Options

| Form | Example | When to Use |
|------|---------|-------------|
| Bool | `memory=True` | Enable with defaults (SQLite) |
| String preset | `memory="redis"` | Use predefined backend |
| URL | `memory="redis://localhost:6379"` | Backend-specific connection |
| Dict | `memory={"backend": "postgres", "user_id": "u1"}` | Custom config |

## Memory Presets

| Preset | Backend |
|--------|---------|
| `"file"` | Local file storage |
| `"sqlite"` | SQLite database (default) |
| `"redis"` | Redis server |
| `"postgres"` | PostgreSQL |
| `"mongodb"` | MongoDB |

## Session Persistence

```python
from praisonaiagents import Agent, MemoryConfig

# With session_id - persists across restarts
agent = Agent(
    name="Assistant",
    instructions="...",
    memory={"session_id": "my-session-123"}
)

# Or with full config
agent = Agent(
    name="Assistant",
    instructions="...",
    memory=MemoryConfig(
        session_id="my-session",
        user_id="user-456",
        backend="file"
    )
)
```

## Memory Tiers

| Tier | Purpose | Storage | Retention |
|------|---------|---------|-----------|
| Short-Term (STM) | Active conversation | SQLite | Ephemeral |
| Long-Term (LTM) | Persistent knowledge | SQLite + Vector | Permanent |
| Entity Memory | Structured entities | LTM subset | Permanent |
| User Memory | User preferences | LTM with user_id | Permanent |

## Key Methods

| Method | Description |
|--------|-------------|
| `store_short_memory()` | Store in STM |
| `store_long_memory()` | Store in LTM |
| `search_memories()` | Search across tiers |
| `get_short_memories()` | Retrieve STM |
| `get_long_memories()` | Retrieve LTM |

## How Memory Works

1. **Input**: You send a message
2. **Retrieve**: Agent checks memory for context
3. **Process**: Combines memory + new input
4. **Respond**: Generates informed response
5. **Save**: Stores important info for later

## Best Practices

- Use `user_id` for multi-user apps to isolate memory
- Set session_id for persistence across restarts
- Clear short-term memory regularly
- Use checkpoints before major changes
- Search before adding duplicates

## Context vs Memory

| Aspect | Context | Memory |
|--------|---------|--------|
| Lifetime | Single session | Persists across sessions |
| Storage | In-memory only | File/Database |
| Scope | Current workflow | All workflows |
| Use Case | Passing data between agents | Learning & remembering |
| Performance | Fast (no I/O) | Slower (disk/network)