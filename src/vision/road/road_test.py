import cv2

# 1. Захват видео с веб-камеры
cap = cv2.VideoCapture(0)

# 2. Определение кодека и создание объекта VideoWriter
# 'XVID' — распространенный кодек для .avi, 'mp4v' — для .mp4
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 3. Запись кадра
    out.write(frame)

    # Отображение (опционально)
    cv2.imshow('Recording', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 4. Освобождение ресурсов
cap.release()
out.release()
cv2.destroyAllWindows()
