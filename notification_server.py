#!/usr/bin/env python3

import os
import subprocess
from typing import Dict, Optional
from fastmcp import FastMCP


class SoundManager:
    """
    Manages sound playback for notifications using macOS system sounds.
    """
    
    # Default system sounds directory on macOS
    SYSTEM_SOUNDS_DIR = "/System/Library/Sounds/"
    
    # Default sounds (will be used if no custom sounds are specified)
    DEFAULT_INPUT_NEEDED_SOUND = "Submarine.aiff"
    DEFAULT_TASK_COMPLETED_SOUND = "Glass.aiff"
    DEFAULT_TOOL_PERMISSION_SOUND = "Funk.aiff"
    
    # Environment variable names for custom sounds
    ENV_INPUT_SOUND = "CLAUDE_INPUT_SOUND"
    ENV_COMPLETED_SOUND = "CLAUDE_COMPLETED_SOUND"
    ENV_TOOL_PERMISSION_SOUND = "CLAUDE_TOOL_PERMISSION_SOUND"
    
    @classmethod
    def get_input_needed_sound(cls) -> str:
        """Get the path to the sound file for input needed notifications."""
        custom_sound = os.environ.get(cls.ENV_INPUT_SOUND)
        if custom_sound and os.path.exists(custom_sound):
            return custom_sound
            
        return os.path.join(cls.SYSTEM_SOUNDS_DIR, cls.DEFAULT_INPUT_NEEDED_SOUND)
    
    @classmethod
    def get_task_completed_sound(cls) -> str:
        """Get the path to the sound file for task completed notifications."""
        custom_sound = os.environ.get(cls.ENV_COMPLETED_SOUND)
        if custom_sound and os.path.exists(custom_sound):
            return custom_sound
            
        return os.path.join(cls.SYSTEM_SOUNDS_DIR, cls.DEFAULT_TASK_COMPLETED_SOUND)
    
    @classmethod
    def get_tool_permission_sound(cls) -> str:
        """Get the path to the sound file for tool permission notifications."""
        custom_sound = os.environ.get(cls.ENV_TOOL_PERMISSION_SOUND)
        if custom_sound and os.path.exists(custom_sound):
            return custom_sound
            
        return os.path.join(cls.SYSTEM_SOUNDS_DIR, cls.DEFAULT_TOOL_PERMISSION_SOUND)
    
    @staticmethod
    def play_sound(sound_file: str) -> None:
        """Play a sound file using macOS afplay command."""
        try:
            subprocess.run(
                ["afplay", sound_file],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error playing sound: {e}")
        except FileNotFoundError:
            print("afplay command not found. Are you running on macOS?")


# Create the MCP server
mcp = FastMCP("notify-user")


@mcp.tool()
def user_input_needed(message: str = "User input required") -> Dict[str, str]:
    """
    ‼️ MANDATORY: Plays notification when user input is needed.

    📢 YOU MUST USE THIS TOOL:
       • At start of EVERY conversation
       • When asking questions or requesting information
       • When user needs to review content or make decisions
    
    ⚠️ CRITICAL: Users rely on these sounds to know when to return to the conversation.

    Args:
        message (str): Message describing what input is needed
        
    Returns:
        dict: Status information about the notification
    """
    sound_file = SoundManager.get_input_needed_sound()
    SoundManager.play_sound(sound_file)
    
    return {"status": "success", "message": message, "sound": sound_file}


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
    sound_file = SoundManager.get_task_completed_sound()
    SoundManager.play_sound(sound_file)
    
    return {"status": "success", "message": message, "sound": sound_file}


@mcp.tool()
def tool_permission_needed(message: str = "Tool permission required") -> Dict[str, str]:
    """
    ‼️ MANDATORY: Plays notification when tool permission is needed.

    📢 YOU MUST USE THIS TOOL:
       • When attempting to use a tool that requires user approval
       • Before actions that will generate permission popups
       • When accessing external resources requiring authorization
    
    ⚠️ CRITICAL: Users need to know when to approve tool access.

    Args:
        message (str): Message describing what permission is needed
        
    Returns:
        dict: Status information about the notification
    """
    sound_file = SoundManager.get_tool_permission_sound()
    SoundManager.play_sound(sound_file)
    
    return {"status": "success", "message": message, "sound": sound_file}


if __name__ == "__main__":
    print("🔔 Claude Notification Server")
    print("📋 Available tools:")
    print("  • user_input_needed: MUST use when user input is needed")
    print("  • task_completed: MUST use when task is finished")
    print("  • tool_permission_needed: MUST use when tool approval is required")
    mcp.run()
