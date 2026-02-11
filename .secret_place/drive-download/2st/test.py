import cv2
import numpy
import os

imPath = os.walk('images')
for i in imPath:
    imPath = i[2]
i = 0
while i < 20:
    frame = cv2.imread('images/' + imPath[i])
    img = cv2.resize(frame, (480, 270))
    fr = img.copy()
    binimg = cv2.inRange(img, (0, 0, 0), (55, 55, 55))
    contours, _ = cv2.findContours(binimg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    kubs = 0
    lines = []
    for j in range(len(contours)):
        # cv2.drawContours(img, contours, j, (0, 0, 255), 2)
        (x, y, w, h) = cv2.boundingRect(contours[j])
        if w > 40 and h > 40:
            kubs += 1
            # cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            marker = img[y:y + h, x:x + w]
            bmarker = cv2.inRange(marker, (0, 0, 0), (55, 55, 55))
            bmarker = cv2.inRange(bmarker, 0, 0)
            bmarker = cv2.erode(bmarker, None, iterations=2)
            bmarker = cv2.dilate(bmarker, None, iterations=3)
            contours1, _ = cv2.findContours(bmarker, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours1 = sorted(contours1, key=cv2.contourArea, reverse=True)
            (mx1, my1, mx2, my2) = 600, 600, 0, 0
            for k in range(len(contours1)):
                (x1, y1, w1, h1) = cv2.boundingRect(contours1[k])
                if w1 > 30 or h1 > 30:
                    cv2.rectangle(marker, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2)
                    # print(j, k, x1, y1, x1+w1, y1+h1)
                    mx1, my1 = min(x1, mx1), min(y1, my1)
                    mx2, my2 = max(x1 + w1, mx2), max(y1+h1, my2)
            cv2.rectangle(marker, (mx1, my1), (mx2,  my2), (255, 0, 255), 1)
            cuted = bmarker[my1:my2, mx1:mx2]
            if numpy.sum(cuted) > 490000:
                lines.append(3)
            elif 490001 > numpy.sum(cuted) > 290000:
                lines.append(2)
            else:
                lines.append(1)
            # print(j, numpy.sum(cuted))
            # cv2.rectangle(img, (x, y), (x + w, y + h), (255,0, 0), 2)
            # cv2.drawContours(marker, contours1, 0, (0, 0, 255), 2)
            # cv2.imshow(str(j), marker)
            cv2.imshow('b'+str(j), cuted)
            #cv2.drawContours(img, contours, j, (0, 0, 255), 2)
    print(imPath[i][-10:], sorted(lines))



    cv2.imshow('img', img)
    cv2.imshow('bin', binimg)
    key = cv2.waitKey(1)
    if key == ord('n'):
        cv2.destroyAllWindows()
        i += 1
    if key == ord('q'):
        cv2.destroyAllWindows()
        break