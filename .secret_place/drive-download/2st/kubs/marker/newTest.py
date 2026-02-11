import cv2
import numpy as np

fon = np.zeros((300, 300, 3), np.uint8)
fon[:] = (163, 163, 163)
font = cv2.FONT_HERSHEY_COMPLEX
img_size = [300, 300]

while 1 > 0:
    img2 = cv2.imread('images/z1kIVN4cYn-7ahb-4G7S-nY0M-HXqtLxZ2a8oA.jpg')
    img2 = cv2.resize(img2, (img_size[1], img_size[0]))
    row, col = img2.shape[:2]
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

    cv2.imshow('img', img)

    _, threshold = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    contours = contours[1]
    cv2.drawContours(frame, contours, -1, (0, 0, 0), 5)

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
        print(points)
        for c in range(16):
            br = False
            for i in range(len(points)):
                for j in range(len(points)):
                    if (abs(points[i][0] - points[j][0]) < 20 and abs(points[i][1] - points[j][1]) < 20) and i != j:
                        br = True
                        points.pop(i)
                        break
                if br:
                    break

    points = np.float32(points)
    cv2.imshow('image2', img2)

    #m = cv2.getPerspectiveTransform(points, scr)
    #frame = cv2.warpPerspective(frame, m, (img_size[1], img_size[0]), flags=cv2.INTER_LINEAR)
    cv2.imshow("frame", frame)


    key = cv2.waitKey(1)
    if key == ord('q'):
        cv2.destroyAllWindows()
        break
