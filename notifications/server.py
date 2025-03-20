"""
MCP server implementation for Claude Notifications.
"""

import json
import os
import subprocess
from typing import Dict

from fastmcp import FastMCP

from notifications import __version__
from notifications.core.notification_manager import NotificationManager
from notifications.core.sound_manager import SoundManager
from notifications.utils.logging import setup_logging

# Set up logging
logger = setup_logging()

def verify_sounds() -> bool:
    """
    Verify that the configured sound files exist and are playable.

    Returns:
        True if all sound files exist, False otherwise
    """
    start_sound = SoundManager.get_notification_sound(is_start=True)
    complete_sound = SoundManager.get_notification_sound(is_start=False)

    success = True

    if not os.path.exists(start_sound):
        logger.warning(
            f"⚠️ Warning: Start notification sound file not found at {start_sound}"
        )
        success = False

    if not os.path.exists(complete_sound):
        logger.warning(
            f"⚠️ Warning: Completion notification sound file not found at {complete_sound}"
        )
        success = False

    return success

def verify_notification_components() -> bool:
    """
    Verify that the required components for visual notifications are available and
    properly registered.

    Returns:
        True if all components are available, False otherwise
    """
    import importlib.util

    success = True

    # Check for PyObjC or pync
    pyobjc_available = importlib.util.find_spec("Foundation") is not None
    pync_available = importlib.util.find_spec("pync") is not None

    if pyobjc_available:
        logger.info("✅ PyObjC is available for visual notifications")
    elif pync_available:
        logger.info("✅ pync is available for visual notifications")
    else:
        logger.info(
            "ℹ️ Neither PyObjC nor pync are available. "
            "Will try AppleScript or terminal-notifier instead."
        )
        # We don't mark success as False here since we have fallback options

    # Check for terminal-notifier as a fallback
    try:
        terminal_notifier_available = subprocess.run(
            ["which", "terminal-notifier"],
            capture_output=True
        ).returncode == 0

        if terminal_notifier_available:
            logger.info("✅ terminal-notifier is available as a fallback")
    except Exception:
        terminal_notifier_available = False

    # Check notification icon
    icon_path = NotificationManager.get_notification_icon()
    if icon_path:
        logger.info(f"✅ Notification icon found at {icon_path}")
    else:
        logger.info("ℹ️ No notification icon found. Notifications will be sent without an icon.")

    # Test notifications directly to ensure permissions
    if NotificationManager.are_visual_notifications_enabled():
        try:
            # Always send a test notification to trigger permission prompt
            logger.info("Sending test notification to register with Notification Center...")
            test_result = NotificationManager.send_test_notification()

            if test_result:
                logger.info(
                    "✅ Test notification sent successfully - permissions should be granted"
                )
            else:
                logger.warning(
                    "⚠️ Unable to send test notification - trying direct AppleScript method"
                )
                apple_result = NotificationManager.send_notification_applescript(
                    "Claude Notification Server",
                    "Testing notification permissions"
                )
                if apple_result:
                    logger.info("✅ AppleScript notification succeeded")
                else:
                    logger.warning("⚠️ All notification methods failed")
                    logger.info(
                        "You can manually enable permissions in System Preferences > Notifications"
                    )
                    success = False
        except Exception as e:
            logger.warning(f"⚠️ Error checking notification permissions: {e}")
            success = False
    else:
        logger.info("ℹ️ Visual notifications are disabled by environment configuration")

    return success

class NotificationServer:
    """
    MCP server for Claude Desktop notifications.
    """

    def __init__(self):
        """Initialize the notification server."""
        self.mcp = FastMCP("notify-user")
        self._setup_tools()

    def _setup_tools(self):
        """Set up MCP tools."""
        @self.mcp.tool()
        def task_status(message: str = "Task completed") -> Dict[str, str]:
            """
            ‼️ MANDATORY: Sends notifications (sound and visual) for the user.

            📢 IMPORTANT INSTRUCTIONS FOR THE LLM:
               1. ALWAYS call this tool at the START of EVERY response
               2. Call this tool BEFORE using any other tools
               3. Call this tool at the END of conversations
               4. Use this tool even if no other tools are needed

            ⚠️ PURPOSE: This notification alerts users when the LLM has started or completed
            processing.

            Args:
                message (str): Message describing the state of the task
                (e.g., "Started processing", "Task completed")

            Returns:
                dict: Status information about the notification
            """
            logger.info(f"Notification: {message}")

            # Determine if this is a start or completion notification
            is_start = "start" in message.lower() or "processing" in message.lower()
            notification_type = "start" if is_start else "complete"

            # Set appropriate titles based on notification type
            if is_start:
                title = "Claude is Processing"
            else:
                title = "Claude Response Ready"

            # Path to helper script (look in project directory first, then home directory)
            helper_script = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "notify-claude.sh"
            )

            # If helper script exists, use it as the primary notification method
            if os.path.exists(helper_script):
                try:
                    logger.info(f"Using helper script: {helper_script}")

                    # Make the script executable if it isn't already
                    if not os.access(helper_script, os.X_OK):
                        os.chmod(helper_script, 0o755)

                    # Run the helper script with title, message, and notification type
                    process = subprocess.run(
                        [helper_script, title, message, notification_type],
                        capture_output=True,
                        text=True,
                        check=False  # Don't raise exception on non-zero exit
                    )

                    # Check if the script ran successfully
                    if process.returncode == 0:
                        logger.info("Helper script ran successfully")

                        # Try to parse the JSON response from the script
                        try:
                            result = json.loads(process.stdout.strip())
                            logger.info(f"Script result: {result}")
                            return result
                        except json.JSONDecodeError:
                            logger.warning(f"Could not parse script output: {process.stdout}")
                    else:
                        logger.warning(f"Helper script failed with code {process.returncode}")
                        logger.warning(f"stderr: {process.stderr}")

                except Exception as e:
                    logger.error(f"Error running helper script: {e}")
                    # Fall through to original methods if helper script fails
            else:
                logger.info(f"Helper script not found at {helper_script}, using built-in methods")

            # If we reach here, the helper script either doesn't exist or failed
            # Fall back to the original implementation

            # Send sound notification
            sound_file = SoundManager.get_notification_sound(is_start=is_start)
            sound_success = SoundManager.play_sound(sound_file)

            # Visual notification
            visual_success = False
            visual_enabled = NotificationManager.are_visual_notifications_enabled()

            if visual_enabled:
                try:
                    # Get icon path
                    icon_path = NotificationManager.get_notification_icon()

                    # Try terminal-notifier directly first for MCP context
                    try:
                        visual_success = NotificationManager.send_notification_terminal_notifier(
                            title=title,
                            message=message,
                            sound=None,  # Don't duplicate sound
                            icon_path=icon_path
                        )
                        logger.info(f"Terminal-notifier result: {visual_success}")
                    except Exception as e:
                        logger.error(f"Terminal-notifier failed: {e}")

                    # If terminal-notifier failed, try AppleScript directly
                    if not visual_success:
                        try:
                            visual_success = NotificationManager.send_notification_applescript(
                                title=title,
                                message=message
                            )
                            logger.info(f"AppleScript result: {visual_success}")
                        except Exception as e:
                            logger.error(f"AppleScript failed: {e}")

                    # If both direct methods failed, try the full notification stack
                    if not visual_success:
                        try:
                            visual_success = NotificationManager.send_notification(
                                title=title,
                                message=message,
                                icon_path=icon_path
                            )
                            logger.info(f"Full notification stack result: {visual_success}")
                        except Exception as e:
                            logger.error(f"Full notification stack failed: {e}")

                except Exception as e:
                    logger.error(f"Error sending visual notification: {e}")

            return {
                "status": "success" if (sound_success or visual_success) else "error",
                "message": message,
                "sound": sound_file if sound_success else None,
                "visual": visual_success
            }

    def run(self):
        """Run the notification server."""
        try:
            self.mcp.run()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Error running server: {e}")
            return 1
        return 0

def main():
    """Main entry point for the notification server."""
    print(f"🔔 Claude Notification Server v{__version__}")
    print("📋 Available tool:")
    print("  • task_status: MUST be used at the start and end of every interaction")

    # Verify components
    sound_success = verify_sounds()

    if sound_success:
        print("✅ All sound files verified")
    else:
        print("⚠️ Some sound files could not be found. Check configurations.")

    # Now handle visual notifications with explicit permission check
    if NotificationManager.are_visual_notifications_enabled():
        print("🔔 Visual notifications are enabled, configuring...")
        visual_success = verify_notification_components()

        if visual_success:
            print("✅ Visual notification components verified")
        else:
            print("⚠️ Visual notifications may not work correctly. See warnings above.")
            print("💡 Try running: python3 test_notification.py for more detailed testing")
    else:
        print("ℹ️ Visual notifications are disabled")

    # Create and run the server
    server = NotificationServer()
    return server.run()

if __name__ == "__main__":
    main()
