"""Search Agent - Fast web search with free tools"""

import requests
import re
from typing import List, Dict, Optional


class SearchTools:
    """Free search tools for Jarvis"""
    
    @staticmethod
    def duckduckgo_search(query: str, max_results: int = 10) -> List[Dict]:
        """Search using DuckDuckGo (Free, no API key)"""
        try:
            url = "https://html.duckduckgo.com/html/"
            data = {"q": query, "b": ""}
            
            response = requests.post(url, data=data, timeout=15)
            
            results = []
            # Find all result blocks
            result_pattern = r'<a class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>.*?<a class="result__snippet"[^>]*>([^<]+)</a>'
            
            for match in re.finditer(result_pattern, response.text, re.DOTALL)[:max_results]:
                url = match.group(1)
                title = match.group(2).strip()
                snippet = match.group(3).strip()
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
            
            return results if results else [{"error": "No results found"}]
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def searxng_search(query: str, instances: List[str] = None) -> List[Dict]:
        """Search using SearXNG instances (Free, no API key)"""
        if instances is None:
            instances = [
                "https://searx.be",
                "https://searx.org",
                "https://search.bcats.xyz"
            ]
        
        for instance in instances:
            try:
                url = f"{instance}/search?q={query}&format=json"
                response = requests.get(url, timeout=10)
                data = response.json()
                
                results = []
                for r in data.get("results", [])[:10]:
                    results.append({
                        "title": r.get("title", "N/A"),
                        "url": r.get("url", ""),
                        "snippet": r.get("content", "")[:200]
                    })
                
                if results:
                    return results
            except:
                continue
        
        return [{"error": "All SearXNG instances unavailable"}]
    
    @staticmethod
    def fetch_url(url: str) -> Dict:
        """Fetch and extract content from URL"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            
            # Simple text extraction
            text = response.text
            
            # Remove scripts and styles
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            
            # Get title
            title_match = re.search(r'<title>([^<]+)</title>', text, re.IGNORECASE)
            title = title_match.group(1) if title_match else "No title"
            
            # Get main content (first few paragraphs)
            paragraphs = re.findall(r'<p[^>]*>([^<]+)</p>', text)
            content = ' '.join(paragraphs[:5])[:500]
            
            return {
                "title": title,
                "content": content,
                "url": url
            }
        except Exception as e:
            return {"error": str(e)}


class SearchAgent:
    """
    Fast Search Agent with free tools:
    - DuckDuckGo (primary)
    - SearXNG (backup)
    - URL content extraction
    - No API keys required
    """
    
    def __init__(self):
        self.tools = SearchTools()
        self._instructions = """You are Jarvis Search Agent, a fast and accurate information retrieval assistant.
Your role is to find the most relevant information quickly.
Always provide source links.
Present information in a clear, organized manner.
Be concise but thorough."""
    
    def get_instructions(self, user_context: str = "") -> str:
        base = self._instructions
        if user_context:
            return base + f"\n\nUser context: {user_context}"
        return base
    
    def search(self, query: str, max_results: int = 5) -> str:
        """Perform web search"""
        results = self.tools.duckduckgo_search(query, max_results)
        
        if "error" in results[0]:
            # Try SearXNG as backup
            results = self.tools.searxng_search(query, max_results)
            if "error" in results[0]:
                return f"Search failed: {results[0]['error']}"
        
        lines = [f"🔍 Results for '{query}':\n"]
        
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r.get('title', 'N/A')}")
            lines.append(f"   {r.get('snippet', '')[:150]}")
            lines.append(f"   🔗 {r.get('url', '')}\n")
        
        return "\n".join(lines)
    
    def quick_search(self, query: str) -> str:
        """Quick search with minimal output"""
        results = self.tools.duckduckgo_search(query, max_results=3)
        
        if "error" in results[0]:
            return "No results found."
        
        lines = []
        for r in results[:3]:
            lines.append(f"• {r.get('title', 'N/A')}")
            lines.append(f"  {r.get('snippet', '')[:100]}...")
        
        return "\n".join(lines)
    
    def fetch(self, url: str) -> str:
        """Fetch and summarize a URL"""
        data = self.tools.fetch_url(url)
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        return f"📄 {data.get('title', 'N/A')}\n\n{data.get('content', 'No content')}..."
    
    def compare(self, item1: str, item2: str) -> str:
        """Compare two items"""
        query = f"compare {item1} vs {item2}"
        return self.search(query, max_results=5)
    
    def trending(self, topic: str = "technology") -> str:
        """Get trending topics"""
        query = f"trending {topic} this week"
        return self.quick_search(query)