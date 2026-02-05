import cv2
import numpy as np
import time
import serial

# --- НАСТРОЙКИ SERIAL ---
SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2) 
    print(f"✅ Успешное подключение к {SERIAL_PORT}")
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    ser = None

# --- НАСТРОЙКИ МОДЕЛИ ---
net = cv2.dnn.readNetFromONNX("/home/stefano/Documents/ATS_nto (copy)/src/detection/models/best.onnx")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL)

cap = cv2.VideoCapture(0)
FRAME_W = 640
FRAME_H = 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
TOTAL_AREA = FRAME_W * FRAME_H

last_sent_speed = -1

while True:
    ret, frame = cap.read()
    if not ret: break

    # Препроцессинг
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (640, 640), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward()
    outputs = np.array([cv2.transpose(outputs[0])])
    
    rows = outputs[0].shape[0]
    boxes, confidences = [], []
    x_factor, y_factor = FRAME_W / 640, FRAME_H / 640

    max_person_area_pct = 0 # Процент площади самого "большого" человека

    for i in range(rows):
        prob = outputs[0][i][4]
        if prob >= 0.4:
            x, y, w, h = outputs[0][i][0:4]
            
            # Координаты для отрисовки
            left = int((x - 0.5 * w) * x_factor)
            top = int((y - 0.5 * h) * y_factor)
            width = int(w * x_factor)
            height = int(h * y_factor)
            
            boxes.append([left, top, width, height])
            confidences.append(float(prob))
            
            # Считаем площадь текущего объекта в % от кадра
            current_area_pct = (width * height) / TOTAL_AREA * 100
            if current_area_pct > max_person_area_pct:
                max_person_area_pct = current_area_pct

    # Отрисовка всех найденных (NMS чтобы не дублировать рамки)
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.4, 0.4)
    if len(indices) > 0:
        for i in indices.flatten():
            b = boxes[i]
            # Тонкая рамка (thickness=1)
            cv2.rectangle(frame, (b[0], b[1]), (b[0]+b[2], b[1]+b[3]), (0, 255, 0), 1)

    # --- ЛОГИКА СКОРОСТИ ---
    if max_person_area_pct == 0:
        # Людей нет - едем быстро
        current_speed = 100
    elif max_person_area_pct >= 5:
        # Человек слишком близко (занимает > 40% кадра)
        current_speed = 0
    elif max_person_area_pct <= 0.5:
        # Человек очень далеко
        current_speed = 100
    else:
        # Плавное замедление от 5% до 40% площади
        # Интерполяция: если 5% -> 100, если 40% -> 0
        interp = (max_person_area_pct - 0.3) / (6 - 0.3) # значение от 0.0 до 1.0
        current_speed = int(100 * (1 - interp))

    # Ограничение скорости (на всякий случай)
    current_speed = max(0, min(100, current_speed))

    # --- ОТПРАВКА В SERIAL ---
    if ser and current_speed != last_sent_speed:
        try:
            ser.write(f"{current_speed}\n".encode('utf-8'))
            last_sent_speed = current_speed
        except Exception as e:
            print(f"📡 Ошибка связи: {e}")

    # Инфо на экране
    cv2.putText(frame, f"Speed: {current_speed} | Area: {max_person_area_pct:.1f}%", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    cv2.imshow("Smart Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

if ser:
    ser.write(f"0\n".encode('utf-8'))
    ser.close()
cap.release()
cv2.destroyAllWindows()