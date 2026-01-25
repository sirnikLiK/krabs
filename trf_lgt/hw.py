import cv2 as cv
# --- Hardware Test Script ---
# Purpose: Simple script to test if the camera is working and readable.

cap = cv.VideoCapture(1)
 
while(True):
    ret, frame = cap.read()
    cv.imshow("frame", frame)
    if cv.waitKey(1)==ord("q"):
        break
cap.release()
cv.destroyAllWindows()
