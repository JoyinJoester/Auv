#!/bin/bash

# AUV File Organizer - Quick Setup Script
# Support for macOS and Linux

set -e  # Exit on error

echo "=========================================="
echo "         AUV File Organizer"
echo "         Quick Setup Script"
echo "=========================================="
echo

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    USER_BIN_PATH="$HOME/Library/Python"
    SHELL_RC="$HOME/.zshrc"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    USER_BIN_PATH="$HOME/.local/bin"
    SHELL_RC="$HOME/.bashrc"
else
    echo "[ERROR] Unsupported operating system: $OSTYPE"
    exit 1
fi

echo "[OK] Detected operating system: $OS"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found. Please install Python 3.7+"
    if [[ "$OS" == "macOS" ]]; then
        echo "Install command: brew install python3"
        echo "Or visit: https://www.python.org/downloads/"
    else
        echo "Install command: sudo apt update && sudo apt install python3 python3-pip"
    fi
    exit 1
fi

echo "[OK] Python3 is installed"
python3 --version

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "[ERROR] pip3 not found"
    if [[ "$OS" == "Linux" ]]; then
        echo "Install command: sudo apt install python3-pip"
    else
        echo "Please install pip3"
    fi
    exit 1
fi

echo "[OK] pip3 is installed"

echo
echo "[INFO] Installing dependencies..."
pip3 install --user watchdog>=2.1.0 psutil>=5.8.0 click>=8.0.0

echo
echo "[INFO] Installing AUV..."
pip3 install --user -e .

echo
echo "[INFO] Configuring environment variables..."

# Determine correct PATH
if [[ "$OS" == "macOS" ]]; then
    # macOS: Find Python version and build path
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    BIN_PATH="$HOME/Library/Python/$PYTHON_VERSION/bin"
else
    # Linux
    BIN_PATH="$HOME/.local/bin"
fi

# Check if path exists
if [[ ! -d "$BIN_PATH" ]]; then
    echo "[WARN] Expected bin directory not found: $BIN_PATH"
    echo "[INFO] Searching for actual installation path..."
    
    # Search for possible paths
    POSSIBLE_PATHS=(
        "$HOME/.local/bin"
        "$HOME/Library/Python/3.*/bin"
        "$HOME/.python/bin"
    )
    
    for path in "${POSSIBLE_PATHS[@]}"; do
        # Support wildcard expansion
        for expanded_path in $path; do
            if [[ -d "$expanded_path" ]] && [[ -f "$expanded_path/auv" ]]; then
                BIN_PATH="$expanded_path"
                echo "[OK] Found AUV installation path: $BIN_PATH"
                break 2
            fi
        done
    done
    
    if [[ ! -d "$BIN_PATH" ]]; then
        echo "[ERROR] Cannot find AUV installation path"
        echo "[INFO] Please manually add the directory containing auv command to PATH"
        exit 1
    fi
fi

# Check if already in PATH
if echo "$PATH" | grep -q "$BIN_PATH"; then
    echo "[OK] Environment variable already configured"
else
    echo "[INFO] Adding to PATH: $BIN_PATH"
    
    # Add to shell configuration file
    if [[ "$OS" == "macOS" ]]; then
        echo "export PATH=\"$BIN_PATH:\$PATH\"" >> "$SHELL_RC"
        echo "[OK] Added to $SHELL_RC"
    else
        echo "export PATH=\"$BIN_PATH:\$PATH\"" >> "$SHELL_RC"
        echo "[OK] Added to $SHELL_RC"
    fi
    
    # Apply to current session
    export PATH="$BIN_PATH:$PATH"
fi

echo
echo "[INFO] Testing installation..."

# Test auv command
if command -v auv &> /dev/null; then
    echo "[OK] AUV installed successfully!"
    echo
    auv --version
else
    echo "[WARN] Command test failed, may need to reload shell configuration"
    echo "[INFO] Please run: source $SHELL_RC"
    echo "Or restart your terminal window"
fi

echo
echo "=========================================="
echo "          Setup Complete!"
echo "=========================================="
echo
echo "Usage Examples:"
echo "  auv --help               # Show help"
echo "  auv status               # Show current status"
echo "  auv -pdf                 # Organize PDFs in current folder"
echo "  auv -d -pdf              # Organize PDFs in downloads folder"
echo "  auv here -pdf            # Create PDF folder in current directory"
echo "  auv set downloads ~/Downloads  # Set downloads folder path"
echo
echo "[TIP] If commands don't work, run: source $SHELL_RC"
echo