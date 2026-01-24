import cv2 as cv
cap = cv.VideoCapture(1)
 
while(True):
    

    ret, frame = cap.read()
    cv.imshow("frame", frame)
    if cv.waitKey(1)==ord("q"):
        break
cap.release()
cv.destroyAllWindows()
