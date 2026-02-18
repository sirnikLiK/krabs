import os
import sys

try:
    from ultralytics import YOLO
except ImportError:
    print("Error: Ultralytics not installed. Please wait for the installation to finish.")
    sys.exit(1)

# --- CONFIGURATION ---
DATASET_DIR = "/home/stefano/Documents/ATS_nto/ATS_final/tresh/dataset_damage"
PROJECT_NAME = "damage_classification"
MODEL_NAME = "damage_model"

def train():
    # Load a pretrained YOLOv11n-cls model
    model = YOLO("yolo11n-cls.pt")  # load a pretrained model (recommended for training)

    # Train the model
    print("Starting YOLO training...")
    results = model.train(
        data=DATASET_DIR,
        epochs=50,
        imgsz=224,
        batch=16,
        name=MODEL_NAME,
        project=PROJECT_NAME
    )

    print(f"Training complete. Model saved in {PROJECT_NAME}/{MODEL_NAME}/weights/best.pt")

if __name__ == "__main__":
    train()
