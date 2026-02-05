import cv2
import numpy as np
import serial
import time

# --- НАСТРОЙКИ ---
SERIAL_PORT = '/dev/ttyACM0'  # Твой порт
BAUD_RATE = 9600

# --- ИНИЦИАЛИЗАЦИЯ SERIAL ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)  # Пауза для инициализации Arduino
    print(f"✅ Успешное подключение к {SERIAL_PORT}")
except Exception as e:
    print(f"❌ Ошибка подключения к {SERIAL_PORT}: {e}")
    ser = None

# --- ИНИЦИАЛИЗАЦИЯ ДЕТЕКТОРА ЛЮДЕЙ (HOG) ---
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cap = cv2.VideoCapture(0)

current_speed = 100 # По умолчанию едем, если никого нет
last_sent_speed = -1

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Опционально: уменьшаем размер кадра для ускорения обработки
    frame_resized = cv2.resize(frame, (640, 480))

    # Обнаружение пешеходов
    # rects - список прямоугольников, где найдены люди
    (rects, weights) = hog.detectMultiScale(frame_resized, winStride=(8, 8), padding=(4, 4), scale=1.05)

    # Логика определения скорости:
    if len(rects) > 0:
        # Человек в кадре есть -> Скорость 0
        current_speed = 0
        color = (0, 0, 255) # Красный прямоугольник
    else:
        # Человека нет -> Скорость 100
        current_speed = 100
        color = (0, 255, 0) # Зеленый (не используется, так как рамок нет)

    # Рисуем рамки, если люди найдены
    for (x, y, w, h) in rects:
        cv2.rectangle(frame_resized, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame_resized, "PERSON: STOP", (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Индикация текущей команды на экране
    status_text = f"Speed: {current_speed}"
    cv2.putText(frame_resized, status_text, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # --- ОТПРАВКА ДАННЫХ В SERIAL ---
    # Отправляем только если скорость изменилась, чтобы не спамить в порт
    if ser and current_speed != last_sent_speed:
        try:
            ser.write(f"{current_speed}\n".encode('utf-8'))
            print(f"🚀 Команда отправлена: {current_speed}")
            last_sent_speed = current_speed
        except Exception as e:
            print(f"📡 Ошибка связи: {e}")

    # Показываем видео
    cv2.imshow("Human Detection", frame_resized)
    
    if cv2.waitKey(1) == ord('q'):
        break

# Очистка ресурсов
if ser:
    ser.close()
cap.release()
cv2.destroyAllWindows()