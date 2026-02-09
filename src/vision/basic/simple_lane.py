import cv2
import numpy as np

# --- SETTINGS ---
# LOWER_WHITE = np.array([0, 0, 200]) # HSV Lower
# UPPER_WHITE = np.array([180, 50, 255]) # HSV Upper
# Use a range that catches white/yellow lines
LOWER_LANE = np.array([0, 0, 200])   # Adjust these for your lighting!
UPPER_LANE = np.array([180, 50, 255])

ROI_Y_TOP = 240 # Only look at bottom half of image
ROI_Y_BOTTOM = 480 

def get_steering_angle(frame):
    """
    Returns a steering angle (0-180, 90 is straight) based on the largest contour.
    """
    height, width = frame.shape[:2]
    
    # Crop to Region of Interest (ROI)
    roi = frame[int(height/2):, :] # Bottom half
    
    # HSV Conversion
    hls = cv2.cvtColor(roi, cv2.COLOR_BGR2HLS) # Use HLS for better white detection
    
    # Thresholding (S channel is good for saturation, L for lightness)
    # Here we use L channel for white lines
    lower = np.array([0, 150, 0])
    upper = np.array([180, 255, 255])
    mask = cv2.inRange(hls, lower, upper)
    
    # Morphology (Noise removal)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Find Contours
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) > 0:
        # Assume largest contour is the lane (or part of it)
        c = max(contours, key=cv2.contourArea)
        
        # Find Centroid
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            # Draw for debug
            cv2.drawContours(roi, [c], -1, (0, 255, 0), 2)
            cv2.circle(roi, (cx, cy), 5, (0, 0, 255), -1)
            
            # Calculate Error (Offset from center)
            # screen_center_x = width // 2
            # error = cx - screen_center_x
            
            # Map x position to angle (Simple P-controller logic)
            # Left side (x=0) -> Angle > 90 (Turn Right)
            # Right side (x=width) -> Angle < 90 (Turn Left)
            # Or vice versa depending on servo setup. 
            # Assuming 90 is straight, <90 turns left, >90 turns right.
            
            # Normalize x to -1 to 1
            norm_x = (cx - width/2) / (width/2) 
            
            angle = 90 - (norm_x * 45) # Max turn 45 degrees
            return int(angle), roi
            
    return 90, roi # Default straight

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    
    print("Simple Lane Detection")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        angle, debug_frame = get_steering_angle(frame)
        
        cv2.putText(frame, f"Angle: {angle}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Original", frame)
        cv2.imshow("Lane Debug", debug_frame)
        
        if cv2.waitKey(1) == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
