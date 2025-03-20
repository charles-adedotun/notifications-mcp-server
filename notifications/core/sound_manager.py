"""
Sound manager for Claude Notifications MCP Server.
Handles sound playback for notifications using macOS system sounds.
"""

import logging
import os
import subprocess

logger = logging.getLogger("claude-notifications")

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

    @classmethod
    def get_notification_sound(cls, is_start: bool = True) -> str:
        """Get the path to the sound file for notifications.

        Args:
            is_start: True for start sound, False for completion sound
        """
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
