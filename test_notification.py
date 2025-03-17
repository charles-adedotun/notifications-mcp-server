#!/usr/bin/env python3
"""
Simple test script to verify macOS notifications are working properly.
This can help diagnose issues with the Claude MCP notification server.
"""

import sys
import subprocess

def test_pyobjc_notification():
    """Test notification using PyObjC."""
    try:
        print("Testing PyObjC notification...")
        
        # Try to import the necessary modules
        import objc
        from Foundation import NSUserNotification, NSUserNotificationCenter
        
        # Create a notification
        notification = NSUserNotification.alloc().init()
        notification.setTitle_("Test Notification")
        notification.setInformativeText_("This is a test notification from the Claude MCP test script")
        
        # Get the notification center and deliver the notification
        center = NSUserNotificationCenter.defaultUserNotificationCenter()
        center.deliverNotification_(notification)
        
        print("PyObjC notification sent successfully!")
        return True
    except ImportError:
        print("PyObjC is not installed. Install it with: pip install pyobjc-core pyobjc-framework-Cocoa")
        return False
    except Exception as e:
        print(f"Error sending PyObjC notification: {e}")
        return False

def test_applescript_notification():
    """Test notification using AppleScript."""
    try:
        print("Testing AppleScript notification...")
        
        # AppleScript to display a notification
        script = '''
        display notification "This is a test notification from AppleScript" with title "Test Notification"
        '''
        
        # Run the AppleScript
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, 
            text=True,
            check=True
        )
        
        print("AppleScript notification sent successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running AppleScript: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error with AppleScript: {e}")
        return False

def test_sound():
    """Test playing a sound using afplay."""
    try:
        print("Testing sound playback...")
        
        # Path to a system sound
        sound_file = "/System/Library/Sounds/Glass.aiff"
        
        # Play the sound
        result = subprocess.run(
            ["afplay", sound_file],
            capture_output=True,
            check=True
        )
        
        print("Sound played successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error playing sound: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error playing sound: {e}")
        return False

def test_terminal_notifier():
    """Test notification using terminal-notifier if installed."""
    try:
        print("Testing terminal-notifier...")
        
        # Check if terminal-notifier is installed
        which_result = subprocess.run(
            ["which", "terminal-notifier"],
            capture_output=True,
            text=True
        )
        
        if which_result.returncode != 0:
            print("terminal-notifier is not installed. Install it with: brew install terminal-notifier")
            return False
        
        # Send a notification using terminal-notifier
        result = subprocess.run(
            [
                "terminal-notifier",
                "-title", "Test Notification",
                "-message", "This is a test notification from terminal-notifier",
                "-sound", "Glass"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("terminal-notifier notification sent successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error with terminal-notifier: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error with terminal-notifier: {e}")
        return False

def diagnose_notification_issues():
    """Run diagnostic checks for notification issues."""
    print("\n=== Notification System Diagnostics ===\n")
    
    # Check macOS version
    try:
        macos_version = subprocess.run(
            ["sw_vers", "-productVersion"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        print(f"macOS Version: {macos_version}")
    except Exception as e:
        print(f"Could not determine macOS version: {e}")
    
    # Check notification settings access
    print("\nChecking notification settings...")
    try:
        # This is a generic check to see if terminal has notification permissions
        settings_check = subprocess.run(
            ["defaults", "read", "com.apple.Terminal", "NSStatusItem Visible NotificationCenter"],
            capture_output=True,
            text=True
        )
        if settings_check.returncode == 0:
            print("Terminal appears to have notification settings configured.")
        else:
            print("Could not verify Terminal notification settings - this is expected on newer macOS versions")
    except Exception as e:
        print(f"Error checking notification settings: {e}")
    
    print("\nSuggested fixes if notifications aren't working:")
    print("1. Open System Preferences/Settings -> Notifications")
    print("2. Find 'Terminal' or 'Python' in the list")
    print("3. Ensure notifications are enabled")
    print("4. For command-line solutions, consider installing terminal-notifier: brew install terminal-notifier")
    
if __name__ == "__main__":
    print("=== Claude MCP Notification Test ===")
    
    success_count = 0
    tests_run = 0
    
    print("\n=== Testing PyObjC Notifications ===")
    if test_pyobjc_notification():
        success_count += 1
    tests_run += 1
    
    print("\n=== Testing AppleScript Notifications ===")
    if test_applescript_notification():
        success_count += 1
    tests_run += 1
    
    print("\n=== Testing Sound Playback ===")
    if test_sound():
        success_count += 1
    tests_run += 1
    
    print("\n=== Testing terminal-notifier ===")
    if test_terminal_notifier():
        success_count += 1
    tests_run += 1
    
    print(f"\n=== Results: {success_count}/{tests_run} tests passed ===")
    
    if success_count < tests_run:
        print("\nSome tests failed. Running diagnostics...")
        diagnose_notification_issues()
    
    print("\nTest complete!")
