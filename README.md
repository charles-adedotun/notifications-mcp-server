# Claude Notification Server

A lightweight MCP server that provides auditory notifications for Claude Desktop on macOS. This server lets you know when Claude starts processing your request and when it has completed a task.

## Features

- 🔔 Different sound notifications at the beginning and end of Claude responses
- 💻 Compatible with macOS native system sounds (`.aiff` files)
- 🎵 Easily customizable notification sounds via environment variables
- 🚀 Simple setup with minimal dependencies

## Quick Start

1. **Prerequisites:** Python 3.8+ and macOS

2. **Clone the repository:**
   ```bash
   git clone https://github.com/charles-adedotun/notifications-mcp-server.git
   cd notifications-mcp-server
   ```

3. **Make the server executable:**
   ```bash
   chmod +x notification_server.py
   ```

4. **Install uv (if not already installed):**
   ```bash
   # Option 1: Using curl
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Option 2: Using Homebrew
   brew install uv
   ```

5. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv pip install fastmcp
   
   # Or using standard pip
   pip install fastmcp
   ```

6. **Register with Claude Desktop:**
   ```bash
   fastmcp install notification_server.py
   ```

7. **Verify installation:**
   ```bash
   fastmcp list
   # You should see "notify-user" in the list
   ```

## How It Works

Once installed, the server automatically connects with Claude Desktop and offers the `task_status` notification tool. Claude will call this tool at the start and end of each interaction, producing an audible notification.

### The `task_status` Tool

This tool plays a sound notification to alert you when:
- Claude begins processing your request ("Glass" sound by default)
- Claude completes a task or finishes processing ("Hero" sound by default)

The tool automatically detects whether it's being called at the start or end of a task based on the message parameter.

**Instruction for Claude (automatically included in the tool's documentation):**
- ALWAYS call this tool at the START of EVERY response
- Call this tool BEFORE using any other tools
- Call this tool at the END of conversations
- Use this tool even if no other tools are needed

## Customizing the Notification Sounds

### Default Sounds
- Start of task: "Glass.aiff" from macOS system sounds
- End of task: "Hero.aiff" from macOS system sounds

### Customizing Individual Sounds

**For start notifications:**
```bash
export CLAUDE_START_SOUND="/System/Library/Sounds/Ping.aiff"
fastmcp install notification_server.py
```

**For completion notifications:**
```bash
export CLAUDE_COMPLETE_SOUND="/System/Library/Sounds/Purr.aiff"
fastmcp install notification_server.py
```

**Legacy option (same sound for both):**
```bash
export CLAUDE_NOTIFICATION_SOUND="/System/Library/Sounds/Submarine.aiff"
fastmcp install notification_server.py
```

### Make it permanent
Add to your shell profile (~/.zshrc, ~/.bashrc, or similar):
```bash
# For different sounds
echo 'export CLAUDE_START_SOUND="/System/Library/Sounds/Ping.aiff"' >> ~/.zshrc
echo 'export CLAUDE_COMPLETE_SOUND="/System/Library/Sounds/Purr.aiff"' >> ~/.zshrc

# Or for the same sound
# echo 'export CLAUDE_NOTIFICATION_SOUND="/System/Library/Sounds/Submarine.aiff"' >> ~/.zshrc

source ~/.zshrc
```

### Available System Sounds

macOS provides these built-in sounds in `/System/Library/Sounds/`:

| Sound Name | Description |
|------------|-------------|
| Basso.aiff | Deep, serious tone |
| Blow.aiff | Wind-like sound |
| Bottle.aiff | Bottle pop sound |
| Frog.aiff | Frog croak |
| Funk.aiff | Funky electronic sound |
| Glass.aiff | Glass tapping sound (default) |
| Hero.aiff | Triumphant sound |
| Morse.aiff | Short morse code beep |
| Ping.aiff | Classic ping notification |
| Pop.aiff | Short pop sound |
| Purr.aiff | Gentle purr sound |
| Sosumi.aiff | Apple's classic alert |
| Submarine.aiff | Submarine ping |
| Tink.aiff | Light tink sound |

You can preview these sounds with:
```bash
afplay /System/Library/Sounds/Glass.aiff
```

**Custom Sounds:** You can also use your own .aiff files by providing the full path.

## Troubleshooting

### No Sound Playing

1. **Check macOS compatibility:**
   - This server uses the macOS `afplay` command and only works on macOS.

2. **Verify sound settings:**
   - Make sure your system volume is not muted
   - Try `afplay /System/Library/Sounds/Glass.aiff` to test directly

3. **Check notification file:**
   - Ensure your custom sound file exists (if specified)
   - Use only `.aiff` files for best compatibility

4. **Check server logs:**
   - Look for error messages in the terminal where the server is running

### Claude Not Using Notifications

1. **Check server status:**
   ```bash
   fastmcp list
   # Should show "notify-user" in the active servers
   ```

2. **Restart the server:**
   ```bash
   fastmcp uninstall notify-user
   fastmcp install notification_server.py
   ```

## Uninstallation

To remove the notification server:
```bash
fastmcp uninstall notify-user
```

## Development

- **Requirements:** Python 3.8+, fastmcp library
- **Main files:** notification_server.py, pyproject.toml
- **Version:** 1.0.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use, modify, and distribute as needed.
