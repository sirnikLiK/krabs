import cv2

# 0 — это индекс стандартной камеры. 
# Если у вас несколько камер, попробуйте 1, 2 и т.д.
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Ошибка: Не удалось открыть камеру.")
    exit()

print("Нажмите 'q', чтобы выйти.")

while True:
    # Захватываем кадр за кадром
    ret, frame = cap.read()

    # Если кадр прочитан верно, ret будет True
    if not ret:
        print("Ошибка: Не удается получить кадр.")
        break

    # Отображаем кадр в окне
    cv2.imshow('Camera View', frame)

    # Ждем нажатия клавиши 'q' для выхода
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождаем ресурсы
cap.release()
cv2.destroyAllWindows()