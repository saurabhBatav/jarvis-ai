"""News Summary Agent - Fetches news and creates 10-slide presentation"""

import os
import requests
import re
from typing import List, Dict
from datetime import datetime


class NewsSummaryAgent:
    """
    Agent that fetches latest news and creates a 10-slide presentation summary.
    
    Usage:
        agent = NewsSummaryAgent()
        news = agent.fetch_news("technology")
        slides = agent.create_slides(news)
        agent.save_presentation(slides, "presentation.md")
    """
    
    def __init__(self, max_slides: int = 10):
        self.max_slides = max_slides
        self.news_results = []
    
    def fetch_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """Fetch latest news for a given query"""
        try:
            url = "https://html.duckduckgo.com/html/"
            headers = {"User-Agent": "Mozilla/5.0"}
            data = {"q": f"{query} latest news", "b": ""}
            
            response = requests.post(url, data=data, headers=headers, timeout=15)
            
            results = []
            link_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
            links = re.findall(link_pattern, response.text)
            
            for i, (url, title) in enumerate(links[:max_results]):
                results.append({
                    "id": i + 1,
                    "title": title.strip(),
                    "url": url.strip()
                })
            
            self.news_results = results
            return results
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def create_slides(self, news: List[Dict] = None) -> str:
        """Create a 10-slide presentation from news"""
        news_data = news or self.news_results
        
        slides = []
        slides.append("# News Summary Presentation")
        slides.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        slides.append(f"Total Slides: {len(news_data[:self.max_slides])}")
        slides.append("---")
        
        for i, item in enumerate(news_data[:self.max_slides], 1):
            title = item.get('title', 'No title')
            url = item.get('url', '')
            
            slides.append(f"## Slide {i}: {title}")
            slides.append(f"Source: {url}")
            slides.append("")
            slides.append("*Brief summary of the news item goes here...*")
            slides.append("---")
        
        return "\n".join(slides)
    
    def save_presentation(self, slides: str, filename: str = "news_summary.md") -> str:
        """Save presentation to file"""
        try:
            with open(filename, 'w') as f:
                f.write(slides)
            return f"Saved to {filename}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def run(self, topic: str, output_file: str = "news_summary.md") -> str:
        """Complete workflow: fetch news, create slides, save"""
        news = self.fetch_news(topic)
        slides = self.create_slides(news)
        result = self.save_presentation(slides, output_file)
        return result


if __name__ == "__main__":
    agent = NewsSummaryAgent()
    result = agent.run("technology")
    print(result)