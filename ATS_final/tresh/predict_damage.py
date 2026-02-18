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
            # Calculate weighted average damage
            total_weighted_damage = 0.0
            total_prob = 0.0
            
            print(f"Image: {image_path}")
            
            for class_idx, class_name in result.names.items():
                try:
                    probability = probs.data[class_idx].item()
                    
                    # Parse range from class name, assuming format like 'damage_00_09'
                    parts = class_name.split('_')
                    if len(parts) >= 3:
                        start_val = float(parts[-2])
                        end_val = float(parts[-1])
                        midpoint = (start_val + end_val) / 2.0
                        
                        total_weighted_damage += probability * midpoint
                        total_prob += probability
                except (ValueError, IndexError):
                    continue
            
            if total_prob > 0:
                print(f"Exact Damage: {total_weighted_damage:.4f}")
            else:
                print("Could not calculate exact damage (naming format issue?)")

def main():
    parser = argparse.ArgumentParser(description="Predict wall damage level using YOLO")
    parser.add_argument("image", help="Path to the image for prediction")
    
    # Construct default model path relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_model_path = os.path.join(script_dir, "runs", "classify", "damage_classification", "damage_model2",
                                      "weights",
                                      "C:\\Users\\mpjqw\\PycharmProjects\\krabs\\ATS_final\\tresh\\runs\\classify\\damage_classification\\damage_model2\\weights\\best.pt")

    parser.add_argument("--model", default=default_model_path, help="Path to the trained model")
    
    args = parser.parse_args()
    
    predict(args.image, args.model)

if __name__ == "__main__":
    main()
