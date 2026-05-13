"""Health Agent - Personal health tracking and wellness"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class HealthTracker:
    """Personal health tracking (local storage)"""
    
    def __init__(self, storage_path: str = "./memory/health.json"):
        self.storage_path = storage_path
        self.data = self._load()
    
    def _load(self) -> Dict:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "weight_log": [],
            "exercise_log": [],
            "sleep_log": [],
            "mood_log": [],
            "symptoms": [],
            "water_log": [],
            "medications": []
        }
    
    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def log_weight(self, weight: float, unit: str = "kg") -> str:
        entry = {
            "date": datetime.now().isoformat(),
            "weight": weight,
            "unit": unit
        }
        self.data["weight_log"].append(entry)
        self._save()
        return f"✅ Logged weight: {weight}{unit}"
    
    def log_exercise(self, activity: str, duration: int, intensity: str = "moderate") -> str:
        entry = {
            "date": datetime.now().isoformat(),
            "activity": activity,
            "duration_minutes": duration,
            "intensity": intensity
        }
        self.data["exercise_log"].append(entry)
        self._save()
        return f"✅ Logged exercise: {activity} for {duration} minutes"
    
    def log_sleep(self, hours: float, quality: str = "good") -> str:
        entry = {
            "date": datetime.now().isoformat(),
            "hours": hours,
            "quality": quality
        }
        self.data["sleep_log"].append(entry)
        self._save()
        return f"✅ Logged sleep: {hours} hours ({quality})"
    
    def log_mood(self, mood: str, note: str = "") -> str:
        entry = {
            "date": datetime.now().isoformat(),
            "mood": mood,
            "note": note
        }
        self.data["mood_log"].append(entry)
        self._save()
        return f"✅ Logged mood: {mood}"
    
    def log_water(self, amount: int) -> str:
        entry = {
            "date": datetime.now().isoformat(),
            "amount_ml": amount
        }
        self.data["water_log"].append(entry)
        self._save()
        return f"✅ Logged water: {amount}ml"
    
    def log_symptom(self, symptom: str, severity: int = 1) -> str:
        entry = {
            "date": datetime.now().isoformat(),
            "symptom": symptom,
            "severity": severity
        }
        self.data["symptoms"].append(entry)
        self._save()
        return f"✅ Logged symptom: {symptom} (severity: {severity})"
    
    def get_summary(self, days: int = 7) -> str:
        lines = ["📊 Health Summary (Last 7 days):\n"]
        
        # Weight
        recent_weight = self.data["weight_log"][-days:] if self.data["weight_log"] else []
        if recent_weight:
            avg = sum(e["weight"] for e in recent_weight) / len(recent_weight)
            lines.append(f"Weight: {avg:.1f} kg (avg)")
        
        # Exercise
        recent_exercise = self.data["exercise_log"][-days:] if self.data["exercise_log"] else []
        total_mins = sum(e["duration_minutes"] for e in recent_exercise)
        lines.append(f"Exercise: {total_mins} minutes total")
        
        # Sleep
        recent_sleep = self.data["sleep_log"][-days:] if self.data["sleep_log"] else []
        if recent_sleep:
            avg_hours = sum(e["hours"] for e in recent_sleep) / len(recent_sleep)
            lines.append(f"Sleep: {avg_hours:.1f} hours (avg)")
        
        # Water
        recent_water = self.data["water_log"][-days:] if self.data["water_log"] else []
        total_ml = sum(e["amount_ml"] for e in recent_water)
        lines.append(f"Water: {total_ml}ml total")
        
        # Mood
        recent_mood = self.data["mood_log"][-days:] if self.data["mood_log"] else []
        if recent_mood:
            moods = [e["mood"] for e in recent_mood]
            most_common = max(set(moods), key=moods.count)
            lines.append(f"Mood: {most_common} (most common)")
        
        return "\n".join(lines)


class HealthTips:
    """Free health information"""
    
    @staticmethod
    def get_bmi(weight_kg: float, height_m: float) -> Dict:
        bmi = weight_kg / (height_m ** 2)
        
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"
        
        return {"bmi": round(bmi, 1), "category": category}
    
    @staticmethod
    def get_water_goal(weight_kg: float) -> int:
        """Calculate daily water intake goal (ml)"""
        return int(weight_kg * 35)
    
    @staticmethod
    def get_sleep_requirements(age: int) -> Dict:
        if age < 1:
            return {"hours": "12-16", "description": "including naps"}
        elif age < 3:
            return {"hours": "11-14", "description": "including naps"}
        elif age < 6:
            return {"hours": "10-13", "description": "including naps"}
        elif age < 13:
            return {"hours": "9-11", "description": "nightly"}
        elif age < 18:
            return {"hours": "8-10", "description": "nightly"}
        else:
            return {"hours": "7-9", "description": "nightly"}


class HealthAgent:
    """
    Personal Health Agent:
    - Weight, exercise, sleep, mood tracking
    - Water intake logging
    - Symptom tracking
    - Health summaries
    - BMI calculator
    - All data stored locally (free, private)
    """
    
    def __init__(self):
        self.tracker = HealthTracker()
        self.tools = HealthTips()
        self._instructions = """You are Jarvis Health Agent, a personal health and wellness assistant.
Your role is to help users track their health, exercise, sleep, and overall wellbeing.
Provide encouraging and supportive responses.
Never provide medical diagnosis - always recommend consulting a professional.
Focus on healthy habits and positive reinforcement."""
    
    def get_instructions(self, user_context: str = "") -> str:
        base = self._instructions
        if user_context:
            return base + f"\n\nUser context: {user_context}"
        return base
    
    def log_weight(self, weight: float, unit: str = "kg") -> str:
        return self.tracker.log_weight(weight, unit)
    
    def log_exercise(self, activity: str, duration: int, intensity: str = "moderate") -> str:
        return self.tracker.log_exercise(activity, duration, intensity)
    
    def log_sleep(self, hours: float, quality: str = "good") -> str:
        return self.tracker.log_sleep(hours, quality)
    
    def log_mood(self, mood: str, note: str = "") -> str:
        return self.tracker.log_mood(mood, note)
    
    def log_water(self, amount: int) -> str:
        return self.tracker.log_water(amount)
    
    def log_symptom(self, symptom: str, severity: int = 1) -> str:
        return self.tracker.log_symptom(symptom, severity)
    
    def summary(self) -> str:
        return self.tracker.get_summary()
    
    def calculate_bmi(self, weight: float, height_cm: float) -> str:
        height_m = height_cm / 100
        result = self.tools.get_bmi(weight, height_m)
        return f"BMI: {result['bmi']} ({result['category']})"
    
    def water_goal(self, weight_kg: float) -> str:
        goal = self.tools.get_water_goal(weight_kg)
        return f"Daily water goal: {goal}ml ({goal/1000:.1f}L)"
    
    def quick_tip(self) -> str:
        tips = [
            "💧 Remember to drink water throughout the day!",
            "😴 Aim for 7-9 hours of sleep for optimal health.",
            "🚶 Take a short walk every hour if you sit a lot.",
            "🥗 Include vegetables in at least two meals today.",
            "🧘 Take 5 minutes to practice deep breathing.",
            "📱 Take a break from screens every 30 minutes.",
            "💪 Even a 10-minute workout is better than none!",
            "😴 Try to go to bed at the same time each night."
        ]
        import random
        return random.choice(tips)