"""
macOS-specific sound functions for Claude Notifications MCP Server.
"""

import os
import subprocess
import logging

logger = logging.getLogger("claude-notifications")

def play_sound_afplay(sound_file: str) -> bool:
    """
    Play a sound file using macOS afplay command.
    
    Args:
        sound_file: Path to the sound file to play
        
    Returns:
        True if sound played successfully, False otherwise
    """
    if not os.path.exists(sound_file):
        logger.error(f"Sound file does not exist: {sound_file}")
        return False
        
    try:
        logger.info(f"Playing sound with afplay: {sound_file}")
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

def get_system_sounds_dir() -> str:
    """
    Get the directory containing macOS system sounds.
    
    Returns:
        Path to the macOS system sounds directory
    """
    return "/System/Library/Sounds/"

def list_available_system_sounds() -> list:
    """
    List all available system sounds on macOS.
    
    Returns:
        List of sound file names (without path)
    """
    sounds_dir = get_system_sounds_dir()
    try:
        return [f for f in os.listdir(sounds_dir) if f.endswith('.aiff')]
    except Exception as e:
        logger.error(f"Error listing system sounds: {e}")
        return []
