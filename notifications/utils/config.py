"""
Configuration constants and helpers for Claude Notifications MCP Server.
"""

import os
import logging

logger = logging.getLogger("claude-notifications")

# Environment variable names
ENV_START_SOUND = "CLAUDE_START_SOUND"
ENV_COMPLETE_SOUND = "CLAUDE_COMPLETE_SOUND"
ENV_VISUAL_NOTIFICATIONS = "CLAUDE_VISUAL_NOTIFICATIONS"
ENV_NOTIFICATION_ICON = "CLAUDE_NOTIFICATION_ICON"

# Default system sounds
DEFAULT_START_SOUND = "Glass.aiff"
DEFAULT_COMPLETE_SOUND = "Hero.aiff"
SYSTEM_SOUNDS_DIR = "/System/Library/Sounds/"

# Default icon paths
def get_project_root():
    """Get the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOCAL_ICON_PATH = os.path.join(get_project_root(), "claude-ai-icon.png")
APP_ICON_PATH = "/Applications/Claude.app/Contents/Resources/AppIcon.icns"

def get_env_bool(env_var: str, default: bool = True) -> bool:
    """
    Get a boolean value from an environment variable.
    
    Args:
        env_var: Environment variable name
        default: Default value if environment variable is not set
        
    Returns:
        Boolean value
    """
    value = os.environ.get(env_var, str(default)).lower()
    return value in ("true", "1", "yes", "y", "on")

def get_env_path(env_var: str, default_path: str = None) -> str:
    """
    Get a file path from an environment variable, checking if it exists.
    
    Args:
        env_var: Environment variable name
        default_path: Default path to use if environment variable is not set
        
    Returns:
        File path if it exists, otherwise None
    """
    path = os.environ.get(env_var)
    if path and os.path.exists(path):
        logger.info(f"Using path from {env_var}: {path}")
        return path
    
    if default_path and os.path.exists(default_path):
        logger.info(f"Using default path: {default_path}")
        return default_path
    
    return None
