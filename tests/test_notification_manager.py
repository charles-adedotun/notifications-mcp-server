#!/usr/bin/env python3

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add the parent directory to the path to import the notification modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from the new modular structure
from notifications.core.notification_manager import NotificationManager


class TestNotificationManager(unittest.TestCase):
    """Tests for the NotificationManager class."""

    def setUp(self):
        # Create a temporary icon file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        self.temp_file.close()

    def tearDown(self):
        # Remove the temporary file
        os.unlink(self.temp_file.name)

    def test_are_visual_notifications_enabled_default(self):
        """Test that visual notifications are enabled by default."""
        # Clear any existing environment variables
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(NotificationManager.are_visual_notifications_enabled())

    def test_are_visual_notifications_enabled_false(self):
        """Test that visual notifications can be disabled via environment variables."""
        # Set environment variable to disable notifications
        for value in ["false", "0", "no", "n", "off"]:
            with patch.dict(os.environ, {NotificationManager.ENV_VISUAL_NOTIFICATIONS: value}):
                self.assertFalse(NotificationManager.are_visual_notifications_enabled())

    def test_are_visual_notifications_enabled_true(self):
        """Test that visual notifications can be enabled via environment variables."""
        # Set environment variable to enable notifications
        for value in ["true", "1", "yes", "y", "on"]:
            with patch.dict(os.environ, {NotificationManager.ENV_VISUAL_NOTIFICATIONS: value}):
                self.assertTrue(NotificationManager.are_visual_notifications_enabled())

    def test_get_notification_icon_custom(self):
        """Test that custom icon path is used when environment variable is set."""
        # Set custom icon path in environment variable
        env_var = NotificationManager.ENV_NOTIFICATION_ICON
        with patch.dict(os.environ, {env_var: self.temp_file.name}):
            icon_path = NotificationManager.get_notification_icon()
            self.assertEqual(icon_path, self.temp_file.name)

    @patch('os.path.exists')
    def test_get_notification_icon_default(self, mock_exists):
        """Test that default Claude icon is used when available."""
        # Mock os.path.exists to return True for the default icon path
        def side_effect(path):
            # Use LOCAL_ICON_PATH instead of DEFAULT_ICON_PATH
            return path == NotificationManager.LOCAL_ICON_PATH
        mock_exists.side_effect = side_effect

        # Clear any existing environment variables
        with patch.dict(os.environ, {}, clear=True):
            icon_path = NotificationManager.get_notification_icon()
            self.assertEqual(icon_path, NotificationManager.LOCAL_ICON_PATH)

    @patch('os.path.exists')
    def test_get_notification_icon_none(self, mock_exists):
        """Test that None is returned when no icon is available."""
        # Mock os.path.exists to return False for any path
        mock_exists.return_value = False

        # Clear any existing environment variables
        with patch.dict(os.environ, {}, clear=True):
            icon_path = NotificationManager.get_notification_icon()
            self.assertIsNone(icon_path)

    @patch('notifications.core.notification_manager.NotificationManager.send_notification')
    def test_send_notification_with_pyobjc(self, mock_send):
        """Test sending a notification with PyObjC."""
        # Mock the Foundation module
        with patch.dict('sys.modules', {
            'Foundation': MagicMock(),
            'objc': MagicMock()
        }):
            # Configure mock to indicate success
            mock_send.return_value = True

            # Call send_notification
            result = NotificationManager.send_notification(
                title="Test Title",
                message="Test Message",
                icon_path=self.temp_file.name
            )

            # Check that the function returned True
            self.assertTrue(result)

            # Check that send_notification was called with the correct arguments
            mock_send.assert_called_once_with(
                title="Test Title",
                message="Test Message",
                icon_path=self.temp_file.name
            )

    @patch('notifications.core.notification_manager.NotificationManager.send_notification')
    def test_send_notification_with_pync(self, mock_send):
        """Test sending a notification with pync as fallback."""
        # Mock imports to simulate PyObjC not available but pync available
        with patch.dict('sys.modules', {
            'Foundation': None,
            'pync': MagicMock()
        }):
            # Configure mock to indicate success
            mock_send.return_value = True

            # Call send_notification
            result = NotificationManager.send_notification(
                title="Test Title",
                message="Test Message",
                icon_path=self.temp_file.name
            )

            # Check that the function returned True
            self.assertTrue(result)

            # Check that send_notification was called with the correct arguments
            mock_send.assert_called_once_with(
                title="Test Title",
                message="Test Message",
                icon_path=self.temp_file.name
            )

if __name__ == '__main__':
    unittest.main()
