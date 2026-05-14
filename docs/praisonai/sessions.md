# PraisonAI Sessions

> Persist conversation history across application restarts

Sessions automatically save and restore conversation history, enabling persistent chats.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Application Instance                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                     Session                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │  Chat 1    │  │  Chat 2     │  │  Chat 3     │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Session Store (Disk/DB)                │   │
│  │              ~/.praisonai/sessions/                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Python

```python
from praisonaiagents import Session, Agent

# Create a new session (automatically loads if exists)
session = Session.new("user-123-chat")

# Add messages
session.add_user_message("My name is Alice")
session.add_assistant_message("Nice to meet you, Alice!")

# Session automatically saved to disk
```

### Load Existing Session

```python
from praisonaiagents import Session

# Explicitly load an existing session
session = Session.load("user-123-chat")

# Get message history
history = session.get_history()
for msg in history:
    print(f"{msg.role}: {msg.content}")
```

### Use with Agent

```python
from praisonaiagents import Session, Agent

# Create session
session = Session.new("chat-123")

# Use with agent
agent = Agent(
    name="Assistant",
    session=session,
    memory=True
)

agent.chat("Hello!")
```

## Session Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `session_id` | `str` | `"default"` | Unique session identifier |
| `max_messages` | `int` | `100` | Max messages to retain |
| `directory` | `Path` | `~/.praisonai/sessions/` | Storage location |

## Session Methods

| Method | Description |
|--------|-------------|
| `Session.new(id)` | Create new session |
| `Session.load(id)` | Load existing session from storage |
| `session.save()` | Explicitly save session to disk |
| `session.add_message(msg)` | Add a message |
| `session.add_user_message(text)` | Add user message |
| `session.add_assistant_message(text)` | Add assistant message |
| `session.get_history()` | Get all messages |
| `session.clear()` | Clear all messages |
| `session.delete()` | Delete session from storage |

## Session Storage

### Default Location

```
~/.praisonai/sessions/
├── user-123-chat.json
├── user-456-chat.json
└── support-session.json
```

### Custom Directory

```python
from praisonaiagents import Session, FileSessionStore
from pathlib import Path

# Create with custom directory
store = FileSessionStore.with_dir("/custom/path/sessions")
session = Session.with_store("chat-123", store)
```

### Session File Format

```json
{
  "session_id": "user-123-chat",
  "messages": [
    {
      "role": "user",
      "content": "My name is Alice"
    },
    {
      "role": "assistant", 
      "content": "Nice to meet you, Alice!"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:31:00Z"
}
```

## Multi-User Application Pattern

### Per-User Sessions

```python
from praisonaiagents import Session, Agent

async def handle_user(user_id: str, message: str) -> str:
    # Each user gets their own persistent session
    session = Session.load(user_id) or Session.new(user_id)
    
    agent = Agent(
        name="Assistant",
        session=session,
        memory=True
    )
    
    return agent.chat(message)
```

### Session with Database Store

```python
from praisonaiagents import Session, DatabaseSessionStore

# Use database for server-wide session storage
store = DatabaseSessionStore(connection=db_connection)
session = Session.with_store("user-123", store)
```

## Session with Memory

Combine session persistence with memory capabilities:

```python
from praisonaiagents import Session, Agent

# Create persistent session
session = Session.new("user-123")

# Agent with session + memory
agent = Agent(
    name="Assistant",
    session=session,    # Session persistence
    memory=True,        # In-conversation memory
    max_messages=50
)

# First conversation
agent.chat("I love pizza")

# After restart - still remembers
agent.chat("What's my favorite food?")
# Returns: "Your favorite food is pizza"
```

## Lifecycle Methods

### Save on Update

```python
from praisonaiagents import Session

session = Session.new("my-session")

# Add message (auto-saves)
session.add_user_message("Hello")

# Or manual save
session.save()

# Check if dirty
if session.is_dirty():
    session.save()
```

### Auto-Load on Init

```python
# Creates new if doesn't exist, loads if exists
session = Session.load("user-123")
# or
session = Session.new("user-123").unwrap_or_else_load()
```

## Error Handling

```python
from praisonaiagents import Session

# Safe session loading
try:
    session = Session.load("user-123")
except SessionNotFound:
    session = Session.new("user-123")
except SessionCorrupted:
    # Handle corrupted session
    session = Session.new("user-123")
    session.clear()
```

## Best Practices

### 1. Use Meaningful Session IDs

Include user ID or context in session IDs for easy management:

```python
# Good
session = Session.new(f"user-{user_id}-support")
session = Session.new(f"chat-{room_id}")

# Avoid
session = Session.new("abc123")
```

### 2. Handle Load Failures

```python
# Create new if doesn't exist
session = Session.load(user_id).unwrap_or_else(|_| Session.new(user_id))
```

### 3. Limit Message History

```python
# Sessions auto-trim to max_messages
session = Session.new("chat", max_messages=100)
```

### 4. Clean Up Old Sessions

```python
# Delete when no longer needed
session = Session.load("old-session")
session.delete()

# Or bulk cleanup
Session.cleanup(older_than_days=30)
```

## Session vs Memory

| Feature | Session | Memory |
|---------|---------|--------|
| Persistence | Disk/DB | In-memory |
| Cross-restart | Yes | No (without config) |
| Use case | Long-term storage | Conversation context |
| Search | Limited | Vector search available |
| Configuration | Storage location | Backend adapter |

## Use Cases

### 1. User Chats

```python
@app.route("/chat", methods=["POST"])
def chat():
    user_id = request.json["user_id"]
    message = request.json["message"]
    
    session = Session.load(user_id) or Session.new(user_id)
    agent = Agent(session=session, memory=True)
    
    response = agent.chat(message)
    return {"response": response}
```

### 2. Support Threads

```python
# Each support conversation is a session
session = Session.new(f"support-{ticket_id}")

agent = Agent(session=session)
agent.chat(f"I need help with ticket #{ticket_id}")
```

### 3. Game Progress

```python
# Store game state in session
session = Session.load(f"game-{player_id}")

agent = Agent(session=session)
agent.chat("I found a sword")
agent.chat("What's in my inventory?")
```

## Related

- [Memory Documentation](./memory.md) - In-memory conversation
- [Agent Documentation](./agent.md) - Agent configuration