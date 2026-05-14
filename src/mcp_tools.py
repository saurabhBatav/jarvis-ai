"""MCP Tools for Jarvis - External integrations"""

import os
import requests
import json
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any

# Load env
_base = os.path.dirname(os.path.abspath(__file__))
_project = os.path.dirname(os.path.dirname(_base))
load_dotenv(os.path.join(_project, '.env'), override=True)

API_KEY = os.environ.get("OPENAI_API_KEY", "")
TAVILY_KEY = os.environ.get("TAVILY_API_KEY", "")


def call_llm(prompt: str, max_tokens: int = 400) -> str:
    """Direct Groq API call"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    try:
        resp = requests.post(url, headers=headers, json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": max_tokens
        }, timeout=60)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"Error: {resp.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


class FileSystemMCP:
    """MCP #1: Filesystem - Read/write local files"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
    
    def read(self, path: str) -> str:
        """Read a file"""
        try:
            full_path = os.path.join(self.root_dir, path) if not path.startswith('/') else path
            with open(full_path, 'r') as f:
                return f.read()[:3000]  # Limit to 3000 chars
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def write(self, path: str, content: str) -> str:
        """Write to a file"""
        try:
            full_path = os.path.join(self.root_dir, path) if not path.startswith('/') else path
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
            return f"✅ Written to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def list_dir(self, path: str = ".") -> str:
        """List directory contents"""
        try:
            full_path = os.path.join(self.root_dir, path) if not path.startswith('/') else path
            items = os.listdir(full_path)
            return f"Files in {path}:\n" + "\n".join(f"  - {i}" for i in items[:20])
        except Exception as e:
            return f"Error: {str(e)}"


class BraveSearchMCP:
    """MCP #2: Brave Search - Web search"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("BRAVE_API_KEY", "")
    
    def search(self, query: str, num_results: int = 5) -> str:
        """Search the web"""
        if not self.api_key:
            # Fallback to Tavily or LLM
            return self._fallback_search(query)
        
        try:
            url = "https://api.brave.com/res/v1/web/search"
            headers = {"Accept": "application/json", "X-Subscription-Token": self.api_key}
            params = {"q": query, "count": num_results}
            
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("web", {}).get("results", [])
                output = f"🔍 **Search results for: {query}**\n\n"
                for r in results[:5]:
                    output += f"**{r.get('title', 'No title')}**\n{r.get('url', '')}\n{r.get('description', '')[:150]}...\n\n"
                return output
        except Exception as e:
            pass
        
        return self._fallback_search(query)
    
    def _fallback_search(self, query: str) -> str:
        """Use LLM for search fallback"""
        result = call_llm(f"Provide current information about: {query}", max_tokens=300)
        return f"🔍 **Web Search (via LLM): {query}**\n\n{result}"


class GitHubMCP:
    """MCP #3: GitHub - Repo operations"""
    
    def __init__(self, token: str = None):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base_url = "https://api.github.com"
    
    def search_repos(self, query: str) -> str:
        """Search GitHub repositories"""
        if not self.token:
            return "GitHub token not configured. Set GITHUB_TOKEN in .env"
        
        try:
            url = f"{self.base_url}/search/repositories"
            params = {"q": query, "per_page": 5}
            headers = {"Authorization": f"token {self.token}"}
            
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                output = f"📂 **GitHub Repos: {query}**\n\n"
                for r in data.get("items", [])[:5]:
                    output += f"**{r['full_name']}**\n  ⭐ {r['stargazers_count']} | 🍴 {r['forks_count']}\n  {r.get('description', 'No description')[:100]}...\n  {r['html_url']}\n\n"
                return output
        except Exception as e:
            return f"Error: {str(e)}"
        
        return "Could not search GitHub"
    
    def get_user(self, username: str) -> str:
        """Get GitHub user info"""
        if not self.token:
            return "GitHub token not configured"
        
        try:
            url = f"{self.base_url}/users/{username}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                u = resp.json()
                return f"👤 **{username}**\n  Repos: {u.get('public_repos', 0)} | Followers: {u.get('followers', 0)}\n  {u.get('bio', 'No bio')}"
        except:
            return "User not found"


class MemoryMCP:
    """MCP #4: Memory - Persistent memory across sessions"""
    
    def __init__(self):
        self.memory_file = os.path.join(_project, "memory", "persistent_memory.json")
        self._ensure_memory_file()
        self.memory = self._load()
    
    def _ensure_memory_file(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump({}, f)
    
    def _load(self):
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def set(self, key: str, value: str) -> str:
        """Store a memory"""
        self.memory[key] = value
        self._save()
        return f"✅ Remembered: {key}"
    
    def get(self, key: str) -> str:
        """Retrieve a memory"""
        return self.memory.get(key, "No memory found")
    
    def list_keys(self) -> str:
        """List all memories"""
        if not self.memory:
            return "No memories stored"
        return "💾 **Stored memories:**\n" + "\n".join(f"  - {k}" for k in self.memory.keys())


class TimeMCP:
    """MCP #5: Time - Current time and timezones"""
    
    def now(self, timezone: str = "UTC") -> str:
        """Get current time"""
        from datetime import datetime
        
        if timezone != "UTC":
            import pytz
            try:
                tz = pytz.timezone(timezone)
                dt = datetime.now(tz)
                return f"🕐 **{timezone}**: {dt.strftime('%Y-%m-%d %H:%M:%S')}"
            except:
                pass
        
        dt = datetime.now()
        return f"🕐 **Current time**: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    
    def format_timestamp(self, timestamp: int) -> str:
        """Format Unix timestamp"""
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')


class SlackMCP:
    """MCP #6: Slack - Send messages"""
    
    def __init__(self, token: str = None):
        self.token = token or os.environ.get("SLACK_BOT_TOKEN", "")
    
    def send_message(self, channel: str, text: str) -> str:
        """Send a message to Slack"""
        if not self.token:
            return "Slack token not configured. Set SLACK_BOT_TOKEN in .env"
        
        try:
            url = "https://slack.com/api/chat.postMessage"
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
            data = {"channel": channel, "text": text}
            
            resp = requests.post(url, headers=headers, json=data, timeout=10)
            if resp.status_code == 200 and resp.json().get("ok"):
                return f"✅ Sent to #{channel}"
        except Exception as e:
            return f"Error: {str(e)}"
        
        return "Failed to send message"


# Initialize all MCP tools
def get_mcp_tools():
    """Return all available MCP tools"""
    return {
        "filesystem": FileSystemMCP(),
        "brave_search": BraveSearchMCP(),
        "github": GitHubMCP(),
        "memory": MemoryMCP(),
        "time": TimeMCP(),
        "slack": SlackMCP()
    }


if __name__ == "__main__":
    # Test MCP tools
    print("=" * 60)
    print("MCP TOOLS TEST")
    print("=" * 60)
    
    tools = get_mcp_tools()
    
    # Test Memory
    print("\n🔹 Memory MCP:")
    print(tools["memory"].set("favorite_color", "blue"))
    print(tools["memory"].get("favorite_color"))
    
    # Test Time
    print("\n🔹 Time MCP:")
    print(tools["time"].now())
    
    # Test FileSystem
    print("\n🔹 Filesystem MCP:")
    print(tools["filesystem"].list_dir("."))
    
    print("\n" + "=" * 60)