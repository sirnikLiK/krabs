import cv2
import dlib
import numpy as np
import serial
import time

# --- НАСТРОЙКИ ---
SERIAL_PORT = '/dev/ttyACM0'  # Порт из твоего скриншота
BAUD_RATE = 9600
MODEL_PATH = "/home/stefano/Documents/ATS_nto/src/detection/tld_test.svm"

# --- ИНИЦИАЛИЗАЦИЯ SERIAL ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2) # Пауза для сброса Arduino
    print(f"✅ Успешное подключение к {SERIAL_PORT}")
except Exception as e:
    print(f"❌ Ошибка подключения к {SERIAL_PORT}: {e}")
    ser = None

# Инициализация детектора и камеры
detector = dlib.simple_object_detector(MODEL_PATH)
cap = cv2.VideoCapture(0)

current_speed = 0
last_sent_speed = -1

while True:
    ret, frame = cap.read()
    if not ret: break

    boxes = detector(frame)
    
    # Сбрасываем флаг детекции для текущего кадра
    traffic_light_found = False

    for box in boxes:
        traffic_light_found = True
        x1, y1, x2, y2 = box.left(), box.top(), box.right(), box.bottom()
        
        # Обрезаем ROI
        roi = frame[max(0, y1):min(frame.shape[0], y2), max(0, x1):min(frame.shape[1], x2)]
        if roi.size == 0: continue
        
        # Обработка цвета
        roi_viz = cv2.resize(roi, (150, 300))
        v = cv2.cvtColor(roi_viz, cv2.COLOR_BGR2HSV)[:, :, 2]

        red_s = np.sum(v[0:100, :])
        yellow_s = np.sum(v[100:200, :])
        green_s = np.sum(v[200:300, :])

        if red_s > yellow_s and red_s > green_s:
            current_speed = 0
            bgr = (0, 0, 255)
        elif green_s > red_s and green_s > yellow_s:
            current_speed = 100
            bgr = (0, 255, 0)
        else:
            #current_speed = 0
            bgr = (0, 255, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)

    # Если светофор исчез из кадра — останавливаемся (для безопасности)
    if not traffic_light_found:
        current_speed = 0

    # --- ОТПРАВКА ДАННЫХ ---
    if ser and current_speed != last_sent_speed:
        try:
            ser.write(f"{current_speed}\n".encode('utf-8'))
            print(f"🚀 Команда на Arduino: {current_speed}")
            last_sent_speed = current_speed
        except Exception as e:
            print(f"📡 Ошибка связи: {e}")

    cv2.imshow("Detection", frame)
    if cv2.waitKey(1) == ord('q'): break

if ser: ser.close()
cap.release()
cv2.destroyAllWindows()