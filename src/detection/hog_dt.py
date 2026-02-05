import cv2
import serial
import time

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

# --- ИНИЦИАЛИЗАЦИЯ ДЕТЕКТОРА HOG ---
hog = cv2.dnn.readNetFromONNX("/home/stefano/Documents/ATS_nto (copy)/src/detection/models/best.onnx") # Если хочешь оставить ONNX
# Но так как ты просил на базе HOG:
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cap = cv2.VideoCapture(0)
FRAME_W = 640
FRAME_H = 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)

TOTAL_AREA = FRAME_W * FRAME_H
last_sent_speed = -1

print("Система запущена. Нажмите 'q' для выхода.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1. Обнаружение (HOG)
    # winStride — шаг окна, padding — отступы, scale — коэффициент пирамиды кадров
    (rects, weights) = hog.detectMultiScale(frame, winStride=(8, 8), padding=(8, 8), scale=1.05)

    max_person_area_pct = 0

    # 2. Анализ найденных людей
    for (x, y, w, h) in rects:
        # Рисуем тонкую рамку (1 пиксель)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
        
        # Считаем площадь в %
        current_area_pct = (w * h) / TOTAL_AREA * 100
        if current_area_pct > max_person_area_pct:
            max_person_area_pct = current_area_pct

    # 3. ЛОГИКА СКОРОСТИ (Плавное замедление)
    if max_person_area_pct == 0:
        current_speed = 100  # Дорога пуста
    elif max_person_area_pct >= 5:
        current_speed = 0    # Человек слишком близко
    elif max_person_area_pct <= 0.3:
        current_speed = 100  # Человек очень далеко
    else:
        # Интерполяция: чем больше площадь (от 5 до 40), тем меньше скорость (от 100 до 0)
        ratio = (max_person_area_pct - 0.3) / (5 - 0.3)
        current_speed = int(100 * (1 - ratio))

    # 4. ОТПРАВКА В ARDUINO
    if ser and current_speed != last_sent_speed:
        try:
            ser.write(f"{current_speed}\n".encode('utf-8'))
            last_sent_speed = current_speed
            print(f"Sent: {current_speed} | Max Area: {max_person_area_pct:.1f}%")
        except Exception as e:
            print(f"Ошибка связи: {e}")

    # Визуализация данных
    color = (0, 255, 0) if current_speed > 0 else (0, 0, 255)
    cv2.putText(frame, f"Speed: {current_speed}%", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(frame, f"Area: {max_person_area_pct:.1f}%", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

    cv2.imshow('HOG Detection Control', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Остановка перед выходом
if ser:
    ser.write(f"0\n".encode('utf-8'))
    ser.close()

cap.release()
cv2.destroyAllWindows()h