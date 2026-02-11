import atexit
import time
import random
from pathlib import Path

import cv2
import numpy as np
import yolopy

from AcsPI import *

from arduino import Arduino
from road_utils import *
from Server import Server

model = yolopy.Model('best2.tmfile', use_uint8=True, use_timvx=True, cls_num=1)
model.set_anchors([18, 33, 33, 48, 25, 71, 58, 76, 40, 113, 87, 140])
server = Server()


def apply_perspective(frame, points):
    width, height = 640, 640
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    transformed = cv2.warpPerspective(frame, matrix, (width, height))
    return transformed


def detect_yolo(frame):
    # frame = apply_perspective(frame, [(511, 392), (725, 391), (406, 713), (841, 715)])

    classes, scores, boxes = model.detect(frame)

    return len(classes) > 0


DIST_METER = 1825  # ticks to finish 1m
CAR_SPEED = 1600
THRESHOLD = 200
CAMERA_ID = '/dev/video0'
ARDUINO_PORT = '/dev/ttyUSB0'

GO = 'GO'
STOP = 'STOP'
CROSS_STRAIGHT = 'CROSS_STRAIGHT'
CROSS_RIGHT = 'CROSS_RIGHT'
CROSS_LEFT = 'CROSS_LEFT'
_CROSS_LEFT_STRAIGHT = '_CROSS_LEFT_STRAIGHT'
_CROSS_LEFT_LEFT = '_CROSS_LEFT_LEFT'
_CROSS_LEFT_STRAIGHT_AGAIN = '_CROSS_LEFT_STRAIGHT_AGAIN'

PREV_SUBSTATE = None
SUBSTATE = None

START_ACTION = False

STATE = GO
PREV_STATE = None
last_detect = time.time()
last_acur_detect = time.time()
detect_count = 0
client = CheckClient(2, 'car')

arduino = Arduino(ARDUINO_PORT, baudrate=115_200, timeout=0.1)
time.sleep(2)
print("Arduino port:", arduino.port)

cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print('[ERROR] Cannot open camera ID:', CAMERA_ID)
    quit()


def fill_points(bin_frame):
    contours, _ = cv2.findContours(bin_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    new_mask = np.zeros_like(bin_frame)
    if contours:
        min_x = min(cv2.boundingRect(cnt)[0] for cnt in contours)
        max_x = max(cv2.boundingRect(cnt)[0] + cv2.boundingRect(cnt)[2] for cnt in contours)

        tolerance = 50

        left_contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[0] <= min_x + tolerance]
        right_contours = [cnt for cnt in contours if
                          cv2.boundingRect(cnt)[0] + cv2.boundingRect(cnt)[2] >= max_x - tolerance]

        cv2.drawContours(new_mask, left_contours, -1, 255, thickness=cv2.FILLED)
        cv2.drawContours(new_mask, right_contours, -1, 255, thickness=cv2.FILLED)
    return new_mask


find_lines = centre_mass2

for i in range(40):
    ret, frame = cap.read()

data = server.get_task()
while len(data) == 0:
    data = server.get_task()
    time.sleep(0.5)
algorithm = []
points = []
points_cnt = 0
prev_r = 0
prev_l = 0
for step in data:
    if step == "STRAIGHT":
        algorithm.append(CROSS_STRAIGHT)
    elif step == "RIGHT":
        algorithm.append(CROSS_RIGHT)
    elif step == "LEFT":
        algorithm.append(CROSS_LEFT)
    else:
        points.append(step)

current_step = 0

last_err = 0
while True:
    start_time = time.time()
    ret, frame = cap.read()
    if not ret:
        break

    orig_frame = frame.copy()
    frame = cv2.resize(frame, SIZE)

    if detect_yolo(trans_perspective(frame, TRAP, RECT, SIZE)):
        detect_count += 1
        print("temp detected", detect_count)
        if time.time() - last_acur_detect > 2 and detect_count > 2:
            last_acur_detect = time.time()
            print("DETECTED!")
            server.visit_point(points[points_cnt])
            points_cnt += 1

            # Останавливаем беспилотник
            arduino.stop()
            # Получаем данные от акселерометра
            client.send()
            response = client.get_output()
            # print(response)

            # Функция для перевода данных от акселерометра к массиву numpy
            def string_to_numpy_array(data_string: str, dtype=float) -> np.ndarray:
                string_numbers = data_string.split()
                numeric_values = list(map(dtype, string_numbers))
                numpy_array = np.array(numeric_values)
                return numpy_array

            # Загружаем модель классификатора из файла
            model = load_model('Class.h5')
            X_test = string_to_numpy_array(strintg_chis)
            X_test = np.expand_dims(X_test, axis=1)
            X_test = np.expand_dims(X_test, axis=0)
            # Определяем класс сценария разрушения
            y_pred = model.predict(X_test)
            predicted_classes = np.argmax(y_pred, axis=1)
            # print("Предсказанный класс:", predicted_classes[0])
            next_model_name = ["Regress_1.h5", "Regress_2.h5", "Regress_3.h5",
                               "Regress_4.h5", "Regress_5.h5", "Regress_6.h5",
                               "Regress_7.h5", "Regress_8.h5"]
            # Загружаем регрессионную модель для конкретного сценария
            model = load_model(next_model_name[predicted_classes[0]])
            # Определяем оставшийся срок службы и выводим в терминал
            y_pred = model.predict(X_test)
            y_pred = round(y_pred[0][0])
            print(y_pred)



    bin = binarize(frame, THRESHOLD)

    wrapped = fill_points(trans_perspective(bin, TRAP, RECT, SIZE))

    if time.time() - last_detect > 1:
        detect_count = 0

    bin_line = bin.copy()

    left, right = find_lines(wrapped)

    if STATE == CROSS_RIGHT:
        if not START_ACTION and not find_lines.left_found:
            START_ACTION = True

    if STATE == CROSS_RIGHT and START_ACTION:
        left = int(right - wrapped.shape[1] * 0.6)

        if detect_return_road(wrapped, find_lines.left_side_amount, find_lines.right_side_amount):
            STATE = GO

    if STATE == CROSS_STRAIGHT:
        if not START_ACTION:
            START_ACTION = True
            SUBSTATE = 0

    if STATE == CROSS_STRAIGHT and START_ACTION:
        if SUBSTATE == 0:
            bottom_offset_percet = 0.3
            line_amount_percent = 0.15
        else:
            bottom_offset_percet = 0.1
            line_amount_percent = 0.3

        pixel_offset = int(bin.shape[1] * 0.3)
        idx, max_dist = cross_center_path_v4_2(bin, pixel_offset=pixel_offset,
                                               bottom_offset_percent=bottom_offset_percet,
                                               line_amount_percent=line_amount_percent, show_all_lines=False)

        left = idx
        right = idx
        print(left, right)
        cv2.line(bin_line, (idx, 0), (idx, bin_line.shape[0]), 255)

        img_h, img_w = bin.shape[:2]
        h = int(0.9 * img_h)
        w = int(0.7 * img_w)
        cv2.line(bin_line, (w, h), (img_w, h), 200)  # hori
        cv2.line(bin_line, (w, 0), (w, img_h), 200)  # vert
        crop = bin[h:, w:]
        crop_pixels = crop.shape[0] * crop.shape[1]
        crop_white_pixels = np.sum(crop) // 255
        if crop_white_pixels == 0:
            SUBSTATE = 1

        if detect_return_road(wrapped, find_lines.left_side_amount, find_lines.right_side_amount) and not detect_stop2(
                wrapped):
            STATE = GO

    if STATE == CROSS_LEFT:
        STATE = _CROSS_LEFT_STRAIGHT
        meters = 0.4
        arduino.dist(int(DIST_METER * meters))
        print(f'Task: go {meters} meters ({int(DIST_METER * meters)} ticks)')

    if STATE == _CROSS_LEFT_STRAIGHT_AGAIN:
        pixel_offset = int(bin.shape[1] * 0.1)
        idx, max_dist = cross_center_path_v4_2(bin, pixel_offset=pixel_offset, line_amount_percent=0.3,
                                               bottom_offset_percent=0.1)
        idx = max(0, idx)
        left = idx
        right = idx
        cv2.line(bin_line, (idx, 0), (idx, bin_line.shape[0]), 255)

        if detect_return_road(wrapped, find_lines.left_side_amount, find_lines.right_side_amount) and not detect_stop2(
                wrapped):
            STATE = GO

    if STATE == _CROSS_LEFT_LEFT:
        # left = right = 0
        arduino.check()
        if arduino.waiting():
            arduino_status = arduino.read_data()
            if 'end' in arduino_status:
                STATE = _CROSS_LEFT_STRAIGHT_AGAIN
                # arduino.dist(int(DIST_METER*0.7))

    if STATE == _CROSS_LEFT_STRAIGHT:
        pixel_offset = int(bin.shape[1] * 0.3)
        idx, max_dist = cross_center_path_v4_2(bin, pixel_offset=pixel_offset)
        left = idx
        right = idx
        cv2.line(bin_line, (idx, 0), (idx, bin_line.shape[0]), 255)

        check_start = time.time()
        arduino.check()
        if arduino.waiting():
            arduino_status = arduino.read_data()
            if 'end' in arduino_status:
                STATE = _CROSS_LEFT_LEFT
                meters = 0.7
                arduino.dist(int(DIST_METER * meters))
                print(f'Task: go {meters} meters ({int(DIST_METER * meters)} ticks)')
    # --- GO LEFT END --- #
    left -= 60
    err = 0 - ((left + right) // 2 - wrapped.shape[1] // 2)
    prev_l = left
    prev_r = right
    angle = int(90 + KP * err + KD * (err - last_err))  # EXPERIMENT 90 -> 85
    last_err = err

    if STATE == _CROSS_LEFT_LEFT:
        angle = 120

    # angle += 5
    angle = min(max(50, angle), 120)

    if STATE == GO and detect_stop2(wrapped):
        START_ACTION = False
        if len(algorithm) == current_step:
            STATE = STOP
        else:
            STATE = algorithm[current_step]
            current_step += 1

    if PREV_STATE != STATE or PREV_SUBSTATE != SUBSTATE:
        print(f'STATE: {STATE} ({SUBSTATE})')
        PREV_STATE = STATE
        PREV_SUBSTATE = SUBSTATE

    if STATE != STOP:
        arduino.set_speed(CAR_SPEED)
        arduino.set_angle(angle)
    else:
        arduino.stop()

    end_time = time.time()

    fps = 1 / (end_time - start_time)
    if fps < 10:
        print(f'[WARNING] FPS is too low! ({fps:.1f} fps)')
