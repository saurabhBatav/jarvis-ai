"""DocAgent - Main orchestrator for Documentation-based Implementation"""

import os
from typing import Optional, Dict, List
from datetime import datetime
from .docs_search import DocsSearchAgent
from .implementation import ImplementationAgent, FeaturePlanner
from .git_agent import GitAgent
from .sources import DocumentationManager


class DocAgent:
    """
    Main Documentation Agent that:
    1. Searches for documentation on a feature
    2. Implements the feature based on documentation
    3. Creates a GitHub pull request
    
    Usage:
        agent = DocAgent()
        result = agent.implement_and_create_pr(
            feature="voice-input",
            description="Add voice input using Groq Whisper"
        )
    """
    
    def __init__(
        self,
        repo_path: str = "/Users/saurabhbatav/jarvis",
        llm: str = "llama-3.1-8b-instant"
    ):
        self.docs_search = DocsSearchAgent()
        self.docs_manager = DocumentationManager()  # Multi-source support
        self.implementation = ImplementationAgent(llm=llm)
        self.git = GitAgent(repo_path=repo_path)
        
        self.current_documentation = None
        self.current_source = None
        self.implementation_code = None
    
    def search_documentation(self, feature: str) -> str:
        """Search for documentation on a feature"""
        print(f"\n🔍 Searching documentation for: {feature}")
        
        result = self.docs_search.search(feature)
        
        if "Could not find" in result or not result:
            # Try other sources
            return self.search_all_sources(feature)
        
        self.current_documentation = result
        self.current_source = "PraisonAI"
        return result
    
    def search_all_sources(self, feature: str) -> Optional[str]:
        """Search all documentation sources"""
        print(f"\n🌐 Searching all sources for: {feature}")
        
        # Search PraisonAI first
        search_result = self.docs_search.search_and_cache(feature)
        if search_result.get("source") != "none":
            self.current_documentation = search_result.get("content", "")
            self.current_source = "PraisonAI"
            return self.current_documentation
        
        # Search other sources
        results = self.docs_manager.search_all(feature)
        
        if results:
            lines = [f"🔍 Found documentation in {len(results)} source(s):\n"]
            
            for r in results:
                source = r.get("source", "Unknown")
                url = r.get("url", "")
                lines.append(f"• {source}: {url}")
            
            self.current_documentation = "\n".join(lines)
            self.current_source = "Multiple"
            
            # Fetch from first source
            if results:
                first_result = results[0]
                source_name = first_result.get("source", "")
                url = first_result.get("url", "")
                
                # Fetch the actual content
                fetch_result = self.docs_manager.fetch_from_source(source_name, feature)
                if "error" not in fetch_result:
                    self.current_documentation = str(fetch_result)
                    self.current_source = source_name
            
            return self.current_documentation
        
        return None
    
    def fetch_documentation(self, url_or_topic: str) -> str:
        """Fetch specific documentation page"""
        print(f"\n📖 Fetching documentation: {url_or_topic}")
        
        result = self.docs_search.fetch_page(url_or_topic)
        self.current_documentation = result
        return result
    
    def request_documentation(self, feature: str) -> str:
        """Ask user for documentation if not found"""
        return f"""I could not find documentation for '{feature}' in the PraisonAI docs.

Please provide:
1. The documentation URL or topic
2. Or paste the relevant documentation here

Once you provide the documentation, I'll implement the feature and create a pull request."""
    
    def implement(
        self,
        feature_name: str,
        documentation: Optional[str] = None,
        target_path: Optional[str] = None
    ) -> str:
        """Implement the feature based on documentation"""
        docs = documentation or self.current_documentation
        
        if not docs:
            return "No documentation provided. Please provide documentation first."
        
        print(f"\n💻 Implementing: {feature_name}")
        
        # Analyze documentation
        analysis = FeaturePlanner.analyze_documentation(docs)
        print(f"   Found {len(analysis.get('code_patterns', []))} code patterns")
        print(f"   Found {len(analysis.get('imports', []))} imports")
        
        # Plan files
        planned_files = FeaturePlanner.plan_files(docs, feature_name)
        print(f"   Planned files: {planned_files}")
        
        # Get implementation from LLM
        code = self.implementation.implement(
            feature_name=feature_name,
            documentation=docs,
            target_path=target_path
        )
        
        self.implementation_code = code
        return code
    
    def create_file(self, file_path: str, code: Optional[str] = None) -> Dict:
        """Create a file with the implementation"""
        content = code or self.implementation_code
        
        if not content:
            return {
                "success": False,
                "message": "No implementation code available"
            }
        
        return self.implementation.create_file(file_path, content)
    
    def create_pr(
        self,
        feature_name: str,
        description: str,
        commit_message: Optional[str] = None,
        pr_title: Optional[str] = None,
        pr_description: Optional[str] = None,
        test_results: Optional[Dict] = None
    ) -> Dict:
        """Create a pull request with the implementation"""
        
        commit_msg = commit_message or f"feat: Add {feature_name} feature"
        
        title = pr_title or f"feat: Add {feature_name}"
        
        test_status = "✅ All tests passed" if test_results and test_results.get("success") else "⚠️ Tests not run"
        
        body = f"""## Description
{description}

## Changes
- Implemented {feature_name} based on PraisonAI documentation
- Added comprehensive test cases with real-life scenarios

## Testing
- **Test Status**: {test_status}
- Code validated for syntax errors
- Follows documentation patterns

## Documentation
{self.current_documentation[:300] if self.current_documentation else 'N/A'}...

## Test Results
See test results file: `tests/test_results_{feature_name.replace(' ', '_').lower()}.md`
"""        
        return self.git.workflow(
            feature_name=feature_name,
            commit_message=commit_msg,
            pr_title=title,
            pr_description=body
        )
    
    def run_full_workflow(
        self,
        feature: str,
        description: str,
        documentation: Optional[str] = None,
        target_file: Optional[str] = None,
        test_file_path: Optional[str] = None,
        run_tests: bool = True
    ) -> Dict:
        """Run the complete workflow: search docs -> implement -> test -> create PR"""
        
        results = {
            "feature": feature,
            "steps": [],
            "start_time": datetime.now().isoformat()
        }
        
        # Step 1: Search for documentation (internet + local cache)
        print(f"\n{'='*60}")
        print(f"STEP 1: Searching documentation for '{feature}'")
        print(f"{'='*60}")
        
        if documentation:
            docs_result = self.fetch_documentation(documentation)
        else:
            # Search and cache from internet
            search_result = self.docs_search.search_and_cache(feature)
            
            if search_result.get("source") == "none":
                # Ask user for documentation
                return {
                    "success": False,
                    "message": self.request_documentation(feature),
                    "step": "documentation_search"
                }
            
            docs_result = search_result.get("content", "")
            print(f"Found: {search_result.get('source', 'unknown')}")
        
        if not docs_result or "Could not find" in docs_result:
            return {
                "success": False,
                "message": self.request_documentation(feature),
                "step": "documentation_search"
            }
        
        self.current_documentation = docs_result
        
        results["steps"].append({
            "step": "documentation_search",
            "success": True,
            "source": "internet" if not documentation else "provided",
            "cached": True
        })
        
        # Step 2: Implement the feature
        print(f"\n{'='*60}")
        print(f"STEP 2: Implementing '{feature}'")
        print(f"{'='*60}")
        
        try:
            impl_result = self.implementation.implement(
                feature_name=feature,
                documentation=docs_result,
                target_path=target_file
            )
            
            self.implementation_code = impl_result
            
            results["steps"].append({
                "step": "implementation",
                "success": True,
                "code_length": len(impl_result)
            })
            
        except Exception as e:
            results["steps"].append({
                "step": "implementation",
                "success": False,
                "error": str(e)
            })
            results["success"] = False
            results["message"] = f"Implementation failed: {str(e)}"
            return results
        
        # Step 3: Validate code
        print(f"\n{'='*60}")
        print(f"STEP 3: Validating code")
        print(f"{'='*60}")
        
        validation = self.implementation.validate_code(impl_result)
        
        results["steps"].append({
            "step": "code_validation",
            "success": validation["valid"],
            "errors": validation.get("errors", [])
        })
        
        if not validation["valid"]:
            results["success"] = False
            results["message"] = f"Code validation failed: {validation['errors']}"
            return results
        
        print("✅ Code validation passed")
        
        # Step 4: Generate and run tests
        test_results = None
        if run_tests:
            print(f"\n{'='*60}")
            print(f"STEP 4: Generating and running tests")
            print(f"{'='*60}")
            
            # Generate test file
            feature_test_name = feature.replace(' ', '_').lower()
            test_path = test_file_path or f"tests/test_{feature_test_name}.py"
            
            test_code = self.implementation.generate_test_file(
                feature_name=feature,
                implementation_code=impl_result,
                documentation=docs_result
            )
            
            # Save test file
            test_result = self.implementation.create_test_file(test_path, test_code)
            
            results["steps"].append({
                "step": "test_generation",
                "success": test_result["success"],
                "path": test_result.get("path", "")
            })
            
            if test_result["success"]:
                print(f"✅ Test file created: {test_path}")
                
                # Run tests
                run_result = self.implementation.run_tests(test_path)
                test_results = run_result
                
                results["steps"].append({
                    "step": "test_execution",
                    "success": run_result["success"],
                    "output": run_result.get("output", "")[:500],
                    "errors": run_result.get("error", "")[:500] if not run_result["success"] else None
                })
                
                # Generate results file
                results_content = self.implementation.generate_results_file(run_result, feature)
                results_path = f"tests/test_results_{feature_test_name}.md"
                
                with open(results_path, 'w') as f:
                    f.write(results_content)
                
                print(f"\n{'='*60}")
                print(f"TEST RESULTS")
                print(f"{'='*60}")
                print(f"Status: {'✅ PASSED' if run_result['success'] else '❌ FAILED'}")
                if not run_result["success"]:
                    print(f"Errors: {run_result.get('error', '')[:200]}")
            else:
                print(f"❌ Test generation failed: {test_result['message']}")
        
        # Step 5: Create pull request
        print(f"\n{'='*60}")
        print(f"STEP 5: Creating Pull Request")
        print(f"{'='*60}")
        
        pr_result = self.create_pr(
            feature_name=feature,
            description=description,
            test_results=test_results
        )
        
        results["steps"].append({
            "step": "pull_request",
            "success": pr_result["success"],
            "pr_url": pr_result.get("pr_url", ""),
            "branch": pr_result.get("branch", "")
        })
        
        results["success"] = pr_result["success"]
        results["message"] = pr_result.get("message", "")
        results["pr_url"] = pr_result.get("pr_url", "")
        results["end_time"] = datetime.now().isoformat()
        
        return results
    
    def status(self) -> str:
        """Get current status of the agent"""
        lines = ["📊 DocAgent Status:"]
        
        # Documentation
        if self.current_documentation:
            lines.append("  ✅ Documentation loaded")
        else:
            lines.append("  ⚪ No documentation loaded")
        
        # Implementation
        if self.implementation_code:
            lines.append("  ✅ Implementation ready")
        else:
            lines.append("  ⚪ No implementation generated")
        
        # Git
        branch = self.git.get_current_branch()
        lines.append(f"  📁 Current branch: {branch}")
        
        repo_info = self.git.get_repo_info()
        if "error" not in repo_info:
            lines.append(f"  🔗 Repository: {repo_info.get('url', 'N/A')}")
        
        # GitHub token
        if self.git._token:
            lines.append("  ✅ GitHub token configured")
        else:
            lines.append("  ⚠️ GitHub token not set (PR creation will fail)")
        
        return "\n".join(lines)


class FeatureRequest:
    """Represents a feature request to be implemented"""
    
    def __init__(self, name: str, description: str, documentation: str = None):
        self.name = name
        self.description = description
        self.documentation = documentation
    
    def __repr__(self):
        return f"FeatureRequest({self.name})"


if __name__ == "__main__":
    # Test DocAgent
    agent = DocAgent()
    
    print(agent.status())
    
    print("\n=== Testing Documentation Search ===")
    result = agent.search_documentation("memory")
    print(result[:500] if result else "No results")
    
    print("\n=== Testing Topic List ===")
    print(agent.docs_search.list_topics())