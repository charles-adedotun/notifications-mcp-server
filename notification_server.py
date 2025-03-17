#!/usr/bin/env python3

import os
import subprocess
import logging
from typing import Dict, Optional, Tuple
from fastmcp import FastMCP

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("claude-notifications")

# Version
__version__ = "1.1.0"

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
    Manages macOS visual notifications using PyObjC.
    """
    
    # Environment variable names for enabling/disabling visual notifications
    ENV_VISUAL_NOTIFICATIONS = "CLAUDE_VISUAL_NOTIFICATIONS"
    ENV_NOTIFICATION_ICON = "CLAUDE_NOTIFICATION_ICON"
    
    # Default icon path (Claude icon if available, otherwise None)
    DEFAULT_ICON_PATH = "/Applications/Claude.app/Contents/Resources/AppIcon.icns"
    
    @classmethod
    def are_visual_notifications_enabled(cls) -> bool:
        """Check if visual notifications are enabled."""
        env_value = os.environ.get(cls.ENV_VISUAL_NOTIFICATIONS, "true").lower()
        return env_value in ("true", "1", "yes", "y", "on")
    
    @classmethod
    def get_notification_icon(cls) -> Optional[str]:
        """Get the path to the icon for notifications."""
        # Check environment variable first
        custom_icon = os.environ.get(cls.ENV_NOTIFICATION_ICON)
        if custom_icon and os.path.exists(custom_icon):
            logger.info(f"Using custom notification icon: {custom_icon}")
            return custom_icon
        
        # Use default Claude icon if available
        if os.path.exists(cls.DEFAULT_ICON_PATH):
            logger.info(f"Using default Claude icon: {cls.DEFAULT_ICON_PATH}")
            return cls.DEFAULT_ICON_PATH
            
        return None
    
    @staticmethod
    def send_notification(title: str, message: str, icon_path: Optional[str] = None) -> bool:
        """
        Send a macOS notification using PyObjC.
        
        Args:
            title: The notification title
            message: The notification message
            icon_path: Path to the icon file (optional)
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            # Try importing Foundation and required classes
            try:
                from Foundation import NSUserNotification, NSUserNotificationCenter, NSImage
                use_pyobjc = True
            except ImportError:
                logger.info("PyObjC not available, trying pync as fallback")
                use_pyobjc = False
                try:
                    import pync
                except ImportError:
                    logger.error("Neither PyObjC nor pync are available. Please install one of them: "
                                 "pip install pyobjc or pip install pync")
                    return False
            
            if use_pyobjc:
                # Send notification using PyObjC
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
                logger.info(f"Sent notification using PyObjC: {title} - {message}")
            else:
                # Send notification using pync as fallback
                if icon_path:
                    pync.notify(message, title=title, contentImage=icon_path, appIcon=icon_path)
                else:
                    pync.notify(message, title=title)
                logger.info(f"Sent notification using pync: {title} - {message}")
            
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    @classmethod
    def check_notification_permission(cls) -> bool:
        """
        Check if the application has permission to send notifications.
        
        Returns:
            True if permission is granted, False otherwise
        """
        try:
            from Foundation import UNUserNotificationCenter
            import objc
            
            UNUserNotificationCenter = objc.lookUpClass('UNUserNotificationCenter')
            center = UNUserNotificationCenter.currentNotificationCenter()
            
            # Create a semaphore to wait for the async callback
            from threading import Semaphore
            semaphore = Semaphore(0)
            
            result = {}
            def completion_handler(settings):
                result['authorized'] = settings.authorizationStatus() == 2  # 2 = Authorized
                semaphore.release()
            
            center.getNotificationSettingsWithCompletionHandler_(completion_handler)
            semaphore.acquire()
            
            return result['authorized']
        except Exception as e:
            logger.error(f"Error checking notification permission: {e}")
            # If we can't check permissions, assume we can send notifications
            return True
    
    @classmethod
    def request_notification_permission(cls) -> bool:
        """
        Request permission to send notifications if not already granted.
        
        Returns:
            True if permission is granted, False otherwise
        """
        # First check if we already have permission
        if cls.check_notification_permission():
            logger.info("Notification permission already granted")
            return True
            
        try:
            from Foundation import UNUserNotificationCenter, UNAuthorizationOptions
            import objc
            
            UNUserNotificationCenter = objc.lookUpClass('UNUserNotificationCenter')
            center = UNUserNotificationCenter.currentNotificationCenter()
            
            # Create a semaphore to wait for the async callback
            from threading import Semaphore
            semaphore = Semaphore(0)
            
            result = {}
            def completion_handler(granted, error):
                result['granted'] = granted
                result['error'] = error
                semaphore.release()
            
            # Request alert, sound, and badge permissions
            options = UNAuthorizationOptions.Alert | UNAuthorizationOptions.Sound | UNAuthorizationOptions.Badge
            center.requestAuthorizationWithOptions_completionHandler_(options, completion_handler)
            semaphore.acquire()
            
            if result.get('granted', False):
                logger.info("Notification permission granted")
                return True
            else:
                logger.warning(f"Notification permission denied: {result.get('error')}")
                return False
        except Exception as e:
            logger.error(f"Error requesting notification permission: {e}")
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
    """Verify that the required components for visual notifications are available."""
    success = True
    
    # Check for PyObjC or pync
    try:
        from Foundation import NSUserNotification
        logger.info("✅ PyObjC is available for visual notifications")
    except ImportError:
        try:
            import pync
            logger.info("✅ pync is available for visual notifications")
        except ImportError:
            logger.warning("⚠️ Neither PyObjC nor pync are available. Visual notifications will be disabled.")
            logger.warning("To enable visual notifications, install one of them: pip install pyobjc or pip install pync")
            success = False
            
    # Check notification icon
    icon_path = NotificationManager.get_notification_icon()
    if icon_path:
        logger.info(f"✅ Notification icon found at {icon_path}")
    else:
        logger.info("ℹ️ No notification icon found. Notifications will be sent without an icon.")
        
    # Check notification permissions
    if NotificationManager.are_visual_notifications_enabled():
        if success:  # Only check permissions if we have the required components
            try:
                if NotificationManager.check_notification_permission():
                    logger.info("✅ Notification permissions are granted")
                else:
                    logger.warning("⚠️ Notification permissions are not granted. "
                                   "Attempting to request permissions...")
                    if NotificationManager.request_notification_permission():
                        logger.info("✅ Notification permissions successfully granted")
                    else:
                        logger.warning("⚠️ Notification permissions denied. Visual notifications may not work.")
                        logger.warning("You can enable permissions in System Preferences > Notifications")
            except Exception as e:
                logger.warning(f"⚠️ Error checking notification permissions: {e}")
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
    
    # Send sound notification
    sound_file = SoundManager.get_notification_sound(is_start=is_start)
    sound_success = SoundManager.play_sound(sound_file)
    
    # Send visual notification if enabled
    visual_success = False
    if NotificationManager.are_visual_notifications_enabled():
        # Determine notification title and message
        if is_start:
            title = "Claude is Processing"
            notification_message = "Claude has started processing your request"
        else:
            title = "Claude Response Ready"
            notification_message = "Claude has completed your request"
        
        # Get icon path
        icon_path = NotificationManager.get_notification_icon()
        
        # Send notification
        visual_success = NotificationManager.send_notification(
            title=title,
            message=notification_message,
            icon_path=icon_path
        )
    
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
    
    # Verify components
    sound_success = verify_sounds()
    visual_success = verify_notification_components()
    
    if sound_success:
        print("✅ All sound files verified")
    else:
        print("⚠️ Some sound files could not be found. Check configurations.")
        
    if NotificationManager.are_visual_notifications_enabled():
        if visual_success:
            print("✅ Visual notification components verified")
        else:
            print("⚠️ Visual notifications may not work correctly. See warnings above.")
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
    exit(main())