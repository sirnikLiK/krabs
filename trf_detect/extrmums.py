import cv2
import numpy as np

def nothing(x):
    pass

cap = cv2.VideoCapture(1)

cv2.namedWindow('BGR_Settings')


# Трекбары для Синего, Зеленого и Красного
cv2.createTrackbar('B_min', 'BGR_Settings', 0, 255, nothing)
cv2.createTrackbar('G_min', 'BGR_Settings', 0, 255, nothing)
cv2.createTrackbar('R_min', 'BGR_Settings', 0, 255, nothing)
cv2.createTrackbar('B_max', 'BGR_Settings', 255, 255, nothing)
cv2.createTrackbar('G_max', 'BGR_Settings', 255, 255, nothing)
cv2.createTrackbar('R_max', 'BGR_Settings', 255, 255, nothing)

while True:
    ret, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if not ret:
        break

    # Считываем значения (в BGR порядке)
    b_min = cv2.getTrackbarPos('B_min', 'BGR_Settings')
    g_min = cv2.getTrackbarPos('G_min', 'BGR_Settings')
    r_min = cv2.getTrackbarPos('R_min', 'BGR_Settings')
    
    b_max = cv2.getTrackbarPos('B_max', 'BGR_Settings')
    g_max = cv2.getTrackbarPos('G_max', 'BGR_Settings')
    r_max = cv2.getTrackbarPos('R_max', 'BGR_Settings')

    # Создаем массивы порогов
    lower_bgr = np.array([b_min, g_min, r_min])
    upper_bgr = np.array([b_max, g_max, r_max])

    # Маска по BGR
    mask = cv2.inRange(hsv, lower_bgr, upper_bgr)
    
    # Результат (накладываем маску на оригинал)
    result = cv2.bitwise_and(hsv, hsv, mask=mask)

    cv2.imshow('BGR_Settings', result)
    cv2.imshow('Mask', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print(f"BGR Lower: [{b_min}, {g_min}, {r_min}]")
        print(f"BGR Upper: [{b_max}, {g_max}, {r_max}]")
        break

cap.release()
cv2.destroyAllWindows()