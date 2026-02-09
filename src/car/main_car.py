import cv2
import time
from car_vision import CarVision

# --- STATES ---
STATE_IDLE = 0
STATE_FOLLOW = 1
STATE_AVOID = 2
STATE_STOP = 3

STATE_NAMES = {
    0: "IDLE",
    1: "FOLLOW",
    2: "AVOID",
    3: "STOP"
}

def main():
    print("--- CAR SYSTEM STARTING ---")
    
    vision = CarVision()
    cap = cv2.VideoCapture(0)
    
    current_state = STATE_IDLE
    speed = 0
    steering = 90 # 90 is straight
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # Vision Processing
        leader_box = vision.track_leader(frame)
        debris_detected = vision.detect_debris(frame)
        
        # --- STATE MACHINE ---
        if current_state == STATE_IDLE:
            speed = 0
            if leader_box:
                print("Leader detected! Following...")
                current_state = STATE_FOLLOW
        
        elif current_state == STATE_FOLLOW:
            if debris_detected:
                print("Debris! Taking evasive action.")
                current_state = STATE_AVOID
            elif leader_box:
                # PID / Simple P logic
                error = vision.get_steering_error(frame, leader_box)
                steering = 90 + int(error * 45) # Max 45 deg turn
                
                # Distance control based on box width (larger box = closer)
                _, _, w, h = leader_box
                if w > 150: # Too close
                    speed = 0
                elif w < 50: # Too far
                    speed = 60
                else: # Good distance
                    speed = 40
            else:
                print("Lost leader...")
                speed = 0
                # Optionally switch to lane following or search mode
        
        elif current_state == STATE_AVOID:
            # Simple open-loop avoidance or complex path planning
            speed = 30
            steering = 60 # Turn left/right to avoid
            # Check if clear, then return to FOLLOW
            if not debris_detected:
                current_state = STATE_FOLLOW
                
        elif current_state == STATE_STOP:
            speed = 0
            
        # --- OUTPUT ---
        # Draw Debug
        if leader_box:
            x, y, w, h = leader_box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "LEADER", (x, y-10), 0, 0.5, (0, 255, 0), 1)
            
        cv2.putText(frame, f"State: {STATE_NAMES[current_state]}", (10, 30), 0, 1, (0, 255, 255), 2)
        cv2.putText(frame, f"Speed: {speed} Angle: {steering}", (10, 70), 0, 1, (255, 255, 0), 2)
        
        cv2.imshow("Car View", frame)
        
        if cv2.waitKey(1) == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
