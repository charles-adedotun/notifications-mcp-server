# Claude Notification Server

A lightweight MCP server that provides both auditory and visual notifications for Claude Desktop on macOS. This server lets you know when Claude starts processing your request and when it has completed a task.

## Features

- 🔔 Different sound notifications at the beginning and end of Claude responses
- 💻 Compatible with macOS native system sounds (`.aiff` files)
- 🎵 Easily customizable notification sounds via environment variables
- 🔔 Visual desktop notifications through macOS Notification Center
- 🖼️ Custom icons for visual notifications
- 🚀 Simple setup with minimal dependencies
- 📱 Multiple notification methods with fallbacks (PyObjC, pync, AppleScript, terminal-notifier)

## Installation and Setup

### Prerequisites
- macOS (notifications rely on macOS-specific features)
- Python 3.8 or higher
- Claude Desktop application

### Quick Install

1. **Clone the repository:**
   ```bash
   git clone https://github.com/charles-adedotun/notifications-mcp-server.git
   cd notifications-mcp-server
   ```

2. **Make the server executable:**
   ```bash
   chmod +x notification_server.py
   ```

3. **Install uv (if not already installed):**
   ```bash
   # Option 1: Using curl
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Option 2: Using Homebrew
   brew install uv
   ```

4. **Install dependencies with uv:**
   ```bash
   # Install the required fastmcp library
   uv pip install fastmcp
   
   # Install ONE of these visual notification libraries
   uv pip install pyobjc-core pyobjc-framework-Cocoa  # Recommended
   # OR
   uv pip install pync  # Alternative with simpler API
   
   # Optional: Install terminal-notifier as a fallback method
   brew install terminal-notifier
   ```

5. **Register with Claude Desktop:**
   ```bash
   # Install the MCP server
   fastmcp install notification_server.py
   ```

6. **Configure Claude Desktop:**

   Edit Claude's configuration to include the notification server:

   ```bash
   # First, create a backup of the current config
   cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup
   
   # Open the config file in a text editor
   open -a TextEdit ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

   Add the following to the `mcpServers` section of the JSON file:

   ```json
   "mcpServers": [
     {
       "name": "Claude Notifications",
       "command": "/usr/bin/python3",
       "args": ["/full/path/to/notification_server.py"],
       "autoStart": true
     }
   ]
   ```
   
   Replace `/full/path/to/notification_server.py` with the actual path to your notification_server.py file.
   
   If the `mcpServers` array already exists, just add this new object to it.

7. **Restart Claude Desktop**

8. **Test the notifications:**
   ```bash
   python3 test_notification.py
   ```
   This will test all available notification methods and help diagnose any issues.

## How It Works

Once installed, the server automatically connects with Claude Desktop and offers the `task_status` notification tool. Claude will call this tool at the start and end of each interaction, producing both audible and visual notifications.

### Architecture

```
┌─────────────────┐     MCP Protocol      ┌─────────────────┐     System Command    ┌─────────────┐
│                 │ ──────────────────>   │                 │ ──────────────────>   │ macOS Sound │
│  Claude Desktop │                       │   Notification  │                       │    System   │
│   Application   │ <──────────────────   │   MCP Server    │ <──────────────────   │             │
│                 │                       │                 │                       └─────────────┘
                                          │                 │                       ┌───────────-──┐
                                          │                 │ ──────────────────>   │ macOS        │
                                          │                 │                       │ Notification │
                                          │                 │ <──────────────────   │ Center       │
                                          └─────────────────┘                       └─────────────-┘
```

The notification server uses multiple methods to deliver visual notifications, with automatic fallbacks:

1. **PyObjC** (native macOS notifications) - Tried first
2. **pync** (if installed) - Tried if PyObjC fails
3. **AppleScript** (works consistently) - Used as fallback
4. **terminal-notifier** (if installed) - Last resort option

This ensures that at least one notification method should work on your system.

## Customizing Notifications

### Sound Notifications

#### Default Sounds
- Start of task: "Glass.aiff" from macOS system sounds
- End of task: "Hero.aiff" from macOS system sounds

#### Customizing Sounds

```bash
# For start notifications
export CLAUDE_START_SOUND="/System/Library/Sounds/Ping.aiff"

# For completion notifications
export CLAUDE_COMPLETE_SOUND="/System/Library/Sounds/Purr.aiff"

# Legacy option (same sound for both)
export CLAUDE_NOTIFICATION_SOUND="/System/Library/Sounds/Submarine.aiff"

# After setting environment variables, reinstall the server
fastmcp install notification_server.py
```

### Visual Notifications

```bash
# Disable visual notifications
export CLAUDE_VISUAL_NOTIFICATIONS="false"

# Set custom notification icon
export CLAUDE_NOTIFICATION_ICON="/path/to/your/custom/icon.png"

# After setting environment variables, reinstall the server
fastmcp install notification_server.py
```

### Making Settings Permanent

Add to your shell profile (~/.zshrc, ~/.bashrc, or similar):

```bash
# For different sounds
echo 'export CLAUDE_START_SOUND="/System/Library/Sounds/Ping.aiff"' >> ~/.zshrc
echo 'export CLAUDE_COMPLETE_SOUND="/System/Library/Sounds/Purr.aiff"' >> ~/.zshrc

# For visual notifications
echo 'export CLAUDE_VISUAL_NOTIFICATIONS="true"' >> ~/.zshrc
echo 'export CLAUDE_NOTIFICATION_ICON="/path/to/your/icon.png"' >> ~/.zshrc

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

You can also use your own .aiff files by providing the full path.

## Troubleshooting

### Visual Notifications Not Working

1. **Run the test script:**
   ```bash
   python3 test_notification.py
   ```
   This comprehensive test will try all notification methods and provide diagnostic information.

2. **Check notification permissions:**
   - Go to System Preferences → Notifications
   - Look for applications that might handle notifications:
     - Python
     - Terminal
     - osascript (AppleScript)
   - Ensure notifications are enabled for these applications
   
   You can open notification preferences directly with:
   ```bash
   open "x-apple.systempreferences:com.apple.preference.notifications"
   ```

3. **Try installing terminal-notifier:**
   ```bash
   brew install terminal-notifier
   ```
   This provides an additional fallback method for notifications.

4. **Check the server logs:**
   - Look for error messages in the terminal where the server is running
   - In Claude Desktop, enable Developer Mode (Help menu → Enable Developer Mode)
   - Check the MCP Log File in the Developer menu

### Sound Notifications Not Working

1. **Verify your macOS sound settings:**
   - Make sure your system volume is not muted
   - Try playing a sound directly: `afplay /System/Library/Sounds/Glass.aiff`

2. **Check custom sound paths:**
   - If you specified custom sounds, make sure the paths are correct
   - Use only `.aiff` files for best compatibility

### Server Not Connecting

1. **Verify Claude Desktop configuration:**
   - Check that the path to the notification_server.py file is correct in claude_desktop_config.json
   - Make sure the server is registered with `fastmcp install notification_server.py`

2. **Restart everything:**
   ```bash
   # Reinstall the server
   fastmcp install notification_server.py
   
   # Restart Claude Desktop
   ```

## Uninstallation

To remove the notification server:

1. **Edit Claude Desktop configuration file:**
   ```bash
   # Open the config file
   open -a TextEdit ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
   
   Remove the server entry from the `mcpServers` section.

2. **If you installed Python packages:**
   ```bash
   # Remove packages installed with uv
   uv pip uninstall fastmcp pyobjc-core pyobjc-framework-Cocoa pync
   ```

## Development

- **Requirements:** Python 3.8+, fastmcp library, notification libraries
- **Running tests with uv:** 
  ```bash
  uv pip install pytest pytest-cov
  pytest
  ```

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Built using the [FastMCP](https://github.com/anthropics/mcp) library from Anthropic
- Special thanks to all contributors and the Claude community
