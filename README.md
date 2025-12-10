# Notifications MCP Server

MCP server that plays sounds and shows notifications when Claude Desktop completes tasks.

## Why This Exists

You kick off a long Claude task and tab away to check email, review PRs, or write docs. Ten minutes later you realize Claude finished five minutes ago. This server fixes that. Sound plays, notification appears, you're back in action.

## What It Does

Integrates with Claude Desktop to provide real-time completion feedback:

- **System Notifications** - Native macOS notifications when tasks complete
- **Sound Alerts** - Customizable audio feedback (success, error, warning tones)
- **Task Status** - Clear indication of completion state
- **Non-Intrusive** - Works in background, no polling required

## Tech Stack

- Python 3.8+
- FastMCP for Model Context Protocol integration
- macOS Notification Center
- PyObjC for native system integration

## Features

### Notification Types

- **Success** - Task completed successfully
- **Error** - Task failed with error details
- **Warning** - Task completed with warnings
- **Info** - General task updates

### Sound Options

- Built-in system sounds
- Custom sound file support
- Volume control
- Sound enable/disable toggle

### Configuration

```json
{
  "notifications": {
    "enabled": true,
    "sound": true,
    "sound_file": "Glass",
    "volume": 0.7
  }
}
```

## Quick Start

### Installation

```bash
pip install notifications-mcp-server
```

### Configuration

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "notifications": {
      "command": "python",
      "args": ["-m", "notifications_mcp_server"]
    }
  }
}
```

Restart Claude Desktop. Notifications are now active.

## Architecture

```
notifications-mcp-server/
├── core/
│   ├── notification_manager.py    # Notification logic
│   └── sound_manager.py           # Audio playback
├── platform/
│   ├── macos.py                   # macOS integration
│   └── base.py                    # Platform interface
├── utils/
│   ├── config.py                  # Configuration management
│   └── logger.py                  # Logging utilities
└── server.py                      # MCP server entry point
```

### Design Principles

1. **Modular Platform Support** - Clean abstraction for future Linux/Windows support
2. **Zero Configuration** - Works out of box with sensible defaults
3. **Non-Blocking** - Never delays Claude's operations
4. **Fail Safe** - Notification failures don't break Claude tasks

## Platform Support

- **macOS** - Full support (notifications + sound)
- **Linux** - Planned (via notify-send)
- **Windows** - Planned (via Windows Toast)

## Usage Examples

Claude Desktop automatically triggers notifications. No manual invocation needed.

### Custom Sounds

Place custom audio files in `~/.config/notifications-mcp/sounds/`:

```bash
mkdir -p ~/.config/notifications-mcp/sounds
cp my-notification.wav ~/.config/notifications-mcp/sounds/
```

Update config to use custom sound:

```json
{
  "notifications": {
    "sound_file": "my-notification.wav"
  }
}
```

## Future Ideas

- **Linux Support** - Native notification support via libnotify
- **Windows Support** - Windows 10/11 Toast notifications
- **Custom Sound Uploads** - Web interface for managing notification sounds
- **Slack Integration** - Post completion updates to Slack channels
- **Discord Integration** - Send notifications to Discord webhooks
- **Notification History** - Track and review past task completions
- **Smart Notifications** - Only notify for tasks exceeding time threshold
- **Team Notifications** - Share task completion across team members

## Development

```bash
# Clone repository
git clone https://github.com/[YOUR-USERNAME]/notifications-mcp-server.git
cd notifications-mcp-server

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/
```

## Troubleshooting

### Notifications Not Appearing

1. Check macOS Notification Center permissions
2. Verify Claude Desktop config syntax
3. Check server logs: `tail -f ~/.config/notifications-mcp/logs/server.log`

### Sound Not Playing

1. Verify sound file exists
2. Check volume settings
3. Test sound file: `afplay /path/to/sound.wav`

## Contributing

Found a bug? Open an issue with reproduction steps. Built Windows/Linux support? Submit a PR. Keep platform modules isolated and tested.

## License

MIT
