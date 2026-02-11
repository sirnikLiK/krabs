from time import sleep
import numpy as np
import cv2
font = cv2.FONT_HERSHEY_COMPLEX

cap = cv2.VideoCapture('output2.avi')
for k in range(1):
    cap = cv2.VideoCapture('output2.avi')
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('video feed', frame)
        binary = []
        cutedFrame = frame[50:420, 150:450, :]
        # hsv = cv2.cvtColor(cutedFrame, cv2.COLOR_BGR2HSV)
        # s_mask = cv2.inRange(hsv[:, :, 1], 100, 200)
        # cv2.imshow('hsv', hsv[:, :, 1])
        # cv2.imshow('hsv2', s_mask)
        blur = cv2.medianBlur(cutedFrame, 5)
        # sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        # cutedFrame = cv2.filter2D(blur, -1, sharpen_kernel)
        rr = np.array(list(cutedFrame[:, :, 2]), dtype=int)
        gg = np.array(list(cutedFrame[:, :, 1]), dtype=int)
        bb = np.array(list(cutedFrame[:, :, 0]), dtype=int)
        d = abs(rr - gg) + abs(bb-gg)
        s = np.array(d)
        mask1 = cv2.inRange(s, 0, 43)
        mask1 = cv2.erode(mask1, None, iterations=1)
        mask1 = cv2.dilate(mask1, None, iterations=3)
        cv2.imshow('ss', mask1)
        mask2 = cv2.inRange(cutedFrame, (82, 82, 82), (240, 240, 240))
        mask2 = cv2.erode(mask2, None, iterations=1)
        mask2 = cv2.dilate(mask2, None, iterations=2)
        cv2.imshow('mask2', mask2)
        mask = cv2.bitwise_and(mask1, mask2)
        mask = cv2.erode(mask, None, iterations=1)
        mask = cv2.dilate(mask, None, iterations=2)
        # mask = cv2.inRange(mask, 0, 0)

        '''
        _, threshold = cv2.threshold(mask, 110, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        contours = contours[1]
        approx = cv2.approxPolyDP(contours, 0.009 * cv2.arcLength(contours, True), True)
        cv2.drawContours(cutedFrame, [approx], 0, (0, 255, 255), 2)
        '''

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        if len(contours) >= 3:
            contours = contours[2]
        else:
            contours = contours
        cv2.drawContours(cutedFrame, contours, -1, (0, 255, 255), 2)
        (x, y, w, h) = cv2.boundingRect(contours)
        cv2.rectangle(cutedFrame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        '''
        point = tuple(contours[:, 0][contours[:, :, 0].argmin()])
        cv2.putText(cutedFrame, 'A', (point[0], point[1]), font, 0.5, (0, 255, 0))
        '''

        cv2.imshow('cut', cutedFrame)
        cv2.imshow("MAAASK", mask)

        '''
        approx = cv2.approxPolyDP(contours, 0.009 * cv2.arcLength(contours, True), True)

        n = approx.ravel()
        i = 0
        points = []
        left_n = [100000, 100000]
        right_n = [0, 100000]
        left_v = [1000000, 0]
        right_v = [0, 0]
        for j in n:
            if i % 2 == 0:
                x = n[i]
                y = n[i + 1]
                string = str(x) + " " + str(y)
                '''
        '''
                if i == 0:
                    cv2.putText(frame, string, (x, y), font, 0.5, (255, 0, 0))
                else:
                    cv2.putText(frame, string, (x, y), font, 0.5, (0, 255, 0))
                points.append([x, y])
                '''
        '''
                if x < left_n[0] and y < left_n[1]:
                    left_n[0] = x
                    left_n[1] = y
                if x > right_n[0] and y < right_n[1]:
                    right_n[0] = x
                    right_n[1] = y
                if x > right_v[0] and y > right_v[1]:
                    right_v[0] = x
                    right_v[1] = y
                if x < left_v[0] and y > left_v[1]:
                    left_v[0] = x
                    left_v[1] = y
            i += 1

        points.append(right_v)
        points.append(right_n)
        points.append(left_v)
        points.append(left_n)

        cv2.putText(cutedFrame, 'right_n', (right_n[0], right_n[1]), font, 0.5, (0, 255, 0))
        cv2.putText(cutedFrame, 'R_v', (right_v[0], right_v[1]), font, 0.5, (0, 255, 0))
        cv2.putText(cutedFrame, 'l_v', (left_v[0], left_v[1]), font, 0.5, (0, 255, 0))
        cv2.putText(cutedFrame, 'l_n', (left_n[0], left_n[1]), font, 0.5, (0, 255, 0))
        cv2.imshow('sharp', cutedFrame)
        '''
        cv2.imshow("MAAASK", mask)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        sleep(0.1)
cap.release()
cv2.destroyAllWindows()
