"""GitHub Agent - Handle Git operations and Pull Requests"""

import os
import subprocess
import json
from typing import Optional, Dict, List
import requests


class GitAgent:
    """
    Agent for handling Git operations and creating GitHub pull requests.
    Uses gh CLI for GitHub operations.
    """
    
    def __init__(
        self,
        repo_path: str = ".",
        remote: str = "origin",
        default_branch: str = "main"
    ):
        self.repo_path = repo_path
        self.remote = remote
        self.default_branch = default_branch
        self._token = os.getenv("GITHUB_TOKEN", "")
    
    def _run_command(self, cmd: List[str], capture_output: bool = True) -> Dict:
        """Run a shell command and return result"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                timeout=30
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
                "error": str(e),
                "output": "",
                "returncode": -1
            }
    
    def get_current_branch(self) -> str:
        """Get current branch name"""
        result = self._run_command(["git", "branch", "--show-current"])
        return result["output"].strip() if result["success"] else ""
    
    def get_status(self) -> Dict:
        """Get git status"""
        result = self._run_command(["git", "status", "--porcelain"])
        return {
            "success": result["success"],
            "changed": len(result["output"].strip().split("\n")) if result["output"].strip() else 0,
            "files": result["output"].strip().split("\n") if result["output"].strip() else []
        }
    
    def create_branch(self, branch_name: str) -> Dict:
        """Create a new branch"""
        # Check if branch exists
        check = self._run_command(["git", "show-ref", f"--verify", f"refs/heads/{branch_name}"])
        
        if check["success"]:
            # Branch exists, just checkout
            return self.checkout_branch(branch_name)
        
        # Create and checkout new branch
        result = self._run_command(["git", "checkout", "-b", branch_name])
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Created and checked out branch: {branch_name}",
                "branch": branch_name
            }
        
        return {
            "success": False,
            "message": f"Failed to create branch: {result['error']}"
        }
    
    def checkout_branch(self, branch_name: str) -> Dict:
        """Checkout an existing branch"""
        result = self._run_command(["git", "checkout", branch_name])
        
        return {
            "success": result["success"],
            "message": f"Checked out branch: {branch_name}" if result["success"] else result["error"],
            "branch": branch_name
        }
    
    def add_files(self, files: List[str]) -> Dict:
        """Stage files for commit"""
        if not files:
            files = ["."]
        
        result = self._run_command(["git", "add"] + files)
        
        return {
            "success": result["success"],
            "message": "Files staged" if result["success"] else result["error"]
        }
    
    def commit(self, message: str) -> Dict:
        """Commit staged changes"""
        result = self._run_command(["git", "commit", "-m", message])
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Committed: {message}",
                "commit_hash": self._get_last_commit_hash()
            }
        
        return {
            "success": False,
            "message": f"Commit failed: {result['error']}"
        }
    
    def _get_last_commit_hash(self) -> str:
        """Get the hash of the last commit"""
        result = self._run_command(["git", "rev-parse", "HEAD"])
        return result["output"].strip()[:8] if result["success"] else ""
    
    def push(self, branch: Optional[str] = None, force: bool = False) -> Dict:
        """Push branch to remote"""
        branch = branch or self.get_current_branch()
        
        cmd = ["git", "push", self.remote, branch]
        if force:
            cmd.append("--force")
        
        result = self._run_command(cmd)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Pushed {branch} to {self.remote}",
                "branch": branch
            }
        
        return {
            "success": False,
            "message": f"Push failed: {result['error']}"
        }
    
    def get_remote_url(self) -> Optional[str]:
        """Get the remote URL"""
        result = self._run_command(["git", "remote", "get-url", self.remote])
        return result["output"].strip() if result["success"] else None
    
    def get_repo_info(self) -> Dict:
        """Get repository information"""
        remote_url = self.get_remote_url()
        
        if not remote_url:
            return {"error": "No remote configured"}
        
        # Parse GitHub URL
        # git@github.com:owner/repo.git or https://github.com/owner/repo
        owner_repo = ""
        if "git@" in remote_url:
            owner_repo = remote_url.split(":")[-1].replace(".git", "")
        elif "github.com" in remote_url:
            owner_repo = remote_url.split("github.com/")[-1].replace(".git", "")
        
        if "/" in owner_repo:
            owner, repo = owner_repo.split("/", 1)
            return {
                "owner": owner,
                "repo": repo,
                "url": f"https://github.com/{owner}/{repo}"
            }
        
        return {"error": "Could not parse repository URL"}
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        base_branch: Optional[str] = None,
        head_branch: Optional[str] = None
    ) -> Dict:
        """Create a pull request using gh CLI"""
        if not self._token:
            return {
                "success": False,
                "message": "GITHUB_TOKEN not set. Please set it in .env"
            }
        
        base = base_branch or self.default_branch
        head = head_branch or self.get_current_branch()
        
        # Use gh CLI
        cmd = [
            "gh", "pr", "create",
            "--title", title,
            "--body", body,
            "--base", base,
            "--head", head
        ]
        
        result = self._run_command(cmd)
        
        if result["success"]:
            # Extract PR URL from output
            pr_url = ""
            if "https://github.com" in result["output"]:
                for line in result["output"].split("\n"):
                    if "github.com" in line and "pull" in line:
                        pr_url = line.strip()
                        break
            
            return {
                "success": True,
                "message": f"Created pull request",
                "pr_url": pr_url or result["output"].strip(),
                "title": title,
                "head": head,
                "base": base
            }
        
        return {
            "success": False,
            "message": f"Failed to create PR: {result['error']}",
            "error": result["error"]
        }
    
    def create_pr_with_api(
        self,
        title: str,
        body: str,
        base_branch: Optional[str] = None,
        head_branch: Optional[str] = None
    ) -> Dict:
        """Create PR using GitHub API directly"""
        if not self._token:
            return {
                "success": False,
                "message": "GITHUB_TOKEN not set"
            }
        
        repo_info = self.get_repo_info()
        
        if "error" in repo_info:
            return repo_info
        
        base = base_branch or self.default_branch
        head = head_branch or self.get_current_branch()
        
        url = f"https://api.github.com/repos/{repo_info['owner']}/{repo_info['repo']}/pulls"
        
        headers = {
            "Authorization": f"token {self._token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "title": title,
            "body": body,
            "base": base,
            "head": head
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 201:
                pr_data = response.json()
                return {
                    "success": True,
                    "message": "Pull request created",
                    "pr_url": pr_data["html_url"],
                    "pr_number": pr_data["number"],
                    "title": title
                }
            else:
                return {
                    "success": False,
                    "message": f"API error: {response.status_code}",
                    "error": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    def workflow(
        self,
        feature_name: str,
        commit_message: str,
        pr_title: str,
        pr_description: str
    ) -> Dict:
        """Complete workflow: create branch, commit, push, create PR"""
        
        # 1. Create branch
        branch_name = f"feature/{feature_name.replace(' ', '-').lower()}"
        
        branch_result = self.create_branch(branch_name)
        if not branch_result["success"]:
            return {
                "success": False,
                "message": f"Failed to create branch: {branch_result['message']}"
            }
        
        # 2. Add files
        add_result = self.add_files(["."])
        
        # 3. Commit
        commit_result = self.commit(commit_message)
        if not commit_result["success"]:
            return {
                "success": False,
                "message": f"Failed to commit: {commit_result['message']}"
            }
        
        # 4. Push
        push_result = self.push()
        if not push_result["success"]:
            return {
                "success": False,
                "message": f"Failed to push: {push_result['message']}"
            }
        
        # 5. Create PR
        pr_result = self.create_pr_with_api(pr_title, pr_description)
        
        return {
            "success": pr_result["success"],
            "message": pr_result["message"],
            "pr_url": pr_result.get("pr_url", ""),
            "branch": branch_name,
            "commit": commit_result.get("commit_hash", "")
        }


if __name__ == "__main__":
    # Test git agent
    agent = GitAgent("/Users/saurabhbatav/jarvis")
    
    print("=== Git Agent Test ===")
    print(f"Current branch: {agent.get_current_branch()}")
    
    print(f"\nRepo info: {agent.get_repo_info()}")
    
    print(f"\nStatus: {agent.get_status()}")