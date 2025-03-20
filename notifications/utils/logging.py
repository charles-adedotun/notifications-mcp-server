"""
Logging setup for Claude Notifications MCP Server.
"""

import logging
import sys


def setup_logging(level=logging.INFO):
    """
    Set up logging for the notification server.

    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )

    # Create logger
    logger = logging.getLogger("claude-notifications")
    logger.setLevel(level)

    # Ensure we don't add duplicate handlers
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(level)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger
