import os
import sys
from ultralytics import YOLO
import argparse

def predict(image_path, model_path):
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return

    # Load the trained model
    model = YOLO(model_path)

    # Predict on the image
    results = model.predict(image_path)

    # Display results
    for result in results:
        probs = result.probs
        if probs is not None:
            # Get the top class and its confidence
            top1_idx = probs.top1
            top1_conf = probs.top1conf.item()
            label = result.names[top1_idx]
            
            print(f"Image: {image_path}")
            print(f"Top Prediction: {label}")
            print(f"Confidence: {top1_conf:.2f}")
            
            # Map back bucket name to damage range
            damage_range = label.split('_')[1:] # ['00', '09']
            if len(damage_range) == 2:
                print(f"Estimated Damage Level: {damage_range[0]}% - {damage_range[1]}%")

def main():
    parser = argparse.ArgumentParser(description="Predict wall damage level using YOLO")
    parser.add_argument("image", help="Path to the image for prediction")
    parser.add_argument("--model", default="runs/classify/damage_classification/damage_model/weights/best.pt", help="Path to the trained model")
    
    args = parser.parse_args()
    
    predict(args.image, args.model)

if __name__ == "__main__":
    main()
