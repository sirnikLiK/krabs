import cv2
import numpy 

# --- Traffic Light Detection ---
# Purpose: Detect traffic light state (Red/Yellow/Green) by analyzing 
# color value sums in specific regions of interest (ROI).

stream_url = "http://10.160.166.218:5000/video_feed"

stream = cv2.VideoCapture(stream_url)
while(True):
    ret, frame = stream.read()
    # Resize frame to a small vertical strip (60x120)
    # This implies the camera is focused/cropped on a specific traffic light
    rgb = cv2.resize(frame,(60, 120))


    # Crop the traffic light region (approx vertical middle)
    cat = rgb[20:101, 8:27] 
    # Convert to HSV to analyze brightness/value
    hsv = cv2.cvtColor(cat, cv2.COLOR_BGR2HSV)
    v = hsv[:, :, 2] # V-channel (Brightness)

    # Calculate sum of brightness for each light position
    # Coordinates are hardcoded for a specific 60x120 image layout
    red_s = numpy.sum(v[0:27, 0:19])    # Top region (Red)
    yellow_s = numpy.sum(v[28:54, 0:19]) # Middle region (Yellow)
    green_s = numpy.sum(v[55:81, 0:19])  # Bottom region (Green)

    # Vizualize regions
    cv2.rectangle(cat, (0, 0), (19, 27), (0, 0, 255), 2)
    cv2.rectangle(cat, (0, 28), (19, 54), (0, 255, 255), 2)
    cv2.rectangle(cat, (0, 55), (19, 81), (0, 255, 0), 2)
    
    # Determine active light by comparing brightness sums
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