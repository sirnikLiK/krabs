# Olympiad Preparation Files

This project contains starter code for the drone, car, and service center tasks.

## 1. Data Collection
Use these tools to collect dataset images for training your YOLO models.

- **Collect Data**: `python3 src/detection/yolo_training/collect_data_advanced.py`
  - Press `SPACE` to save an image.
  - Press `c` to change class (Person, Defect, Wheel, Debris).
  - Press `v` to switch between Train/Val sets.

- **Create Config**: `python3 src/detection/yolo_training/create_yolo_config.py --name my_dataset --classes person defect`

## 2. Advanced Training Tools
If you have limited data or time, use these tools:

- **Augment Data**: Multiply your dataset with rotations/flips.
  `python3 src/detection/yolo_training/augment_data.py --input datasets/raw --output datasets/augmented --count 3`

- **Split Dataset**: Automatically organize raw images/labels into Train/Val folders.
  `python3 src/detection/yolo_training/split_dataset.py --input datasets/augmented --output datasets/final --ratio 0.8`

- **Train Manager**: Easy training with auto-save.
  `python3 src/detection/yolo_training/train_manager.py --data datasets/final/data.yaml --model yolov8n.pt --epochs 100`

## 3. Drone System
Controls the quadcopter state machine.

- **Run**: `python3 src/drone/main_drone.py`
- **Vision Logic**: Edit `src/drone/drone_vision.py` to refine detection logic.
- **Models**: Place trained YOLO models in the project root and update paths in `drone_vision.py`.

## 3. Car System
Controls the unmanned vehicle.

- **Run**: `python3 src/car/main_car.py`
- **Vision Logic**: Edit `src/car/car_vision.py` for leader tracking and debris avoidance.

## 4. Service Center
Analyzes wheels.

- **Run**: `python3 src/service/main_service.py`
- **Logic**: Edit `src/service/wheel_analysis.py` for bolt detection and wheel classification.

## Next Steps
1.  **Train Models**: Use the data collection tools to gather data for "defects", "debris", and "wheels". Train YOLOv8 models on this data.
2.  **Update Paths**: Update `MODEL_PATH` variables in `drone_vision.py`, `wheel_analysis.py`, etc., to point to your best `.pt` files.
3.  **Hardware Integration**: Replace mock `cv2.VideoCapture(0)` with actual camera streams and add serial communication code for drone/car control.
