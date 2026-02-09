import cv2
import numpy as np
from ultralytics import YOLO

WHEEL_MODEL_PATH = "best_wheel.pt" 

class WheelAnalysis:
    def __init__(self):
        self.model = None
        try:
            self.model = YOLO(WHEEL_MODEL_PATH)
            print(f"WheelAnalysis: Loaded {WHEEL_MODEL_PATH}")
        except:
            print(f"WheelAnalysis: WARNING - Could not load {WHEEL_MODEL_PATH}. Using mock logic.")

    def detect_wheel(self, frame):
        """
        Locates the wheel in the frame.
        Returns: (x, y, w, h) or None
        """
        # If model exists, use it to find 'wheel' class
        if self.model:
            results = self.model(frame, verbose=False)
            for r in results:
                for box in r.boxes:
                    # check class if needed
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    return (x1, y1, x2-x1, y2-y1)
        
        # Mock: Return center crop if simple
        h, w = frame.shape[:2]
        return (int(w*0.25), int(h*0.25), int(w*0.5), int(h*0.5))

    def classify_wheel(self, wheel_img):
        """
        Classifies wheel as 'Normal' or 'Reinforced'.
        """
        # In reality: Run a classifier model or check specific features (spokes, text)
        # Mock: Random or based on brightness
        avg_color = np.mean(wheel_img)
        return "Reinforced" if avg_color > 100 else "Normal"

    def find_bolts(self, wheel_img):
        """
        Finds bolts and holes.
        Returns: list of (x, y, type) where type is 'bolt' or 'hole'
        """
        # Use Hough Circles or Blob Detection
        gray = cv2.cvtColor(wheel_img, cv2.COLOR_BGR2GRAY)
        
        # Blur
        gray = cv2.medianBlur(gray, 5)
        
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                   param1=50, param2=30, minRadius=10, maxRadius=30)
        
        bolts = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                # Mock logic: if darker center -> hole, lighter -> bolt (simplified)
                center_val = gray[i[1], i[0]]
                b_type = 'hole' if center_val < 100 else 'bolt'
                bolts.append((i[0], i[1], b_type))
                
        return bolts
