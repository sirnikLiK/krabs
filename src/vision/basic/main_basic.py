import cv2
import time
# import serial

# Import our simple modules
from simple_lane import get_steering_angle
from simple_traffic import detect_traffic_light
from simple_signs import detect_sign

# --- CONFIG ---
SERIAL_PORT = '/dev/ttyACM0' 
DO_SERIAL = False # Set to True if Arduino is connected

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640) # Width
    cap.set(4, 480) # Height
    
    if DO_SERIAL:
        try:
            # ser = serial.Serial(SERIAL_PORT, 9600, timeout=1)
            pass
        except:
            print("Serial connection failed")
    
    print("Starting Main Basic Control...")
    
    speed = 0
    angle = 90
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # 1. Lane Detection
        angle, lane_debug = get_steering_angle(frame)
        
        # 2. Traffic Light
        tl_state, _ = detect_traffic_light(frame)
        
        # 3. Signs
        sign_shape, _ = detect_sign(frame)
        
        # --- LOGIC ---
        if tl_state == 'red':
            speed = 0
            print("STOP: Red Light")
        elif tl_state == 'yellow':
            speed = 30
            print("SLOW: Yellow Light")
        elif sign_shape == 'circle': 
            # Example: Circle means speed limit or stop?
            pass
        else:
            speed = 50 # Normal speed
            
        # --- SEND TO ARDUINO ---
        cmd = f"{speed};{angle}\n"
        # if DO_SERIAL: ser.write(cmd.encode())
        
        # --- DISPLAY ---
        cv2.putText(frame, f"Speed: {speed} Angle: {angle}", (10, 30), 0, 1, (255, 255, 0), 2)
        cv2.putText(frame, f"TL: {tl_state} Sign: {sign_shape}", (10, 70), 0, 0.7, (0, 255, 255), 2)
        
        # Stack images (optional)
        cv2.imshow("Main View", frame)
        cv2.imshow("Lane View", lane_debug)
        
        if cv2.waitKey(1) == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
