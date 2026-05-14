"""Documentation Sources - Add more frameworks"""

import os
import json
import requests
import re
from typing import Dict, List, Optional
from datetime import datetime


class DocumentationSource:
    """Base class for documentation sources"""
    
    def __init__(self, name: str, base_url: str, topics: Dict[str, str]):
        self.name = name
        self.base_url = base_url
        self.topics = topics
        self.cache_dir = "./memory/docs_cache"
        
    def find_doc(self, query: str) -> Optional[str]:
        """Find documentation URL for a topic"""
        query_lower = query.lower()
        
        # Direct match
        if query_lower in self.topics:
            return self.topics[query_lower]
        
        # Partial match
        for key, url in self.topics.items():
            if key in query_lower or query_lower in key:
                return url
        
        return None
    
    def fetch_page(self, path: str) -> Dict:
        """Fetch a documentation page"""
        url = self.base_url + path if not path.startswith("http") else path
        
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=15)
            
            # Extract content
            text = response.text
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            
            title_match = re.search(r'<title>([^<]+)</title>', text, re.IGNORECASE)
            
            return {
                "title": title_match.group(1) if title_match else path,
                "url": url,
                "content": text[:5000],
                "source": self.name
            }
        except Exception as e:
            return {"error": str(e), "source": self.name}
    
    def save_to_cache(self, topic: str, content: str) -> str:
        """Save documentation to cache"""
        os.makedirs(self.cache_dir, exist_ok=True)
        
        filename = f"{self.name.lower()}_{re.sub(r'[^a-z0-9]', '_', topic.lower())[:30]}"
        filepath = os.path.join(self.cache_dir, f"{filename}.json")
        
        data = {
            "source": self.name,
            "topic": topic,
            "content": content,
            "cached_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath


class LangChainSource(DocumentationSource):
    """LangChain documentation source"""
    
    def __init__(self):
        super().__init__(
            name="LangChain",
            base_url="https://python.langchain.com",
            topics={
                "agents": "/docs/docs_modules/agents",
                "agent": "/docs/docs_modules/agents",
                "chain": "/docs/docs_modules/chains",
                "llm": "/docs/docs_modules/models",
                "memory": "/docs/docs_modules/memory",
                "vectorstore": "/docs/docs_modules/indexes/vectorstores",
                "rag": "/docs_docs_modules/indexes/vectorstores",
                "chat": "/docs/docs_modules/model_lab/chat",
                "prompt": "/docs/docs_modules/prompts",
                "tool": "/docs/docs_modules/agents/tools",
                "retrieval": "/docs/docs_modules/indexes retrieval",
            }
        )


class CrewAISource(DocumentationSource):
    """CrewAI documentation source"""
    
    def __init__(self):
        super().__init__(
            name="CrewAI",
            base_url="https://docs.crewai.com",
            topics={
                "agents": "/core-concepts/agents",
                "crew": "/core-concepts/crews",
                "task": "/core-concepts/tasks",
                "tools": "/core-concepts/tools",
                "process": "/core-concepts/process",
                "memory": "/core-concepts/memory",
                "llm": "/core-concepts/llms",
                "flow": "/core-concepts/flow",
            }
        )


class AutoGenSource(DocumentationSource):
    """AutoGen (Microsoft) documentation source"""
    
    def __init__(self):
        super().__init__(
            name="AutoGen",
            base_url="https://microsoft.github.io/autogen",
            topics={
                "agents": "/docs/agent",
                "groupchat": "/docs/groupchat",
                "tool": "/docs/tools",
                "llm": "/docs/topics/llm-configuration",
                "coding": "/docs/topics/code-executor",
                "multi-agent": "/docs/topics/multi-agent",
            }
        )


class OllamaSource(DocumentationSource):
    """Ollama documentation source"""
    
    def __init__(self):
        super().__init__(
            name="Ollama",
            base_url="https://github.com/ollama/ollama",
            topics={
                "api": "/docs/api",
                "python": "/docs/api/python",
                "model": "/docs/api/model",
                "embedding": "/docs/api/embedding",
                "run": "/docs/api/run",
            }
        )


class HayStackSource(DocumentationSource):
    """HayStack documentation source"""
    
    def __init__(self):
        super().__init__(
            name="HayStack",
            base_url="https://docs.haystack.com",
            topics={
                "pipelines": "/docs/pipelines",
                "components": "/docs/components",
                "retriever": "/docs/components/retriever",
                "reader": "/docs/components/reader",
                "document-store": "/docs/components/document-store",
            }
        )


class LlamaIndexSource(DocumentationSource):
    """LlamaIndex documentation source"""
    
    def __init__(self):
        super().__init__(
            name="LlamaIndex",
            base_url="https://docs.llamaindex.ai",
            topics={
                "index": "/en/stable/core_modules/index_modules",
                "llm": "/en/stable/core_modules/llms",
                "agent": "/en/stable/use_cases/agents",
                "query": "/en/stable/core_modules/query_pipeline",
                "data": "/en/stable/core_modules/data_modules",
                "embeddings": "/en/stable/core_modules/embeddings",
            }
        )


class LocalExamplesSource(DocumentationSource):
    """Local PraisonAI examples from examples/ folder"""
    
    def __init__(self):
        # Get project root - go up from src/agents/documentation/sources.py
        import sys
        import os
        # sources.py is in src/agents/documentation/, so go up 3 levels to get project root
        current_file = os.path.abspath(__file__)
        # Go up: sources.py -> documentation -> agents -> src -> project_root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        examples_dir = os.path.join(project_root, "examples")
        
        super().__init__(
            name="LocalExamples",
            base_url="file://" + examples_dir,
            topics=self._scan_examples(examples_dir)
        )
        self.examples_dir = examples_dir
    
    def _scan_examples(self, examples_dir: str) -> Dict[str, str]:
        """Scan examples folder and create topic mapping"""
        topics = {}
        
        if not os.path.exists(examples_dir):
            return topics
        
        # Map common topics to example files
        topic_map = {
            "agent": "consolidated_params/basic_agent.py",
            "agents": "consolidated_params/basic_agents.py",
            "multi agent": "consolidated_params/basic_agents.py",
            "workflow": "consolidated_params/basic_workflow.py",
            "memory": "consolidated_params/basic_memory.py",
            "guardrails": "consolidated_params/basic_guardrails.py",
            "planning": "consolidated_params/basic_planning.py",
            "reflection": "consolidated_params/basic_reflection.py",
            "hooks": "consolidated_params/basic_hooks.py",
            "web": "consolidated_params/basic_web.py",
            "knowledge": "consolidated_params/basic_knowledge.py",
            "caching": "consolidated_params/basic_caching.py",
            "autonomy": "consolidated_params/basic_autonomy.py",
            "context": "consolidated_params/basic_context.py",
            "output": "consolidated_params/basic_output.py",
            "execution": "consolidated_params/basic_execution.py",
            "serve": "serve/serve_example.py",
            "server": "serve/serve_example.py",
            "api": "serve/agent_as_api_single.py",
            "mcp": "mcp/mcp_example.py",
            "yaml": "yaml/simple_yaml_agent.py",
            "template": "templates/00_agent_templates_basic.py",
            "recipe": "recipes/example_llm_recipes.py",
            "persistence": "persistence/minimal_agent_db.py",
            "database": "persistence/simple_db_agent.py",
            "redis": "persistence/redis_state.py",
            "sqlite": "persistence/sqlite_local.py",
            "postgres": "persistence/postgres_conversation_store.py",
            "mysql": "persistence/mysql_conversation_store.py",
            "mongodb": "persistence/mongodb_state_store.py",
            "approval": "approval/agent_approval.py",
            "policy": "policy/policy_example.py",
            "reflection": "reflection/00_agent_reflection_basic.py",
            "eval": "eval/accuracy_example.py",
            "routing": "routing/routellm_example.py",
        }
        
        for topic, path in topic_map.items():
            topics[topic] = f"file://{examples_dir}/{path}"
        
        return topics
    
    def find_doc(self, query: str) -> Optional[str]:
        """Find local example for a topic"""
        query_lower = query.lower()
        
        # Direct match
        if query_lower in self.topics:
            return self.topics[query_lower]
        
        # Partial match
        for key, url in self.topics.items():
            if key in query_lower or query_lower in key:
                return url
        
        return None
    
    def fetch_page(self, path: str) -> Dict:
        """Read local example file"""
        if path.startswith("file://"):
            file_path = path.replace("file://", "")
        else:
            file_path = path
        
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            return {
                "title": os.path.basename(file_path),
                "content": content,
                "source": "local",
                "path": file_path
            }
        except Exception as e:
            return {"error": str(e)}


class DocumentationManager:
    """Manage all documentation sources"""
    
    def __init__(self):
        self.sources: List[DocumentationSource] = [
            # Already have PraisonAI in docs_search.py
            LocalExamplesSource(),  # Local examples folder
            LangChainSource(),
            CrewAISource(),
            AutoGenSource(),
            OllamaSource(),
            HayStackSource(),
            LlamaIndexSource(),
        ]
        
        self.cache_dir = "./memory/docs_cache"
    
    def search_all(self, query: str) -> List[Dict]:
        """Search all sources for a topic"""
        results = []
        
        for source in self.sources:
            url = source.find_doc(query)
            if url:
                results.append({
                    "source": source.name,
                    "topic": query,
                    "url": url,
                    "base_url": source.base_url
                })
        
        return results
    
    def get_all_topics(self) -> Dict[str, List[str]]:
        """Get all available topics grouped by source"""
        all_topics = {}
        
        for source in self.sources:
            all_topics[source.name] = list(source.topics.keys())
        
        return all_topics
    
    def fetch_from_source(self, source_name: str, topic: str) -> Dict:
        """Fetch documentation from specific source"""
        for source in self.sources:
            if source.name.lower() == source_name.lower():
                url = source.find_doc(topic)
                if url:
                    return source.fetch_page(url)
        
        return {"error": f"Source {source_name} not found"}


def create_sitemap() -> str:
    """Create a comprehensive sitemap of all documentation"""
    
    manager = DocumentationManager()
    topics = manager.get_all_topics()
    
    sitemap = """# Jarvis Documentation Sitemap

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

"""
    
    # Add PraisonAI
    sitemap += """## PraisonAI
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

*Last updated: """ + datetime.now().strftime("%Y-%m-%d") + """*

*Generated by Jarvis DocAgent*
"""
    
    return sitemap


# Save sitemap
if __name__ == "__main__":
    sitemap = create_sitemap()
    
    # Save to file
    with open("docs/DOCUMENTATION_SITEMAP.md", "w") as f:
        f.write(sitemap)
    
    print("Sitemap saved to docs/DOCUMENTATION_SITEMAP.md")
    print(f"Total lines: {len(sitemap.split(chr(10)))}")