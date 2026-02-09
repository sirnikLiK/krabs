import cv2
import os
import albumentations as A
import argparse
import glob
from tqdm import tqdm

def load_yolo_label(label_path, img_width, img_height):
    bboxes = []
    classes = []
    if os.path.exists(label_path):
        with open(label_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split()
                cls = int(parts[0])
                cx = float(parts[1])
                cy = float(parts[2])
                w = float(parts[3])
                h = float(parts[4])
                bboxes.append([cx, cy, w, h])
                classes.append(cls)
    return bboxes, classes

def save_yolo_label(label_path, bboxes, classes):
    with open(label_path, 'w') as f:
        for bbox, cls in zip(bboxes, classes):
            # clamp values to 0-1
            bbox = [max(0.0, min(1.0, x)) for x in bbox]
            f.write(f"{cls} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n")

def augment_dataset(input_dir, output_dir, multiplier=1):
    """
    Augments images and labels in input_dir and saves to output_dir.
    """
    img_dir = os.path.join(input_dir, "images")
    lbl_dir = os.path.join(input_dir, "labels")
    
    out_img_dir = os.path.join(output_dir, "images")
    out_lbl_dir = os.path.join(output_dir, "labels")
    
    os.makedirs(out_img_dir, exist_ok=True)
    os.makedirs(out_lbl_dir, exist_ok=True)
    
    # Define augmentation pipeline
    transform = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.5),
        A.Rotate(limit=15, p=0.5),
        A.GaussianBlur(p=0.2),
        A.CLAHE(p=0.2),
    ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

    image_files = glob.glob(os.path.join(img_dir, "*.jpg")) + glob.glob(os.path.join(img_dir, "*.png"))
    
    print(f"Found {len(image_files)} images to augment.")
    
    for img_path in tqdm(image_files):
        filename = os.path.basename(img_path)
        name, ext = os.path.splitext(filename)
        label_path = os.path.join(lbl_dir, name + ".txt")
        
        image = cv2.imread(img_path)
        if image is None: continue
        h, w = image.shape[:2]
        
        bboxes, classes = load_yolo_label(label_path, w, h)
        
        # Save original
        cv2.imwrite(os.path.join(out_img_dir, filename), image)
        save_yolo_label(os.path.join(out_lbl_dir, name + ".txt"), bboxes, classes)
        
        # Generate augmented versions
        for i in range(multiplier):
            try:
                transformed = transform(image=image, bboxes=bboxes, class_labels=classes)
                aug_img = transformed['image']
                aug_bboxes = transformed['bboxes']
                aug_classes = transformed['class_labels']
                
                new_name = f"{name}_aug_{i}"
                cv2.imwrite(os.path.join(out_img_dir, new_name + ext), aug_img)
                save_yolo_label(os.path.join(out_lbl_dir, new_name + ".txt"), aug_bboxes, aug_classes)
            except Exception as e:
                print(f"Error augmenting {filename}: {e}")

def main():
    parser = argparse.ArgumentParser(description="YOLO Data Augmentation")
    parser.add_argument("--input", required=True, help="Input directory (must contain 'images' and 'labels' folders)")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--count", type=int, default=1, help="Number of augmented versions per image")
    
    args = parser.parse_args()
    
    augment_dataset(args.input, args.output, args.count)

if __name__ == "__main__":
    main()
