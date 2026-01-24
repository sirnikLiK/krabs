import cv2
import numpy 

cap = cv2.VideoCapture(1)   
while(True):
    ret, frame = cap.read()
    rgb = cv2.resize(frame,(60, 120))


    cat = rgb[20:101, 8:27] 
    hsv = cv2.cvtColor(cat, cv2.COLOR_BGR2HSV)
    v = hsv[:, :, 2]

    red_s = numpy.sum(v[0:27, 0:19])
    yellow_s = numpy.sum(v[28:54, 0:19])
    green_s = numpy.sum(v[55:81, 0:19])

    cv2.rectangle(cat, (0, 0), (19, 27), (0, 0, 255), 2)
    cv2.rectangle(cat, (0, 28), (19, 54), (0, 255, 255), 2)
    cv2.rectangle(cat, (0, 55), (19, 81), (0, 255, 0), 2)
    
    if red_s > yellow_s and red_s > green_s:
        print("red")
    elif yellow_s > red_s and yellow_s > green_s:
        print("yellow")
    elif green_s > red_s and green_s > yellow_s:
        print("green")
    
    cv2.imshow("frame", rgb)
    cv2.imshow("cat", cat)
    cv2.imshow("v", v)
    if cv2.waitKey(1) == ord("q"):
        break



cap.release()
cv2.destroyAllWindows()    