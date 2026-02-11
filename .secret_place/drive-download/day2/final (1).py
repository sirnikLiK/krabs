import cv2
import numpy as np
import os

sdr = np.float32([
    [0, 0],
    [300, 0],
    [0, 300],
    [300, 300]
])

imPath = os.walk('images/images/')
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
    binimg = cv2.inRange(imgfl, (40, 40, 40), (255, 255, 255))
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
        if w > 60 and h > 60 and w - h <= 7:
            rect = cv2.minAreaRect(contours[j])  # пытаемся вписать прямоугольник
            box = cv2.boxPoints(rect)  # поиск четырех вершин прямоугольника
            box = np.int0(box)  # округление координат
            cv2.drawContours(img, [box], 0, (255, 0, 0), 2)
            box = list(box)
            box[2], box[3] = box[3], box[2]
            box = np.float32(box)
            mm = cv2.getPerspectiveTransform(box, sdr)
            marker = cv2.warpPerspective(img, mm, (300, 300), flags=cv2.INTER_LINEAR)
            red_mask = cv2.inRange(marker, (0, 0, 125), (75, 75, 255))
            green_mask = cv2.inRange(marker, (0, 125, 0), (100, 255, 160))

            cv2.imshow("mark"+str(j), green_mask)
    cv2.imshow("bin", binimg)
    cv2.imshow("imgfl", imgfl)
    cv2.imshow("img", img)
    key = cv2.waitKey(1)
    if key == ord('n'):
        cv2.destroyAllWindows()
        i += 1
    if key == ord('q'):
        cv2.destroyAllWindows()
        break