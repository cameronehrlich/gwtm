#!/bin/bash

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help              Show this help message"
    echo "  --local             Install locally with a symlink only (default)"
    echo "  --dev               Install in development mode with pip"
    echo "  --global            Install globally with pip"
    echo ""
    echo "Installation types:"
    echo "  --local  : Creates a symlink in ~/bin or ~/.local/bin"
    echo "  --dev    : Installs package with 'pip install -e .'"
    echo "  --global : Installs package with 'pip install .'"
}

install_local() {
    echo "Installing GWTM locally with symlink..."
    
    # Make script executable
    SCRIPT_PATH="$(pwd)/src/main.py"
    chmod +x "$SCRIPT_PATH"

    # Determine the appropriate bin directory
    if [ -d "$HOME/bin" ] || [ "$FORCE_HOME_BIN" = "true" ]; then
        BIN_DIR="$HOME/bin"
    else
        BIN_DIR="$HOME/.local/bin"
    fi
    
    # Create bin directory if it doesn't exist
    mkdir -p "$BIN_DIR"
    
    # Create symlink
    SYMLINK_PATH="$BIN_DIR/gwtm"
    if [ -L "$SYMLINK_PATH" ]; then
        rm "$SYMLINK_PATH"
    fi

    ln -s "$SCRIPT_PATH" "$SYMLINK_PATH"
    echo "Created symlink at $SYMLINK_PATH"
    echo "Make sure $BIN_DIR is in your PATH."
}

install_dev() {
    echo "Installing GWTM in development mode..."
    
    # Check if pip is installed
    if ! command -v pip &> /dev/null; then
        echo "Error: pip is not installed. Please install Python and pip first."
        exit 1
    fi
    
    # Install in development mode
    pip install -e .
    echo "Installed development version with pip"
}

install_global() {
    echo "Installing GWTM globally..."
    
    # Check if pip is installed
    if ! command -v pip &> /dev/null; then
        echo "Error: pip is not installed. Please install Python and pip first."
        exit 1
    fi
    
    # Install globally
    pip install .
    echo "Installed global version with pip"
}

install_config() {
    # Copy sample config to user's home directory if not exists
    if [ ! -f ~/.gwtmrc ]; then
        echo "Creating default configuration file at ~/.gwtmrc"
        cp sample.gwtmrc ~/.gwtmrc
    else
        echo "Config file already exists at ~/.gwtmrc"
    fi
}

# Default installation type
INSTALL_TYPE="local"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            print_usage
            exit 0
            ;;
        --local)
            INSTALL_TYPE="local"
            shift
            ;;
        --dev)
            INSTALL_TYPE="dev"
            shift
            ;;
        --global)
            INSTALL_TYPE="global"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

echo "Installing Git WorkTree Manager (gwtm)..."

# Perform the chosen installation
case $INSTALL_TYPE in
    local)
        install_local
        ;;
    dev)
        install_dev
        install_local
        ;;
    global)
        install_global
        ;;
esac

# Install config file
install_config

echo "Installation complete!"
echo "To use gwtm, run: gwtm --help"