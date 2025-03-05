#!/usr/bin/env python3

"""
Comprehensive test script for GWTM.
This will test the core functionality and clean up any test repositories created.

Usage:
  python tests.py           # Run all tests
  python tests.py basic     # Run only basic tests
  python tests.py full      # Run comprehensive tests
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

# Import the GWTM classes for direct testing
try:
    from main import GitWorktreeManager
    from ide import IDEHandler
except ImportError:
    print("Error: Could not import GWTM modules. Make sure you're running this from the project root.")
    sys.exit(1)

def run_command(cmd, cwd=None):
    """Run a command and print its output."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    print(f"Exit code: {result.returncode}")
    if result.stdout:
        print("Output:")
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print("Error:")
        print(result.stderr)
    print("-" * 50)
    return result

def create_test_repo():
    """Create a test Git repository."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="gwtm_test_")
    print(f"Created test directory: {temp_dir}")
    
    # Initialize a Git repository
    run_command("git init", cwd=temp_dir)
    
    # Create a test file
    test_file = os.path.join(temp_dir, "test-file.txt")
    with open(test_file, "w") as f:
        f.write("This is a test file for GWTM.")
    
    # Make an initial commit
    run_command("git add test-file.txt", cwd=temp_dir)
    run_command("git config user.name 'GWTM Tester'", cwd=temp_dir)
    run_command("git config user.email 'test@example.com'", cwd=temp_dir)
    run_command("git commit -m 'Initial commit'", cwd=temp_dir)
    
    # Create a test branch
    run_command("git checkout -b test-branch", cwd=temp_dir)
    
    # Go back to main branch
    run_command("git checkout master || git checkout main", cwd=temp_dir)
    
    return temp_dir

def cleanup_test_repo(repo_dir):
    """Clean up the test repository."""
    print(f"Cleaning up test repository: {repo_dir}")
    try:
        shutil.rmtree(repo_dir)
        print(f"Removed test directory: {repo_dir}")
    except Exception as e:
        print(f"Error removing test directory: {e}")

def run_gwtm_command(cmd, repo_dir):
    """Run a GWTM command."""
    gwtm_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "main.py"))
    full_cmd = f"python {gwtm_path} {cmd}"
    return run_command(full_cmd, cwd=repo_dir)

def test_direct_import():
    """Test direct import of GWTM classes."""
    print("Testing direct import of GWTM classes...")
    
    # Test GitWorktreeManager
    manager = GitWorktreeManager()
    assert isinstance(manager, GitWorktreeManager), "Failed to create GitWorktreeManager instance"
    
    # Test IDEHandler
    ide_paths = {"xcode": "/Applications/Xcode.app", "androidstudio": "/Applications/Android Studio.app"}
    ide_handler = IDEHandler(ide_paths)
    assert isinstance(ide_handler, IDEHandler), "Failed to create IDEHandler instance"
    
    supported_ides = IDEHandler.get_supported_ides()
    assert "xcode" in supported_ides, "Xcode not in supported IDEs"
    assert "androidstudio" in supported_ides, "Android Studio not in supported IDEs"
    
    print("Direct import tests passed.")
    print("-" * 50)

def test_cli_interface(repo_dir):
    """Test the CLI interface."""
    print("Testing CLI interface...")
    
    # Test help command
    result = run_gwtm_command("--help", repo_dir)
    assert result.returncode == 0, "Help command failed"
    
    # Test list command
    result = run_gwtm_command("list", repo_dir)
    assert result.returncode == 0, "List command failed"
    
    # Create a worktree directory
    worktree_path = os.path.join(repo_dir, "worktrees", "test-worktree")
    
    # Test add command
    result = run_gwtm_command(f"add {worktree_path} test-branch", repo_dir)
    assert result.returncode == 0, "Add command failed"
    assert os.path.exists(worktree_path), f"Worktree directory not created at {worktree_path}"
    
    # Test list command again
    result = run_gwtm_command("list", repo_dir)
    assert result.returncode == 0, "List command failed after adding worktree"
    
    # Test switch command
    result = run_gwtm_command(f"switch {worktree_path}", repo_dir)
    assert result.returncode == 0, "Switch command failed"
    
    # Test remove command
    result = run_gwtm_command(f"remove {worktree_path}", repo_dir)
    assert result.returncode == 0, "Remove command failed"
    
    # Check if worktree was removed
    assert not os.path.exists(worktree_path), f"Worktree directory not removed at {worktree_path}"
    
    print("CLI interface tests passed.")
    print("-" * 50)

def test_new_branch_creation(repo_dir):
    """Test creating a new branch with a worktree."""
    print("Testing new branch creation...")
    
    # Create a worktree with a new branch
    worktree_path = os.path.join(repo_dir, "worktrees", "new-branch-test")
    result = run_gwtm_command(f"add {worktree_path} new-feature-branch -b", repo_dir)
    assert result.returncode == 0, "Creating worktree with new branch failed"
    
    # Verify the branch exists
    branch_check = run_command("git branch", cwd=repo_dir)
    assert "new-feature-branch" in branch_check.stdout, "New branch not created"
    
    # Clean up the worktree
    run_gwtm_command(f"remove {worktree_path}", repo_dir)
    
    print("New branch creation tests passed.")
    print("-" * 50)

def test_config_handling():
    """Test config file handling."""
    print("Testing configuration handling...")
    
    # Create a test config file
    config_path = os.path.join(tempfile.gettempdir(), "test_gwtmrc")
    with open(config_path, "w") as f:
        f.write("""
[defaults]
ide = vscode

[paths]
xcode = /Applications/Xcode-test.app
androidstudio = /Applications/Android Studio-test.app
vscode = /Applications/VSCode-test.app
""")
    
    # Create manager with the test config
    manager = GitWorktreeManager(config_path)
    
    # Check if config was loaded
    assert manager.config.get("defaults", "ide") == "vscode", "Config not loaded correctly"
    assert manager.config.get("paths", "xcode") == "/Applications/Xcode-test.app", "IDE path not loaded correctly"
    
    # Clean up
    os.remove(config_path)
    
    print("Configuration handling tests passed.")
    print("-" * 50)

def run_basic_tests():
    """Run basic command-line tests."""
    print("Running basic tests for GWTM - Git WorkTree Manager")
    print("=" * 70)
    
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
    
    print("Basic tests completed.")
    return 0

def run_comprehensive_tests():
    """Run all tests including unit tests."""
    print("Running comprehensive tests for GWTM - Git WorkTree Manager")
    print("=" * 70)
    
    test_repo_dir = None
    
    try:
        # Test direct imports
        test_direct_import()
        
        # Test config handling
        test_config_handling()
        
        # Create a test repository
        test_repo_dir = create_test_repo()
        
        # Test CLI interface
        test_cli_interface(test_repo_dir)
        
        # Test new branch creation
        test_new_branch_creation(test_repo_dir)
        
        print("=" * 70)
        print("All comprehensive tests passed successfully!")
        
    except AssertionError as e:
        print(f"Test failed: {e}")
        return 1
    except Exception as e:
        print(f"Error during tests: {e}")
        return 1
    finally:
        # Clean up
        if test_repo_dir and os.path.exists(test_repo_dir):
            cleanup_test_repo(test_repo_dir)
    
    return 0

def main():
    """Determine which tests to run based on arguments."""
    if len(sys.argv) > 1:
        # Get the test type from command line arguments
        test_type = sys.argv[1].lower()
        
        if test_type == "basic":
            return run_basic_tests()
        elif test_type == "full" or test_type == "comprehensive":
            return run_comprehensive_tests()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available options: basic, full")
            return 1
    else:
        # Default to comprehensive tests
        return run_comprehensive_tests()

if __name__ == "__main__":
    sys.exit(main())