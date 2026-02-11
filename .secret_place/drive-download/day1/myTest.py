import cv2
import numpy as np
import os

font = cv2.FONT_HERSHEY_COMPLEX
sdr = np.float32([
    [0, 300],
    [300, 300],
    [300, 0],
    [0, 0]
])

def make_bin_mask(frame):
    filter = np.array([[-1, -1, -1],
                       [-1, 8, -1],
                       [-1, -1, -1]], dtype=np.float32)
    img = cv2.resize(frame, (480, 270))
    imgfl = cv2.filter2D(img, -1, filter)
    cv2.imshow('fl', imgfl)
    binimg = cv2.inRange(imgfl, (20, 20, 20), (255, 255, 255))

    # binimg = cv2.dilate(binimg, None, iterations=2)
    # binimg = cv2.erode(binimg, None, iterations=1)
    cv2.imshow('bin', binimg)
    return binimg

def make_presp(_contours, new_frame, cutedFrame):
    approxx = cv2.approxPolyDP(contours, 0.009 * cv2.arcLength(contours, True), True)
    nn = approxx.ravel()
    ii = 0
    point = []
    left_nn = [100000, 100000]  # left
    right_nn = [0, 100000]  # buttom
    left_vv = [1000000, 0]  # right
    right_vv = [0, 0]  # up
    for _ in nn:
        if ii % 2 == 0:
            xx = nn[ii]
            yy = nn[ii + 1]
            if xx < left_nn[0]:  # and y < left_n[1]:
                left_nn[0] = xx
                left_nn[1] = yy
            if yy < right_nn[1]:  # and y < right_n[1]:
                right_nn[0] = xx
                right_nn[1] = yy
            if xx > right_vv[0]:
                right_vv[0] = xx
                right_vv[1] = yy
            if yy > left_vv[1]:
                left_vv[0] = xx
                left_vv[1] = yy
        ii += 1

    point.append(right_vv)
    point.append(left_vv)
    point.append(left_nn)
    point.append(right_nn)

    point = np.float32(point)
    # print(point)

    cv2.putText(cutedFrame, 'r_n', (right_nn[0], right_nn[1]), font, 0.5, (255, 0, 0))
    cv2.putText(cutedFrame, 'R_v', (right_vv[0], right_vv[1]), font, 0.5, (0, 255, 0))
    cv2.putText(cutedFrame, 'l_v', (left_vv[0], left_vv[1]), font, 0.5, (0, 255, 0))
    cv2.putText(cutedFrame, 'l_n', (left_nn[0], left_nn[1]), font, 0.5, (0, 255, 0))

    point = np.float32(point)
    mm = cv2.getPerspectiveTransform(point, sdr)
    new_frame = cv2.warpPerspective(new_frame, mm, (300, 300), flags=cv2.INTER_LINEAR)
    return new_frame

imPath = os.walk('images/images')
for i in imPath:
    imPath = i[2]
i = 0
while i < 20:
    frame = cv2.imread('images/images/' + imPath[i])
    frame = cv2.resize(frame, (480, 270))
    bin_img = make_bin_mask(frame)
    contours, _ = cv2.findContours(bin_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    cv2.drawContours(frame, contours, 0, (0, 0, 255), 2)
    n_f = frame.copy()
    pr = make_presp(contours[0], n_f, frame)
    cv2.imshow('frame', frame)
    cv2.imshow('pr', pr)
    key = cv2.waitKey(1)
    if key == ord('n'):
        cv2.destroyAllWindows()
        i += 1
    if key == ord('q'):
        cv2.destroyAllWindows()
        break