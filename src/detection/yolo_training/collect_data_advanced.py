import cv2
import os
import argparse
import time

# --- CONFIGURATION (Default) ---
DATASET_ROOT = "datasets"
CLASSES = ["person", "defect", "wheel", "debris"] # Default classes

def get_next_filename(directory, prefix="img"):
    if not os.path.exists(directory):
        return f"{prefix}_0.jpg"
        
    existing_files = [f for f in os.listdir(directory) if f.lower().endswith(".jpg")]
    max_num = -1
    for f in existing_files:
        try:
            # Assumes format: prefix_123.jpg
            parts = f.split("_")
            if len(parts) >= 2:
                num_part = parts[-1].split(".")[0]
                num = int(num_part)
                if num > max_num:
                    max_num = num
        except:
            pass
    return f"{prefix}_{max_num + 1}.jpg"

def main():
    parser = argparse.ArgumentParser(description="Advanced Data Collection for YOLO")
    parser.add_argument("--root", default=DATASET_ROOT, help="Dataset root directory")
    args = parser.parse_args()

    # Setup directories
    train_dir = os.path.join(args.root, "images/train")
    val_dir = os.path.join(args.root, "images/val")
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # Optional: usage high res
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    current_class_idx = 0
    current_set = "train" # or "val"
    
    print(f"--- ADVANCED DATA COLLECTION ---")
    print(f"Saving to: {os.path.abspath(args.root)}")
    print(f"[SPACE] Capture FULL Image")
    print(f"[r] Select ROI and Save CROP")
    print(f"[v] Toggle Train/Val (Current: {current_set.upper()})")
    print(f"[c] Change Class")
    print(f"[q] Quit")

    while True:
        ret, frame = cap.read()
        if not ret: break

        current_class_name = CLASSES[current_class_idx]
        
        # Overlay Info
        display_frame = frame.copy()
        color = (0, 255, 0) if current_set == "train" else (0, 165, 255)
        
        cv2.putText(display_frame, f"Class: {current_class_name.upper()} [{current_class_idx}]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display_frame, f"Set: {current_set.upper()}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(display_frame, "[SPACE] Full  [r] Crop", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("Data Collection", display_frame)
        
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('v'):
            current_set = "val" if current_set == "train" else "train"
        elif key == ord('c'):
            current_class_idx = (current_class_idx + 1) % len(CLASSES)
        elif key == ord('r'):
            # Select ROI
            roi = cv2.selectROI("Select ROI (ENTER to confirm, ESC to cancel)", frame, fromCenter=False)
            cv2.destroyWindow("Select ROI (ENTER to confirm, ESC to cancel)")
            
            if roi != (0, 0, 0, 0):
                x, y, w, h = roi
                crop = frame[y:y+h, x:x+w]
                
                target_dir = train_dir if current_set == "train" else val_dir
                prefix = f"{current_class_name}_crop"
                filename = get_next_filename(target_dir, prefix)
                filepath = os.path.join(target_dir, filename)
                
                cv2.imwrite(filepath, crop)
                print(f"Saved CROP [{current_set.upper()}][{current_class_name}]: {filename}")
                
                # Feedback
                cv2.imshow("Data Collection", 255 - display_frame)
                cv2.waitKey(100)
        elif key == ord(' '):
            # Save Full Image
            target_dir = train_dir if current_set == "train" else val_dir
            prefix = current_class_name
            filename = get_next_filename(target_dir, prefix)
            filepath = os.path.join(target_dir, filename)
            
            cv2.imwrite(filepath, frame)
            print(f"Saved FULL [{current_set.upper()}][{current_class_name}]: {filename}")
            
            # Flash effect
            cv2.imshow("Data Collection", 255 - display_frame)
            cv2.waitKey(50)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
