# Jarvis Agent Building Guide

## Overview
This guide covers how to build, integrate, and test domain agents in Jarvis using the PraisonAI framework.

## Quick Reference: Adding a New Agent

### Step 1: Create the Agent Class
```python
# File: src/agents/domain/your_agent.py

class YourAgent:
    """Agent description"""
    
    def __init__(self):
        self.name = "Your Agent"
    
    def run(self, query: str) -> str:
        # Your agent logic
        return result
    
    def help(self) -> str:
        return "What this agent does"
```

### Step 2: Register in Jarvis
```python
# File: src/main.py

# 1. Import the agent
from src.agents.domain.your_agent import YourAgent

class Jarvis:
    def __init__(self):
        # 2. Initialize the agent
        self.your_agent = YourAgent()
```

### Step 3: Add Routing Logic
```python
# File: src/main.py - route_task() method

# Add keywords that trigger your agent
if any(k in msg_lower for k in ['keyword1', 'keyword2', 'trigger phrase']):
    return self._handle_your_agent(message)
```

### Step 4: Create Handler Method
```python
# File: src/main.py

def _handle_your_agent(self, message: str) -> str:
    """Handle your agent requests"""
    # Extract parameters from message
    # Call your agent
    # Return formatted result
    return self.your_agent.run(query)
```

---

## Testing Checklist

Before declaring an agent working, verify:

1. **Direct Agent Test**
   ```python
   from src.agents.domain.your_agent import YourAgent
   agent = YourAgent()
   result = agent.run("test query")
   ```

2. **Route Task Test**
   ```python
   from src.main import Jarvis
   j = Jarvis()
   result = j.route_task("test keyword")
   ```

3. **Interactive Chat Test**
   ```bash
   python src/main.py
   # Type your keyword
   ```

---

## Common Issues & Solutions

### Issue: Handler Not Called
**Symptoms**: Keywords match but handler not triggered

**Checks**:
1. Verify keywords are unique (not matching other handlers)
2. Add debug print in handler to confirm it's called
3. Ensure handler returns string, not None

**Debug Pattern**:
```python
if any(k in msg_lower for k in ['your keyword']):
    print(f"[DEBUG] Triggered handler for: {message}")
    return self._handle_your_agent(message)
```

### Issue: Agent Returns None
**Fix**: Always return a string
```python
def run(self, query: str) -> str:
    if not query:
        return "Please provide a query"
    # ... logic
    return result  # Never return None
```

### Issue: Topic Extraction Broken
**Bad**:
```python
topic = msg_lower.split('about')[-1]  # "about climate" not "climate"
```

**Good**:
```python
import re
match = re.search(r'(?:about|for|on)\s+(\w+)', msg_lower)
topic = match.group(1) if match else "default"
```

---

## Routing Order Matters

The order of handlers in `route_task()` affects which one triggers:

```
1. URL detection
2. Search keywords
3. **NEW AGENT HANDLERS** (insert here)
4. Domain-specific (finance, research, etc.)
5. Default (LLM agent)
```

**Rule**: More specific keywords should come BEFORE generic ones.

**Example**:
```python
# GOOD - Specific before generic
if any(k in msg_lower for k in ['news summary', 'create presentation']):
    return self._handle_news_summary(message)

# BAD - Will match 'news' for anything
if 'news' in msg_lower:
    return self._handle_news(message)
```

---

## Agent Design Patterns

### Pattern 1: Simple Query Agent
```python
class SimpleAgent:
    def __init__(self):
        self.tools = [...]  # Optional
    
    def run(self, query: str) -> str:
        # Process query
        return result
```

### Pattern 2: PraisonAI Agent with Tools
```python
from praisonaiagents import Agent

class PraisonAgent:
    def __init__(self):
        self.agent = Agent(
            name="MyAgent",
            instructions="You are a helpful assistant",
            tools=[tool1, tool2]
        )
    
    def run(self, query: str) -> str:
        return self.agent.start(query)
```

### Pattern 3: Multi-Tool Agent
```python
class MultiToolAgent:
    def __init__(self):
        pass
    
    def tool1(self, arg):
        return result
    
    def tool2(self, arg):
        return result
    
    def run(self, query: str) -> str:
        # Route to appropriate tool
        if 'tool1' in query.lower():
            return self.tool1(...)
        return self.tool2(...)
```

---

## Integration with Jarvis Memory

### Store to Memory
```python
# In handler
self._store_to_ltm(message, response)
self.memory.add_message('user', message)
self.memory.add_message('assistant', response)
```

### Query Memory
```python
# In handler
results = self.memory.ltm.search(query)
if results:
    context = " | ".join([r['text'] for r in results])
```

---

## Best Practices

1. **Always Return Strings**
   ```python
   def run(self, query: str) -> str:
       if not query:
           return "Error: No query provided"
       # ...
   ```

2. **Add Help Methods**
   ```python
   def help(self) -> str:
       return """Available commands:
       - command1: Does thing 1
       - command2: Does thing 2"""
   ```

3. **Test at Three Levels**
   - Unit: Direct agent test
   - Integration: route_task test
   - End-to-end: Interactive chat

4. **Use Clear Keywords**
   - Avoid generic words like "get", "make", "do"
   - Use specific phrases like "news summary", "create presentation"

5. **Add Debug Prints During Development**
   ```python
   print(f"[DEBUG] Processing: {message}")
   ```

---

## File Structure

```
jarvis/
├── src/
│   ├── main.py              # Jarvis main interface
│   ├── agents/
│   │   ├── base.py          # Base JarvisAssistant
│   │   ├── domain/
│   │   │   ├── finance.py   # Finance Agent
│   │   │   ├── research.py  # Research Agent
│   │   │   ├── health.py    # Health Agent
│   │   │   ├── worklife.py  # Work-Life Agent
│   │   │   ├── search.py    # Search Agent
│   │   │   └── news_summary.py  # News Summary Agent
│   │   └── documentation/   # Documentation Agent
│   └── memory/
│       └── memory.py        # Memory management
└── tests/
    └── test_*.py            # Agent tests
```

---

## Reference: PraisonAI Basics

### Single Agent
```python
from praisonaiagents import Agent

agent = Agent(
    name="Researcher",
    instructions="You are a research expert",
    llm="llama-3.1-8b-instant"
)
result = agent.start("Research AI trends")
```

### Multi-Agent Team
```python
from praisonaiagents import Agent, AgentTeam

agent1 = Agent(instructions="Researcher agent")
agent2 = Agent(instructions="Summarizer agent")

team = AgentTeam(agents=[agent1, agent2])
result = team.start("Research and summarize AI news")
```

### With Tools
```python
from praisonaiagents import Agent

def search_tool(query: str) -> str:
    return search(query)

agent = Agent(
    instructions="Research assistant",
    tools=[search_tool]
)
```

---

## Related Documentation
- [PraisonAI Agents Documentation](https://docs.praison.ai/docs/concepts/agents.md)
- [PraisonAI Tools](https://docs.praison.ai/docs/concepts/tools.md)
- [PraisonAI Memory](https://docs.praison.ai/docs/concepts/memory.md)
- [ Jarvis Documentation Sitemap](DOCUMENTATION_SITEMAP.md)