"""
Test the modular structure of the Claude Notifications MCP Server.
"""

import os
import sys
import unittest
import importlib

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestModularStructure(unittest.TestCase):
    """Test the modular structure of the Claude Notifications MCP Server."""
    
    def test_package_imports(self):
        """Test that all package modules can be imported."""
        # Test main package
        import notifications
        self.assertIsNotNone(notifications.__version__)
        
        # Test core modules
        from notifications.core import sound_manager, notification_manager
        self.assertIsNotNone(sound_manager.SoundManager)
        self.assertIsNotNone(notification_manager.NotificationManager)
        
        # Test platform modules
        from notifications.platform.macos import sound, notification
        self.assertIsNotNone(sound.play_sound_afplay)
        self.assertIsNotNone(notification.send_notification_applescript)
        
        # Test utility modules
        from notifications.utils import config, logging
        self.assertIsNotNone(config.ENV_START_SOUND)
        self.assertIsNotNone(logging.setup_logging)
        
        # Test server module
        from notifications import server
        self.assertIsNotNone(server.NotificationServer)
    
    def test_sound_manager_functionality(self):
        """Test that SoundManager functionality works in the new structure."""
        from notifications.core.sound_manager import SoundManager
        
        # Test that we can get notification sounds
        start_sound = SoundManager.get_notification_sound(is_start=True)
        complete_sound = SoundManager.get_notification_sound(is_start=False)
        
        self.assertIsNotNone(start_sound)
        self.assertIsNotNone(complete_sound)
        self.assertTrue(isinstance(start_sound, str))
        self.assertTrue(isinstance(complete_sound, str))
    
    def test_notification_manager_functionality(self):
        """Test that NotificationManager functionality works in the new structure."""
        from notifications.core.notification_manager import NotificationManager
        
        # Test that we can check if visual notifications are enabled
        enabled = NotificationManager.are_visual_notifications_enabled()
        self.assertIsNotNone(enabled)
        self.assertTrue(isinstance(enabled, bool))
        
        # Test that we can get the notification icon
        icon = NotificationManager.get_notification_icon()
        self.assertTrue(icon is None or isinstance(icon, str))

if __name__ == '__main__':
    unittest.main()
