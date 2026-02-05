import cv2
import dlib
import numpy as np

model_path = "/home/stefano/Documents/ATS_nto/src/detection/models/tld_test.svm"
detector = dlib.simple_object_detector(model_path)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break

    boxes = detector(frame)
    for box in boxes:
        # Исходные координаты от dlib
        x1, y1, x2, y2 = box.left(), box.top(), box.right(), box.bottom()
        
        # Считаем размеры
        w = x2 - x1
        h = y2 - y1

        # --- НАСТРОЙКИ ПРИБЛИЖЕНИЯ (ЗУМ) ---
        # 0.05 - это 5% отступа с каждой стороны
        pad_w = int(w * 0.05) 
        pad_h_top = int(h * 0.05) # сверху чуть-чуть убираем рамку
        pad_h_bottom = int(h * 0.20) # убираем 20% снизу (подставка + рамка)

        # Новые координаты с учетом отступов
        nx1 = max(0, x1 + pad_w)
        nx2 = min(frame.shape[1], x2 - pad_w)
        ny1 = max(0, y1 + pad_h_top)
        ny2 = min(frame.shape[0], y2 - pad_h_bottom)

        # Вырезаем "чистый" светофор
        roi = frame[ny1:ny2, nx1:nx2]
        if roi.size == 0: continue

        # Масштабируем для анализа
        roi_viz = cv2.resize(roi, (150, 300))
        v = cv2.cvtColor(roi_viz, cv2.COLOR_BGR2HSV)[:, :, 2]

        # Зоны (теперь они считаются по "чистому" изображению)
        red_s = np.sum(v[0:100, :])
        yellow_s = np.sum(v[100:200, :])
        green_s = np.sum(v[200:300, :])

        # Логика цвета
        res_color = "WAIT"
        bgr = (255, 255, 255)
        if red_s > yellow_s and red_s > green_s:
            res_color = "RED"; bgr = (0, 0, 255)
        elif yellow_s > red_s and yellow_s > green_s:
            res_color = "YELLOW"; bgr = (0, 255, 255)
        elif green_s > red_s and green_s > yellow_s:
            res_color = "GREEN"; bgr = (0, 255, 0)

        # Рисуем сетку на отдельном окне
        cv2.rectangle(roi_viz, (0, 0), (149, 100), (0, 0, 255), 2)
        cv2.rectangle(roi_viz, (0, 100), (149, 200), (0, 255, 255), 2)
        cv2.rectangle(roi_viz, (0, 200), (149, 298), (0, 255, 0), 2)
        
        # Рисуем результат на основном кадре
        cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
        cv2.putText(frame, res_color, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, bgr, 2)

        cv2.imshow("Zoomed ROI", roi_viz)

    cv2.imshow("Main Feed", frame)
    if cv2.waitKey(1) == ord('q'): break

cap.release()
cv2.destroyAllWindows()