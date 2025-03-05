# GWTM - Git WorkTree Manager

A command-line tool for managing Git worktrees with IDE integration, optimized for multi-agent workflows in a "agent world" where different tools or environments need to work with different branches simultaneously.

## Overview

GWTM (Git WorkTree Manager) streamlines creating, switching, and managing Git worktrees while providing seamless integration with IDEs like Xcode and Android Studio. It wraps Git's built-in worktree functionality with a more intuitive interface and adds agent-oriented features.

## Features

- **Worktree Management**: Create, list, and remove Git worktrees with simple commands
- **Context Switching**: Easily switch between different worktrees
- **IDE Integration**: Open worktrees directly in Xcode, Android Studio, or other IDEs
- **Configuration**: Customize settings via a config file
- **Multi-Agent Support**: Enable multiple "agents" (terminal windows, IDE sessions) to work simultaneously on different branches

## Installation

From PyPI (recommended):
```bash
pip install gwtm
```

From source:
```bash
git clone https://github.com/your-username/gwtm.git
cd gwtm
pip install -e .
```

## Requirements

- Python 3.7+
- Git 2.5+

## Usage

### Creating a worktree

```bash
# Create a worktree for an existing branch with a specific path
gwtm add path/to/worktree existing-branch

# Create a worktree for a new branch based on current HEAD
gwtm add path/to/worktree -b new-branch

# Use the default location (.gwtm/worktrees/<branch-name>)
gwtm add existing-branch

# Create a new branch in the default location
gwtm add -b new-branch new-branch
```

The default worktree location is `.gwtm/worktrees/` in your repository root. This directory is automatically added to `.gitignore` to prevent accidentally committing worktree files.

### Listing worktrees

```bash
gwtm list
```

### Removing a worktree

```bash
gwtm remove path/to/worktree
```

### Switching to a worktree

```bash
gwtm switch path/to/worktree
```

### Opening in an IDE

```bash
# Open in the default IDE (from config)
gwtm open path/to/worktree

# Open in a specific IDE
gwtm open path/to/worktree xcode
gwtm open path/to/worktree androidstudio
```

For React Native or other multi-platform projects:
- When opening with `xcode`, GWTM will look for an `ios` directory first
- When opening with `androidstudio`, GWTM will look for an `android` directory first
- This allows you to open just the platform-specific parts of a larger project

### Merging changes from a worktree

```bash
# Merge changes from a worktree branch into the current branch
gwtm merge path/to/worktree

# Merge changes into a specific target branch
gwtm merge path/to/worktree --into main
```

**Important:** You must commit your changes in the worktree branch before merging. The merge command:
1. Checks for uncommitted changes in the worktree
2. Ensures the branch exists and has commits
3. Merges the local worktree branch into the target branch
4. Shows a summary of the changes that were merged

## Configuration

Create a `.gwtmrc` file in your home directory (`~/.gwtmrc`) or in the repository root to configure default settings:

```ini
[defaults]
# Default IDE to use when opening a worktree without specifying an IDE
ide = xcode

# Default location for worktrees (relative to repository root)
worktree_location = .gwtm/worktrees

[paths]
# Paths to IDE applications
xcode = /Applications/Xcode.app
androidstudio = /Applications/Android Studio.app
```

A sample configuration file is provided at `sample.gwtmrc`.

## Multi-Agent Workflow Example

1. Set up worktrees for different features (using the default location):
   ```bash
   # Create worktrees for existing branches
   gwtm add feature-a
   gwtm add feature-b
   
   # Or create new branches
   gwtm add -b new-ios-feature new-ios-feature
   gwtm add -b new-android-feature new-android-feature
   ```

2. Open them in different IDEs:
   ```bash
   # For multi-platform projects, these will automatically find ios/android subdirectories
   gwtm open .gwtm/worktrees/new-ios-feature xcode
   gwtm open .gwtm/worktrees/new-android-feature androidstudio
   ```

3. Now you can work on iOS features in Xcode and Android features in Android Studio simultaneously.

4. Make and commit your changes in each worktree:
   ```bash
   # In the iOS worktree
   cd .gwtm/worktrees/new-ios-feature
   git add .
   git commit -m "Add new iOS feature"
   
   # In the Android worktree
   cd .gwtm/worktrees/new-android-feature
   git add .
   git commit -m "Add new Android feature"
   ```

5. When you're ready to integrate the changes:
   ```bash
   # Go back to the main repository
   cd /path/to/main/repo
   
   # First, merge iOS feature changes into development branch
   gwtm merge .gwtm/worktrees/new-ios-feature --into dev
   
   # Then, merge Android feature changes
   gwtm merge .gwtm/worktrees/new-android-feature --into dev
   ```

## Troubleshooting

- Run with `--debug` flag for detailed logging:
  ```bash
  gwtm --debug list
  ```

- Ensure your `.gwtmrc` file has correct paths to your IDEs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License