"""
Notification manager for Claude Notifications MCP Server.
Handles macOS visual notifications using various methods with fallbacks.
"""

import os
import subprocess
import logging
import time
from typing import Optional
import importlib.util

logger = logging.getLogger("claude-notifications")

class NotificationManager:
    """
    Manages macOS visual notifications using PyObjC, pync, AppleScript, or terminal-notifier.
    """
    
    # Environment variable names for enabling/disabling visual notifications
    ENV_VISUAL_NOTIFICATIONS = "CLAUDE_VISUAL_NOTIFICATIONS"
    ENV_NOTIFICATION_ICON = "CLAUDE_NOTIFICATION_ICON"
    
    # Default icon paths
    # Local icon is preferred, then app icon, then None
    LOCAL_ICON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "claude-ai-icon.png")
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
                    title=title,
                    message=message,
                    sound=None  # Don't specify sound to avoid duplicate sounds
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
