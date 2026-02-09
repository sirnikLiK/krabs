import cv2
import serial
import time

# --- SETTINGS ---
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

# --- CONNECT TO ARDUINO ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)
    print(f"✅ Connected to {SERIAL_PORT}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    ser = None

# --- SETUP HOG DETECTOR ---
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
print("✅ HOG Descriptor initialized")

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

    # Resize for faster HOG detection (optional but recommended for HOG)
    # Using 640x480 is fine, but downscaling can speed it up
    # frame_resized = cv2.resize(frame, (400, 300))
    
    # Detect
    # winStride: step size
    # padding: pad around image
    # scale: image pyramid scale
    (rects, weights) = hog.detectMultiScale(frame, winStride=(8, 8), padding=(8, 8), scale=1.05)

    max_person_area_pct = 0
    
    for (x, y, w, h) in rects:
        # HOG often returns boxes inside one another, can apply NMS if needed.
        # For simplicity, we just take the largest area.
        
        area_pct = (w * h) / TOTAL_AREA * 100
        if area_pct > max_person_area_pct:
            max_person_area_pct = area_pct

        # Draw box
        color = (0, 255, 0) if current_speed > 0 else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    # --- SPEED LOGIC ---
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

    cv2.imshow("HOG Smart Stop", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
if ser:
    ser.write(b"0;90\n")
    ser.close()
cap.release()
cv2.destroyAllWindows()
