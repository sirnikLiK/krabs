from time import sleep
import numpy as np
import cv2


def make_mask(_frame):
    r = np.array(list(cutedFrame[:, :, 2]), dtype=int)
    g = np.array(list(_frame[:, :, 1]), dtype=int)
    b = np.array(list(_frame[:, :, 0]), dtype=int)
    dd = abs(r - g) + abs(b - g)
    ss = np.array(dd)
    mask_1 = cv2.inRange(ss, 0, 50)
    mask_1 = cv2.erode(mask_1, None, iterations=1)
    mask_1 = cv2.dilate(mask_1, None, iterations=3)
    mask_2 = cv2.inRange(cutedFrame, (55, 55, 55), (250, 250, 250))
    mask_2 = cv2.erode(mask_2, None, iterations=1)
    mask_2 = cv2.dilate(mask_2, None, iterations=2)
    hsv = cv2.cvtColor(cutedFrame, cv2.COLOR_BGR2HSV)
    m_3 = cv2.inRange(hsv[:, :, 1], 0, 90)
    m_3 = cv2.erode(m_3, None, iterations=1)
    m_3 = cv2.dilate(m_3, None, iterations=2)
    # mask_3 = cv2.inRange(cutedFrame, (80, 50, 85), (180, 180, 180))
    # cv2.imshow('mask_3', mask_3)
    cv2.imshow('vvv', hsv[:, :, 2])
    mask_5 = cv2.inRange(hsv[:, :, 2], 130, 255)
    #mask_5 = cv2.inRange(mask_5, 0, 0)
    mask_5 = cv2.erode(mask_5, None, iterations=1)
    mask_5 = cv2.dilate(mask_5, None, iterations=2)
    cv2.imshow('m5', mask_5)
    mask_4 = cv2.bitwise_and(mask_1, mask_2)
    mask_ = cv2.bitwise_and(mask_4, m_3)
    mask_ = cv2.erode(mask_, None, iterations=1)
    mask_ = cv2.dilate(mask_, None, iterations=2)
    mask_ = cv2.bitwise_and(mask_, mask_5)
    mask_ = cv2.inRange(mask_, 0, 0)
    #mask_ = cv2.bitwise_and(mask_, mask_5)
    return mask_


def make_presp(_contours, new_frame):
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


def know_color(marker_frame):
    # print('CCCCCCCCC', marker_frame)
    # marker_frame = cv2.flip(marker_frame, 0)
    n_f = marker_frame.copy()
    cv2.circle(n_f, (75, 75), 2, (0, 255, 0), 2)
    cv2.circle(n_f, (225, 75), 2, (0, 0, 255), 2)
    cv2.circle(n_f, (75, 225), 2, (0, 255, 255), 2)
    cv2.circle(n_f, (225, 225), 2, (255, 0, 0), 2)
    cv2.imshow('nf', n_f)
    print('BBBBBBBBBBBB', marker_frame[75, 75])
    count = 0
    colors_list = []
    while count < 4:
        colors = []
        for l in range(2):
            for j in range(2):
                color_dict = {
                    0: [(255, 255, 255), (225, 225, 225)],  # white
                    1: [(105, 105, 105), (55, 55, 55)],    # black
                    2: [(140, 145, 255), (80, 75, 200)],  # red
                    3: [(115, 215, 255), (70, 125, 220)],  # orange
                    4: [(75, 245, 245), (45, 215, 215)],  # yellow
                    5: [(135, 235, 75), (100, 180, 0)],  # green
                    6: [(260, 250, 20),(215, 200, 0)],  # cyan
                    7: [(255, 205, 55), (205, 150, 25)],  # blue
                    8: [(210, 155, 105),(175, 115, 75)],  # violet
                    9: [(255, 215, 255),(175, 125, 185)]  # pink
                }
                pic_color = marker_frame[int(l * 150 + 75), int(j * 150 + 75)]
                pic_b = pic_color[0]
                pic_g = pic_color[1]
                pic_r = pic_color[2]
                print(pic_color, j, l, colors, count)
                for col_num, col_bgr in color_dict.items():
                    b_col_mn = col_bgr[1][0]
                    g_col_mn = col_bgr[1][1]
                    r_col_mn = col_bgr[1][2]
                    b_col_mx = col_bgr[0][0]
                    g_col_mx = col_bgr[0][1]
                    r_col_mx = col_bgr[0][2]
                    if (b_col_mn <= pic_b <= b_col_mx) and (g_col_mn <= pic_g <= g_col_mx) and (r_col_mn <= pic_r <= r_col_mx):
                        colors.append(col_num)
                        break
        print("COLORS", colors)
        if len(colors) > 3:
            if (colors[0] + colors[1]) == 11 and (colors[0] + colors[2]) != 11:
                colors_list = colors[:]
                break
            else:
                count += 1
                print("POVOROT")
                marker_frame = cv2.rotate(marker_frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            count += 1
            print("BAD LEN")
    print('HHHHHHHHHHHHHHHHHHHH')
    return colors_list


font = cv2.FONT_HERSHEY_COMPLEX
img_size = [300, 370]
sdr = np.float32([
    [0, 300],
    [300, 300],
    [300, 0],
    [0, 0]
])

cap = cv2.VideoCapture('output10.avi')
markNum = {2, 9, 1, 7}
while True:
    ret, frame = cap.read()
    if not ret:
        break

    cutedFrame = frame[50:410, 140:400, :]
    blur = cv2.medianBlur(cutedFrame, 5)
    newFrame = cutedFrame.copy()

    mask = make_mask(cutedFrame)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) >= 4:
        contours_1 = sorted(contours, key=cv2.contourArea, reverse=True)
        for i in range(1, len(contours_1)):
            print("LEN CONTOURS", len(contours_1))
            contours = contours_1[i]

            cv2.drawContours(cutedFrame, contours, -1, (0, 255, 255), 2)
            x, y, w, h = 0, 0, 0, 0
            try:
                (x, y, w, h) = cv2.boundingRect(contours)
                marker = newFrame[y:y + h, x:x + w]
                cv2.rectangle(cutedFrame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            except():
                marker = cutedFrame
            # cv2.circle(marker, (10, 10), 2, (0, 255, 0), 2)
            cv2.imshow("MAAASK", mask)

            hh, ww, c = marker.shape
            if hh >= 8 and ww >= 8:
                pic = marker[7][7]
            else:
                pic = marker[0][0]

            if 85 < pic[0] < 175 and 35 < pic[2] < 123 and 55 < pic[2] < 120 \
                    and (pic[0] > pic[1] and pic[0] > pic[2]) and len(marker[0]) >= 5:
                # print('NO')
                marker = make_presp(contours, newFrame)
                # cv2.putText(cutedFrame, 'A', (10, 10), font, 0.5, (255, 0, 255))
            else:
                marker = cv2.resize(marker, (300, 300))
                # print("YES")

            # print('AAAAAAAAAAAAA', marker[75, 75])
            # print('MMMMMM', marker)
            colorsList = know_color(marker)
            print("COLORLIST", colorsList)
            if len(colorsList) != 0:

                cv2.circle(cutedFrame, ((x + w//2), (y + h//2)), 2, (255, 255, 0), 2)
                print("YEEEEEEEEEEEEEESS", i)
                colorMarker = set()
                for string_x in colorsList:
                    colorMarker.add(string_x)
                if markNum == colorMarker:
                    cv2.rectangle(cutedFrame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imshow('cut', cutedFrame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    sleep(0.1)
