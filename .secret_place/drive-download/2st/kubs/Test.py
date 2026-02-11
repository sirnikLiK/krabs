import glob

import cv2
import numpy as np
import os
path = 'C:/Users/Nastya/Desktop/Pyton/NTO/marker/user_task/images'
files = glob.glob(os.path.join(path, '*jpg'))


k = 0
font = cv2.FONT_HERSHEY_COMPLEX
img_size = [300, 300]

color_dict = {
    0: (255, 255, 255),  # white
    1: (0, 0, 0),  # black
    2: (0, 0, 255),  # red
    3: (0, 136, 255),  # orange
    4: (0, 255, 255),  # yellow
    5: (0, 255, 0),  # green
    6: (255, 255, 0),  # cyan
    7: (255, 0, 0),  # blue
    8: (255, 0, 136),  # violet
    9: (255, 0, 255)
}  # magenta

while k < len(files) + 1:

    # -------------------------------------------------------------------------------------------------

    img2 = cv2.imread('forTest/'+str(k)+'.jpg')
    img2 = cv2.resize(img2, (img_size[1], img_size[0]))
    img2 = cv2.copyMakeBorder(
        img2,
        top=10,
        bottom=10,
        left=10,
        right=10,
        borderType=cv2.BORDER_CONSTANT,
        value=[163, 163, 163]
    )
    cv2.resize(img2, (300, 300))

    frame = img2.copy()
    img = cv2.inRange(img2, (152, 152, 152), (172, 172, 172))
    scr = np.float32([
        [0, img_size[0]],
        [img_size[1], img_size[0]],
        [img_size[1], 0],
        [0, 0]
    ])

    _, threshold = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    contours = contours[1]

    approx = cv2.approxPolyDP(contours, 0.009 * cv2.arcLength(contours, True), True)
    cv2.drawContours(img2, [approx], 0, (0, 0, 255), 2)
    n = approx.ravel()
    i = 0
    points = []
    for j in n:
        if i % 2 == 0:
            x = n[i]
            y = n[i + 1]
            string = str(x) + " " + str(y)

            if i == 0:
                cv2.putText(img2, string, (x, y), font, 0.5, (255, 0, 0))
            else:
                cv2.putText(img2, string, (x, y), font, 0.5, (0, 255, 0))
            points.append([x, y])
        i += 1
    if len(points) > 4:
        for c in range(16):
            br = False
            for i in range(len(points)):
                for j in range(len(points)):
                    if abs(points[i][0] - points[j][0]) < 20 and abs(points[i][1] - points[j][1]) < 20 and i != j:
                        br = True
                        points.pop(i)
                        break
                if br:
                    break
    if len(points) > 4:
        break

    points = np.float32(points)
    cv2.imshow('image2', img2)

    m = cv2.getPerspectiveTransform(points, scr)
    frame = cv2.warpPerspective(frame, m, (img_size[1], img_size[0]), flags=cv2.INTER_LINEAR)
    cv2.imshow("frame", frame)

    # -------------------------------------------------------------------------------------------------
    colors_list = []
    frame = frame[::-1]
    cv2.imshow('frame_flip', frame)
    count = 0
    while count < 4:
        colors = []
        for i in range(4):
            for j in range(4):
                x = int(j*37.5+37.5)
                y = int(i*37.5+37.5)
                pic_color = frame[int(i*75+37.5)][int(j*75+37.5)]
                pic_b = pic_color[0]
                pic_g = pic_color[1]
                pic_r = pic_color[2]
                for col_num, col_bgr in color_dict.items():
                    b_col = col_bgr[0]
                    g_col = col_bgr[1]
                    r_col = col_bgr[2]
                    if abs(b_col - pic_b) < 10 and abs(g_col - pic_g) < 10 and abs(r_col - pic_r) < 10:
                        colors.append(col_num)
                        break
        if (colors[1] + colors[4]) == 7 and (colors[8] + colors[13]) != 7:
            colors_list = colors[:]
            break
        else:
            count += 1
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    cv2.imshow('frame2', frame)
    cv2.imshow('img', img)

    key = cv2.waitKey(1)
    if key == ord('n'):
        cv2.destroyAllWindows()
        k += 1
        print(str(colors_list))
        print('KKKKKKKKKKKKK' + str(k))
    if key == ord('q'):
        cv2.destroyAllWindows()
        break
