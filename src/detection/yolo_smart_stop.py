import cv2
import serial
import time
from ultralytics import YOLO

# --- SETTINGS ---
SERIAL_PORT = '/dev/ttyACM0'  # Adjust if needed
BAUD_RATE = 9600
MODEL_PATH = "/home/stefano/Documents/ATS_nto/src/detection/best.pt" # Assumes best.pt is in the same directory or provide absolute path
CONF_THRESHOLD = 0.5

# --- CONNECT TO ARDUINO ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)  # Wait for Arduino reset
    print(f"✅ Connected to {SERIAL_PORT}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    ser = None

# --- LOAD YOLO MODEL ---
try:
    model = YOLO(MODEL_PATH)
    print(f"✅ Model loaded: {MODEL_PATH}")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    exit()

# --- CAMERA SETUP ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

# Set resolution (optional, for performance)
FRAME_W = 640
FRAME_H = 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
TOTAL_AREA = FRAME_W * FRAME_H

last_sent_speed = -1
current_speed = 100

print("🚀 System started. Press 'q' to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO detection
    results = model(frame, verbose=False, stream=True)

    max_person_area_pct = 0
    detections = []

    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Check if it is a person (class 0 in COCO, or check your custom model classes)
            # Assuming class 0 is person or single class model
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            # If your model has specific classes, check names: model.names[cls_id]
            # For now, we assume everything detected is what we want or check for 'person'
            # if model.names[cls_id] != 'person': continue 

            if conf > CONF_THRESHOLD:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w = x2 - x1
                h = y2 - y1
                
                area_pct = (w * h) / TOTAL_AREA * 100
                if area_pct > max_person_area_pct:
                    max_person_area_pct = area_pct
                
                detections.append((x1, y1, x2, y2, conf))

    # --- SPEED LOGIC ---
    # 0% - 5% area: Speed 100
    # 5% - 10% area: Speed decreases 100 -> 0
    # > 10% area: Speed 0 (STOP)
    
    # Let's use the user's requested 5-10% range logic more strictly
    # "when he was about 5-10 percent of the area on the camera he stopped completely"
    
    STOP_THRESHOLD_PCT = 10.0 # Completely stop here
    SLOW_START_PCT = 1.0      # Start slowing down from here (1%)
                              # Adjusted from 5% to start slowing earlier for smoother stop, 
                              # or can map 0-10 directly.
    
    if max_person_area_pct >= STOP_THRESHOLD_PCT:
        current_speed = 0
    elif max_person_area_pct <= SLOW_START_PCT:
        current_speed = 100
    else:
        # Linear mapping from SLOW_START_PCT (100 speed) to STOP_THRESHOLD_PCT (0 speed)
        # speed = 100 * (1 - (current - start) / (end - start))
        ratio = (max_person_area_pct - SLOW_START_PCT) / (STOP_THRESHOLD_PCT - SLOW_START_PCT)
        current_speed = int(100 * (1.0 - ratio))
        if current_speed < 0: current_speed = 0

    # --- SERIAL COMMUNICATION ---
    if ser and current_speed != last_sent_speed:
        try:
            ser.write(f"{current_speed};90\n".encode('utf-8'))
            print(f"📡 Sent: {current_speed} (Max Area: {max_person_area_pct:.1f}%)")
            last_sent_speed = current_speed
        except Exception as e:
            print(f"Error writing to serial: {e}")

    # --- VISUALIZATION ---
    for (x1, y1, x2, y2, conf) in detections:
        color = (0, 255, 0) if current_speed > 0 else (0, 0, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Info Overlay
    cv2.putText(frame, f"Speed: {current_speed}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(frame, f"Max Area: {max_person_area_pct:.1f}%", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("YOLO Smart Stop", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
if ser:
    ser.write(b"0;90\n")
    ser.close()
cap.release()
cv2.destroyAllWindows()
