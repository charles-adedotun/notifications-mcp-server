# Claude Notification Server

A lightweight MCP server that provides auditory notifications for Claude Desktop on macOS.

## Features

- ⚡ Sound notifications when Claude needs tool permission approval
- ⚡ Sound notifications when Claude completes a task
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

The server provides two mandatory tools to the Claude LLM:

### tool_permission_needed
Claude MUST call this tool:
- When attempting to use a tool that requires user approval
- Before actions that will generate permission popups
- When accessing external resources requiring authorization
- ANYTIME Claude needs you to take an action to grant permissions

### task_completed
Claude MUST call this tool:
- At the end of conversations
- After completing significant tasks
- When finishing data processing or generation
- When the final response is ready

## Customizing Sounds

Default system sounds:
- "Funk.aiff" for tool permission required
- "Glass.aiff" for task completed

Customize with environment variables:
- `CLAUDE_TOOL_PERMISSION_SOUND`: Path for tool permission sound
- `CLAUDE_COMPLETED_SOUND`: Path for completion sound

Example:
```bash
export CLAUDE_TOOL_PERMISSION_SOUND="/System/Library/Sounds/Blow.aiff"
export CLAUDE_COMPLETED_SOUND="/System/Library/Sounds/Hero.aiff"
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
5. Look at the logs (the server now uses Python's logging module)
6. Try running `afplay /System/Library/Sounds/Funk.aiff` to test sound playback

If Claude is not using notification tools:
1. Check server is running (`fastmcp list`)
2. Verify tools are exposed (check server logs)
3. Reinstall if necessary (`fastmcp install notification_server.py`)
4. Explicitly instruct Claude to use notification tools

## Development

- Requirements: Python 3.8+, fastmcp library
- Files: notification_server.py, install.sh, pyproject.toml
