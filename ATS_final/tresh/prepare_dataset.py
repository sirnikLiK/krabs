import os
import shutil
import re
import random

# --- CONFIGURATION ---
SOURCE_DIR = "/home/stefano/Documents/ATS_nto/ATS_final/tresh/st"
DATASET_ROOT = "/home/stefano/Documents/ATS_nto/ATS_final/tresh/dataset_damage"
TRAIN_RATIO = 0.8

def extract_damage(filename):
    """Extract digits from filename."""
    match = re.search(r'(\d+)', filename)
    if match:
        return int(match.group(1))
    return None

def get_bucket(damage):
    """Group damage into 10 buckets (0-9, 10-19, ..., 90-100)."""
    bucket_idx = damage // 10
    if bucket_idx > 9: bucket_idx = 9
    return f"damage_{bucket_idx}0_{bucket_idx}9"

def prepare():
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory {SOURCE_DIR} does not exist.")
        return

    # Clean previous dataset
    if os.path.exists(DATASET_ROOT):
        shutil.rmtree(DATASET_ROOT)
    
    os.makedirs(DATASET_ROOT)

    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    random.shuffle(files)

    split_idx = int(len(files) * TRAIN_RATIO)
    train_files = files[:split_idx]
    val_files = files[split_idx:]

    def process_split(split_files, split_name):
        for f in split_files:
            damage = extract_damage(f)
            if damage is None: continue
            
            bucket_name = get_bucket(damage)
            target_dir = os.path.join(DATASET_ROOT, split_name, bucket_name)
            
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            shutil.copy(os.path.join(SOURCE_DIR, f), os.path.join(target_dir, f))

    print(f"Processing {len(train_files)} training images...")
    process_split(train_files, "train")
    
    print(f"Processing {len(val_files)} validation images...")
    process_split(val_files, "val")

    print(f"Dataset prepared at: {DATASET_ROOT}")

if __name__ == "__main__":
    prepare()
