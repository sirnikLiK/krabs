from ultralytics import YOLO
import os

# --- SETTINGS ---
MODEL_NAME = "yolov8n.pt" # Load a pretrained model (recommended for transfer learning)
DATA_CONFIG = "data.yaml"
EPOCHS = 50
IMG_SIZE = 640

def main():
    # Load a model
    model = YOLO(MODEL_NAME)  # load a pretrained model (recommended for training)

    # Train the model
    # ensure data.yaml absolute path is correct or relative working dir is correct
    print(f"Starting training with {DATA_CONFIG}...")
    
    results = model.train(
        data=DATA_CONFIG,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        plots=True,
        batch=16,
        name='yolo_nto_train' # experiment name, saved in runs/detect/
    )

    print("Training complete.")
    print(f"Best model saved at: {results.save_dir}/weights/best.pt")

if __name__ == "__main__":
    main()
