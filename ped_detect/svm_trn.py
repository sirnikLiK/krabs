import os
import sys
import dlib
import cv2
import glob
import xml.etree.ElementTree as ET

def train_svm():
    # Define paths relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    labels_dir = os.path.join(base_dir, "labels")
    img_dir = os.path.join(base_dir, "img")
    
    xml_files = glob.glob(os.path.join(labels_dir, "*.xml"))
    
    if not xml_files:
        print(f"No XML files found in {labels_dir}")
        return

    images = []
    annots = []
    
    print(f"Found {len(xml_files)} xml files. Processing...")

    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        filename = root.find("filename").text
        
        # Verify image exists
        image_path = os.path.join(img_dir, filename)
        if not os.path.exists(image_path):
            print(f"Warning: Image {image_path} not found. Skipping.")
            continue
            
        # Load image
        # dlib expects RGB images. cv2 loads as BGR.
        img = cv2.imread(image_path)
        if img is None:
            print(f"Warning: Could not read image {image_path}. Skipping.")
            continue
            
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        boxes = []
        for obj in root.findall("object"):
            bndbox = obj.find("bndbox")
            xmin = int(float(bndbox.find("xmin").text))
            ymin = int(float(bndbox.find("ymin").text))
            xmax = int(float(bndbox.find("xmax").text))
            ymax = int(float(bndbox.find("ymax").text))
            
            # dlib.rectangle(left, top, right, bottom)
            boxes.append(dlib.rectangle(xmin, ymin, xmax, ymax))
            
        if boxes:
            images.append(rgb_img)
            annots.append(boxes)
            
    if not images:
        print("No valid training data found.")
        return

    print(f"Training with {len(images)} images...")
    
    options = dlib.simple_object_detector_training_options()
    # You can tune these options (C, epsilon, etc.) if needed. 
    # options.C = 5
    # options.add_jittering = True
    
    detector = dlib.train_simple_object_detector(images, annots, options)
    
    output_path = os.path.join(base_dir, "tld.svm")
    detector.save(output_path)
    
    print(f"Training finished. Detector saved to {output_path}")
    
    # Optional: Test on training data (metrics)
    print("Training metrics: {}".format(
        dlib.test_simple_object_detector(images, annots, detector)))

if __name__ == "__main__":
    train_svm()