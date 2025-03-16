# Claude Notification Server

A lightweight MCP server that provides auditory notifications for Claude Desktop on macOS.

## Features

- ⚡ Sound notifications when Claude needs user input
- ⚡ Sound notifications when Claude completes a task
- ⚡ Sound notifications when Claude requests tool permissions
- Uses native macOS system sounds (`.aiff` files)
- Allows customization of sounds via environment variables

## Installation

1. Ensure Python 3.8+ is installed
2. Install dependencies:

```bash
uv pip install fastmcp
```

3. Register with Claude Desktop:

```bash
cd /path/to/notifications-mcp-server
fastmcp install notification_server.py
```

Or run the installation script:

```bash
chmod +x install.sh
./install.sh
```

## Usage

The server provides three mandatory tools to the Claude LLM:

### user_input_needed
Claude MUST call this tool:
- At the beginning of EVERY conversation
- When asking questions or requesting information
- When user review or decisions are needed

### task_completed
Claude MUST call this tool:
- At the end of conversations
- After completing significant tasks
- When finishing data processing or generation
- When the final response is ready

### tool_permission_needed
Claude MUST call this tool:
- When attempting to use a tool that requires user approval
- Before actions that will generate permission popups
- When accessing external resources requiring authorization

## Customizing Sounds

Default system sounds:
- "Submarine.aiff" for user input needed
- "Glass.aiff" for task completed
- "Funk.aiff" for tool permission required

Customize with environment variables:
- `CLAUDE_INPUT_SOUND`: Path for input sound
- `CLAUDE_COMPLETED_SOUND`: Path for completion sound
- `CLAUDE_TOOL_PERMISSION_SOUND`: Path for tool permission sound

Example:
```bash
export CLAUDE_INPUT_SOUND="/System/Library/Sounds/Purr.aiff"
export CLAUDE_COMPLETED_SOUND="/System/Library/Sounds/Hero.aiff"
export CLAUDE_TOOL_PERMISSION_SOUND="/System/Library/Sounds/Blow.aiff"
fastmcp install notification_server.py
```

### Available System Sounds

macOS system sounds in `/System/Library/Sounds/`:
Basso.aiff, Blow.aiff, Bottle.aiff, Frog.aiff, Funk.aiff, Glass.aiff, 
Hero.aiff, Morse.aiff, Ping.aiff, Pop.aiff, Purr.aiff, Sosumi.aiff, 
Submarine.aiff, Tink.aiff

## Troubleshooting

If sound notifications aren't working:
1. Verify you're on macOS
2. Check sound files exist and are accessible
3. Ensure system audio is not muted
4. Verify custom sounds use a supported format (`.aiff` recommended)

If Claude is not using notification tools:
1. Check server is running (`fastmcp list`)
2. Verify tools are exposed (check server logs)
3. Reinstall if necessary (`fastmcp install notification_server.py`)
4. Explicitly instruct Claude to use notification tools

## Development

- Requirements: Python 3.8+, fastmcp library
- Files: notification_server.py, install.sh, pyproject.toml
