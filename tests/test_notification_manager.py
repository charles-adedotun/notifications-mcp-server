#!/usr/bin/env python3

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, call, patch

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

    # ------------------------------------------------------------------
    # are_visual_notifications_enabled
    # ------------------------------------------------------------------

    def test_are_visual_notifications_enabled_default(self):
        """Test that visual notifications are enabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(NotificationManager.are_visual_notifications_enabled())

    def test_are_visual_notifications_enabled_false(self):
        """Test that visual notifications can be disabled via environment variables."""
        for value in ["false", "0", "no", "n", "off"]:
            with patch.dict(os.environ, {NotificationManager.ENV_VISUAL_NOTIFICATIONS: value}):
                self.assertFalse(NotificationManager.are_visual_notifications_enabled())

    def test_are_visual_notifications_enabled_true(self):
        """Test that visual notifications can be enabled via environment variables."""
        for value in ["true", "1", "yes", "y", "on"]:
            with patch.dict(os.environ, {NotificationManager.ENV_VISUAL_NOTIFICATIONS: value}):
                self.assertTrue(NotificationManager.are_visual_notifications_enabled())

    # ------------------------------------------------------------------
    # get_notification_icon
    # ------------------------------------------------------------------

    def test_get_notification_icon_custom(self):
        """Test that custom icon path is used when environment variable is set."""
        env_var = NotificationManager.ENV_NOTIFICATION_ICON
        with patch.dict(os.environ, {env_var: self.temp_file.name}):
            icon_path = NotificationManager.get_notification_icon()
            self.assertEqual(icon_path, self.temp_file.name)

    @patch('os.path.exists')
    def test_get_notification_icon_default(self, mock_exists):
        """Test that default Claude icon is used when available."""
        def side_effect(path):
            return path == NotificationManager.LOCAL_ICON_PATH
        mock_exists.side_effect = side_effect

        with patch.dict(os.environ, {}, clear=True):
            icon_path = NotificationManager.get_notification_icon()
            self.assertEqual(icon_path, NotificationManager.LOCAL_ICON_PATH)

    @patch('os.path.exists')
    def test_get_notification_icon_none(self, mock_exists):
        """Test that None is returned when no icon is available."""
        mock_exists.return_value = False

        with patch.dict(os.environ, {}, clear=True):
            icon_path = NotificationManager.get_notification_icon()
            self.assertIsNone(icon_path)

    # ------------------------------------------------------------------
    # send_notification_applescript — mocks subprocess.run at the boundary
    # ------------------------------------------------------------------

    @patch('notifications.core.notification_manager.subprocess.run')
    def test_send_notification_applescript_success(self, mock_run):
        """AppleScript method calls osascript and returns True on success."""
        mock_run.return_value = MagicMock(returncode=0, stdout=b'', stderr=b'')

        result = NotificationManager.send_notification_applescript(
            title="Test Title",
            message="Test Message"
        )

        self.assertTrue(result)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        cmd = args[0]
        self.assertEqual(cmd[0], "osascript")
        self.assertIn("Test Title", cmd[2])
        self.assertIn("Test Message", cmd[2])

    @patch('notifications.core.notification_manager.subprocess.run')
    def test_send_notification_applescript_failure(self, mock_run):
        """AppleScript method returns False when osascript exits non-zero."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["osascript"], stderr=b"error"
        )

        result = NotificationManager.send_notification_applescript(
            title="Title",
            message="Message"
        )

        self.assertFalse(result)

    @patch('notifications.core.notification_manager.subprocess.run')
    def test_send_notification_applescript_timeout(self, mock_run):
        """AppleScript method returns False when osascript times out."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["osascript"], timeout=5)

        result = NotificationManager.send_notification_applescript(
            title="Title",
            message="Message"
        )

        self.assertFalse(result)

    # ------------------------------------------------------------------
    # send_notification_terminal_notifier — mocks subprocess.run at the boundary
    # ------------------------------------------------------------------

    @patch('notifications.core.notification_manager.subprocess.run')
    def test_send_notification_terminal_notifier_success(self, mock_run):
        """terminal-notifier method calls terminal-notifier binary and returns True."""
        # First call is `which terminal-notifier` (returns 0), second is the actual send
        which_result = MagicMock(returncode=0, stdout=b'/usr/local/bin/terminal-notifier')
        notify_result = MagicMock(returncode=0, stdout=b'', stderr=b'')
        mock_run.side_effect = [which_result, notify_result]

        result = NotificationManager.send_notification_terminal_notifier(
            title="Test Title",
            message="Test Message"
        )

        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)
        # Second call must invoke terminal-notifier
        second_call_cmd = mock_run.call_args_list[1][0][0]
        self.assertEqual(second_call_cmd[0], "terminal-notifier")
        self.assertIn("Test Title", second_call_cmd)
        self.assertIn("Test Message", second_call_cmd)

    @patch('notifications.core.notification_manager.subprocess.run')
    def test_send_notification_terminal_notifier_not_installed(self, mock_run):
        """`which` returning non-zero means terminal-notifier is absent; returns False."""
        mock_run.return_value = MagicMock(returncode=1, stdout=b'')

        result = NotificationManager.send_notification_terminal_notifier(
            title="Title",
            message="Message"
        )

        self.assertFalse(result)
        # Should only have called `which`, not terminal-notifier itself
        self.assertEqual(mock_run.call_count, 1)
        self.assertIn("which", mock_run.call_args_list[0][0][0])

    @patch('notifications.core.notification_manager.subprocess.run')
    def test_send_notification_terminal_notifier_failure(self, mock_run):
        """terminal-notifier CalledProcessError returns False."""
        import subprocess
        which_result = MagicMock(returncode=0, stdout=b'/usr/local/bin/terminal-notifier')
        mock_run.side_effect = [
            which_result,
            subprocess.CalledProcessError(returncode=1, cmd=["terminal-notifier"], stderr=b"err")
        ]

        result = NotificationManager.send_notification_terminal_notifier(
            title="Title",
            message="Message"
        )

        self.assertFalse(result)

    # ------------------------------------------------------------------
    # send_notification_with_pyobjc — mocks the Foundation import boundary
    # ------------------------------------------------------------------

    @unittest.skipIf(sys.platform != "darwin", "PyObjC only available on macOS")
    @patch('notifications.core.notification_manager.subprocess.run')
    def test_send_notification_with_pyobjc(self, mock_run):
        """
        PyObjC path inside send_notification is exercised when applescript and
        terminal-notifier both fail and Foundation can be imported.

        We mock:
          - subprocess.run so applescript + terminal-notifier fail
          - The Foundation module so PyObjC calls succeed without a real macOS framework
        """
        import subprocess

        # Make both subprocess-based methods fail
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["osascript"], stderr=b""
        )

        # Build a minimal mock for the Foundation classes
        mock_notification = MagicMock()
        mock_center = MagicMock()
        mock_center.defaultUserNotificationCenter.return_value = mock_center

        mock_foundation = MagicMock()
        mock_foundation.NSUserNotification.alloc.return_value.init.return_value = mock_notification
        mock_foundation.NSUserNotificationCenter.defaultUserNotificationCenter.return_value = (
            mock_center
        )
        mock_foundation.NSImage = MagicMock()

        with patch.dict('sys.modules', {'Foundation': mock_foundation}):
            result = NotificationManager.send_notification(
                title="Test Title",
                message="Test Message",
                icon_path=None
            )

        # The PyObjC path should have set success=True
        self.assertTrue(result)
        # Verify NSUserNotification was actually created
        mock_foundation.NSUserNotification.alloc.assert_called_once()

    def test_send_notification_with_pyobjc_import_error_falls_through(self):
        """
        When Foundation is not importable, the PyObjC block is skipped and execution
        continues to the pync fallback (or returns False if pync also absent).
        The real fallback logic runs — this is not a mock-the-unit test.
        """
        import subprocess

        # Make subprocess calls fail so applescript + terminal-notifier fail too
        with patch('notifications.core.notification_manager.subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1, cmd=["osascript"], stderr=b""
            )
            # Foundation unavailable AND pync unavailable
            with patch.dict('sys.modules', {'Foundation': None, 'pync': None}):
                result = NotificationManager.send_notification(
                    title="Title",
                    message="Message"
                )

        # All four paths failed → False
        self.assertFalse(result)

    # ------------------------------------------------------------------
    # send_notification_with_pync — mocks pync.notify at the boundary
    # ------------------------------------------------------------------

    def test_send_notification_with_pync(self):
        """
        pync fallback inside send_notification is exercised when applescript,
        terminal-notifier, and PyObjC all fail but pync is importable.

        Mocks at system boundaries:
          - subprocess.run  → makes applescript + terminal-notifier fail
          - Foundation      → ImportError so PyObjC skipped
          - pync module     → real pync.notify replaced with a MagicMock
        """
        import subprocess

        mock_pync = MagicMock()
        # pync.notify returns None on success (library convention)
        mock_pync.notify.return_value = None

        with patch('notifications.core.notification_manager.subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1, cmd=["osascript"], stderr=b""
            )
            with patch.dict('sys.modules', {'Foundation': None, 'pync': mock_pync}):
                result = NotificationManager.send_notification(
                    title="Test Title",
                    message="Test Message",
                    icon_path=self.temp_file.name
                )

        self.assertTrue(result)
        # Verify pync.notify was actually called with the right arguments
        mock_pync.notify.assert_called_once_with(
            "Test Message",
            title="Test Title",
            contentImage=self.temp_file.name,
            appIcon=self.temp_file.name
        )

    def test_send_notification_with_pync_no_icon(self):
        """pync fallback is called without icon kwargs when icon_path is None."""
        import subprocess

        mock_pync = MagicMock()
        mock_pync.notify.return_value = None

        with patch('notifications.core.notification_manager.subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1, cmd=["osascript"], stderr=b""
            )
            with patch.dict('sys.modules', {'Foundation': None, 'pync': mock_pync}):
                result = NotificationManager.send_notification(
                    title="Title",
                    message="Message",
                    icon_path=None
                )

        self.assertTrue(result)
        mock_pync.notify.assert_called_once_with("Message", title="Title")

    # ------------------------------------------------------------------
    # Fallback chain ordering
    # ------------------------------------------------------------------

    @patch('notifications.core.notification_manager.subprocess.run')
    def test_fallback_chain_applescript_first(self, mock_run):
        """AppleScript is attempted before terminal-notifier."""
        # AppleScript succeeds → terminal-notifier should not be called
        mock_run.return_value = MagicMock(returncode=0, stdout=b'', stderr=b'')

        result = NotificationManager.send_notification(
            title="Title",
            message="Message"
        )

        self.assertTrue(result)
        # Only one subprocess.run call: the osascript one
        self.assertEqual(mock_run.call_count, 1)
        self.assertIn("osascript", mock_run.call_args_list[0][0][0])

    @patch('notifications.core.notification_manager.subprocess.run')
    def test_fallback_chain_terminal_notifier_second(self, mock_run):
        """terminal-notifier is tried after AppleScript fails."""
        import subprocess

        # First call is osascript (fail), then `which terminal-notifier` (found),
        # then terminal-notifier (success)
        mock_run.side_effect = [
            subprocess.CalledProcessError(returncode=1, cmd=["osascript"], stderr=b""),
            MagicMock(returncode=0, stdout=b'/usr/local/bin/terminal-notifier'),  # which
            MagicMock(returncode=0, stdout=b'', stderr=b''),                       # terminal-notifier
        ]

        result = NotificationManager.send_notification(
            title="Title",
            message="Message"
        )

        self.assertTrue(result)
        cmds = [mock_run.call_args_list[i][0][0][0] for i in range(mock_run.call_count)]
        self.assertIn("osascript", cmds)
        self.assertIn("which", cmds)
        self.assertIn("terminal-notifier", cmds)

    def test_fallback_chain_all_fail_returns_false(self):
        """send_notification returns False when every backend fails."""
        import subprocess

        with patch('notifications.core.notification_manager.subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1, cmd=["osascript"], stderr=b""
            )
            with patch.dict('sys.modules', {'Foundation': None, 'pync': None}):
                result = NotificationManager.send_notification(
                    title="Title",
                    message="Message"
                )

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
