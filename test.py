#!/usr/bin/env python3

"""
Test script for GWTM.
This will run some basic commands to test the functionality.
"""

import os
import subprocess

def run_command(cmd):
    """Run a command and print its output."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Exit code: {result.returncode}")
    if result.stdout:
        print("Output:")
        print(result.stdout)
    if result.stderr:
        print("Error:")
        print(result.stderr)
    print("-" * 50)
    return result.returncode

def main():
    """Run test commands."""
    print("Testing GWTM - Git WorkTree Manager")
    print("=" * 50)
    
    # Test help command
    run_command("python src/main.py --help")
    
    # Test list command (should fail if not in a git repo)
    run_command("python src/main.py list")
    
    # Create a test git repo if we're not in one
    if not os.path.exists(".git"):
        print("Creating a test git repository...")
        run_command("git init")
        run_command("touch test-file.txt")
        run_command("git add test-file.txt")
        run_command("git commit -m 'Initial commit'")
    
    # Now test list command again
    run_command("python src/main.py list")
    
    print("Tests completed.")

if __name__ == "__main__":
    main()