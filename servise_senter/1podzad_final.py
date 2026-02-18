
import cv2
import numpy as np

# Increase varThreshold to 100+ to ignore sensor noise/flicker
motion_detector = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=150, detectShadows=False)
motion_counter = 0

# Variables for stabilization logic
stabilization_counter = 0
last_wheel_center = None
stabilization_threshold = 1  # frames wheel must stay in similar position
distance_threshold = 30  # pixels - how much wheel can move to still be considered "stable"
paused_frame = None
is_paused = False

def detect_any_wheel(frame, is_image=False):
    global motion_counter, stabilization_counter, last_wheel_center, paused_frame, is_paused
    
    # If paused, just return the saved "stop frame"
    if is_paused:
        return paused_frame
    
    h, w = frame.shape[:2]
    roi_w = int(w * 0.65)
    frame_roi = frame[:, :roi_w]
    h_roi, w_roi = frame_roi.shape[:2]

    # Enhance brightness for better detection
    img_bright = cv2.convertScaleAbs(frame_roi, alpha=1.2, beta=45)
    
    if not is_image:
        # Motion detection on ROI
        fg_mask = motion_detector.apply(frame_roi)
        fg_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        
        motion_pixels = cv2.countNonZero(fg_mask)
        
        if motion_pixels > 3000: # Threshold for significant motion
            motion_counter = 0
            stabilization_counter = 0
            last_wheel_center = None
            cv2.putText(img_bright, "Moving...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return img_bright
        else:
            motion_counter += 1

        if motion_counter < 15:
            cv2.putText(img_bright, "Waiting for stop...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            stabilization_counter = 0
            last_wheel_center = None
            return img_bright

    # Image Pre-processing for Circle Detection
    gray = cv2.cvtColor(img_bright, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0).apply(gray)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100,
        param1=30, param2=35, minRadius=80, maxRadius=95
    )

    if circles is not None:
        valid_wheels = []
        for c in circles[0, :]:
            cx, cy, r = map(int, c) # Cast to int for safety
            
            # Safe brightness sampling
            center_brightness = gray[np.clip(cy, 0, h_roi-1), np.clip(cx, 0, w_roi-1)]
            edge_points = [
                (np.clip(cy-r, 0, h_roi-1), cx), (np.clip(cy+r, 0, h_roi-1), cx),
                (cy, np.clip(cx-r, 0, w_roi-1)), (cy, np.clip(cx+r, 0, w_roi-1))
            ]
            edge_brightness = np.mean([gray[y, x] for y, x in edge_points])
            
            # Simple validation: center should be darker than edges (hub hole)
            if center_brightness < edge_brightness * 0.85:
                valid_wheels.append(((cx, cy, r), center_brightness))
        
        if valid_wheels:
            # Select rightmost wheel
            wheel_data, _ = max(valid_wheels, key=lambda x: x[0][0])
            cx, cy, r = wheel_data
            padding = int(r * 1.35)
            
            # Distance-based stabilization
            current_center = (cx, cy)
            if last_wheel_center is not None:
                distance = np.sqrt((current_center[0] - last_wheel_center[0])**2 + 
                                 (current_center[1] - last_wheel_center[1])**2)
                if distance < distance_threshold:
                    stabilization_counter += 1
                else:
                    stabilization_counter = 0
            else:
                stabilization_counter = 1
            
            last_wheel_center = current_center
            
            # Draw detections onto the frame
            # cv2.circle(img_bright, (cx, cy), r, (255, 0, 0), 2)
            cv2.rectangle(img_bright, (cx-padding, cy-padding), (cx+padding, cy+padding), (0, 255, 0), 3)
            
            # Check if stabilized enough to freeze
            if stabilization_counter >= stabilization_threshold:
                cv2.putText(img_bright, "STABILIZED - Press 'd' to resume", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                is_paused = True
                paused_frame = img_bright.copy() # Store the "stop frame"
                return paused_frame
        else:
            stabilization_counter = 0
            last_wheel_center = None
    else:
        stabilization_counter = 0
        last_wheel_center = None

    return img_bright

def main():
    global is_paused, stabilization_counter, last_wheel_center, paused_frame, motion_counter, motion_detector
    
    # Update this to your camera or image path
    source = "rtsp://172.16.65.140:8554/cam1" 
    is_image = source.lower().endswith(('.png', '.jpg', '.jpeg'))
    cap = cv2.VideoCapture(source)
    if not cap.isOpened(): 
        print("Error: Could not open source.")
        return

    while True:
        if is_paused:
            # Read and discard frames to keep the RTSP buffer empty
            ret, _ = cap.read()
            if not ret: break
            result = paused_frame
        else:
            ret, frame = cap.read()
            if not ret:
                if is_image: cv2.waitKey(0)
                break
            result = detect_any_wheel(frame, is_image)
        
        cv2.imshow("Detection", result)
        
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('d'):
            # FULL RESET logic to start detecting again
            is_paused = False
            paused_frame = None
            stabilization_counter = 0
            last_wheel_center = None
            motion_counter = 0
            # Reset the background subtractor to avoid instant motion triggers from old frames
            motion_detector = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=150, detectShadows=False)
            print("System Resumed.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
