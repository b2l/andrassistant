#!/bin/bash
#
# Termux setup script for Android Voice Assistant
# Run this script inside Termux on your Android device
#
# Prerequisites:
#   - Install Termux from F-Droid (NOT Play Store)
#   - Install Termux:API from F-Droid
#   - Install Termux:Boot from F-Droid (optional, for auto-start)
#

set -e

echo "=== Termux Voice Assistant Setup ==="
echo ""

# Check if running in Termux
if [ -z "$TERMUX_VERSION" ]; then
    echo "Warning: This script is designed to run in Termux on Android."
    echo "Some commands may not work on regular Linux."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "[1/6] Updating packages..."
pkg update -y && pkg upgrade -y

echo "[2/6] Installing system dependencies..."
pkg install -y python git termux-api espeak

echo "[3/6] Setting up storage access..."
termux-setup-storage || echo "Storage setup skipped (may already be configured)"

echo "[4/6] Creating directories..."
mkdir -p ~/notes
mkdir -p ~/.termux

echo "[5/6] Installing Python packages..."
pip install --upgrade pip
pip install anthropic

echo "[6/6] Setting up assistant..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
chmod +x "$SCRIPT_DIR/assistant.py"

# Create a convenience alias
echo "" >> ~/.bashrc
echo "# Termux Voice Assistant" >> ~/.bashrc
echo "alias assistant='python $SCRIPT_DIR/assistant.py'" >> ~/.bashrc
echo "alias assistant-voice='python $SCRIPT_DIR/assistant.py --voice'" >> ~/.bashrc

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo ""
echo "1. Set your Anthropic API key:"
echo "   export ANTHROPIC_API_KEY='sk-ant-your-key-here'"
echo "   echo 'export ANTHROPIC_API_KEY=\"sk-ant-your-key-here\"' >> ~/.bashrc"
echo ""
echo "2. Grant permissions to Termux:API app:"
echo "   Android Settings -> Apps -> Termux:API -> Permissions"
echo "   Enable: Microphone, SMS, Contacts, Notifications"
echo ""
echo "3. Restart Termux or run: source ~/.bashrc"
echo ""
echo "4. Run the assistant:"
echo "   assistant          # Text mode (for testing)"
echo "   assistant-voice    # Voice mode"
echo ""
echo "5. (Optional) Disable battery optimization for Termux:"
echo "   Android Settings -> Apps -> Termux -> Battery -> Unrestricted"
echo ""
