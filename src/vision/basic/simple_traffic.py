import cv2
import numpy as np

def detect_traffic_light(frame):
    """
    Detects traffic light state based on color brightness in ROIs.
    Assumes traffic light is in a specific part of the frame or uses general color detection.
    
    Returns: 'red', 'yellow', 'green', or 'none'
    """
    
    # --- ROI SETTINGS ---
    # Define ROI for traffic light (x, y, w, h)
    # This needs to be calibrated!
    # Example: Top right corner
    x, y, w, h = 400, 0, 240, 200 
    roi = frame[y:y+h, x:x+w]
    
    if roi.size == 0: return 'none', frame
    
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Define Red, Yellow, Green ranges
    # Red has two ranges in HSV (0-10 and 170-180)
    lower_red1, upper_red1 = np.array([0, 100, 100]), np.array([10, 255, 255])
    lower_red2, upper_red2 = np.array([170, 100, 100]), np.array([180, 255, 255])
    
    lower_yellow, upper_yellow = np.array([20, 100, 100]), np.array([30, 255, 255])
    lower_green, upper_green = np.array([40, 100, 100]), np.array([90, 255, 255]) # 40-90 covers typical green/cyan
    
    # Apple masks
    mask_r1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_r2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_r1, mask_r2)
    
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    
    # Count pixels
    red_pixels = cv2.countNonZero(mask_red)
    yellow_pixels = cv2.countNonZero(mask_yellow)
    green_pixels = cv2.countNonZero(mask_green)
    
    # Threshold to consider signal active
    THRESHOLD = 50 
    
    state = 'none'
    color = (0, 0, 0)
    
    # Priority: Red > Yellow > Green 
    # Or simply Max
    
    counts = {'red': red_pixels, 'yellow': yellow_pixels, 'green': green_pixels}
    max_color = max(counts, key=counts.get)
    max_val = counts[max_color]
    
    if max_val > THRESHOLD:
        state = max_color
        if state == 'red': color = (0, 0, 255)
        elif state == 'yellow': color = (0, 255, 255)
        elif state == 'green': color = (0, 255, 0)
        
    # Draw ROI on frame
    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
    cv2.putText(frame, f"TL: {state} ({max_val})", (x, y+h+20), 0, 0.7, color, 2)
    
    return state, frame

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        state, frame = detect_traffic_light(frame)
        
        cv2.imshow("Simple Traffic Light", frame)
        if cv2.waitKey(1) == ord('q'): break
        
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
