#!/bin/bash
# Claude Notification Server Installation

echo "=== Claude Notification Server Installation ==="
echo

# Ensure executable
chmod +x notification_server.py

# Install uv if needed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo
fi

# Install dependencies
echo "Installing dependencies..."
uv pip install fastmcp
echo

# Register with Claude
echo "Registering with Claude Desktop..."
fastmcp install notification_server.py
echo

# Tool information
echo "=== ⚠️ MANDATORY NOTIFICATION TOOLS ⚠️ ==="
echo "Claude MUST use these notification tools:"
echo
echo "⚡ user_input_needed:"
echo "  • At start of every conversation"
echo "  • When asking for user input"
echo "  • When user review is needed"
echo
echo "⚡ task_completed:"
echo "  • At end of conversations"
echo "  • After completing tasks"
echo "  • When final response is ready"
echo
echo "⚡ tool_permission_needed:"
echo "  • When attempting to use tools requiring approval"
echo "  • Before actions generating permission popups"
echo "  • When accessing external resources"
echo

# Customization options
echo "=== Sound Customization ==="
echo "Set environment variables to customize sounds:"
echo "  CLAUDE_INPUT_SOUND: Sound for user input notifications"
echo "  CLAUDE_COMPLETED_SOUND: Sound for task completion notifications"
echo "  CLAUDE_TOOL_PERMISSION_SOUND: Sound for tool permission notifications"
echo
echo "Example:"
echo "  export CLAUDE_INPUT_SOUND=\"/System/Library/Sounds/Purr.aiff\""
echo "  export CLAUDE_COMPLETED_SOUND=\"/System/Library/Sounds/Hero.aiff\""
echo "  export CLAUDE_TOOL_PERMISSION_SOUND=\"/System/Library/Sounds/Blow.aiff\""
echo

echo "Installation complete! The notification server is now available in Claude Desktop."
