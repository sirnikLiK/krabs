import cv2
import numpy as np

# Инициализируем камеру (0 — стандартный индекс для встроенной вебки)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Ошибка: не удалось открыть камеру")
    exit()

print("Нажмите 'q' для выхода")

while True:
    # 1. Захватываем кадр
    ret, frame = cap.read()
    if not ret:
        break


    # 2. Подготовка: ч/б и размытие
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    # 3. Поиск кругов
    # Здесь param2 увеличено до 50, чтобы было меньше ложных срабатываний от шума камеры
    circles = cv2.HoughCircles(
        gray, 
        cv2.HOUGH_GRADIENT, 
        dp=1.2, 
        minDist=100,
        param1=100, 
        param2=85, 
        minRadius=20, 
        maxRadius=150
    )

    # 4. Визуализация
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # Рисуем контур круга
            cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # Рисуем точку в центре
            cv2.circle(frame, (i[0], i[1]), 2, (0, 0, 255), 3)
            # Выводим координаты центра рядом
            cv2.putText(frame, f"Center: {i[0]},{i[1]}", (i[0]-40, i[1]-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        

    # Выводим результат в окно
    cv2.imshow('Camera Hough Circles', frame)

    # Выход по клавише 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождаем ресурсы
cap.release()
cv2.destroyAllWindows()