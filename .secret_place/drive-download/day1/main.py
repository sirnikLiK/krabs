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
    filter = np.array([[-1, -1, -1],
                        [-1, 8, -1],
                        [-1, -1, -1]], dtype=np.float32)
    img = cv2.resize(frame, (480, 270))
    imgfl = cv2.filter2D(img, -1, filter) #delta=100)
    binimg = cv2.inRange(imgfl, (35, 35, 35), (255, 255, 255))
    # binimg = cv2.erode(binimg, None, iterations=1)
    binimg = cv2.dilate(binimg, None, iterations=1)
    binimg = cv2.erode(binimg, None, iterations=1)
    #binimg = cv2.inRange(binimg, 0, 0)
    contours, _ = cv2.findContours(binimg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    kubs = 0
    lines = []
    x_coordinates = []
    y_coordinates = []
    cv2.drawContours(imgfl, contours[0], -1, (0, 0, 255), 2)
    for j in range(len(contours)):
        # cv2.drawContours(img, contours, j, (0, 0, 255), 2)
        (x, y, w, h) = cv2.boundingRect(contours[j])
        if w > 40 and h > 40 and w-h <= 10:
            kubs += 1
            #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            marker = img[y:y + h, x:x + w]

            cv2.drawContours(imgfl, contours[j], 0, (0, 0, 255), 2)
            same = False
            cv2.circle(imgfl, ((x + w // 2), (y + h // 2)), 2, (255, 255, 0), 2)
            for ii in range(len(x_coordinates)):
                if abs((x + w // 2) - x_coordinates[ii]) < 10 and abs((y + h // 2) - y_coordinates[ii]) < 10:
                    same = True
                    break
            if not same:
                kubs += 1
                x_coordinates.append(x + w // 2)
                y_coordinates.append(y + h // 2)
                cv2.rectangle(imgfl, (x, y), (x + w, y + h), (255, 0, 0), 2)
                marker_r = cv2.inRange(marker, (0, 0, 150), (100, 100, 255))
                marker_r = cv2.inRange(marker, (0, 0, 150), (100, 100, 255))
                cv2.imshow("mark"+str(j), marker)
    cv2.imshow("imgfl", binimg)
    cv2.imshow("img", imgfl)
    key = cv2.waitKey(1)
    if key == ord('n'):
        cv2.destroyAllWindows()
        i += 1
    if key == ord('q'):
        cv2.destroyAllWindows()
        break