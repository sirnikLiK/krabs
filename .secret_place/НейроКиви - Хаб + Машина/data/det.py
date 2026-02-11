import argparse
import time
from pathlib import Path

import cv2
import numpy as np
import serial
import yolopy

from arduino import Arduino
from utils import *



ARDUINO_PORT = '/dev/ttyUSB0'
CAMERA_ID = '/dev/video0'


cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('./output10.avi', fourcc, 30, (1280, 720))

model_file = 'yolo_best_uint8.tmfile'
model = yolopy.Model(model_file, use_uint8=True, use_timvx=True, cls_num=12)
try:
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        classes, scores, boxes = model.detect(frame)
        print('Objects was detect:', len(classes))
        out.write(frame)
        # img = cv2.resize(frame, SIZE)
        # binary = binarize(img, THRESHOLD)
        # perspective = trans_perspective(binary, TRAP, RECT, SIZE)
        #
        # left, right = centre_mass(perspective)
        # bottom = perspective[150:250, :]
        # #cv2.imshow('bot', bottom)
        # if np.sum(bottom) > 1300000:
        #     old = time.time()
        #     #arduino.stop()
        #     #while time.time() - old < 0.1:
        #     #     continue
        #     arduino.set_angle(90)
        #     arduino.set_speed(CAR_SPEED)
        #     arduino.dist(CAR_SPEED, METER)
        #     print("STOOOOOOOOOOOOP")
        # err = 0 - ((left + right) // 2 - SIZE[0] // 2)
        # if abs(right - left) < 100:
        #     err = last_err
        #
        # angle = int(90 + KP * err + KD * (err - last_err))
        #
        # if angle < 60:
        #     angle = 60
        # elif angle > 120:
        #     angle = 120
        #
        # last_err = err
        # print(f'angle={angle}')
        # arduino.set_angle(angle)
except KeyboardInterrupt as e:
    print('Program stopped!', e)


arduino.stop()
arduino.set_angle(90)
cap.release()
out.release()
