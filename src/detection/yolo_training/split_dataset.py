import os
import shutil
import random
import argparse
import glob

def split_dataset(input_dir, output_dir, split_ratio=0.8):
    """
    Splits data into train and val sets.
    """
    # Source paths
    # Assumes input_dir has flat structure or images/labels
    # We'll look for pairs of (jpg/png, txt)
    
    # Try to find images
    all_images = glob.glob(os.path.join(input_dir, "*.jpg")) + \
                 glob.glob(os.path.join(input_dir, "*.png")) + \
                 glob.glob(os.path.join(input_dir, "images", "*.jpg")) + \
                 glob.glob(os.path.join(input_dir, "images", "*.png"))
                 
    unique_names = list(set([os.path.splitext(os.path.basename(f))[0] for f in all_images]))
    
    random.shuffle(unique_names)
    
    split_idx = int(len(unique_names) * split_ratio)
    train_names = unique_names[:split_idx]
    val_names = unique_names[split_idx:]
    
    # Setup Output Dirs
    dirs = [
        "images/train", "images/val",
        "labels/train", "labels/val"
    ]
    for d in dirs:
        os.makedirs(os.path.join(output_dir, d), exist_ok=True)
        
    print(f"Found {len(unique_names)} items. Split: {len(train_names)} Train, {len(val_names)} Val.")
    
    def move_files(names, phase):
        for name in names:
            # Find source image
            src_img = None
            # Check root
            if os.path.exists(os.path.join(input_dir, name + ".jpg")): src_img = os.path.join(input_dir, name + ".jpg")
            elif os.path.exists(os.path.join(input_dir, name + ".png")): src_img = os.path.join(input_dir, name + ".png")
            elif os.path.exists(os.path.join(input_dir, "images", name + ".jpg")): src_img = os.path.join(input_dir, "images", name + ".jpg")
            
            if not src_img: continue
            
            # Find source label
            src_lbl = None
            if os.path.exists(os.path.join(input_dir, name + ".txt")): src_lbl = os.path.join(input_dir, name + ".txt")
            elif os.path.exists(os.path.join(input_dir, "labels", name + ".txt")): src_lbl = os.path.join(input_dir, "labels", name + ".txt")
            
            # Copy Image
            shutil.copy(src_img, os.path.join(output_dir, "images", phase, os.path.basename(src_img)))
            
            # Copy Label (if exists)
            if src_lbl:
                shutil.copy(src_lbl, os.path.join(output_dir, "labels", phase, os.path.basename(src_lbl)))
                
    move_files(train_names, "train")
    move_files(val_names, "val")
    
    print("Done.")

def main():
    parser = argparse.ArgumentParser(description="Split Dataset into Train/Val")
    parser.add_argument("--input", required=True, help="Input directory containing raw images (and labels)")
    parser.add_argument("--output", required=True, help="Output directory for YOLO structure")
    parser.add_argument("--ratio", type=float, default=0.8, help="Train ratio (default 0.8)")
    
    args = parser.parse_args()
    
    split_dataset(args.input, args.output, args.ratio)

if __name__ == "__main__":
    main()
