import json
import time
import os
import threading

# Path to the shared communication file
COMM_FILE = "robot_commands.json"

def robot_listener():
    """
    Simulates the robot waiting for commands in the file.
    """
    last_mtime = 0
    
    print("[ROBOT] Listening for commands in file...")
    
    while True:
        if os.path.exists(COMM_FILE):
            try:
                mtime = os.path.getmtime(COMM_FILE)
                if mtime > last_mtime:
                    # File changed!
                    with open(COMM_FILE, 'r') as f:
                        try:
                            data = json.load(f)
                            print(f"\n[ROBOT] New Command Received: {data}")
                            # Process command here...
                            if data.get("cmd") == "STOP":
                                print("[ROBOT] Stopping engines!")
                        except json.JSONDecodeError:
                            pass # File might be being written to
                    
                    last_mtime = mtime
            except Exception as e:
                print(f"Error reading file: {e}")
        
        time.sleep(0.5)

def controller_sender():
    """
    Simulates the controller writing commands.
    """
    print("[CONTROLLER] Ready to write commands.")
    
    commands = [
        {"cmd": "MOVE", "speed": 50},
        {"cmd": "TURN", "angle": 90},
        {"cmd": "STOP"},
        {"cmd": "MOVE", "speed": 100}
    ]
    
    for cmd in commands:
        time.sleep(2)
        print(f"[CONTROLLER] Writing: {cmd}")
        
        # Atomic write safely?
        # Ideally: write to temp file then rename
        # Simple way for example:
        with open(COMM_FILE, 'w') as f:
            json.dump(cmd, f)

if __name__ == "__main__":
    # Create the file first
    with open(COMM_FILE, 'w') as f:
        json.dump({"status": "init"}, f)

    # Start robot thread
    t = threading.Thread(target=robot_listener, daemon=True)
    t.start()
    
    # Start controller logic in main thread
    controller_sender()
    
    # Keep alive to see robot output
    time.sleep(5)
    print("\nSimulation finished.")
