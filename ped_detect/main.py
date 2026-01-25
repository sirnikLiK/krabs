import cv2
import dlib

model_detector = dlib.simple_object_detector("tld.svm")
cam = cv2.VideoCapture(1)

while(True):
    ret, frame = cam.read()
    
    boxes = model_detector(frame)
    for box in boxes:
        print(box)
        (x, y, w, h) = (box.left(), box.top(), box.right(), box.bottom())
        cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) == ord("q"):
        break

cam.release()
cv2.destroyAllWindows()
    
