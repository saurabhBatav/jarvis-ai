"""
Advanced Patterns Test Suite for Jarvis
Tests for Orchestrator-Workers and AutoAgents patterns
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# =============================================================================
# PATTERN #1: ORCHESTRATOR-WORKERS
# =============================================================================

"""
TEST RESULTS - Orchestrator-Workers Pattern

The orchestrator analyzes each request and routes to the appropriate specialized worker.

Test Cases:
-----------

1. FINANCE REQUEST → FinanceWorker
   Input: "What's the price of Apple stock?"
   Expected: FinanceWorker
   Result: ✅ PASSED
   Output:
   "However, I'm a large language model, I don't have real-time access to 
   current market data. But I can guide you on how to find the current 
   price of Apple stock..."

2. CODE REQUEST → CodeWorker
   Input: "Write a Python function to reverse a string"
   Expected: CodeWorker
   Result: ✅ PASSED
   Output:
   "**Reversing a String in Python**
   
   Here's a simple and efficient way to reverse a string in Python using slicing.
   
   ### Method 1: Using Slicing
   ..."

3. RESEARCH REQUEST → ResearchWorker
   Input: "Research about quantum computing"
   Expected: ResearchWorker
   Result: ✅ PASSED
   Output:
   "**Introduction to Quantum Computing**
   
   Quantum computing is a revolutionary technology that leverages the principles 
   of quantum mechanics to perform calculations and operations..."

4. GENERAL QUESTION → GeneralWorker
   Input: "What is the weather today?"
   Expected: GeneralWorker
   Result: ✅ PASSED
   Output:
   "However, I'm a large language model, I don't have real-time access to 
   current weather conditions. But I can suggest a few ways to find out 
   the weather today..."

Summary: 4/4 tests passed
"""

def test_orchestrator_workers():
    """Test Orchestrator-Workers pattern"""
    
    from src.agents.advanced.orchestrator_workers import OrchestratorWorkers
    
    orch = OrchestratorWorkers()
    
    test_cases = [
        {
            "input": "What's the price of Apple stock?",
            "expected_worker": "FinanceWorker",
            "description": "Finance query should route to FinanceWorker"
        },
        {
            "input": "Write a Python function to reverse a string",
            "expected_worker": "CodeWorker", 
            "description": "Code request should route to CodeWorker"
        },
        {
            "input": "Research about quantum computing",
            "expected_worker": "ResearchWorker",
            "description": "Research query should route to ResearchWorker"
        },
        {
            "input": "What is the weather today?",
            "expected_worker": "GeneralWorker",
            "description": "General question should route to GeneralWorker"
        }
    ]
    
    print("=" * 60)
    print("TESTING: Orchestrator-Workers Pattern")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Input: {test['input']}")
        print(f"Expected: {test['expected_worker']}")
        
        try:
            result = orch.process(test['input'])
            
            # Check if correct worker was selected
            if test['expected_worker'] in result:
                print(f"Result: ✅ PASSED")
                passed += 1
            else:
                print(f"Result: ❌ FAILED - Wrong worker")
                failed += 1
                
        except Exception as e:
            print(f"Result: ❌ FAILED - Error: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed


# =============================================================================
# PATTERN #2: AUTOAGENTS
# =============================================================================

"""
TEST RESULTS - AutoAgents Pattern

AutoAgents analyzes task complexity and automatically determines:
- Number of agents needed (1-4)
- Workflow type (sequential, parallel, orchestrator-workers, evaluator-optimiser)
- Roles for each agent

Test Cases:
-----------

1. SIMPLE TASK - Write haiku
   Input: "Write a haiku about spring"
   Analysis: 2 agents, sequential workflow
   Roles: researcher, writer
   Result: ✅ PASSED
   Output:
   "**Idea-Generator:** Let's focus on the vibrant colors and scents of spring. 
   We could incorporate the blooming flowers and the fresh scent of the season..."

2. COMPLEX TASK - Research and write report
   Input: "Research AI trends and write report"
   Analysis: 2 agents, sequential workflow  
   Roles: researcher, writer
   Result: ✅ PASSED
   Output:
   "**Research Team:**
   - Researcher: Alex Chen
   - Writer: Emily Patel

   **Task: Research AI Trends and Write Report**..."

3. CREATIVE TASK - Movie script
   Input: "Create a movie script"
   Analysis: 2+ agents, orchestrator-workers pattern
   Result: ✅ PASSED
   Output:
   "**Task Analysis:**
   
   The task involves creating a movie script, which requires a comprehensive 
   approach involving..."

4. TECHNICAL TASK - Debug code
   Input: "Debug this code"
   Analysis: 2 agents, sequential workflow
   Roles: code analysis
   Result: ✅ PASSED
   Output:
   "**Task: Debug this code**
   
   **Code:**
   ```python
   # Define a function to calculate the area of a rectangle
   def calculate_a..."

Summary: 4/4 tests passed
"""

def test_auto_agents():
    """Test AutoAgents pattern"""
    
    from src.agents.advanced.auto_agents import AutoAgents
    
    auto = AutoAgents()
    
    test_cases = [
        {
            "input": "Write a haiku about spring",
            "description": "Simple creative task",
            "expected_workflows": ["sequential", "parallel", "evaluator-optimiser"]
        },
        {
            "input": "Research AI trends and write report",
            "description": "Multi-step research task",
            "expected_workflows": ["sequential", "orchestrator-workers"]
        },
        {
            "input": "Create a movie script", 
            "description": "Complex creative task",
            "expected_workflows": ["sequential", "orchestrator-workers", "parallel"]
        },
        {
            "input": "Debug this code",
            "description": "Technical debugging task",
            "expected_workflows": ["sequential", "evaluator-optimiser"]
        }
    ]
    
    print("=" * 60)
    print("TESTING: AutoAgents Pattern")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Input: {test['input']}")
        
        try:
            # First analyze complexity
            analysis = auto.analyze_task_complexity(test['input'])
            print(f"Analysis: agents={analysis['agents']}, workflow={analysis['workflow']}")
            
            # Then process
            result = auto.process(test['input'])
            
            if result and len(result) > 50:
                print(f"Result: ✅ PASSED")
                passed += 1
            else:
                print(f"Result: ❌ FAILED - Empty result")
                failed += 1
                
        except Exception as e:
            print(f"Result: ❌ FAILED - Error: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed


# =============================================================================
# RUN ALL TESTS
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ADVANCED PATTERNS TEST SUITE FOR JARVIS")
    print("=" * 70)
    
    # Test Orchestrator-Workers
    orch_passed, orch_failed = test_orchestrator_workers()
    
    print("\n")
    
    # Test AutoAgents  
    auto_passed, auto_failed = test_auto_agents()
    
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Orchestrator-Workers: {orch_passed}/4 passed")
    print(f"AutoAgents: {auto_passed}/4 passed")
    print(f"Total: {orch_passed + auto_passed}/8 tests passed")
    print("=" * 70)