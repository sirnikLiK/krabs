import cv2

for i in range(4):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Камера найдена на индексе: {i}")
        cap.release()
    else:
        print(f"Индекс {i} не работает")