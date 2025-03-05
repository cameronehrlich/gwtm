# GWTM - Git WorkTree Manager

## Project Summary

GWTM is a command-line tool built in Python that enhances Git's worktree functionality. It's designed for managing multiple branches in a mono-repo, particularly useful in a multi-agent environment where different IDEs (like Xcode and Android Studio) need to work on different branches simultaneously.

## Components

1. **Core Functionality**
   - GitWorktreeManager class: Wraps Git's worktree commands
   - IDEHandler class: Manages IDE-specific operations
   - CLI interface: Parses commands and arguments

2. **Commands**
   - `add`: Create new worktrees with optional branch creation
   - `list`: Display existing worktrees
   - `remove`: Remove worktrees and clean up
   - `switch`: Change to a different worktree 
   - `open`: Open a worktree in an IDE (Xcode, Android Studio)
   - `merge`: Merge changes from a worktree branch into another branch

3. **Configuration**
   - .gwtmrc file: Custom settings for IDE paths and defaults
   - Debug mode: Detailed logging

## Implementation Details

- **Language**: Python 3.7+
- **Dependencies**: Core Python libraries only (no external dependencies)
- **Platform Support**: Cross-platform with special handling for macOS IDEs
- **Error Handling**: Graceful error messages and proper exit codes
- **Testing**: Comprehensive test suite with test repository creation/cleanup

## Project Structure

```
gwtm/
├── CONTRIBUTING.md    # Guidelines for contributors
├── LICENSE           # MIT License
├── README.md         # Project documentation
├── install.sh        # Installation script
├── pyproject.toml    # Project metadata
├── sample.gwtmrc     # Example configuration file
├── setup.py          # Installation script for pip
├── src/
│   ├── __init__.py   # Package initialization
│   ├── ide.py        # IDE handling functionality
│   └── main.py       # Core functionality and CLI
└── tests.py          # Test suite
```

## Key Features

1. **Improved Workflow**: Simplifies working with multiple branches
2. **IDE Integration**: Directly open worktrees in the appropriate IDE
3. **Agent-Oriented**: Designed for environments with multiple "agents" working simultaneously
4. **Extensible**: Easily add support for new IDEs or additional functionality

## Next Steps

1. **Add More IDE Support**: VSCode, IntelliJ, etc.
2. **Enhance Configuration**: Add more customization options
3. **Add CI/CD Integration**: GitHub Actions for testing and releases
4. **Package Distribution**: Upload to PyPI for easy installation

## Installation

```bash
# Install from source
git clone https://github.com/your-username/gwtm.git
cd gwtm
./install.sh
```

After installation, you can use the tool with commands like:
```bash
gwtm add ~/worktrees/feature-a feature-a
gwtm list
gwtm open ~/worktrees/feature-a xcode
```