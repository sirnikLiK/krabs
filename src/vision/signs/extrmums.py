import cv2
import numpy as np

# --- Color Threshold Tuner ---
# Purpose: A utility to find the best color thresholds (Low/High) for segmentation.
# NOTE: Although the Window and variables are named 'BGR' (Blue, Green, Red),
# the code converts the frame to HSV (Hue, Saturation, Value) on line 22 but uses these
# sliders as the bounds.
#
# Therefore:
#   'B' sliders actually control Channel 0: Hue (H)
#   'G' sliders actually control Channel 1: Saturation (S)
#   'R' sliders actually control Channel 2: Value (V)

def nothing(x):
    pass

cap = cv2.VideoCapture(1)

cv2.namedWindow('BGR_Settings')


# Trackbars for Lower and Upper bounds
# Although labeled B/G/R, they adjust H/S/V respectively due to the cvtColor call below.
cv2.createTrackbar('B_min', 'BGR_Settings', 0, 255, nothing) # Adjusts Hue Min
cv2.createTrackbar('G_min', 'BGR_Settings', 0, 255, nothing) # Adjusts Saturation Min
cv2.createTrackbar('R_min', 'BGR_Settings', 0, 255, nothing) # Adjusts Value Min
cv2.createTrackbar('B_max', 'BGR_Settings', 255, 255, nothing) # Adjusts Hue Max
cv2.createTrackbar('G_max', 'BGR_Settings', 255, 255, nothing) # Adjusts Saturation Max
cv2.createTrackbar('R_max', 'BGR_Settings', 255, 255, nothing) # Adjusts Value Max

while True:
    ret, frame = cap.read()
    # Convert frame to HSV (Hue, Saturation, Value)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if not ret:
        break

    # Read slider positions
    b_min = cv2.getTrackbarPos('B_min', 'BGR_Settings') # H min
    g_min = cv2.getTrackbarPos('G_min', 'BGR_Settings') # S min
    r_min = cv2.getTrackbarPos('R_min', 'BGR_Settings') # V min
    
    b_max = cv2.getTrackbarPos('B_max', 'BGR_Settings') # H max
    g_max = cv2.getTrackbarPos('G_max', 'BGR_Settings') # S max
    r_max = cv2.getTrackbarPos('R_max', 'BGR_Settings') # V max

    # Create arrays for bounds
    lower_bgr = np.array([b_min, g_min, r_min])
    upper_bgr = np.array([b_max, g_max, r_max])

    # Apply HSV thresholding
    mask = cv2.inRange(hsv, lower_bgr, upper_bgr)
    
    # Result: Show only the parts of the image that match the color range
    result = cv2.bitwise_and(hsv, hsv, mask=mask)

    cv2.imshow('BGR_Settings', result)
    cv2.imshow('Mask', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print(f"BGR Lower: [{b_min}, {g_min}, {r_min}]")
        print(f"BGR Upper: [{b_max}, {g_max}, {r_max}]")
        break

cap.release()
cv2.destroyAllWindows()