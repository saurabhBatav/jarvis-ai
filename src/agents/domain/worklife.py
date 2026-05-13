"""Work-Life Agent - Productivity and life management with free tools"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests


class WorkLifeTools:
    """Free productivity tools for Jarvis"""
    
    @staticmethod
    def get_weather(location: str = "auto") -> Dict:
        """Get weather (Free: Open-Meteo API - no key required)"""
        try:
            # First get coordinates from location name
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}"
            geo_response = requests.get(geo_url, timeout=10).json()
            
            if not geo_response.get("results"):
                return {"error": "Location not found"}
            
            lat = geo_response["results"][0]["latitude"]
            lon = geo_response["results"][0]["longitude"]
            name = geo_response["results"][0]["name"]
            
            # Get weather
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_response = requests.get(weather_url, timeout=10).json()
            
            if "current_weather" in weather_response:
                cw = weather_response["current_weather"]
                return {
                    "location": name,
                    "temperature": cw["temperature"],
                    "wind_speed": cw["windspeed"],
                    "weather_code": cw["weathercode"]
                }
            return {"error": "Weather data unavailable"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_time_at(location: str) -> Dict:
        """Get time at a location (Free)"""
        try:
            # Using WorldTimeAPI
            # First get timezone from coordinates
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}"
            geo_response = requests.get(geo_url, timeout=10).json()
            
            if not geo_response.get("results"):
                return {"error": "Location not found"}
            
            lat = geo_response["results"][0]["latitude"]
            lon = geo_response["results"][0]["longitude"]
            
            # Get timezone
            tz_url = f"https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&format=json"
            tz_response = requests.get(tz_url, timeout=10).json()
            
            if tz_response.get("results"):
                tz = tz_response["results"][0].get("timezone", "UTC")
                
                # Get time
                time_url = f"http://worldtimeapi.org/api/timezone/{tz}"
                time_response = requests.get(time_url, timeout=10).json()
                
                return {
                    "location": location,
                    "timezone": tz,
                    "datetime": time_response.get("datetime", "N/A"),
                    "utc_offset": time_response.get("utc_offset", "N/A")
                }
            return {"error": "Timezone not found"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_holidays(country: str = "US", year: int = None) -> List[Dict]:
        """Get holidays (Free: Nager.Date API)"""
        try:
            year = year or datetime.now().year
            url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country}"
            response = requests.get(url, timeout=10).json()
            
            if isinstance(response, list):
                return [{"date": h["date"], "name": h["name"], "localName": h.get("localName", "")} for h in response[:10]]
            return []
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def get_news(topic: str = "general") -> List[Dict]:
        """Get news headlines (Free: GNews or Guardian)"""
        try:
            # Using Guardian API (free, no key needed for some endpoints)
            url = f"https://content.guardianapis.com/search?api-key=test&q={topic}&show-fields=headline,thumbnail"
            response = requests.get(url, timeout=10).json()
            
            if "response" in response and "results" in response["response"]:
                return [
                    {
                        "title": r.get("fields", {}).get("headline", "No title"),
                        "url": r.get("webUrl", ""),
                        "date": r.get("webPublicationDate", "")[:10]
                    }
                    for r in response["response"]["results"][:5]
                ]
            return [{"error": "No news available"}]
        except Exception as e:
            return [{"error": str(e)}]


class TaskManager:
    """Simple local task management"""
    
    def __init__(self, storage_path: str = "./memory/tasks.json"):
        self.storage_path = storage_path
        self.tasks = self._load()
    
    def _load(self) -> List[Dict]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add_task(self, title: str, due: str = None, priority: str = "medium") -> str:
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "due": due,
            "priority": priority,
            "status": "pending",
            "created": datetime.now().isoformat()
        }
        self.tasks.append(task)
        self._save()
        return f"✅ Added task: {title}"
    
    def list_tasks(self, status: str = "pending") -> str:
        filtered = [t for t in self.tasks if t.get("status") == status]
        if not filtered:
            return "No tasks found."
        
        lines = ["📋 Tasks:"]
        for t in filtered:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t.get("priority", "medium"), "⚪")
            due = f" (Due: {t['due']})" if t.get("due") else ""
            lines.append(f"{priority_emoji} {t['id']}. {t['title']}{due}")
        
        return "\n".join(lines)
    
    def complete_task(self, task_id: int) -> str:
        for t in self.tasks:
            if t["id"] == task_id:
                t["status"] = "completed"
                t["completed"] = datetime.now().isoformat()
                self._save()
                return f"✅ Completed: {t['title']}"
        return "Task not found"
    
    def delete_task(self, task_id: int) -> str:
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self._save()
        return f"🗑️ Deleted task {task_id}"


class WorkLifeAgent:
    """
    Work-Life Management Agent with free tools:
    - Weather (Open-Meteo - no API key)
    - Time at location (WorldTimeAPI - no key)
    - Holidays (Nager.Date - no key)
    - News (Guardian API - free tier)
    - Task management (local JSON)
    - No API keys required
    """
    
    def __init__(self):
        self.tools = WorkLifeTools()
        self.tasks = TaskManager()
        self._instructions = """You are Jarvis Work-Life Agent, a productivity and life management assistant.
Your role is to help users manage daily tasks, stay organized, and balance work-life.
Be proactive in suggesting improvements.
Keep responses concise and actionable."""
    
    def get_instructions(self, user_context: str = "") -> str:
        base = self._instructions
        if user_context:
            return base + f"\n\nUser context: {user_context}"
        return base
    
    def weather(self, location: str = "auto") -> str:
        """Get current weather"""
        data = self.tools.get_weather(location)
        if "error" in data:
            return f"Error: {data['error']}"
        
        return f"🌤️ {data['location']}: {data['temperature']}°C, Wind: {data['wind_speed']} km/h"
    
    def time_at(self, location: str) -> str:
        """Get time at a location"""
        data = self.tools.get_time_at(location)
        if "error" in data:
            return f"Error: {data['error']}"
        
        dt = data.get("datetime", "").split(".")[0] if data.get("datetime") else ""
        return f"🕐 {data['location']} ({data['timezone']}): {dt} ({data.get('utc_offset', '')})"
    
    def add_task(self, title: str, due: str = None, priority: str = "medium") -> str:
        return self.tasks.add_task(title, due, priority)
    
    def list_tasks(self) -> str:
        return self.tasks.list_tasks()
    
    def complete_task(self, task_id: int) -> str:
        return self.tasks.complete_task(task_id)
    
    def news(self, topic: str = "technology") -> str:
        """Get latest news"""
        articles = self.tools.get_news(topic)
        if not articles or "error" in articles[0]:
            return "No news available."
        
        lines = ["📰 Latest News:"]
        for a in articles[:5]:
            lines.append(f"• {a.get('title', 'N/A')}")
            lines.append(f"  {a.get('url', '')}\n")
        
        return "\n".join(lines)
    
    def holidays(self, country: str = "US") -> str:
        """Get upcoming holidays"""
        holidays = self.tools.get_holidays(country)
        if not holidays or "error" in holidays[0]:
            return "No holidays found."
        
        lines = ["🎉 Upcoming Holidays:"]
        for h in holidays[:5]:
            lines.append(f"  {h['date']}: {h['name']}")
        
        return "\n".join(lines)
    
    def daily_briefing(self) -> str:
        """Generate daily briefing"""
        tasks = self.tasks.list_tasks()
        weather = self.weather()
        news = self.news()[:200]
        
        lines = ["☀️ Good morning! Here's your briefing:\n"]
        lines.append(weather)
        lines.append("\n" + tasks)
        lines.append("\n" + news)
        
        return "\n".join(lines)