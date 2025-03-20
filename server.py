#!/usr/bin/env python3
"""
Entry point for Claude Notifications MCP Server.
"""

import logging
import sys

from notifications.server import NotificationServer, main

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("claude-notifications")

# Create a server object for fastmcp to find
server = NotificationServer()

if __name__ == "__main__":
    sys.exit(main())
