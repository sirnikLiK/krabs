import cv2
import dlib
import os
import sys

# Determine the path to the SVM model
# Assuming the script is run from the project root or ped_detect folder, 
# we try to locate tld.svm relative to this script.
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "tld.svm")

if not os.path.exists(model_path):
    print(f"Error: Model file not found at {model_path}")
    sys.exit(1)

print(f"Loading model from {model_path}...")
detector = dlib.simple_object_detector(model_path)

cam = cv2.VideoCapture(0)

print("Starting camera... Press 'q' to quit.")

while True:
    ret, frame = cam.read()
    if not ret:
        print("Failed to grab frame")
        break

    # dlib requires RGB images
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Run detector
    # You can pass a second argument for upsampling (e.g., 1) to detect smaller objects,
    # but it will be slower. 0 means no upsampling.
    detections = detector(rgb_frame)

    for d in detections:
        # dlib rectangle: left, top, right, bottom
        x1, y1, x2, y2 = d.left(), d.top(), d.right(), d.bottom()
        
        # Draw rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        # Optional: Draw label
        cv2.putText(frame, "Traffic Light", (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) == ord("q"):
        break

cam.release()
cv2.destroyAllWindows()