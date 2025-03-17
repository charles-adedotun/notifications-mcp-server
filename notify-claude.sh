#!/bin/bash
# notify-claude.sh - Helper script for Claude notifications
# Usage: ./notify-claude.sh "Title" "Message" [start|complete]

# Set title from first argument or default
TITLE="${1:-Claude Notification}"

# Set message from second argument or default
MESSAGE="${2:-Task completed}"

# Determine notification type (start or complete)
# Default to complete if not specified
NOTIFICATION_TYPE="${3:-complete}"

# Set sound based on notification type
if [[ "$NOTIFICATION_TYPE" == "start" ]]; then
    SOUND_FILE="/System/Library/Sounds/Glass.aiff"
else
    SOUND_FILE="/System/Library/Sounds/Hero.aiff"
fi

# Try terminal-notifier first (most reliable method)
if command -v terminal-notifier &> /dev/null; then
    # Use terminal-notifier with user-specific icon
    CLAUDE_ICON="/Applications/Claude.app/Contents/Resources/AppIcon.icns"
    
    if [[ -f "$CLAUDE_ICON" ]]; then
        terminal-notifier -title "$TITLE" -message "$MESSAGE" -contentImage "$CLAUDE_ICON" -sender "com.apple.Terminal" -activate "com.anthropic.claude"
    else
        terminal-notifier -title "$TITLE" -message "$MESSAGE" -sender "com.apple.Terminal" -activate "com.anthropic.claude"
    fi
    NOTIFY_STATUS=$?
else
    NOTIFY_STATUS=1  # Set to error to try next method
fi

# If terminal-notifier failed or doesn't exist, try AppleScript
if [[ $NOTIFY_STATUS -ne 0 ]]; then
    # Enhanced AppleScript approach
    osascript <<EOF
    tell application "System Events"
        display notification "$MESSAGE" with title "$TITLE"
    end tell
    delay 0.5
EOF
    NOTIFY_STATUS=$?
fi

# Play sound regardless of notification display status
if [[ -f "$SOUND_FILE" ]]; then
    afplay "$SOUND_FILE"
    SOUND_STATUS=$?
else
    # Fallback to basic sounds if files not found
    if [[ "$NOTIFICATION_TYPE" == "start" ]]; then
        afplay /System/Library/Sounds/Ping.aiff
    else
        afplay /System/Library/Sounds/Submarine.aiff
    fi
    SOUND_STATUS=$?
fi

# Generate JSON response for the MCP server
echo "{ \"status\": \"$([ $NOTIFY_STATUS -eq 0 ] && echo "success" || echo "error")\", \"message\": \"$MESSAGE\", \"sound\": \"$SOUND_FILE\", \"visual\": $([ $NOTIFY_STATUS -eq 0 ] && echo "true" || echo "false") }"

exit $([ $NOTIFY_STATUS -eq 0 -o $SOUND_STATUS -eq 0 ] && echo 0 || echo 1)