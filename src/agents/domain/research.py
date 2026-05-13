"""Research Agent - Academic and web research with free tools"""

import os
import json
from typing import List, Dict, Optional
import requests
import arxiv


class ResearchTools:
    """Free research tools for Jarvis"""
    
    @staticmethod
    def search_arxiv(query: str, max_results: int = 5) -> List[Dict]:
        """Search arXiv for academic papers (Free)"""
        try:
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = []
            for paper in client.results(search):
                results.append({
                    "title": paper.title,
                    "authors": [a.name for a in paper.authors[:3]],
                    "summary": paper.summary[:300] + "...",
                    "published": str(paper.published.date()),
                    "pdf_url": paper.pdf_url,
                    "category": paper.primary_category
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def search_pubmed(query: str, max_results: int = 5) -> List[Dict]:
        """Search PubMed for medical/scientific papers (Free - NCBI API)"""
        try:
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "format": "json"
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            data = response.json()
            
            if "esearchresult" not in data or "idlist" not in data["esearchresult"]:
                return [{"error": "No results found"}]
            
            idlist = data["esearchresult"]["idlist"]
            
            # Fetch summaries
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            summary_params = {
                "db": "pubmed",
                "id": ",".join(idlist),
                "retmode": "json"
            }
            
            summary_response = requests.get(summary_url, params=summary_params, timeout=10)
            summary_data = summary_response.json()
            
            results = []
            for pub_id in idlist:
                if pub_id in summary_data.get("result", {}):
                    item = summary_data["result"][pub_id]
                    results.append({
                        "title": item.get("title", "N/A"),
                        "authors": item.get("authors", [])[:3],
                        "pubdate": item.get("pubdate", "N/A"),
                        "source": item.get("source", "N/A"),
                        "pubmed_id": pub_id
                    })
            
            return results
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def search_web(query: str, max_results: int = 5) -> List[Dict]:
        """Web search using DuckDuckGo (Free)"""
        try:
            # Using DuckDuckGo HTML (no API key needed)
            url = "https://html.duckduckgo.com/html/"
            data = {"q": query, "b": ""}
            
            response = requests.post(url, data=data, timeout=10)
            
            # Simple parsing
            import re
            results = []
            for match in re.finditer(r'<a class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>', response.text)[:max_results]:
                url = match.group(1)
                title = match.group(2)
                
                # Get snippet
                snippet_match = re.search(r'<a class="result__snippet"[^>]*>([^<]+)</a>', response.text[match.end():])
                snippet = snippet_match.group(1) if snippet_match else ""
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet[:200]
                })
            
            return results
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def search_wikipedia(query: str) -> Dict:
        """Search Wikipedia (Free)"""
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "title": data.get("title", query),
                    "extract": data.get("extract", "No summary available"),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "image": data.get("thumbnail", {}).get("source", "")
                }
            return {"error": "Page not found"}
        except Exception as e:
            return {"error": str(e)}


class ResearchAgent:
    """
    Personal Research Agent with free tools:
    - arXiv for academic papers
    - PubMed for medical/scientific research
    - DuckDuckGo for web search
    - Wikipedia for quick facts
    - No API keys required
    """
    
    def __init__(self):
        self.tools = ResearchTools()
        self._instructions = """You are Jarvis Research Agent, a knowledgeable research assistant.
Your role is to help users find information, understand topics, and gather knowledge.
Always verify information from reliable sources.
Provide clear, well-organized summaries.
Cite sources when possible."""
    
    def get_instructions(self, user_context: str = "") -> str:
        base = self._instructions
        if user_context:
            return base + f"\n\nUser context: {user_context}"
        return base
    
    def research(self, query: str, source: str = "all") -> str:
        """
        Perform research with specified source:
        - "arxiv" - Academic papers
        - "pubmed" - Medical/scientific
        - "web" - Web search
        - "wiki" - Wikipedia
        - "all" - All sources
        """
        results = []
        
        if source in ["all", "arxiv"]:
            arxiv_results = self.tools.search_arxiv(query, max_results=3)
            if arxiv_results and "error" not in arxiv_results[0]:
                results.append("📚 arXiv Papers:")
                for r in arxiv_results:
                    results.append(f"  • {r['title']}")
                    results.append(f"    Authors: {', '.join(r['authors'])}")
                    results.append(f"    {r['pdf_url']}")
        
        if source in ["all", "pubmed"]:
            pubmed_results = self.tools.search_pubmed(query, max_results=3)
            if pubmed_results and "error" not in pubmed_results[0]:
                results.append("\n🔬 PubMed Articles:")
                for r in pubmed_results:
                    results.append(f"  • {r['title']}")
                    results.append(f"    Published: {r.get('pubdate', 'N/A')}")
        
        if source in ["all", "wiki"]:
            wiki_result = self.tools.search_wikipedia(query)
            if "error" not in wiki_result:
                results.append(f"\n📖 Wikipedia: {wiki_result['title']}")
                results.append(f"   {wiki_result['extract'][:300]}...")
        
        if source in ["all", "web"]:
            web_results = self.tools.search_web(query, max_results=3)
            if web_results and "error" not in web_results[0]:
                results.append("\n🌐 Web Results:")
                for r in web_results:
                    results.append(f"  • {r['title']}")
                    results.append(f"    {r.get('snippet', '')[:100]}")
        
        if not results:
            return f"No results found for '{query}'. Try a different query or source."
        
        return "\n".join(results)
    
    def quick_fact(self, topic: str) -> str:
        """Get quick fact from Wikipedia"""
        result = self.tools.search_wikipedia(topic)
        if "error" in result:
            return f"I couldn't find information on '{topic}'"
        
        return f"📖 {result['title']}\n\n{result['extract']}"
    
    def deep_research(self, topic: str) -> str:
        """Comprehensive research on a topic"""
        return self.research(topic, source="all")