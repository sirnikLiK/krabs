import os
import shutil
import time
import re
import random
import string

# --- CONFIGURATION ---
WATCH_DIR = "/home/stefano/Documents/ATS_nto/ATS_final/tresh/output"
DEST_DIR = "/home/stefano/Documents/ATS_nto/ATS_final/tresh/st"
POLL_INTERVAL = 0.5 # Seconds

def extract_digits(filename):
    """提取文件名中的所有数字并合并。"""
    digits = "".join(re.findall(r'\d+', filename))
    return digits if digits else "unknown"

def process_files():
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
        print(f"Created destination directory: {DEST_DIR}")

    print(f"Monitoring {WATCH_DIR} for new files...")
    print("Press Ctrl+C to stop.")

    # Get initial set of files to avoid processing existing ones if desired
    # For now, let's process anything found in output to be safe
    
    while True:
        try:
            if not os.path.exists(WATCH_DIR):
                time.sleep(POLL_INTERVAL)
                continue

            files = os.listdir(WATCH_DIR)
            for f in files:
                file_path = os.path.join(WATCH_DIR, f)
                
                # Basic check to ensure it's a file and not being written to (naive)
                if os.path.isfile(file_path):
                    try:
                        # Extract digits and prepare new name
                        digits = extract_digits(f)
                        
                        # Generate 3 or 4 random English letters
                        random_prefix = ''.join(random.choices(string.ascii_letters, k=random.choice([3, 4])))
                        
                        new_name = f"{random_prefix}_{digits}_sk.png"
                        dest_path = os.path.join(DEST_DIR, new_name)

                        # Move and rename
                        shutil.move(file_path, dest_path)
                        print(f"Moved and renamed: {f} -> {new_name}")
                    except Exception as e:
                        print(f"Error processing {f}: {e}")

            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print("\nStopped monitoring.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    process_files()
