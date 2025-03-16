#!/usr/bin/env python3

import os
import subprocess
import logging
from typing import Dict, Optional
from fastmcp import FastMCP

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("claude-notifications")

# Version
__version__ = "1.0.0"

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
            result = subprocess.run(
                ["afplay", sound_file],
                check=True,
                capture_output=True
            )
            logger.info(f"Sound played successfully")
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

# Create the MCP server
mcp = FastMCP("notify-user")

@mcp.tool()
def task_status(message: str = "Task completed") -> Dict[str, str]:
    """
    ‼️ MANDATORY: Plays a notification sound for the user.

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
    sound_file = SoundManager.get_notification_sound(is_start=is_start)
    success = SoundManager.play_sound(sound_file)
    
    return {
        "status": "success" if success else "error",
        "message": message,
        "sound": sound_file
    }

def main():
    """Main entry point for the notification server."""
    print(f"🔔 Claude Notification Server v{__version__}")
    print("📋 Available tool:")
    print("  • task_status: MUST be used at the start and end of every interaction")
    
    if verify_sounds():
        print("✅ All sound files verified")
    else:
        print("⚠️ Some sound files could not be found. Check configurations.")
    
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
