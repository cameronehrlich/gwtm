#!/usr/bin/env python3

import argparse
import configparser
import os
import subprocess
import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    from .ide import IDEHandler
except ImportError:
    # When running directly from main.py
    try:
        from ide import IDEHandler
    except ImportError:
        # When installed via pip as gwtm package
        from gwtm.ide import IDEHandler


class GitWorktreeManager:
    def __init__(self, config_path: Optional[str] = None, debug: bool = False):
        self.config = self._load_config(config_path)
        
        # Setup logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
        self.logger = logging.getLogger('gwtm')
        
        # Initialize IDE handler
        ide_paths = dict(self.config["paths"])
        self.ide_handler = IDEHandler(ide_paths)
    
    def _load_config(self, config_path: Optional[str] = None) -> configparser.ConfigParser:
        """Load configuration from .gwtmrc file"""
        config = configparser.ConfigParser()
        
        # Default configuration
        config["defaults"] = {
            "ide": "xcode",
            "worktree_location": ".gwtm/worktrees"  # Default to .gwtm/worktrees in repo root
        }
        config["paths"] = {
            "xcode": "/Applications/Xcode.app",
            "androidstudio": "/Applications/Android Studio.app"
        }
        
        # Look for config file in these locations (in order of precedence)
        locations = [
            config_path,
            os.path.join(os.getcwd(), ".gwtmrc"),
            os.path.expanduser("~/.gwtmrc")
        ]
        
        for location in locations:
            if location and os.path.exists(location):
                config.read(location)
                break
                
        return config
    
    def _run_git(self, args: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a git command"""
        cmd = ["git"] + args
        return subprocess.run(cmd, capture_output=capture_output, text=True)
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        result = self._run_git(["rev-parse", "--is-inside-work-tree"])
        return result.returncode == 0
        
    def _get_repo_root(self) -> Optional[str]:
        """Get the root directory of the git repository"""
        if not self._is_git_repo():
            return None
        
        result = self._run_git(["rev-parse", "--show-toplevel"])
        if result.returncode == 0:
            return result.stdout.strip()
        return None
        
    def _ensure_worktree_location(self) -> str:
        """Ensure the default worktree location exists and is git-ignored"""
        # Get the repository root
        repo_root = self._get_repo_root()
        if not repo_root:
            print("Error: Not in a git repository")
            sys.exit(1)
            
        # Get the default worktree location from config
        location = self.config.get("defaults", "worktree_location", fallback=".gwtm/worktrees")
        
        # Make it absolute based on repo root
        if not os.path.isabs(location):
            location = os.path.join(repo_root, location)
            
        # Create the directory if it doesn't exist
        os.makedirs(location, exist_ok=True)
        
        # Add to .gitignore if not already there
        gitignore_path = os.path.join(repo_root, ".gitignore")
        relative_location = os.path.relpath(location, repo_root)
        
        # Add entry to .gitignore if it doesn't already contain it
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
                
            # Check if the location is already ignored
            if relative_location not in gitignore_content.split('\n'):
                with open(gitignore_path, 'a') as f:
                    f.write(f"\n# GWTM worktrees\n{relative_location}\n")
                    self.logger.debug(f"Added {relative_location} to .gitignore")
        else:
            # Create .gitignore if it doesn't exist
            with open(gitignore_path, 'w') as f:
                f.write(f"# GWTM worktrees\n{relative_location}\n")
                self.logger.debug(f"Created .gitignore with {relative_location}")
                
        return location
    
    def add_worktree(self, path: Optional[str] = None, branch: Optional[str] = None, new_branch: bool = False) -> None:
        """Add a new worktree"""
        if not self._is_git_repo():
            print("Error: Not in a git repository")
            sys.exit(1)
            
        # If no path provided, use the branch name in the default location
        if not path:
            if not branch:
                print("Error: Either path or branch must be specified")
                sys.exit(1)
                
            # Get the default worktree location
            base_location = self._ensure_worktree_location()
            path = os.path.join(base_location, branch)
            print(f"Using default path: {path}")
        elif not os.path.isabs(path):
            # If a relative path is provided, make it relative to the default location
            base_location = self._ensure_worktree_location()
            path = os.path.join(base_location, path)
            print(f"Using path within default worktree location: {path}")
            
        args = ["worktree", "add"]
        
        # Create the parent directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        
        # Check if we need to create a new branch
        if new_branch and branch:
            args.extend(["-b", branch, path])
            self.logger.debug(f"Creating new branch: {branch}")
        # Use existing branch if provided
        elif branch:
            args.extend([path, branch])
            self.logger.debug(f"Using existing branch: {branch}")
        # Just add worktree for current branch
        else:
            args.append(path)
            self.logger.debug("No branch specified, using current HEAD")
        
        self.logger.debug(f"Running git command: git {' '.join(args)}")
        result = self._run_git(args, capture_output=False)
        
        if result.returncode == 0:
            print(f"Worktree created at {path}")
        else:
            print("Failed to create worktree")
            sys.exit(1)
        
    def list_worktrees(self) -> None:
        """List all worktrees"""
        if not self._is_git_repo():
            print("Error: Not in a git repository")
            sys.exit(1)
            
        result = self._run_git(["worktree", "list"])
        if result.returncode == 0:
            # Format and print the output
            worktrees = result.stdout.strip().split('\n')
            print("\nGit Worktrees:")
            print("=" * 60)
            for i, wt in enumerate(worktrees):
                parts = wt.split()
                if len(parts) >= 2:
                    path = parts[0]
                    branch = parts[1].strip('[]')
                    print(f"{i+1}. {path} - {branch}")
            print("=" * 60)
        else:
            print("Error listing worktrees")
            print(result.stderr)
    
    def remove_worktree(self, path: str, prune: bool = True) -> None:
        """Remove a worktree"""
        if not self._is_git_repo():
            print("Error: Not in a git repository")
            sys.exit(1)
            
        result = self._run_git(["worktree", "remove", path])
        if result.returncode == 0:
            print(f"Worktree at {path} removed")
            
            if prune:
                prune_result = self._run_git(["worktree", "prune"])
                if prune_result.returncode == 0:
                    print("Pruned stale worktree data")
        else:
            print(f"Error removing worktree: {result.stderr}")
    
    def merge_from_worktree(self, path: str, target_branch: Optional[str] = None) -> None:
        """Merge changes from a worktree branch into the target branch (default: current branch)"""
        if not self._is_git_repo():
            print("Error: Not in a git repository")
            sys.exit(1)
            
        # Get absolute path
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            print(f"Error: Worktree path {abs_path} does not exist")
            sys.exit(1)
            
        # Get the branch of the worktree
        self.logger.debug(f"Getting branch for worktree at {abs_path}")
        worktree_list = self._run_git(["worktree", "list", "--porcelain"])
        
        worktree_branch = None
        current_worktree = None
        for line in worktree_list.stdout.split('\n'):
            if line.startswith('worktree '):
                current_worktree = line.replace('worktree ', '').strip()
            elif line.startswith('branch ') and current_worktree == abs_path:
                worktree_branch = line.replace('branch ', '').strip()
                # Convert from refs/heads/branch-name to just branch-name
                if worktree_branch.startswith('refs/heads/'):
                    worktree_branch = worktree_branch[len('refs/heads/'):]
                break
        
        if not worktree_branch:
            print(f"Error: Could not determine branch for worktree at {abs_path}")
            sys.exit(1)
            
        self.logger.debug(f"Worktree branch: {worktree_branch}")
        
        # Check for uncommitted changes in the worktree
        status_result = self._run_git(["--git-dir", os.path.join(abs_path, ".git"), 
                                       "--work-tree", abs_path, "status", "--porcelain"])
        
        if status_result.stdout.strip():
            print(f"Error: Worktree branch '{worktree_branch}' has uncommitted changes:")
            print(status_result.stdout)
            print("Please commit or stash your changes in the worktree first.")
            sys.exit(1)
            
        # Check if the branch has any commits
        branch_check = self._run_git(["branch", "-a"])
        if worktree_branch not in branch_check.stdout:
            print(f"Error: Branch '{worktree_branch}' not found. Have you made any commits in the worktree?")
            sys.exit(1)
            
        # Determine target branch (use current branch if not specified)
        if not target_branch:
            target_branch_result = self._run_git(["branch", "--show-current"])
            target_branch = target_branch_result.stdout.strip()
            if not target_branch:
                print("Error: Could not determine current branch and no target branch specified")
                sys.exit(1)
        
        self.logger.debug(f"Target branch: {target_branch}")
        
        # Check if branches are different
        if worktree_branch == target_branch:
            print(f"Error: Worktree branch '{worktree_branch}' is the same as target branch '{target_branch}'")
            sys.exit(1)
            
        # Perform the merge
        print(f"Merging changes from '{worktree_branch}' into '{target_branch}'...")
        
        # Make sure we have the latest changes from remote if available
        try:
            self._run_git(["fetch", "origin", target_branch])
            print(f"Fetched latest changes for target branch '{target_branch}' from remote")
        except:
            print(f"Note: Could not fetch from remote for branch '{target_branch}' - continuing with local merge")
            
        # Checkout the target branch
        checkout_result = self._run_git(["checkout", target_branch], capture_output=False)
        if checkout_result.returncode != 0:
            print(f"Error: Failed to checkout target branch '{target_branch}'")
            sys.exit(1)
            
        # Merge the local worktree branch (not from remote)
        print(f"Merging local branch '{worktree_branch}'...")
        merge_result = self._run_git(["merge", worktree_branch], capture_output=True)
        
        if merge_result.returncode != 0:
            print(f"Merge conflicts detected. Please resolve conflicts and complete the merge manually.")
            print(f"You can run: git status")
            print(f"Once conflicts are resolved: git add <resolved-files> && git merge --continue")
            sys.exit(1)
        else:
            if "Already up to date" in merge_result.stdout:
                print(f"No changes to merge. Branch '{target_branch}' already contains all commits from '{worktree_branch}'")
            else:
                print(f"Successfully merged '{worktree_branch}' into '{target_branch}'")
                print(f"Merge summary:")
                summary = self._run_git(["log", "-1", "--stat"])
                print(summary.stdout)
    
    def switch_worktree(self, path: str) -> None:
        """Switch to a different worktree"""
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            print(f"Error: Worktree path {abs_path} does not exist")
            sys.exit(1)
            
        # Print instructions for switching
        print(f"To switch to the worktree at {abs_path}, run:")
        print(f"cd {abs_path}")
    
    def open_ide(self, path: str, ide: Optional[str] = None) -> None:
        """Open a worktree in an IDE"""
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            print(f"Error: Worktree path {abs_path} does not exist")
            sys.exit(1)
            
        # Use specified IDE or default from config
        if not ide:
            ide = self.config.get("defaults", "ide", fallback="xcode")
            
        ide = ide.lower()
        supported_ides = IDEHandler.get_supported_ides()
        if ide not in supported_ides:
            print(f"Error: Unsupported IDE '{ide}'. Supported: {', '.join(supported_ides)}")
            sys.exit(1)
            
        self.logger.debug(f"Opening {abs_path} in {ide}")
        
        # Use the IDE handler to open the IDE
        success = self.ide_handler.open_in_ide(abs_path, ide)
        
        if success:
            # The IDE handler already prints a more specific message
            pass
        else:
            print(f"Failed to open {abs_path} in {ide}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Git WorkTree Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Add worktree command
    add_parser = subparsers.add_parser("add", help="Add a new worktree")
    add_parser.add_argument("path", nargs="?", help="Path for the new worktree (optional, defaults to .gwtm/worktrees/<branch>)")
    add_parser.add_argument("branch", nargs="?", help="Branch to checkout (required if no path is provided)")
    add_parser.add_argument("-b", "--new-branch", action="store_true", 
                           help="Create a new branch based on current HEAD")
    
    # List worktrees command
    subparsers.add_parser("list", help="List all worktrees")
    
    # Remove worktree command
    remove_parser = subparsers.add_parser("remove", help="Remove a worktree")
    remove_parser.add_argument("path", help="Path of the worktree to remove")
    remove_parser.add_argument("--no-prune", action="store_true", help="Don't prune stale worktree data")
    
    # Switch worktree command
    switch_parser = subparsers.add_parser("switch", help="Switch to a different worktree")
    switch_parser.add_argument("path", help="Path of the worktree to switch to")
    
    # Open IDE command
    open_parser = subparsers.add_parser("open", help="Open a worktree in an IDE")
    open_parser.add_argument("path", help="Path of the worktree to open")
    open_parser.add_argument("ide", nargs="?", choices=["xcode", "androidstudio"], 
                            help="IDE to use (default from config if not specified)")
    
    # Merge command
    merge_parser = subparsers.add_parser("merge", help="Merge changes from a worktree branch")
    merge_parser.add_argument("path", help="Path of the worktree to merge from")
    merge_parser.add_argument("--into", dest="target_branch", 
                             help="Target branch to merge into (default: current branch)")
    
    # Global options for all commands
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Initialize the manager
    manager = GitWorktreeManager(args.config, args.debug)
    
    # Execute the appropriate command
    if args.command == "add":
        manager.add_worktree(args.path, args.branch, args.new_branch)
    elif args.command == "list":
        manager.list_worktrees()
    elif args.command == "remove":
        manager.remove_worktree(args.path, not args.no_prune)
    elif args.command == "switch":
        manager.switch_worktree(args.path)
    elif args.command == "open":
        manager.open_ide(args.path, args.ide)
    elif args.command == "merge":
        manager.merge_from_worktree(args.path, args.target_branch)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()