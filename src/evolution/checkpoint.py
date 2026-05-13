"""Checkpoint System - Shadow Git for auto-rollback"""

import os
import json
import shutil
import subprocess
from datetime import datetime
from typing import Optional, List, Dict


class CheckpointManager:
    """
    Shadow Git Checkpoint system for Jarvis.
    Creates transparent state snapshots during task execution.
    Enables auto-rollback on failure.
    """
    
    def __init__(self, checkpoint_dir: str = "./memory/checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
        self.current_checkpoint: Optional[str] = None
    
    def create_checkpoint(self, name: str = None) -> str:
        """
        Create a checkpoint of current state.
        
        Args:
            name: Optional name for the checkpoint
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = name or f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create checkpoint directory
        cp_path = os.path.join(self.checkpoint_dir, checkpoint_id)
        os.makedirs(cp_path, exist_ok=True)
        
        # Snapshot key directories
        dirs_to_snapshot = ["src", "config", "agents"]
        
        for dir_name in dirs_to_snapshot:
            src = os.path.join(".", dir_name)
            dst = os.path.join(cp_path, dir_name)
            if os.path.exists(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
        
        # Save metadata
        metadata = {
            "id": checkpoint_id,
            "created": datetime.now().isoformat(),
            "dirs": dirs_to_snapshot
        }
        
        with open(os.path.join(cp_path, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        self.current_checkpoint = checkpoint_id
        return checkpoint_id
    
    def restore_checkpoint(self, checkpoint_id: str = None) -> bool:
        """
        Restore to a previous checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to restore (or current if None)
            
        Returns:
            True if successful
        """
        cp_id = checkpoint_id or self.current_checkpoint
        if not cp_id:
            return False
        
        cp_path = os.path.join(self.checkpoint_dir, cp_id)
        
        if not os.path.exists(cp_path):
            return False
        
        try:
            # Restore each directory
            for item in os.listdir(cp_path):
                if item == "metadata.json":
                    continue
                
                src = os.path.join(cp_path, item)
                dst = os.path.join(".", item)
                
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            
            return True
        except Exception as e:
            print(f"Restore error: {e}")
            return False
    
    def list_checkpoints(self) -> List[Dict]:
        """List all available checkpoints"""
        checkpoints = []
        
        if not os.path.exists(self.checkpoint_dir):
            return checkpoints
        
        for cp_name in os.listdir(self.checkpoint_dir):
            cp_path = os.path.join(self.checkpoint_dir, cp_name)
            meta_path = os.path.join(cp_path, "metadata.json")
            
            if os.path.isdir(cp_path) and os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    meta = json.load(f)
                    checkpoints.append(meta)
        
        return sorted(checkpoints, key=lambda x: x["created"], reverse=True)
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint"""
        cp_path = os.path.join(self.checkpoint_dir, checkpoint_id)
        
        if os.path.exists(cp_path):
            shutil.rmtree(cp_path)
            return True
        return False
    
    def auto_checkpoint(self, task_name: str) -> str:
        """Create checkpoint before risky operation"""
        return self.create_checkpoint(f"auto_{task_name}")
    
    def rollback_on_failure(self, checkpoint_id: str = None) -> bool:
        """Rollback if operation failed (can be called in except block)"""
        return self.restore_checkpoint(checkpoint_id)


class EvolutionLoop:
    """
    Safe Evolution Loop:
    1. Identify: Detect missing tool/error via Self-Reflection
    2. Code: Programming Agent writes fix to tools.py
    3. Test: Run unit tests in sandboxed environment
    4. Commit: Use CheckpointManager for auto-rollback
    """
    
    def __init__(self):
        self.checkpoints = CheckpointManager()
        self.history = []
    
    def run(
        self,
        identify_fn,
        code_fn,
        test_fn,
        max_retries: int = 3
    ) -> Dict:
        """
        Run the evolution loop.
        
        Args:
            identify_fn: Function to identify capability gap
            code_fn: Function to generate code
            test_fn: Function to test the code
            max_retries: Maximum retry attempts
            
        Returns:
            Result dict with success status and details
        """
        result = {
            "success": False,
            "iterations": 0,
            "error": None,
            "solution": None
        }
        
        for iteration in range(max_retries):
            result["iterations"] = iteration + 1
            
            # 1. Identify the issue
            issue = identify_fn()
            if not issue:
                result["success"] = True
                break
            
            # Create checkpoint before changes
            cp_id = self.checkpoints.auto_checkpoint(f"iteration_{iteration}")
            
            # 2. Generate code
            code = code_fn(issue)
            
            # 3. Test the code
            test_result = test_fn(code)
            
            if test_result.get("success"):
                result["success"] = True
                result["solution"] = code
                break
            else:
                # 4. Rollback on failure
                self.checkpoints.rollback_on_failure(cp_id)
                result["error"] = test_result.get("error", "Test failed")
        
        self.history.append(result)
        return result
    
    def get_history(self) -> List[Dict]:
        return self.history