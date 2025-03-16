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
__version__ = "0.1.1"

class SoundManager:
    """
    Manages sound playback for notifications using macOS system sounds.
    """
    
    # Default system sounds directory on macOS
    SYSTEM_SOUNDS_DIR = "/System/Library/Sounds/"
    
    # Default sounds (will be used if no custom sounds are specified)
    DEFAULT_TOOL_PERMISSION_SOUND = "Funk.aiff"
    DEFAULT_TASK_COMPLETED_SOUND = "Glass.aiff"
    
    # Environment variable names for custom sounds
    ENV_TOOL_PERMISSION_SOUND = "CLAUDE_TOOL_PERMISSION_SOUND"
    ENV_COMPLETED_SOUND = "CLAUDE_COMPLETED_SOUND"
    
    @classmethod
    def get_task_completed_sound(cls) -> str:
        """Get the path to the sound file for task completed notifications."""
        custom_sound = os.environ.get(cls.ENV_COMPLETED_SOUND)
        if custom_sound and os.path.exists(custom_sound):
            logger.info(f"Using custom task completed sound: {custom_sound}")
            return custom_sound
            
        sound_file = os.path.join(cls.SYSTEM_SOUNDS_DIR, cls.DEFAULT_TASK_COMPLETED_SOUND)
        logger.info(f"Using default task completed sound: {sound_file}")
        return sound_file
    
    @classmethod
    def get_tool_permission_sound(cls) -> str:
        """Get the path to the sound file for tool permission notifications."""
        custom_sound = os.environ.get(cls.ENV_TOOL_PERMISSION_SOUND)
        if custom_sound and os.path.exists(custom_sound):
            logger.info(f"Using custom tool permission sound: {custom_sound}")
            return custom_sound
            
        sound_file = os.path.join(cls.SYSTEM_SOUNDS_DIR, cls.DEFAULT_TOOL_PERMISSION_SOUND)
        logger.info(f"Using default tool permission sound: {sound_file}")
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
    """Verify that all configured sound files exist and are playable."""
    sounds = {
        "Tool permission": SoundManager.get_tool_permission_sound(),
        "Task completed": SoundManager.get_task_completed_sound()
    }
    
    all_valid = True
    for name, path in sounds.items():
        if not os.path.exists(path):
            logger.warning(f"⚠️ Warning: {name} sound file not found at {path}")
            all_valid = False
    
    return all_valid

# Create the MCP server
mcp = FastMCP("notify-user")

@mcp.tool()
def tool_permission_needed(message: str = "Tool permission required") -> Dict[str, str]:
    """
    ‼️ MANDATORY: Plays notification when tool permission is needed.

    📢 YOU MUST USE THIS TOOL:
       • When attempting to use a tool that requires user approval
       • Before actions that will generate permission popups
       • When accessing external resources requiring authorization
       • ANYTIME you need the user to take an action to grant permissions
    
    ⚠️ CRITICAL: Users need to know when to approve tool access.

    Args:
        message (str): Message describing what permission is needed
        
    Returns:
        dict: Status information about the notification
    """
    logger.info(f"Tool permission needed: {message}")
    sound_file = SoundManager.get_tool_permission_sound()
    success = SoundManager.play_sound(sound_file)
    
    return {
        "status": "success" if success else "error",
        "message": message,
        "sound": sound_file
    }

@mcp.tool()
def task_completed(message: str = "Task completed") -> Dict[str, str]:
    """
    ‼️ MANDATORY: Plays notification when a task is finished.

    📢 YOU MUST USE THIS TOOL:
       • At the END of conversations
       • After completing ANY significant task
       • When finishing data processing or content generation
       • When your final response is ready
    
    ⚠️ CRITICAL: This notification alerts users their request is complete.

    Args:
        message (str): Message describing the completed task
        
    Returns:
        dict: Status information about the notification
    """
    logger.info(f"Task completed: {message}")
    sound_file = SoundManager.get_task_completed_sound()
    success = SoundManager.play_sound(sound_file)
    
    return {
        "status": "success" if success else "error",
        "message": message,
        "sound": sound_file
    }

if __name__ == "__main__":
    print(f"🔔 Claude Notification Server v{__version__}")
    print("📋 Available tools:")
    print("  • tool_permission_needed: MUST use when tool approval is required")
    print("  • task_completed: MUST use when task is finished")
    
    if verify_sounds():
        print("✅ All sound files verified")
    else:
        print("⚠️ Some sound files could not be found. Check configurations.")
    
    mcp.run()
