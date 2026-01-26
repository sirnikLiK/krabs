import cv2
import numpy as np

# --- Configuration & Constants ---
# Defined image size for processing [Height, Width]
img_size = [200, 360] 

# Source points for perspective transform (Trapezoid on the road)
# Order: Bottom-Left, Bottom-Right, Top-Right, Top-Left
src = np.float32([[20, 200], [350, 200], [275, 120], [85, 120]])
src_draw = np.array(src, dtype=np.int32)

# Destination points for perspective transform (Rectangle from top view)
# Order: Bottom-Left, Bottom-Right, Top-Right, Top-Left
dst = np.float32([[0, img_size[0]], [img_size[1], img_size[0]], [img_size[1], 0], [0, 0]])
dst_draw = np.array(dst, dtype=np.int32)

# --- Camera Initialization ---
# Attempt to open the primary camera (index 1)
stream_url = "http://10.160.166.218:5000/video_feed"

cap = cv2.VideoCapture(stream_url)
if not cap.isOpened():
    print("Camera 1 failed, trying Camera 0...")
    # Fallback to secondary camera (index 0)
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open any camera.")
    exit()


while(True):
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")
        break
        
    # Resize frame for faster processing and to match calibration
    resized = cv2.resize(frame, (img_size[1], img_size[0]))
    
    # --- Color Thresholding ---
    # 1. Red Channel Mask (Good for white/yellow lines on dark road)
    r_channel = resized[:, :, 2]
    binnary=np.zeros_like(r_channel)
    # Filter pixels with Red value > 100
    binnary[(r_channel>100)] = 1
    
    # 2. Saturation Channel Mask (HLS Color Space) - Good for shadows/lighting changes
    hls = cv2.cvtColor(resized, cv2.COLOR_BGR2HLS)
    s_channel = hls[:, :, 2]
    binnary2=np.zeros_like(s_channel)
    # Filter pixels with Saturation > 160
    binnary2[(s_channel>160)] = 1
    
    # Combine both makes (Bitwise OR)
    allbinnary = np.zeros_like(binnary)
    allbinnary[(binnary==1) | (binnary2==1)] = 255
    
    # Vizualize the binary mask and the source points
    cv2.imshow("frame", allbinnary)
    allbinnary_vizual = allbinnary.copy()
    cv2.polylines(allbinnary_vizual, [src_draw], True, 255, 2)
    cv2.imshow("allbinnary_vizual", allbinnary_vizual)

    # --- Perspective Transform (Bird's Eye View) ---
    m = cv2.getPerspectiveTransform(src, dst)
    # Warp the binary image to top-down view
    warped = cv2.warpPerspective(allbinnary, m, (img_size[1], img_size[0]), flags = cv2.INTER_LINEAR)
    cv2.imshow("warped", warped)

    # --- Lane Finding: Histogram & Sliding Window ---
    # Take a histogram of the bottom half of the image
    histogram = np.sum(warped[warped.shape[0]//2:,:], axis=0)

    # Find the peak of the left and right halves of the histogram
    # These will be the starting point for the left and right lines
    midpoint = histogram.shape[0]//2
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    # Vizualize histogram peaks
    out = warped.copy()
    cv2.line(out, (leftx_base, 0), (leftx_base, warped.shape[0]), 110, 2)
    cv2.line(out, (rightx_base, 0), (rightx_base, warped.shape[0]), 110, 2)
    cv2.imshow("out", out)
    
    # Sliding Window Parameters
    windows = 9
    windows_high = int(warped.shape[0]/windows)
    windows_half_width = 25 # Width of the window +/- from center

    # Current positions to be updated for each window
    xcentre_left = leftx_base
    xcentre_right = rightx_base

    # Store indices of lane pixels
    left_lane_inds = np.array([],dtype=np.int16)
    right_lane_inds = np.array([],dtype=np.int16)

    # Create an output image to draw on and visualize the result
    out = np.dstack((warped, warped, warped))
    
    # Identify all non-zero pixels in the image
    nonzero = warped.nonzero()
    WhitePixelY = np.array(nonzero[0])
    WhitePixelX = np.array(nonzero[1])


    
    
    for window in range(windows):
        # Identify window boundaries in x and y (and right and left)
        win_ylow = warped.shape[0] - (window+1)*windows_high
        win_yhigh = warped.shape[0] - window*windows_high
        win_x1 = xcentre_left - windows_half_width
        win_x2 = xcentre_left + windows_half_width
        win_x3 = xcentre_right - windows_half_width
        win_x4 = xcentre_right + windows_half_width
           
        # Draw the windows on the visualization image
        cv2.rectangle(out, (win_x1, win_ylow), (win_x2, win_yhigh), (0, 255, 0), 2)
        cv2.rectangle(out, (win_x3, win_ylow), (win_x4, win_yhigh), (0, 255, 0), 2)
        
        # Identify the nonzero pixels in x and y within the window
        gd_left_inds = ((WhitePixelY >= win_ylow) & (WhitePixelY < win_yhigh) & 
                        (WhitePixelX >= win_x1) & (WhitePixelX < win_x2)).nonzero()[0]
                        
        gd_right_inds = ((WhitePixelY >= win_ylow) & (WhitePixelY < win_yhigh) & 
                         (WhitePixelX >= win_x3) & (WhitePixelX < win_x4)).nonzero()[0]
        
        # Append these indices to the lists
        left_lane_inds = np.concatenate((left_lane_inds, gd_left_inds))
        right_lane_inds = np.concatenate((right_lane_inds, gd_right_inds))

        # If you found > 50 pixels, recenter next window on their mean position
        if len(gd_left_inds) > 50:
            xcentre_left = int(np.mean(WhitePixelX[gd_left_inds]))
        if len(gd_right_inds) > 50:
            xcentre_right = int(np.mean(WhitePixelX[gd_right_inds]))
        
    
        # Color the identified lane pixels (Red for left, Blue for right)
        out[WhitePixelY[left_lane_inds], WhitePixelX[left_lane_inds]] = [255, 0, 0]
        out[WhitePixelY[right_lane_inds], WhitePixelX[right_lane_inds]] = [0, 0, 255]

    

    lefty = WhitePixelY[left_lane_inds]
    leftx = WhitePixelX[left_lane_inds]
    righty = WhitePixelY[right_lane_inds]
    rightx = WhitePixelX[right_lane_inds]

    # --- Polynomial Fitting (Curvature Calculation) ---
    if len(lefty) > 0 and len(righty) > 0:
        # Fit a second order polynomial to each
        # Returns [A, B, C] for Ax^2 + Bx + C
        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)
        
        # Calculate the center of the lane (average of left and right polylines)
        center_fit = (left_fit + right_fit) / 2

        # Draw the calculated path
        for ver_ind in range(out.shape[0]):
            # Calculate x position for each y position (ver_ind)
            gor_ind = (center_fit[0]*ver_ind**2 +
                center_fit[1]*ver_ind +
                center_fit[2])
            
            # Draw point (line thickness = 1 makes it look like a curve)
            cv2.circle(out, (int(gor_ind), ver_ind), 1, (255, 0, 255), 2)
    else:
         print("No lanes detected")

    cv2.imshow("out", out)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()