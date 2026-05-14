"""Planning Agent - Todo planner for Jarvis"""

import json
import os
import requests


class TodoPlanner:
    """
    Todo planner for Jarvis
    Creates actionable todo lists stored in memory
    """
    
    def __init__(self):
        self.storage_path = "./memory/todos.json"
        
        # Get API key from environment
        self.llm_key = os.environ.get("GROQ_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
        self.llm_url = "https://api.groq.com/openai/v1/chat/completions"
        self.llm_model = "llama-3.1-8b-instant"
    
    def _load_todos(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                return json.load(f)
        return []
    
    def _save_todos(self, todos):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump(todos, f, indent=2)
    
    def _call_llm(self, prompt: str) -> str:
        """Call Groq LLM"""
        if not self.llm_key:
            return None
            
        headers = {
            "Authorization": f"Bearer {self.llm_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(self.llm_url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except:
            pass
        return None
    
    def plan_and_create_todo(self, topic: str, num_items: int = 5) -> str:
        """Create a todo list for a topic"""
        
        # Try LLM first
        prompt = f"""Create a todo list with {num_items} actionable items for: {topic}

Format as a numbered list. Only return the list."""
        
        todo_text = self._call_llm(prompt)
        
        # Fallback if no LLM
        if not todo_text:
            topic_lower = topic.lower()
            
            # Pre-defined templates
            templates = {
                "learning": [
                    f"Research fundamentals of {topic}",
                    f"Find best online resources for {topic}",
                    f"Create study schedule for {topic}",
                    f"Practice basic concepts of {topic}",
                    f"Build a small project using {topic}"
                ],
                "fitness": [
                    f"Set fitness goal for {topic}",
                    f"Create workout plan for {topic}",
                    f"Track daily progress on {topic}",
                    f"Find resources about {topic}",
                    f"Review and adjust plan weekly"
                ],
                "work": [
                    f"Prioritize tasks for {topic}",
                    f"Set deadlines for {topic}",
                    f"Break down {topic} into steps",
                    f"Track progress on {topic}",
                    f"Review completed items"
                ]
            }
            
            # Find matching template
            items = None
            for key, template in templates.items():
                if key in topic_lower:
                    items = template
                    break
            
            if not items:
                items = [
                    f"Research {topic}",
                    f"Plan first steps for {topic}",
                    f"Gather resources for {topic}",
                    f"Take first action on {topic}",
                    f"Track progress on {topic}"
                ]
            
            todo_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
        
        # Parse and save todos
        todos = self._load_todos()
        new_todos = []
        
        for line in todo_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                if '.' in line:
                    item = line.split('.', 1)[-1].strip()
                elif '-' in line:
                    item = line.split('-', 1)[-1].strip()
                else:
                    item = line
                
                if item:
                    new_todos.append({
                        "id": len(todos) + len(new_todos) + 1,
                        "item": item,
                        "topic": topic,
                        "completed": False
                    })
        
        todos.extend(new_todos)
        self._save_todos(todos)
        
        return f"✅ Created todo list for '{topic}':\n\n{todo_text}\n\nSaved!"
    
    def get_todos(self, topic: str = None) -> list:
        """Get all todos or filter by topic"""
        todos = self._load_todos()
        if topic:
            todos = [t for t in todos if topic.lower() in t.get("topic", "").lower()]
        return todos
    
    def list_todos(self) -> str:
        """Format todo list for display"""
        todos = self._load_todos()
        if not todos:
            return "No todos yet. Say 'create todo for [topic]' to add one!"
        
        active_todos = [t for t in todos if not t.get("completed")]
        completed_todos = [t for t in todos if t.get("completed")]
        
        result = "📋 Your Todo Lists:\n\n"
        
        if active_todos:
            result += "Pending:\n"
            for t in active_todos:
                result += f"  [{t['id']}] {t['item']} (Topic: {t['topic']})\n"
        
        if completed_todos:
            result += "\nCompleted:\n"
            for t in completed_todos:
                result += f"  ✓ {t['item']}\n"
        
        return result
    
    def complete_todo(self, todo_id: int) -> str:
        """Mark a todo as complete"""
        todos = self._load_todos()
        for t in todos:
            if t['id'] == todo_id:
                t['completed'] = True
                self._save_todos(todos)
                return f"✅ Marked '{t['item']}' as completed!"
        return f"Todo #{todo_id} not found."