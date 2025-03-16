#!/usr/bin/env python3

import os
import unittest
from unittest.mock import patch, MagicMock
import sys
import tempfile
import subprocess

# Add the parent directory to the path to import the notification_server module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from notification_server import SoundManager

class TestSoundManager(unittest.TestCase):
    """Tests for the SoundManager class."""
    
    def setUp(self):
        # Create a temporary sound file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.aiff', delete=False)
        self.temp_file.close()
    
    def tearDown(self):
        # Remove the temporary file
        os.unlink(self.temp_file.name)
    
    def test_get_notification_sound_default(self):
        """Test that default sounds are returned when no environment variables are set."""
        # Clear any existing environment variables
        with patch.dict(os.environ, {}, clear=True):
            start_sound = SoundManager.get_notification_sound(is_start=True)
            complete_sound = SoundManager.get_notification_sound(is_start=False)
            
            # Check that default paths are returned
            self.assertTrue(start_sound.endswith(SoundManager.DEFAULT_START_SOUND))
            self.assertTrue(complete_sound.endswith(SoundManager.DEFAULT_COMPLETE_SOUND))
    
    def test_get_notification_sound_custom(self):
        """Test that custom sound paths are used when environment variables are set."""
        # Set custom sound paths in environment variables
        with patch.dict(os.environ, {
            SoundManager.ENV_START_SOUND: self.temp_file.name,
            SoundManager.ENV_COMPLETE_SOUND: self.temp_file.name
        }):
            start_sound = SoundManager.get_notification_sound(is_start=True)
            complete_sound = SoundManager.get_notification_sound(is_start=False)
            
            # Check that custom paths are returned
            self.assertEqual(start_sound, self.temp_file.name)
            self.assertEqual(complete_sound, self.temp_file.name)
    
    def test_get_notification_sound_legacy(self):
        """Test that legacy environment variable takes precedence."""
        # Set legacy environment variable
        with patch.dict(os.environ, {
            SoundManager.ENV_NOTIFICATION_SOUND: self.temp_file.name,
            SoundManager.ENV_START_SOUND: "/another/path.aiff",
            SoundManager.ENV_COMPLETE_SOUND: "/another/path.aiff"
        }):
            start_sound = SoundManager.get_notification_sound(is_start=True)
            complete_sound = SoundManager.get_notification_sound(is_start=False)
            
            # Check that legacy path is returned for both
            self.assertEqual(start_sound, self.temp_file.name)
            self.assertEqual(complete_sound, self.temp_file.name)
    
    @patch('subprocess.run')
    def test_play_sound_success(self, mock_run):
        """Test successful sound playback."""
        # Configure mock to indicate success
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Call play_sound with temporary file
        result = SoundManager.play_sound(self.temp_file.name)
        
        # Check that subprocess.run was called correctly and returned True
        mock_run.assert_called_once()
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_play_sound_failure(self, mock_run):
        """Test handling of playback failures."""
        # Configure mock to raise CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(1, ['afplay'], stderr=b'Error')
        
        # Call play_sound with temporary file
        result = SoundManager.play_sound(self.temp_file.name)
        
        # Check that function handled the error and returned False
        self.assertFalse(result)
    
    def test_play_sound_missing_file(self):
        """Test handling of missing sound files."""
        # Call play_sound with non-existent file
        result = SoundManager.play_sound("/non/existent/file.aiff")
        
        # Check that function detected missing file and returned False
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
