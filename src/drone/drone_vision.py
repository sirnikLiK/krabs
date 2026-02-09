import cv2
from ultralytics import YOLO

# --- MODEL PATHS ---
# Update these paths after training your models!
DEFECT_MODEL_PATH = "best_defect.pt" 
DEBRIS_MODEL_PATH = "best_debris.pt"

class DroneVision:
    def __init__(self):
        self.defect_model = None
        self.debris_model = None
        
        # Load models if they exist, otherwise warn user
        try:
            self.defect_model = YOLO(DEFECT_MODEL_PATH)
            print(f"DroneVision: Loaded {DEFECT_MODEL_PATH}")
        except:
            print(f"DroneVision: WARNING - Could not load {DEFECT_MODEL_PATH}. Using mock logic.")

        try:
            self.debris_model = YOLO(DEBRIS_MODEL_PATH)
            print(f"DroneVision: Loaded {DEBRIS_MODEL_PATH}")
        except:
            print(f"DroneVision: WARNING - Could not load {DEBRIS_MODEL_PATH}. Using mock logic.")

    def detect_defects(self, frame):
        """
        Detects facade defects (cracks, etc).
        Returns: list of detections [(x1, y1, x2, y2, conf, cls)]
        """
        if self.defect_model:
            results = self.defect_model(frame, verbose=False)
            detections = []
            for r in results:
                for box in r.boxes:
                    detections.append(box.xyxy[0].tolist() + [box.conf[0].item(), box.cls[0].item()])
            return detections
        else:
            # Mock logic: Draw a rectangle in center if frame is dark/light (just for testing)
            return []

    def detect_debris(self, frame):
        """
        Detects road debris.
        Returns: list of detections
        """
        if self.debris_model:
            results = self.debris_model(frame, verbose=False)
            detections = []
            for r in results:
                for box in r.boxes:
                    detections.append(box.xyxy[0].tolist() + [box.conf[0].item(), box.cls[0].item()])
            return detections
        else:
            return []

    def draw_detections(self, frame, detections, color=(0, 0, 255)):
        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(frame, f"{conf:.2f}", (int(x1), int(y1)-5), 0, 0.5, color, 1)
        return frame
