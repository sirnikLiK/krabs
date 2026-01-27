import cv2

def main():
    # Инициализация HOG дескриптора
    hog = cv2.HOGDescriptor()
    
    # Установка коэффициентов SVM для детектора людей
    # Мы используем встроенную модель OpenCV (DefaultPeopleDetector)
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    # Попробуем разные индексы камер, если первый не сработал
    cam_index = 0
    cap = cv2.VideoCapture(cam_index)
    
    if not cap.isOpened():
        print(f"Ошибка: Не удалось открыть камеру с индексом {cam_index}")
        return

    # Настройка разрешения (опционально, может помочь с некоторыми камерами)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print(f"Камера {cam_index} открыта. Нажмите 'q' для выхода.")
    print("Если вы видите черное окно, подождите несколько секунд (камере нужно время на прогрев).")

    # Счетчик кадров для отладки
    frame_count = 0

    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Ошибка: Не удалось получить кадр.")
            break
            
        frame_count += 1
        
        # Проверка кадра на "пустоту" (черный экран)
        # Если среднее значение пикселей очень низкое, значит картинка черная
        if frame.mean() < 1.0:
            if frame_count % 30 == 0:
                print(f"Предупреждение: Кадр #{frame_count} почти полностью черный. Проверьте камеру.")
        
        # Детекция людей (может быть медленной, поэтому делаем не в каждом кадре или оптимизируем)
        # Для отладки черного экрана можно временно закомментировать detectMultiScale, 
        # но мы оставим, уменьшив масштаб для скорости.
        (rects, weights) = hog.detectMultiScale(frame, winStride=(8, 8), padding=(8, 8), scale=1.05)

        for (x, y, w, h) in rects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Human", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("Human Detector (OpenCV SVM)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Освобождение ресурсов
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
