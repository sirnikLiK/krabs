import cv2
import numpy as np

# --- CONFIG ---
# Adjust based on leader car marker/color
LEADER_COLOR_LOWER = np.array([0, 100, 100])
LEADER_COLOR_UPPER = np.array([10, 255, 255]) 

class CarVision:
    def __init__(self):
        pass

    def track_leader(self, frame):
        """
        Finds the leader car.
        Returns: (x, y, w, h) of the bounding box or None if not found.
        PRO TIP: Use ArUco markers for robust convoy following in Olympiads.
        """
        # Example: Simple Color Blob Detection (Red Car)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LEADER_COLOR_LOWER, LEADER_COLOR_UPPER)
        
        # Noise removal
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 500:
                rect = cv2.boundingRect(c)
                return rect
                
        return None

    def detect_debris(self, frame):
        """
        Detects debris on the road.
        Returns: True if debris is dangerously close.
        """
        # Placeholder: Check for specific color/object in bottom center of frame
        height, width = frame.shape[:2]
        roi = frame[int(height*0.7):, int(width*0.3):int(width*0.7)]
        
        # Example: Grey debris
        # hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        # mask = cv2.inRange(hsv, ..., ...)
        # if countNonZero > threshold: return True
        return False

    def get_steering_error(self, frame, leader_box):
        """
        Calculates steering error based on leader position or lane.
        Returns: error (-1 to 1), where -1 is full left, 1 is full right.
        """
        height, width = frame.shape[:2]
        center_x = width // 2
        
        if leader_box:
            x, y, w, h = leader_box
            leader_cx = x + w // 2
            
            error = (leader_cx - center_x) / (width / 2)
            return error
            
        return 0.0 # Go straight if no leader
