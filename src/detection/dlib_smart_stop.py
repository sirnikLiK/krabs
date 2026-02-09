import cv2
import dlib
import serial
import time
import os

# --- SETTINGS ---
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600
SVM_MODEL_PATH = "tld.svm"  # Ensure this file is in the same directory

# --- CONNECT TO ARDUINO ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)
    print(f"✅ Connected to {SERIAL_PORT}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    ser = None

# --- LOAD DLIB MODEL ---
if not os.path.exists(SVM_MODEL_PATH):
    print(f"❌ SVM model file not found: {SVM_MODEL_PATH}")
    exit()

try:
    detector = dlib.simple_object_detector(SVM_MODEL_PATH)
    print(f"✅ Loaded SVM model: {SVM_MODEL_PATH}")
except Exception as e:
    print(f"❌ Failed to load SVM model: {e}")
    exit()

# --- CAMERA SETUP ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

# Set resolution
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

    # Convert to RGB for dlib
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect
    detections = detector(rgb_frame)

    max_person_area_pct = 0
    
    for d in detections:
        x1, y1, x2, y2 = d.left(), d.top(), d.right(), d.bottom()
        w = x2 - x1
        h = y2 - y1
        
        # Calculate area percentage
        area_pct = (w * h) / TOTAL_AREA * 100
        if area_pct > max_person_area_pct:
            max_person_area_pct = area_pct

        # Draw box
        color = (0, 255, 0) if current_speed > 0 else (0, 0, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    # --- SPEED LOGIC ---
    # Same logic as YOLO version
    STOP_THRESHOLD_PCT = 10.0 
    SLOW_START_PCT = 1.0     
    
    if max_person_area_pct >= STOP_THRESHOLD_PCT:
        current_speed = 0
    elif max_person_area_pct <= SLOW_START_PCT:
        current_speed = 100
    else:
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

    # Info Overlay
    cv2.putText(frame, f"Speed: {current_speed}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(frame, f"Max Area: {max_person_area_pct:.1f}%", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Dlib Smart Stop", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
if ser:
    ser.write(b"0;90\n")
    ser.close()
cap.release()
cv2.destroyAllWindows()
