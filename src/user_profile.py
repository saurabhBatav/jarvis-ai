"""User Profile - Stores personalized user information"""

import os
import json
from datetime import datetime
from typing import Dict, Optional


class UserProfile:
    """Manages user profile and preferences"""
    
    def __init__(self, storage_path: str = "./memory/user_profile.json"):
        self.storage_path = storage_path
        self.profile: Dict = self._load()
        
    def _load(self) -> Dict:
        """Load profile from file"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except:
                pass
        return self._default_profile()
    
    def _default_profile(self) -> Dict:
        """Default profile for new users"""
        return {
            "name": None,
            "created_at": datetime.now().isoformat(),
            "last_seen": None,
            "preferences": {
                "communication_style": "balanced",  # brief, balanced, detailed
                "formality": "casual",  # casual, balanced, formal
                "personality_mode": "jarvis",  # jarvis, assistant, companion, teacher, friend
                "response_length": "medium",  # short, medium, long
            },
            "interests": [],
            "goals": [],
            "conversation_count": 0,
            "favorite_topics": [],
            "disliked_topics": [],
            "custom_instructions": "",
        }
    
    def save(self):
        """Save profile to file"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.profile["last_seen"] = datetime.now().isoformat()
        with open(self.storage_path, "w") as f:
            json.dump(self.profile, f, indent=2)
    
    def get_name(self) -> str:
        """Get user's name or default"""
        return self.profile.get("name") or "User"
    
    def set_name(self, name: str):
        """Set user's name"""
        self.profile["name"] = name
        self.save()
    
    def get_preference(self, key: str, default=None):
        """Get a preference value"""
        return self.profile.get("preferences", {}).get(key, default)
    
    def set_preference(self, key: str, value):
        """Set a preference"""
        if "preferences" not in self.profile:
            self.profile["preferences"] = {}
        self.profile["preferences"][key] = value
        self.save()
    
    def set_personality_mode(self, mode: str):
        """Set personality mode"""
        valid_modes = ["jarvis", "assistant", "companion", "teacher", "friend"]
        if mode in valid_modes:
            self.profile["preferences"]["personality_mode"] = mode
            self.save()
    
    def is_jarvis_mode(self) -> bool:
        """Check if JARVIS mode is active"""
        return self.profile.get("preferences", {}).get("personality_mode") == "jarvis"
    
    def format_as_jarvis(self, response: str, user_name: str = None) -> str:
        """Format response in JARVIS style"""
        if not self.is_jarvis_mode():
            return response
        
        user = user_name or "sir"
        
        jarvis_phrases = [
            ("at your service", "at your service, " + user),
            ("i'm ", "I am "),
            ("dont", "do not"),
            ("cant", "cannot"),
            ("wont", "will not"),
            ("ive", "I have"),
            ("youre", "you are"),
            ("im ", "I am "),
        ]
        
        result = response
        
        if not response.endswith('.') and not response.endswith('!'):
            result = result.rstrip() + "."
        
        return result
    
    def add_interest(self, interest: str):
        """Add an interest"""
        interests = self.profile.get("interests", [])
        if interest not in interests:
            interests.append(interest)
            self.profile["interests"] = interests
            self.save()
    
    def add_goal(self, goal: str):
        """Add a goal"""
        goals = self.profile.get("goals", [])
        if goal not in goals:
            goals.append(goal)
            self.profile["goals"] = goals
            self.save()
    
    def increment_conversation(self):
        """Increment conversation count"""
        self.profile["conversation_count"] = self.profile.get("conversation_count", 0) + 1
        self.save()
    
    def get_welcome_message(self) -> str:
        """Generate personalized welcome message"""
        name = self.get_name()
        conv_count = self.profile.get("conversation_count", 0)
        mode = self.get_preference("personality_mode", "assistant")
        
        # JARVIS mode messages
        if mode == "jarvis":
            if conv_count == 0:
                return f"🤖 Initializing JARVIS protocol. At your service, {name}. How may I assist you?"
            elif conv_count < 5:
                return f"🤖 Welcome back, {name}. Systems are operational. Awaiting your instructions."
            else:
                return f"🤖 Good to see you again, {name}. {conv_count} sessions logged. Ready when you are."
        
        # Standard messages
        if conv_count == 0:
            return f"👋 Hi {name}! I'm Jarvis, your AI companion. I'm here to help you with anything you need. What would you like to do today?"
        elif conv_count < 5:
            return f"👋 Welcome back, {name}! Good to see you again. How can I help you today?"
        else:
            return f"👋 Hey {name}! Welcome back. We've had {conv_count} conversations together. What are we working on today?"
    
    def get_system_prompt_context(self) -> str:
        """Get context for system prompt"""
        name = self.get_name()
        mode = self.get_preference("personality_mode", "assistant")
        style = self.get_preference("communication_style", "balanced")
        interests = self.profile.get("interests", [])
        
        context = f"""User name: {name}
Personality mode: {mode}
Communication style: {style}
Interests: {', '.join(interests) if interests else 'None set yet'}
"""
        return context
    
    def apply_response_adjustments(self, response: str) -> str:
        """Adjust response based on preferences"""
        length = self.get_preference("response_length", "medium")
        formality = self.get_preference("formality", "casual")
        
        # Adjust length (basic implementation)
        if length == "short":
            sentences = response.split(".")
            if len(sentences) > 3:
                response = ".".join(sentences[:3]) + "."
        elif length == "long":
            # Add more detail (simplified)
            response = response + "\n\nLet me know if you'd like more details!"
        
        return response


# Global profile instance
profile = UserProfile()