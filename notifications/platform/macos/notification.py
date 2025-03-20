"""
macOS-specific notification methods for Claude Notifications MCP Server.
"""

import logging
import os
import subprocess
import time
from typing import Optional

logger = logging.getLogger("claude-notifications")

def send_notification_applescript(title: str, message: str) -> bool:
    """
    Send a notification using AppleScript.

    Args:
        title: The notification title
        message: The notification message

    Returns:
        True if notification was sent successfully, False otherwise
    """
    try:
        # Create an enhanced AppleScript that works better in MCP context
        script = f'''
        tell application "System Events"
            # Capture current frontmost app
            set frontApp to name of first application process whose frontmost is true

            # Ensure notification is shown no matter what application is focused
            display notification "{message}" with title "{title}"

            # Give the notification time to display
            delay 1
        end tell
        '''

        # Run the AppleScript with increased timeout
        logger.info("Attempting to send notification using AppleScript")
        subprocess.run(
            ["osascript", "-e", script],
            check=True,
            capture_output=True,
            timeout=5  # Add timeout to prevent hanging
        )

        logger.info(f"Sent notification using AppleScript: {title} - {message}")

        # Add a small delay after sending to ensure notification displays before control returns
        time.sleep(0.5)

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running AppleScript notification: {e}")
        logger.error(f"stderr: {e.stderr.decode() if e.stderr else 'None'}")
        return False
    except subprocess.TimeoutExpired:
        logger.error("AppleScript notification timed out")
        return False
    except Exception as e:
        logger.error(f"Unexpected error with AppleScript notification: {e}")
        return False

def send_notification_terminal_notifier(title: str, message: str,
                                       sound: Optional[str] = None,
                                       icon_path: Optional[str] = None) -> bool:
    """
    Send a notification using terminal-notifier.

    Args:
        title: The notification title
        message: The notification message
        sound: Optional sound name (default: None to avoid duplicate sounds)
        icon_path: Optional path to icon file

    Returns:
        True if notification was sent successfully, False otherwise
    """
    try:
        # Check if terminal-notifier is installed
        which_result = subprocess.run(
            ["which", "terminal-notifier"],
            capture_output=True,
            text=True
        )

        if which_result.returncode != 0:
            logger.warning(
                "terminal-notifier not found, install it with: brew install terminal-notifier"
            )
            return False

        # Use provided icon or Claude icon or default system icon
        icon = None
        if icon_path and os.path.exists(icon_path):
            icon = icon_path
        else:
            # Look for Claude icon
            claude_icon = "/Applications/Claude.app/Contents/Resources/AppIcon.icns"
            if os.path.exists(claude_icon):
                icon = claude_icon
            else:
                # Use system alert icon as fallback
                system_icon = (
                    "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/AlertNoteIcon.icns"
                )
                if os.path.exists(system_icon):
                    icon = system_icon

        # Build command with additional options for MCP context reliability
        cmd = [
            "terminal-notifier",
            "-title", title,
            "-message", message,
            "-activate", "com.anthropic.claude",  # Try to activate Claude when clicking
            "-sender", "com.apple.Terminal"  # Use Terminal as the sender for better visibility
        ]

        # Add icon if available
        if icon:
            cmd.extend(["-contentImage", icon])
            cmd.extend(["-appIcon", icon])

        # Add sound if specified
        if sound:
            cmd.extend(["-sound", sound])

        # Add additional options to improve visibility
        cmd.extend(["-timeout", "10"])  # 10 second timeout

        # Send notification with increased timeout
        logger.info("Attempting to send notification using terminal-notifier")
        subprocess.run(cmd, check=True, capture_output=True, timeout=5)

        logger.info(f"Sent notification using terminal-notifier: {title} - {message}")

        # Add small delay after notification to ensure it's processed
        time.sleep(0.5)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error with terminal-notifier: {e}")
        logger.error(f"stderr: {e.stderr.decode() if e.stderr else 'None'}")
        return False
    except subprocess.TimeoutExpired:
        logger.error("terminal-notifier command timed out")
        return False
    except Exception as e:
        logger.error(f"Unexpected error with terminal-notifier: {e}")
        return False

def send_notification_pyobjc(title: str, message: str, icon_path: Optional[str] = None) -> bool:
    """
    Send a notification using PyObjC (native macOS API).

    Args:
        title: The notification title
        message: The notification message
        icon_path: Optional path to an icon file

    Returns:
        True if notification was sent successfully, False otherwise
    """
    try:
        from Foundation import NSImage, NSUserNotification, NSUserNotificationCenter

        notification = NSUserNotification.alloc().init()
        notification.setTitle_(title)
        notification.setInformativeText_(message)

        # Set the icon if provided
        if icon_path and os.path.exists(icon_path):
            image = NSImage.alloc().initWithContentsOfFile_(icon_path)
            if image:
                notification.setContentImage_(image)

        center = NSUserNotificationCenter.defaultUserNotificationCenter()
        center.deliverNotification_(notification)
        logger.info("Sent notification using PyObjC")
        return True
    except ImportError:
        logger.info("PyObjC not available")
        return False
    except Exception as e:
        logger.warning(f"PyObjC notification failed: {e}")
        return False

def send_notification_pync(title: str, message: str, icon_path: Optional[str] = None) -> bool:
    """
    Send a notification using pync.

    Args:
        title: The notification title
        message: The notification message
        icon_path: Optional path to an icon file

    Returns:
        True if notification was sent successfully, False otherwise
    """
    try:
        import pync
        if icon_path and os.path.exists(icon_path):
            pync.notify(message, title=title, contentImage=icon_path, appIcon=icon_path)
        else:
            pync.notify(message, title=title)
        logger.info("Sent notification using pync")
        return True
    except ImportError:
        logger.info("pync not available")
        return False
    except Exception as e:
        logger.warning(f"pync notification failed: {e}")
        return False
