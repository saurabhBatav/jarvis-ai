# Jarvis Documentation Sitemap

## Overview
This sitemap provides links to documentation for multiple AI frameworks that Jarvis can use.

---

## Table of Contents

1. [PraisonAI](#praisonai)
2. [LangChain](#langchain)
3. [CrewAI](#crewai)
4. [AutoGen](#autogen)
5. [Ollama](#ollama)
6. [HayStack](#haystack)
7. [LlamaIndex](#llamaindex)

---

## PraisonAI
**Base URL**: https://docs.praison.ai

| Topic | Documentation URL |
|-------|-------------------|
| Agents | https://docs.praison.ai/docs/concepts/agents.md |
| Memory | https://docs.praison.ai/docs/concepts/memory.md |
| Tools | https://docs.praison.ai/docs/concepts/tools.md |
| Workflow | https://docs.praison.ai/docs/concepts/agentflow.md |
| AgentTeam | https://docs.praison.ai/docs/concepts/agentteam.md |
| Session | https://docs.praison.ai/docs/concepts/session-management.md |
| Knowledge | https://docs.praison.ai/docs/concepts/knowledge.md |
| RAG | https://docs.praison.ai/docs/concepts/rag.md |
| LLM Config | https://docs.praison.ai/docs/configuration/llm-config.md |
| Deployment | https://docs.praison.ai/docs/deploy/index |
| CLI | https://docs.praison.ai/docs/cli/cli.md |
| API | https://docs.praison.ai/docs/api.md |
| Voice/Audio | https://docs.praison.ai/docs/audio/overview.md |

---

## LangChain
**Base URL**: https://python.langchain.com

| Topic | Documentation URL |
|-------|-------------------|
| Agents | https://python.langchain.com/docs/docs_modules/agents |
| Chains | https://python.langchain.com/docs/docs_modules/chains |
| LLMs | https://python.langchain.com/docs/docs_modules/models |
| Memory | https://python.langchain.com/docs/docs_modules/memory |
| Vector Stores | https://python.langchain.com/docs/docs_modules/indexes/vectorstores |
| Chat Models | https://python.langchain.com/docs/docs_modules/model_lab/chat |
| Prompts | https://python.langchain.com/docs/docs_modules/prompts |
| Tools | https://python.langchain.com/docs/docs_modules/agents/tools |

---

## CrewAI
**Base URL**: https://docs.crewai.com

| Topic | Documentation URL |
|-------|-------------------|
| Agents | https://docs.crewai.com/core-concepts/agents |
| Crews | https://docs.crewai.com/core-concepts/crews |
| Tasks | https://docs.crewai.com/core-concepts/tasks |
| Tools | https://docs.crewai.com/core-concepts/tools |
| Process | https://docs.crewai.com/core-concepts/process |
| Memory | https://docs.crewai.com/core-concepts/memory |
| LLMs | https://docs.crewai.com/core-concepts/llms |

---

## AutoGen
**Base URL**: https://microsoft.github.io/autogen

| Topic | Documentation URL |
|-------|-------------------|
| Agents | https://microsoft.github.io/autogen/docs/agent |
| Group Chat | https://microsoft.github.io/autogen/docs/groupchat |
| Tools | https://microsoft.github.io/autogen/docs/tools |
| LLM Config | https://microsoft.github.io/autogen/docs/topics/llm-configuration |
| Code Executor | https://microsoft.github.io/autogen/docs/topics/code-executor |
| Multi-Agent | https://microsoft.github.io/autogen/docs/topics/multi-agent |

---

## Ollama
**Base URL**: https://github.com/ollama/ollama

| Topic | Documentation URL |
|-------|-------------------|
| API | https://github.com/ollama/ollama/docs/api |
| Python | https://github.com/ollama/ollama/docs/api/python |
| Models | https://github.com/ollama/ollama/docs/api/model |
| Embeddings | https://github.com/ollama/ollama/docs/api/embedding |

---

## HayStack
**Base URL**: https://docs.haystack.com

| Topic | Documentation URL |
|-------|-------------------|
| Pipelines | https://docs.haystack.com/docs/pipelines |
| Components | https://docs.haystack.com/docs/components |
| Retrievers | https://docs.haystack.com/docs/components/retriever |
| Readers | https://docs.haystack.com/docs/components/reader |
| Document Store | https://docs.haystack.com/docs/components/document-store |

---

## LlamaIndex
**Base URL**: https://docs.llamaindex.ai

| Topic | Documentation URL |
|-------|-------------------|
| Index | https://docs.llamaindex.ai/en/stable/core_modules/index_modules |
| LLMs | https://docs.llamaindex.ai/en/stable/core_modules/llms |
| Agents | https://docs.llamaindex.ai/en/stable/use_cases/agents |
| Query Pipeline | https://docs.llamaindex.ai/en/stable/core_modules/query_pipeline |
| Data Modules | https://docs.llamaindex.ai/en/stable/core_modules/data_modules |
| Embeddings | https://docs.llamaindex.ai/en/stable/core_modules/embeddings |

---

## Quick Reference

### Frameworks by Use Case

| Use Case | Recommended Framework |
|----------|----------------------|
| Multi-agent orchestration | PraisonAI, CrewAI, AutoGen |
| RAG pipelines | LangChain, LlamaIndex, HayStack |
| Local LLM | Ollama |
| Code generation | AutoGen |
| Memory management | PraisonAI, LangChain, CrewAI |

### Common Patterns

```python
# PraisonAI
from praisonaiagents import Agent
agent = Agent(instructions="...", memory=True)

# LangChain
from langchain.agents import AgentExecutor
from langchain import LLMChain

# CrewAI
from crewai import Agent, Task, Crew

# AutoGen
from autogen import ConversableAgent
```

---

*Last updated: 2026-05-14*

*Generated by Jarvis DocAgent*
