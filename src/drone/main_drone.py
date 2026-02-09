import cv2
import time
from drone_vision import DroneVision

# --- STATES ---
STATE_DISARMED = 0
STATE_TAKEOFF = 1
STATE_SCAN_FACADES = 2
STATE_SCAN_ROAD = 3
STATE_LAND = 4
STATE_FINISHED = 5

STATE_NAMES = {
    0: "DISARMED",
    1: "TAKEOFF",
    2: "SCAN_FACADES",
    3: "SCAN_ROAD",
    4: "LAND",
    5: "FINISHED"
}

def main():
    print("--- DRONE SYSTEM STARTING ---")
    
    # Initialize Vision
    vision = DroneVision()
    
    # Initialize Camera
    cap = cv2.VideoCapture(0) # Use drone camera stream
    
    current_state = STATE_DISARMED
    state_start_time = time.time()
    
    # Simulation variables
    facades_scanned = 0
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # --- STATE MACHINE LOGIC ---
        if current_state == STATE_DISARMED:
            # Wait for start command
            cv2.putText(frame, "WAITING FOR START (Press 's')", (50, 240), 0, 1, (0, 255, 255), 2)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                current_state = STATE_TAKEOFF
                state_start_time = time.time()
                print("Taking off...")

        elif current_state == STATE_TAKEOFF:
            # Simulate takeoff duration
            if time.time() - state_start_time > 3.0:
                current_state = STATE_SCAN_FACADES
                print("Taking off complete. Starting Facade Scan.")
            else:
                 cv2.putText(frame, "TAKING OFF...", (50, 240), 0, 1, (0, 255, 0), 2)

        elif current_state == STATE_SCAN_FACADES:
            # TODO: Implement actual flight path logic here
            
            # Run vision
            defects = vision.detect_defects(frame)
            vision.draw_detections(frame, defects, (0, 0, 255))
            
            status_text = f"Scanning Facade... Found: {len(defects)}"
            cv2.putText(frame, status_text, (20, 50), 0, 0.7, (255, 255, 0), 2)
            
            # Simulate finding 2 facades then moving on
            # In real life, use telemetry/markers
            if time.time() - state_start_time > 10.0: # Mock 10s scan
                current_state = STATE_SCAN_ROAD
                state_start_time = time.time()
                print("Facade Scan Complete. Moving to Road Scan.")

        elif current_state == STATE_SCAN_ROAD:
            # Run vision
            debris = vision.detect_debris(frame)
            vision.draw_detections(frame, debris, (0, 165, 255))
            
            status_text = f"Scanning Road... Found: {len(debris)}"
            cv2.putText(frame, status_text, (20, 50), 0, 0.7, (255, 255, 0), 2)
            
            if time.time() - state_start_time > 10.0:
                current_state = STATE_LAND
                state_start_time = time.time()
                print("Road Scan Complete. Landing.")

        elif current_state == STATE_LAND:
             if time.time() - state_start_time > 3.0:
                current_state = STATE_FINISHED
                print("Landed.")
             else:
                 cv2.putText(frame, "LANDING...", (50, 240), 0, 1, (0, 255, 0), 2)
                 
        elif current_state == STATE_FINISHED:
            cv2.putText(frame, "MISSION COMPLETE", (50, 240), 0, 1, (0, 255, 0), 3)
            
        # Display State
        cv2.putText(frame, f"State: {STATE_NAMES[current_state]}", (10, 450), 0, 0.6, (255, 255, 255), 1)
        
        cv2.imshow("Drone View", frame)
        if cv2.waitKey(1) == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
