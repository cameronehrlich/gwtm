#!/bin/bash

echo "Installing Git WorkTree Manager (gwtm) in development mode..."

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed. Please install Python and pip first."
    exit 1
fi

# Install the package in development mode
pip install -e .

# Create symlink to run the script directly
SCRIPT_PATH="$(pwd)/src/main.py"
SYMLINK_PATH="$HOME/.local/bin/gwtm"

mkdir -p "$HOME/.local/bin"
chmod +x "$SCRIPT_PATH"

if [ -L "$SYMLINK_PATH" ]; then
    rm "$SYMLINK_PATH"
fi

ln -s "$SCRIPT_PATH" "$SYMLINK_PATH"
echo "Created symlink at $SYMLINK_PATH"

# Copy sample config to user's home directory if not exists
if [ ! -f ~/.gwtmrc ]; then
    echo "Creating default configuration file at ~/.gwtmrc"
    cp sample.gwtmrc ~/.gwtmrc
fi

echo "Installation complete!"
echo "Make sure $HOME/.local/bin is in your PATH."
echo "To use gwtm, run: gwtm --help"