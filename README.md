# Notifications MCP Server

[![Tests](https://github.com/charles-adedotun/notifications-mcp-server/actions/workflows/python-test.yml/badge.svg)](https://github.com/charles-adedotun/notifications-mcp-server/actions/workflows/python-test.yml)

MCP server that lets Claude Desktop or another MCP client trigger macOS sound and visual notifications through a `task_status` tool.

## Current Status

This is a macOS-focused utility. It is not an automatic Claude completion detector by itself: an MCP client or model must call the `task_status` tool when it wants a notification.

## What Works Today

- Registers a `task_status` MCP tool.
- Plays macOS system sounds with `afplay`.
- Sends visual notifications using terminal-notifier, AppleScript, PyObjC, or pync fallbacks.
- Supports separate start and completion sounds.
- Supports disabling visual notifications through an environment variable.
- Includes tests for the modular notification and sound managers.

## Important Limitations

- macOS is the only implemented platform.
- Linux and Windows support are not implemented.
- Notifications only happen when the MCP tool is called.
- The packaged console script is `claude-notifications`.
- The Python package is `notifications`; there is no `notifications_mcp_server` module entry point.
- Custom sound configuration uses environment variables, not the JSON configuration block that older README versions showed.

## Installation

```bash
pip install notifications-mcp-server
```

Optional visual notification dependencies:

```bash
pip install "notifications-mcp-server[visual]"
pip install "notifications-mcp-server[pync]"
```

For terminal-notifier fallback support:

```bash
brew install terminal-notifier
```

## Claude Desktop Configuration

Use the console script installed by the package:

```json
{
  "mcpServers": {
    "notifications": {
      "command": "claude-notifications"
    }
  }
}
```

Restart Claude Desktop after changing the config.

## Configuration

Environment variables:

```bash
export CLAUDE_START_SOUND="/System/Library/Sounds/Glass.aiff"
export CLAUDE_COMPLETE_SOUND="/System/Library/Sounds/Hero.aiff"
export CLAUDE_VISUAL_NOTIFICATIONS="true"
export CLAUDE_NOTIFICATION_ICON="/path/to/icon.png"
```

If no custom sounds are set, the server uses macOS system sounds.

## MCP Tool

`task_status`

Input:

```json
{
  "message": "Task completed"
}
```

Messages containing `start` or `processing` are treated as start notifications. Other messages are treated as completion notifications.

## Verification Demo

Run the local diagnostic script on macOS to test the available notification paths:

```bash
python3 test_notification.py
```

The MCP tool returns a compact status object after attempting sound and visual notification delivery:

```json
{
  "status": "success",
  "message": "Task completed",
  "sound": "/System/Library/Sounds/Hero.aiff",
  "visual": true
}
```

For a quieter smoke test that skips visual notification prompts:

```bash
CLAUDE_VISUAL_NOTIFICATIONS=false claude-notifications
```

## Development

```bash
git clone https://github.com/charles-adedotun/notifications-mcp-server.git
cd notifications-mcp-server
pip install -e ".[dev]"
pytest
```

## License

MIT
