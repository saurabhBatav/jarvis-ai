"""Documentation Search Agent - Search and fetch PraisonAI documentation"""

import os
import json
import requests
import re
from typing import List, Dict, Optional
from datetime import datetime


class DocsSearchTools:
    """Tools for searching PraisonAI documentation"""
    
    BASE_URL = "https://docs.praison.ai"
    DOCS_INDEX_URL = "https://docs.praison.ai/llms.txt"
    
    # Local storage path
    DOCS_CACHE_DIR = "./memory/docs_cache"
    
    # Common doc topics and their URLs
    TOPIC_URLS = {
        "agents": "/docs/concepts/agents.md",
        "agent": "/docs/concepts/agents.md",
        "memory": "/docs/concepts/memory.md",
        "tools": "/docs/concepts/tools.md",
        "workflow": "/docs/concepts/agentflow.md",
        "team": "/docs/concepts/agentteam.md",
        "session": "/docs/concepts/session-management.md",
        "knowledge": "/docs/concepts/knowledge.md",
        "rag": "/docs/concepts/rag.md",
        "llm": "/docs/configuration/llm-config.md",
        "deployment": "/docs/deploy/index",
        "cli": "/docs/cli/cli.md",
        "api": "/docs/api.md",
        "voice": "/docs/audio/overview.md",
        "audio": "/docs/audio/overview.md",
        "tts": "/docs/audio/overview.md",
        "stt": "/docs/audio/groq.md",
        "whisper": "/docs/audio/groq.md",
    }
    
    def __init__(self):
        os.makedirs(self.DOCS_CACHE_DIR, exist_ok=True)
    
    @staticmethod
    def search_online(query: str) -> List[Dict]:
        """Search the web for PraisonAI documentation"""
        try:
            url = "https://html.duckduckgo.com/html/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            data = {"q": f"PraisonAI {query} documentation", "b": ""}
            
            response = requests.post(url, data=data, headers=headers, timeout=15)
            
            results = []
            link_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
            snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>([^<]+)</a>'
            
            links = re.findall(link_pattern, response.text)
            snippets = re.findall(snippet_pattern, response.text)
            
            for i, (url, title) in enumerate(links[:10]):
                snippet = snippets[i] if i < len(snippets) else ""
                if 'praison.ai' in url or 'docs.praison.ai' in url:
                    results.append({
                        "title": title.strip(),
                        "url": url.strip(),
                        "snippet": snippet.strip()
                    })
            
            return results
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def fetch_doc_page(path: str) -> Dict:
        """Fetch a specific documentation page"""
        try:
            url = DocsSearchTools.BASE_URL + path if not path.startswith("http") else path
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            # Extract title
            title_match = re.search(r'<title>([^<]+)</title>', response.text, re.IGNORECASE)
            title = title_match.group(1) if title_match else path
            
            # Extract content (simplified)
            # Remove scripts and styles
            text = re.sub(r'<script[^>]*>.*?</script>', '', response.text, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            
            # Get code blocks
            code_blocks = re.findall(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', text, re.DOTALL)
            
            # Get headings
            headings = re.findall(r'<h[1-6][^>]*>([^<]+)</h[1-6]>', text)
            
            return {
                "title": title,
                "url": url,
                "headings": headings[:10],
                "code_examples": [cb[:500] for cb in code_blocks[:5]],
                "content_length": len(text)
            }
        except Exception as e:
            return {"error": str(e), "path": path}
    
    @staticmethod
    def get_documentation_index() -> List[str]:
        """Get list of all documentation pages"""
        try:
            response = requests.get(DocsSearchTools.DOCS_INDEX_URL, timeout=15)
            
            # Parse the index (it's a simple text format with links)
            pages = []
            url_pattern = r'https://docs\.praison\.ai/([^\)]+)'
            for match in re.finditer(url_pattern, response.text):
                pages.append(match.group(1))
            
            return pages[:100]  # Limit to 100 pages
        except Exception as e:
            return []
    
    @staticmethod
    def find_topic_doc(topic: str) -> Optional[str]:
        """Find documentation URL for a topic"""
        topic_lower = topic.lower()
        
        # Direct match
        if topic_lower in DocsSearchTools.TOPIC_URLS:
            return DocsSearchTools.TOPIC_URLS[topic_lower]
        
        # Partial match
        for key, url in DocsSearchTools.TOPIC_URLS.items():
            if key in topic_lower or topic_lower in key:
                return url
        
        return None
    
    def save_documentation(self, topic: str, content: str, source_url: str = "") -> str:
        """Save documentation to local cache"""
        filename = re.sub(r'[^a-z0-9]', '_', topic.lower())[:50]
        filepath = os.path.join(self.DOCS_CACHE_DIR, f"{filename}.json")
        
        data = {
            "topic": topic,
            "content": content,
            "source_url": source_url,
            "cached_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def load_documentation(self, topic: str) -> Optional[str]:
        """Load documentation from local cache"""
        filename = re.sub(r'[^a-z0-9]', '_', topic.lower())[:50]
        filepath = os.path.join(self.DOCS_CACHE_DIR, f"{filename}.json")
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data.get("content")
        
        return None
    
    def list_cached_docs(self) -> List[str]:
        """List all cached documentation topics"""
        docs = []
        for f in os.listdir(self.DOCS_CACHE_DIR):
            if f.endswith('.json'):
                docs.append(f.replace('.json', ''))
        return docs
    
    def search_and_cache(self, query: str) -> Dict:
        """Search online and cache results"""
        topic_lower = query.lower()
        
        # Check local cache first
        cached = self.load_documentation(query)
        if cached:
            return {
                "source": "local_cache",
                "content": cached,
                "topic": query
            }
        
        # Try to find topic doc
        topic_url = self.find_topic_doc(query)
        if topic_url:
            doc = self.fetch_doc_page(topic_url)
            if "error" not in doc:
                content = str(doc)
                self.save_documentation(query, content, self.BASE_URL + topic_url)
                return {
                    "source": "web_docs",
                    "content": content,
                    "url": self.BASE_URL + topic_url,
                    "topic": query
                }
        
        # Search online
        results = self.search_online(query)
        if results and "error" not in results[0]:
            # Cache the search results
            content = str(results)
            self.save_documentation(query, content, "")
            return {
                "source": "web_search",
                "content": content,
                "results": results,
                "topic": query
            }
        
        return {"source": "none", "error": "Documentation not found"}


class DocsSearchAgent:
    """Agent for searching and retrieving PraisonAI documentation"""
    
    def __init__(self):
        self.tools = DocsSearchTools()
        self._instructions = """You are Jarvis Documentation Agent.
Your role is to find and retrieve PraisonAI documentation for any feature or capability.
Always provide the exact documentation URL and relevant code examples.
If you cannot find documentation, clearly state that and suggest the user provide it."""
    
    def search(self, query: str) -> str:
        """Search for documentation on a topic"""
        # First try to find topic match
        topic_url = self.tools.find_topic_doc(query)
        
        if topic_url:
            doc = self.tools.fetch_doc_page(topic_url)
            if "error" not in doc:
                lines = [f"📖 Found documentation: {doc['title']}"]
                lines.append(f"URL: {doc['url']}")
                
                if doc.get('headings'):
                    lines.append("\nTopics covered:")
                    for h in doc['headings'][:5]:
                        lines.append(f"  • {h}")
                
                if doc.get('code_examples'):
                    lines.append("\nCode examples available")
                
                return "\n".join(lines)
        
        # Search online
        results = self.tools.search_online(query)
        
        if results and "error" not in results[0]:
            lines = [f"🔍 Search results for '{query}':\n"]
            
            for r in results[:5]:
                lines.append(f"• {r.get('title', 'N/A')}")
                lines.append(f"  {r.get('url', '')}")
                if r.get('snippet'):
                    lines.append(f"  {r['snippet'][:100]}...")
                lines.append("")
            
            return "\n".join(lines)
        
        return f"Could not find documentation for '{query}'. Please provide the documentation URL or topic."
    
    def fetch_page(self, url_or_path: str) -> str:
        """Fetch a specific documentation page"""
        doc = self.tools.fetch_doc_page(url_or_path)
        
        if "error" in doc:
            return f"Error fetching documentation: {doc['error']}"
        
        lines = [f"📖 {doc['title']}"]
        lines.append(f"URL: {doc['url']}\n")
        
        if doc.get('headings'):
            lines.append("Topics:")
            for h in doc['headings'][:10]:
                lines.append(f"  • {h}")
        
        if doc.get('code_examples'):
            lines.append(f"\nCode examples ({len(doc['code_examples'])} found):")
            for i, code in enumerate(doc['code_examples'][:3], 1):
                lines.append(f"\n--- Example {i} ---")
                lines.append(code[:300])
        
        return "\n".join(lines)
    
    def list_topics(self) -> str:
        """List available documentation topics"""
        lines = ["📚 Available PraisonAI Documentation Topics:\n"]
        
        topics = [
            ("agents", "Creating and using AI agents"),
            ("memory", "Memory system (STM, LTM, Entity)"),
            ("tools", "Built-in and custom tools"),
            ("workflow", "AgentFlow workflows"),
            ("team", "AgentTeam multi-agent"),
            ("session", "Session management"),
            ("knowledge", "Knowledge/RAG"),
            ("deployment", "Deployment options"),
            ("cli", "Command line interface"),
            ("api", "API reference"),
            ("voice", "Voice/Audio (TTS, STT)"),
            ("audio", "Audio processing"),
        ]
        
        for topic, desc in topics:
            lines.append(f"• {topic}: {desc}")
        
        return "\n".join(lines)
    
    def search_and_cache(self, query: str) -> Dict:
        """Search for docs, fetch from web, and cache locally"""
        return self.tools.search_and_cache(query)
    
    def load_documentation(self, topic: str) -> Optional[str]:
        """Load from local cache"""
        return self.tools.load_documentation(topic)
    
    def list_cached_docs(self) -> List[str]:
        """List all cached documentation"""
        return self.tools.list_cached_docs()
    
    def get_code_example(self, topic: str) -> str:
        """Get code example for a specific topic"""
        topic_url = self.tools.find_topic_doc(topic)
        
        if not topic_url:
            return f"Unknown topic: {topic}"
        
        doc = self.tools.fetch_doc_page(topic_url)
        
        if "error" in doc or not doc.get('code_examples'):
            return f"No code examples found for {topic}"
        
        return f"Code example for {topic}:\n\n{doc['code_examples'][0]}"


if __name__ == "__main__":
    agent = DocsSearchAgent()
    
    print("=== DocsSearchAgent Test ===")
    print("\n1. List topics:")
    print(agent.list_topics())
    
    print("\n2. Search for 'memory':")
    print(agent.search("memory"))
    
    print("\n3. Get code example for 'agents':")
    print(agent.get_code_example("agents"))