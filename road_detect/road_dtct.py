import cv2
import numpy as np
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Camera 1 failed, trying Camera 0...")
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open any camera.")
    exit()

img_size = [200, 360]

src = np.float32([[20,200], [350, 200], [275, 120], [85, 120]])
src_draw = np.array(src, dtype=np.int32)

dst = np.float32([[0, img_size[0]], [img_size[1], img_size[0]], [img_size[1], 0], [0, 0]])
dst_draw = np.array(dst, dtype=np.int32)


while(True):
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")
        break
        
    resized = cv2.resize(frame, (img_size[1], img_size[0]))
    
    r_channel = resized[:, :, 2]
    # g_channel = resized[:, :, 1]
    # b_channel = resized[:, :, 0]

    binnary=np.zeros_like(r_channel)
    binnary[(r_channel>100)] = 1
    
    hls = cv2.cvtColor(resized, cv2.COLOR_BGR2HLS)
    # h_channel = hls[:, :, 0]
    # l_channel = hls[:, :, 1]
    s_channel = hls[:, :, 2]

    binnary2=np.zeros_like(s_channel)
    binnary2[(s_channel>160)] = 1
    
    allbinnary = np.zeros_like(binnary)
    allbinnary[(binnary==1) | (binnary2==1)] = 255
    cv2.imshow("frame", allbinnary)
    allbinnary_vizual = allbinnary.copy()
    cv2.polylines(allbinnary_vizual, [src_draw], True, 255, 2)
    cv2.imshow("allbinnary_vizual", allbinnary_vizual)

    m = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(allbinnary, m, (img_size[1], img_size[0]), flags = cv2.INTER_LINEAR)
    cv2.imshow("warped", warped)

    histogram = np.sum(warped[warped.shape[0]//2:,:], axis=0)

    midpoint = histogram.shape[0]//2
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    out = warped.copy()
    cv2.line(out, (leftx_base, 0), (leftx_base, warped.shape[0]), 110, 2)
    cv2.line(out, (rightx_base, 0), (rightx_base, warped.shape[0]), 110, 2)
    cv2.imshow("out", out)
    

    windows = 9
    windows_high = int(warped.shape[0]/windows)
    windows_half_width = 25

    xcentre_left = leftx_base
    xcentre_right = rightx_base

    left_lane_inds = np.array([],dtype=np.int16)
    right_lane_inds = np.array([],dtype=np.int16)


    out = np.dstack((warped, warped, warped))
    nonzero = warped.nonzero()
    WhitePixelY = np.array(nonzero[0])
    WhitePixelX = np.array(nonzero[1])

    
    
    for window in range(windows):
        win_ylow = warped.shape[0] - (window+1)*windows_high
        win_yhigh = warped.shape[0] - window*windows_high
        win_x1 = xcentre_left - windows_half_width
        win_x2 = xcentre_left + windows_half_width
        win_x3 = xcentre_right - windows_half_width
        win_x4 = xcentre_right + windows_half_width
           
        cv2.rectangle(out, (win_x1, win_ylow), (win_x2, win_yhigh), (0, 255, 0), 2)
        cv2.rectangle(out, (win_x3, win_ylow), (win_x4, win_yhigh), (0, 255, 0), 2)
        
        gd_left_inds = ((WhitePixelY >= win_ylow) & (WhitePixelY < win_yhigh) & 
                        (WhitePixelX >= win_x1) & (WhitePixelX < win_x2)).nonzero()[0]
                        
        gd_right_inds = ((WhitePixelY >= win_ylow) & (WhitePixelY < win_yhigh) & 
                         (WhitePixelX >= win_x3) & (WhitePixelX < win_x4)).nonzero()[0]
        
        left_lane_inds = np.concatenate((left_lane_inds, gd_left_inds))
        right_lane_inds = np.concatenate((right_lane_inds, gd_right_inds))

        
        if len(gd_left_inds) > 50:
            xcentre_left = int(np.mean(WhitePixelX[gd_left_inds]))
        if len(gd_right_inds) > 50:
            xcentre_right = int(np.mean(WhitePixelX[gd_right_inds]))
        
    
    
        out[WhitePixelY[left_lane_inds], WhitePixelX[left_lane_inds]] = [255, 0, 0]
        out[WhitePixelY[right_lane_inds], WhitePixelX[right_lane_inds]] = [0, 0, 255]

    

    lefty = WhitePixelY[left_lane_inds]
    leftx = WhitePixelX[left_lane_inds]
    righty = WhitePixelY[right_lane_inds]
    rightx = WhitePixelX[right_lane_inds]

    if len(lefty) > 0 and len(righty) > 0:
        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)
        
        center_fit = (left_fit + right_fit) / 2

        for ver_ind in range(out.shape[0]):
            gor_ind = (center_fit[0]*ver_ind**2 +
                center_fit[1]*ver_ind +
                center_fit[2])
            
            cv2.circle(out, (int(gor_ind), ver_ind), 1, (255, 0, 255), 2)
    else:
         print("No lanes detected")

    cv2.imshow("out", out)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()