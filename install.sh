#!/bin/bash

echo "Installing Git WorkTree Manager (gwtm)..."

# Make script executable
SCRIPT_PATH="$(pwd)/src/main.py"
chmod +x "$SCRIPT_PATH"

# Create symlink in user's bin directory
SYMLINK_PATH="$HOME/bin/gwtm"
mkdir -p "$HOME/bin"

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
echo "Make sure $HOME/bin is in your PATH."
echo "To use gwtm, run: gwtm --help"