#!/usr/bin/env python3

import os
import subprocess
import logging
import time
import json
from typing import Dict, Optional
from fastmcp import FastMCP
import importlib.util

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("claude-notifications")

# Version
__version__ = "1.2.0"

class SoundManager:
    """
    Manages sound playback for notifications using macOS system sounds.
    """
    
    # Default system sounds directory on macOS
    SYSTEM_SOUNDS_DIR = "/System/Library/Sounds/"
    
    # Default sounds (will be used if no custom sounds are specified)
    DEFAULT_START_SOUND = "Glass.aiff"
    DEFAULT_COMPLETE_SOUND = "Hero.aiff"
    
    # Environment variable names for custom sounds
    ENV_START_SOUND = "CLAUDE_START_SOUND"
    ENV_COMPLETE_SOUND = "CLAUDE_COMPLETE_SOUND"
    
    # Legacy support for single sound config
    ENV_NOTIFICATION_SOUND = "CLAUDE_NOTIFICATION_SOUND"
    
    @classmethod
    def get_notification_sound(cls, is_start: bool = True) -> str:
        """Get the path to the sound file for notifications.
        
        Args:
            is_start: True for start sound, False for completion sound
        """
        # Check for legacy single sound configuration first
        legacy_sound = os.environ.get(cls.ENV_NOTIFICATION_SOUND)
        if legacy_sound and os.path.exists(legacy_sound):
            logger.info(f"Using legacy custom notification sound: {legacy_sound}")
            return legacy_sound
        
        # Get the appropriate environment variable and default sound based on notification type
        if is_start:
            env_var = cls.ENV_START_SOUND
            default_sound = cls.DEFAULT_START_SOUND
            sound_type = "start"
        else:
            env_var = cls.ENV_COMPLETE_SOUND
            default_sound = cls.DEFAULT_COMPLETE_SOUND
            sound_type = "completion"
        
        # Check for custom sound
        custom_sound = os.environ.get(env_var)
        if custom_sound and os.path.exists(custom_sound):
            logger.info(f"Using custom {sound_type} sound: {custom_sound}")
            return custom_sound
        
        # Use default sound
        sound_file = os.path.join(cls.SYSTEM_SOUNDS_DIR, default_sound)
        logger.info(f"Using default {sound_type} sound: {sound_file}")
        return sound_file
    
    @staticmethod
    def play_sound(sound_file: str) -> bool:
        """
        Play a sound file using macOS afplay command.
        
        Returns True if sound played successfully, False otherwise.
        """
        if not os.path.exists(sound_file):
            logger.error(f"Sound file does not exist: {sound_file}")
            return False
            
        try:
            logger.info(f"Playing sound: {sound_file}")
            subprocess.run(
                ["afplay", sound_file],
                check=True,
                capture_output=True
            )
            logger.info("Sound played successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error playing sound: {e}")
            logger.error(f"stderr: {e.stderr.decode() if e.stderr else 'None'}")
            return False
        except FileNotFoundError:
            logger.error("afplay command not found. Are you running on macOS?")
            return False
        except Exception as e:
            logger.error(f"Unexpected error playing sound: {e}")
            return False


class NotificationManager:
    """
    Manages macOS visual notifications using PyObjC, pync, AppleScript, or terminal-notifier.
    """
    
    # Environment variable names for enabling/disabling visual notifications
    ENV_VISUAL_NOTIFICATIONS = "CLAUDE_VISUAL_NOTIFICATIONS"
    ENV_NOTIFICATION_ICON = "CLAUDE_NOTIFICATION_ICON"
    
    # Default icon paths
    # Local icon is preferred, then app icon, then None
    LOCAL_ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claude-ai-icon.png")
    APP_ICON_PATH = "/Applications/Claude.app/Contents/Resources/AppIcon.icns"
    
    @classmethod
    def are_visual_notifications_enabled(cls) -> bool:
        """Check if visual notifications are enabled."""
        env_value = os.environ.get(cls.ENV_VISUAL_NOTIFICATIONS, "true").lower()
        return env_value in ("true", "1", "yes", "y", "on")
    
    @classmethod
    def get_notification_icon(cls) -> Optional[str]:
        """Get the path to the icon for notifications."""
        # Check environment variable first (highest priority)
        custom_icon = os.environ.get(cls.ENV_NOTIFICATION_ICON)
        if custom_icon and os.path.exists(custom_icon):
            logger.info(f"Using custom notification icon: {custom_icon}")
            return custom_icon
        
        # Use local project icon if available (second priority)
        if os.path.exists(cls.LOCAL_ICON_PATH):
            logger.info(f"Using bundled Claude icon: {cls.LOCAL_ICON_PATH}")
            return cls.LOCAL_ICON_PATH
        
        # Use default Claude app icon if available (third priority)
        if os.path.exists(cls.APP_ICON_PATH):
            logger.info(f"Using default Claude app icon: {cls.APP_ICON_PATH}")
            return cls.APP_ICON_PATH
            
        return None
    
    @staticmethod
    def send_notification_applescript(title: str, message: str) -> bool:
        """
        Send a notification using AppleScript as a fallback method.
        Uses an enhanced script for better reliability in MCP context.
        
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
            logger.info("Attempting to send notification using Enhanced AppleScript")
            process = subprocess.run(
                ["osascript", "-e", script],
                check=True,
                capture_output=True,
                timeout=5  # Add timeout to prevent hanging
            )
            
            logger.info(f"Sent notification using Enhanced AppleScript: {title} - {message}")
            logger.debug(f"AppleScript stdout: {process.stdout.decode() if process.stdout else 'None'}")
            
            # Add a small delay after sending to ensure notification displays before control returns
            time.sleep(0.5)
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running Enhanced AppleScript notification: {e}")
            logger.error(f"stderr: {e.stderr.decode() if e.stderr else 'None'}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("AppleScript notification timed out")
            return False
        except Exception as e:
            logger.error(f"Unexpected error with Enhanced AppleScript notification: {e}")
            return False
    
    @staticmethod
    def send_notification_terminal_notifier(title: str, message: str, sound: Optional[str] = None, icon_path: Optional[str] = None) -> bool:
        """
        Send a notification using terminal-notifier with enhanced reliability for MCP context.
        
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
                logger.warning("terminal-notifier not found, install it with: brew install terminal-notifier")
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
                    system_icon = "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/AlertNoteIcon.icns"
                    if os.path.exists(system_icon):
                        icon = system_icon
            
            # Build command with additional options for MCP context reliability
            cmd = [
                "terminal-notifier", 
                "-title", title, 
                "-message", message,
                "-activate", "com.anthropic.claude",  # Try to activate Claude when clicking notification
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
            logger.info(f"Attempting to send notification using enhanced terminal-notifier with cmd: {cmd}")
            process = subprocess.run(cmd, check=True, capture_output=True, timeout=5)
            
            logger.info(f"Sent notification using enhanced terminal-notifier: {title} - {message}")
            logger.debug(f"terminal-notifier stdout: {process.stdout.decode() if process.stdout else 'None'}")
            
            # Add small delay after notification to ensure it's processed
            time.sleep(0.5)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error with enhanced terminal-notifier: {e}")
            logger.error(f"stderr: {e.stderr.decode() if e.stderr else 'None'}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("terminal-notifier command timed out")
            return False
        except Exception as e:
            logger.error(f"Unexpected error with enhanced terminal-notifier: {e}")
            return False
    
    @staticmethod
    def send_notification(title: str, message: str, icon_path: Optional[str] = None) -> bool:
        """
        Send a macOS notification using multiple methods with fallbacks.
        
        Args:
            title: The notification title
            message: The notification message
            icon_path: Path to the icon file (optional)
            
        Returns:
            True if notification was sent successfully with any method, False otherwise
        """
        logger.info(f"Attempting to send notification: {title} - {message}")
        
        # Try multiple notification methods in sequence
        methods_tried = 0
        success = False
        
        # For MCP server context, first try AppleScript and terminal-notifier as they are more reliable
        # 1. First try AppleScript as it's the most reliable in MCP context
        try:
            success = NotificationManager.send_notification_applescript(title, message)
            methods_tried += 1
            logger.info(f"AppleScript notification attempted: {success}")
        except Exception as e:
            logger.warning(f"Error in AppleScript notification attempt: {e}")
        
        # 2. Try terminal-notifier next
        if not success:
            try:
                success = NotificationManager.send_notification_terminal_notifier(
                    title, message, sound=None  # Don't specify sound to avoid duplicate sounds
                )
                methods_tried += 1
                logger.info(f"Terminal-notifier notification attempted: {success}")
            except Exception as e:
                logger.warning(f"Error in terminal-notifier attempt: {e}")
        
        # 3. Then try with PyObjC
        if not success:
            try:
                try:
                    from Foundation import NSUserNotification, NSUserNotificationCenter, NSImage
                    
                    notification = NSUserNotification.alloc().init()
                    notification.setTitle_(title)
                    notification.setInformativeText_(message)
                    
                    # Set the icon if provided
                    if icon_path:
                        image = NSImage.alloc().initWithContentsOfFile_(icon_path)
                        if image:
                            notification.setContentImage_(image)
                    
                    center = NSUserNotificationCenter.defaultUserNotificationCenter()
                    center.deliverNotification_(notification)
                    logger.info("Sent notification using PyObjC")
                    success = True
                except ImportError:
                    logger.info("PyObjC not available, will try other methods")
                except Exception as e:
                    logger.warning(f"PyObjC notification failed: {e}")
                
                methods_tried += 1
            except Exception as e:
                logger.warning(f"Error in PyObjC notification attempt: {e}")
        
        # 4. Try with pync as last resort
        if not success:
            try:
                try:
                    import pync
                    if icon_path:
                        pync.notify(message, title=title, contentImage=icon_path, appIcon=icon_path)
                    else:
                        pync.notify(message, title=title)
                    logger.info("Sent notification using pync")
                    success = True
                except ImportError:
                    logger.info("pync not available, will try other methods")
                except Exception as e:
                    logger.warning(f"pync notification failed: {e}")
                
                methods_tried += 1
            except Exception as e:
                logger.warning(f"Error in pync notification attempt: {e}")
        
        logger.info(f"Notification result: success={success}, methods_tried={methods_tried}")
        return success
    
    @classmethod
    def send_test_notification(cls) -> bool:
        """
        Send a test notification to ensure the application is registered with Notification Center.
        This will trigger the permission prompt if needed.
        
        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            title = "Claude Notification Server"
            message = "Initializing notification permissions"
            
            # Try multiple methods for the test notification
            success = cls.send_notification(title, message)
            
            # If all methods failed, try the direct method as a last resort
            if not success:
                try:
                    from Foundation import NSUserNotification, NSUserNotificationCenter
                    notification = NSUserNotification.alloc().init()
                    notification.setTitle_(title)
                    notification.setInformativeText_(message)
                    center = NSUserNotificationCenter.defaultUserNotificationCenter()
                    center.deliverNotification_(notification)
                    logger.info("Sent test notification using direct PyObjC method")
                    success = True
                except Exception as e:
                    logger.warning(f"Direct PyObjC test notification failed: {e}")
            
            # Always try AppleScript as well to make sure permissions are requested
            try:
                cls.send_notification_applescript(title, message)
            except Exception as e:
                logger.warning(f"AppleScript test notification failed: {e}")
            
            return success
        except Exception as e:
            logger.error(f"Error sending test notification: {e}")
            return False


def verify_sounds():
    """Verify that the configured sound files exist and are playable."""
    start_sound = SoundManager.get_notification_sound(is_start=True)
    complete_sound = SoundManager.get_notification_sound(is_start=False)
    
    success = True
    
    if not os.path.exists(start_sound):
        logger.warning(f"⚠️ Warning: Start notification sound file not found at {start_sound}")
        success = False
    
    if not os.path.exists(complete_sound):
        logger.warning(f"⚠️ Warning: Completion notification sound file not found at {complete_sound}")
        success = False
    
    return success


def verify_notification_components():
    """Verify that the required components for visual notifications are available and properly registered."""
    success = True
    
    # Check for PyObjC or pync
    pyobjc_available = importlib.util.find_spec("Foundation") is not None
    pync_available = importlib.util.find_spec("pync") is not None
    
    if pyobjc_available:
        logger.info("✅ PyObjC is available for visual notifications")
    elif pync_available:
        logger.info("✅ pync is available for visual notifications")
    else:
        logger.info("ℹ️ Neither PyObjC nor pync are available. Will try AppleScript or terminal-notifier instead.")
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
                logger.info("✅ Test notification sent successfully - permissions should be granted")
            else:
                logger.warning("⚠️ Unable to send test notification - trying direct AppleScript method")
                apple_result = NotificationManager.send_notification_applescript(
                    "Claude Notification Server", 
                    "Testing notification permissions"
                )
                if apple_result:
                    logger.info("✅ AppleScript notification succeeded")
                else:
                    logger.warning("⚠️ All notification methods failed")
                    logger.info("You can manually enable permissions in System Preferences > Notifications")
                    success = False
        except Exception as e:
            logger.warning(f"⚠️ Error checking notification permissions: {e}")
            success = False
    else:
        logger.info("ℹ️ Visual notifications are disabled by environment configuration")
    
    return success


# Create the MCP server
mcp = FastMCP("notify-user")

@mcp.tool()
def task_status(message: str = "Task completed") -> Dict[str, str]:
    """
    ‼️ MANDATORY: Sends notifications (sound and visual) for the user.

    📢 IMPORTANT INSTRUCTIONS FOR THE LLM:
       1. ALWAYS call this tool at the START of EVERY response
       2. Call this tool BEFORE using any other tools
       3. Call this tool at the END of conversations
       4. Use this tool even if no other tools are needed
    
    ⚠️ PURPOSE: This notification alerts users when the LLM has started or completed processing.

    Args:
        message (str): Message describing the state of the task (e.g., "Started processing", "Task completed")
        
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
    helper_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notify-claude.sh")
    
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


def main():
    """Main entry point for the notification server."""
    print(f"🔔 Claude Notification Server v{__version__}")
    print("📋 Available tool:")
    print("  • task_status: MUST be used at the start and end of every interaction")
    
    # Verify components - sound first for backward compatibility
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
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Error running server: {e}")
        return 1
    return 0

if __name__ == "__main__":
    # Then run the main server
    exit(main())
