import cv2
import dlib

# --- Pedestrian/Object Detector ---
# Purpose: Uses a trained SVM model ('tld.svm') to detect objects in the video feed.

# Load the trained dlib detector
model_detector = dlib.simple_object_detector("tld.svm")
cap = cv2.VideoCapture(1)

while(True):
    ret, frame = cap.read()
    
    # Run detector on the frame
    # Returns a list of dlib.rectangle objects
    boxes = model_detector(frame)
    for box in boxes:
        print(box)
        # Extract coordinates
        (x, y, w, h) = (box.left(), box.top(), box.right(), box.bottom())
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
    
