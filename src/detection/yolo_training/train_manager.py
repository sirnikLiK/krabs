from ultralytics import YOLO
import argparse
import os
import shutil

def train_model(data_config, model_name="yolov8n.pt", epochs=50, project="runs/detect", name="exp"):
    print(f"--- STARTING TRAINING ---")
    print(f"Model: {model_name}")
    print(f"Data: {data_config}")
    print(f"Epochs: {epochs}")
    
    model = YOLO(model_name)
    
    results = model.train(
        data=data_config,
        epochs=epochs,
        imgsz=640,
        plots=True,
        project=project,
        name=name,
        exist_ok=True # Overwrite existing exp folder if same name
    )
    
    print(f"--- TRAINING DONE ---")
    print(f"Best weights: {results.save_dir}/weights/best.pt")
    
    # Validation
    metrics = model.val()
    print(f"mAP50-95: {metrics.box.map}")
    
    return results.save_dir

def main():
    parser = argparse.ArgumentParser(description="Advanced YOLO Training Manager")
    parser.add_argument("--data", required=True, help="Path to data.yaml")
    parser.add_argument("--model", default="yolov8n.pt", help="Pretrained model (yolov8n.pt, yolov8s.pt)")
    parser.add_argument("--epochs", type=int, default=50, help="Number of epochs")
    parser.add_argument("--name", default="my_experiment", help="Experiment name")
    
    args = parser.parse_args()
    
    save_dir = train_model(args.data, args.model, args.epochs, name=args.name)
    
    print(f"Results saved to: {save_dir}")

if __name__ == "__main__":
    main()
