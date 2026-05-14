"""Implementation Agent - Write code based on documentation"""

import os
import re
from typing import Optional, Dict, List
from praisonaiagents import Agent


class ImplementationAgent:
    """
    Agent that implements features based on documentation.
    Uses LLM to generate code following the documentation patterns.
    """
    
    def __init__(self, llm: str = "llama-3.1-8b-instant"):
        self.llm = llm
        self._agent = None
        self._instructions = """You are Jarvis Implementation Agent.
Your role is to write code that follows the patterns shown in the documentation.
You must:
1. Follow the exact syntax and patterns from the documentation
2. Use proper PraisonAI imports and configurations
3. Add proper docstrings and comments
4. Test the code conceptually before outputting
5. Follow existing codebase conventions

Output ONLY the code, no explanations unless asked."""
    
    def _create_agent(self) -> Agent:
        return Agent(
            name="Implementation Agent",
            instructions=self._instructions,
            llm=self.llm
        )
    
    def initialize(self):
        if self._agent is None:
            self._agent = self._create_agent()
    
    def implement(
        self,
        feature_name: str,
        documentation: str,
        target_path: Optional[str] = None,
        existing_code: Optional[str] = None
    ) -> str:
        """Implement a feature based on documentation"""
        self.initialize()
        
        prompt = self._build_implementation_prompt(
            feature_name, documentation, target_path, existing_code
        )
        
        result = self._agent.start(prompt)
        
        return result
    
    def _build_implementation_prompt(
        self,
        feature_name: str,
        documentation: str,
        target_path: Optional[str],
        existing_code: Optional[str]
    ) -> str:
        prompt = f"""Implement the following feature based on the documentation:

## Feature Name
{feature_name}

## Documentation
{documentation}
"""
        
        if target_path:
            prompt += f"\n## Target File\n{target_path}\n"
        
        if existing_code:
            prompt += f"\n## Existing Code (for reference/extension)\n{existing_code}\n"
        
        prompt += """
## Requirements
1. Write complete, working code
2. Follow the exact patterns from documentation
3. Include proper imports
4. Add docstrings explaining what the code does
5. Follow Python best practices

## Output
Write the complete implementation code. If modifying an existing file, include the full file content.
"""
        
        return prompt
    
    def create_file(
        self,
        file_path: str,
        content: str
    ) -> Dict[str, str]:
        """Create a new file with the implementation"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write the file
            with open(file_path, 'w') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"Created {file_path}",
                "path": file_path
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating file: {str(e)}",
                "path": file_path
            }
    
    def update_file(
        self,
        file_path: str,
        old_code: str,
        new_code: str
    ) -> Dict[str, str]:
        """Update an existing file with new code"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": f"File not found: {file_path}",
                    "path": file_path
                }
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Replace old code with new code
            if old_code in content:
                new_content = content.replace(old_code, new_code)
            else:
                # Try regex for more flexible matching
                pattern = re.escape(old_code)
                new_content = re.sub(pattern, new_code, content, flags=re.DOTALL)
            
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            return {
                "success": True,
                "message": f"Updated {file_path}",
                "path": file_path
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating file: {str(e)}",
                "path": file_path
            }
    
    def add_to_existing(
        self,
        file_path: str,
        code_to_add: str,
        position: str = "end"
    ) -> Dict[str, str]:
        """Add code to an existing file"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": f"File not found: {file_path}",
                    "path": file_path
                }
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            if position == "end":
                new_content = content + "\n\n" + code_to_add
            elif position == "start":
                new_content = code_to_add + "\n\n" + content
            else:
                return {
                    "success": False,
                    "message": f"Unknown position: {position}. Use 'start' or 'end'",
                    "path": file_path
                }
            
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            return {
                "success": True,
                "message": f"Added code to {file_path}",
                "path": file_path
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error adding code: {str(e)}",
                "path": file_path
            }
    
    def validate_code(self, code: str) -> Dict[str, any]:
        """Validate the code syntax"""
        try:
            compile(code, '<string>', 'exec')
            return {
                "valid": True,
                "errors": []
            }
        except SyntaxError as e:
            return {
                "valid": False,
                "errors": [f"Line {e.lineno}: {e.msg}"]
            }
    
    def suggest_tests(self, code: str, feature_name: str) -> str:
        """Suggest tests for the implemented feature"""
        self.initialize()
        
        prompt = f"""Based on this implementation, suggest unit tests:

## Feature
{feature_name}

## Code
{code}

## Requirements
1. Write pytest-style tests
2. Test both success and failure cases
3. Include mock setup if needed
4. Keep tests simple and focused

Output only the test code, no explanations."""
        
        return self._agent.start(prompt)
    
    def generate_test_file(self, feature_name: str, implementation_code: str, documentation: str) -> str:
        """Generate a comprehensive test file with real-life cases"""
        self.initialize()
        
        prompt = f"""Generate a comprehensive pytest test file for this feature with REAL-LIFE TEST CASES.

## Feature Name
{feature_name}

## Implementation Code
{implementation_code[:2000]}

## Documentation Reference
{documentation[:1000]}

## Requirements for Test File:

1. **Test Class Name**: Test{feature_name.replace(' ', '')}Feature

2. **Real-life Test Cases** - Must include:
   - Test successful initialization with valid inputs
   - Test with various valid parameters
   - Test error handling for invalid inputs
   - Test edge cases
   - Test integration with existing Jarvis components

3. **Use descriptive test method names** like:
   - test_feature_works_with_valid_input()
   - test_feature_handles_empty_input()
   - test_feature_handles_invalid_input()

4. **Add docstrings** explaining the real-life scenario

5. **Include pytest fixtures** where appropriate

6. **Output the full test file code** ready to run

Example real-life test structure:
```python
import pytest
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestVoiceInputFeature:
    '''Real-life tests for Voice Input feature'''
    
    @pytest.fixture
    def feature_instance(self):
        # Setup for tests
        from src.agents.domain.voice import VoiceAgent
        return VoiceAgent()
    
    def test_voice_input_recognizes_speech(self, feature_instance):
        '''Test: User speaks a command and it gets recognized'''
        result = feature_instance.listen(timeout=5)
        assert result is not None
    
    # ... more tests
```

Write the COMPLETE test file now. Include all imports and setup needed."""
        
        return self._agent.start(prompt)
    
    def create_test_file(self, file_path: str, test_code: str) -> Dict:
        """Create the test file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(test_code)
            
            return {
                "success": True,
                "message": f"Created test file: {file_path}",
                "path": file_path
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating test file: {str(e)}",
                "path": file_path
            }
    
    def run_tests(self, test_file_path: str) -> Dict:
        """Run the test file and return results"""
        import subprocess
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", test_file_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_results_file(self, test_results: Dict, feature_name: str) -> str:
        """Generate a test results summary file"""
        results = f"""# Test Results - {feature_name}

## Test Execution Summary

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Status**: {'✅ PASSED' if test_results['success'] else '❌ FAILED'}

---

## Test Output

```
{test_results.get('output', 'No output')}
```

---

## Error Details

```
{test_results.get('error', 'No errors')}
```

---

## Summary

- Tests: {'All passed' if test_results['success'] else 'Some tests failed'}
- Return code: {test_results.get('returncode', -1)}

---

*Generated by Jarvis DocAgent*
"""
        return results


class FeaturePlanner:
    """Plans the implementation based on documentation analysis"""
    
    @staticmethod
    def analyze_documentation(documentation: str) -> Dict:
        """Analyze documentation to extract implementation details"""
        analysis = {
            "features": [],
            "imports": [],
            "code_patterns": [],
            "configuration": {}
        }
        
        # Extract imports
        import_pattern = r'from\s+(\S+)\s+import\s+([^\n]+)'
        for match in re.finditer(import_pattern, documentation):
            analysis["imports"].append({
                "module": match.group(1),
                "items": match.group(2).split(", ")
            })
        
        # Extract code patterns
        code_pattern = r'```python(.*?)```'
        for match in re.finditer(code_pattern, documentation, re.DOTALL):
            analysis["code_patterns"].append(match.group(1).strip())
        
        # Extract configuration options
        config_pattern = r'`(\w+)`(?:\s*:\s*(\w+))?'
        for match in re.finditer(config_pattern, documentation):
            key = match.group(1)
            value_type = match.group(2) or "string"
            analysis["configuration"][key] = value_type
        
        return analysis
    
    @staticmethod
    def plan_files(documentation: str, feature_name: str) -> List[str]:
        """Plan which files need to be created/modified"""
        files = []
        
        # Common patterns for feature implementation
        if "Agent" in documentation:
            files.append(f"src/agents/domain/{feature_name.lower()}.py")
        
        if "tool" in documentation.lower():
            files.append(f"src/tools/{feature_name.lower()}.py")
        
        if "memory" in documentation.lower():
            files.append("src/memory/")
        
        # Add tests
        files.append(f"tests/test_{feature_name.lower()}.py")
        
        return files


if __name__ == "__main__":
    # Test
    agent = ImplementationAgent()
    
    # Test code validation
    valid_code = "def test(): pass"
    result = agent.validate_code(valid_code)
    print("Valid code:", result)
    
    invalid_code = "def test( pass"
    result = agent.validate_code(invalid_code)
    print("Invalid code:", result)
    
    # Test analysis
    doc = """
    ```python
    from praisonaiagents import Agent
    agent = Agent(name="Test", memory=True)
    ```
    
    Configuration: `memory` (bool), `session_id` (str)
    """
    analysis = FeaturePlanner.analyze_documentation(doc)
    print("\nAnalysis:", analysis)